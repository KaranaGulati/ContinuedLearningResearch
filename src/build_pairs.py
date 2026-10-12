"""Link every eligible game to how the same player's previous game ended.

Reads games.tsv.zst from one or more fetch_month.py outputs (pass consecutive
months so sequences carry across the boundary), and writes:

  pairs.parquet       one row per (player, game) whose immediately preceding
                      game was a rapid win by that player on time, by
                      checkmate or by resignation, within the session cutoff
  cell_counts.txt     group sizes, overall and by time control and Elo band

"Previous game" means the previous rated game of any speed. A blitz game in
between breaks the link, because its outcome is the one carried in.

This stage uses no engine output and does not touch the dependent variable,
so running it before preregistration only reveals sample sizes.

Usage:
  python src/build_pairs.py data/2025-03 data/2025-04 --out data/pairs
"""

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from pyarrow import csv as pacsv

WIN_TYPES = ["time", "checkmate", "resign"]

COLUMN_TYPES = {
    "game_id": pa.string(), "white": pa.string(), "black": pa.string(),
    "start_ts": pa.int64(), "speed": pa.string(), "eligible": pa.int8(),
    "tc_base": pa.int32(), "tc_inc": pa.int32(), "white_elo": pa.int32(),
    "black_elo": pa.int32(), "result": pa.string(), "termination": pa.string(),
    "winner": pa.string(), "win_type": pa.string(), "n_ply": pa.int32(),
    "duration_s": pa.float64(), "white_first_clk": pa.float64(),
    "black_first_clk": pa.float64(), "has_clk": pa.int8(), "has_eval": pa.int8(),
}


def check_complete(dirs, allow_partial):
    """Refuse months whose download did not finish, unless told otherwise."""
    for d in dirs:
        path = os.path.join(d, "meta.json")
        meta = json.load(open(path)) if os.path.exists(path) else None
        if meta and meta.get("complete"):
            continue
        reason = "no meta.json" if meta is None else (meta.get("error") or "stopped at --max-games")
        if not allow_partial:
            sys.exit(f"{d} is not a complete month ({reason}). Pass --allow-partial for pilot runs.")
        print(f"warning: {d} is partial ({reason})", file=sys.stderr)


USE_COLUMNS = ["game_id", "white", "black", "start_ts", "eligible", "tc_base", "tc_inc",
               "white_elo", "black_elo", "winner", "win_type", "n_ply", "duration_s", "has_eval"]
WIN_CODE = {"time": 1, "checkmate": 2, "resign": 3}


class Games:
    """Compact column store for a month of games: numpy arrays, player names as codes."""


def read_games(dirs, chunk_rows=2_000_000):
    """Read games.tsv.zst in fixed-size chunks and keep compact arrays only.

    A full month is ~90M rows. Arrow's CSV readers hold far more than that in
    memory (the one-shot reader needs ~14 GB), so pandas reads 2M-row chunks
    from a zstd stream and each chunk is reduced to numpy codes and freed.
    """
    import zstandard

    name_code, names = {}, []
    parts = {k: [] for k in ["game_id", "white", "black", "start", "eligible", "tc_base", "tc_inc",
                             "white_elo", "black_elo", "winner", "win_type", "n_ply", "duration", "has_eval"]}
    dtypes = {"game_id": str, "white": str, "black": str, "winner": str, "win_type": str,
              "start_ts": "float64", "eligible": "float64", "tc_base": "float64", "tc_inc": "float64",
              "white_elo": "float64", "black_elo": "float64", "n_ply": "float64",
              "duration_s": "float64", "has_eval": "float64"}

    def encode(col):
        uniq = pd.unique(col)
        lookup = np.empty(len(uniq), np.int32)
        for i, name in enumerate(uniq):
            code = name_code.get(name)
            if code is None:
                code = name_code[name] = len(names)
                names.append(name)
            lookup[i] = code
        return lookup[pd.Index(uniq).get_indexer(col)]

    for d in dirs:
        raw = zstandard.ZstdDecompressor().stream_reader(open(os.path.join(d, "games.tsv.zst"), "rb"))
        for ch in pd.read_csv(raw, sep="\t", usecols=USE_COLUMNS, dtype=dtypes, chunksize=chunk_rows,
                              keep_default_na=False, na_values=[""], quoting=3, engine="c"):
            ch = ch[ch.start_ts.notna()]
            parts["game_id"].append(ch.game_id.fillna("").to_numpy().astype("S8"))
            parts["white"].append(encode(ch.white.fillna("").to_numpy()))
            parts["black"].append(encode(ch.black.fillna("").to_numpy()))
            parts["start"].append(ch.start_ts.to_numpy().astype(np.int64))
            parts["eligible"].append(ch.eligible.fillna(0).to_numpy().astype(bool))
            parts["tc_base"].append(ch.tc_base.fillna(-1).to_numpy().astype(np.int32))
            parts["tc_inc"].append(ch.tc_inc.fillna(-1).to_numpy().astype(np.int32))
            parts["white_elo"].append(ch.white_elo.to_numpy().astype(np.float32))
            parts["black_elo"].append(ch.black_elo.to_numpy().astype(np.float32))
            w = ch.winner.fillna("").to_numpy()
            parts["winner"].append((w == "white").astype(np.int8) + 2 * (w == "black").astype(np.int8))
            wt = ch.win_type.fillna("").to_numpy()
            code = np.zeros(len(ch), np.int8)
            for label, v in WIN_CODE.items():
                code[wt == label] = v
            parts["win_type"].append(code)
            parts["n_ply"].append(ch.n_ply.fillna(0).to_numpy().astype(np.int32))
            parts["duration"].append(ch.duration_s.fillna(0).to_numpy().astype(np.float32))
            parts["has_eval"].append(ch.has_eval.fillna(0).to_numpy().astype(np.int8))
            del ch

    G = Games()
    for k, v in parts.items():
        setattr(G, k, np.concatenate(v) if v else np.array([]))
        v.clear()
    G.names = np.array(names, dtype=object)
    G.n = len(G.start)
    if len(dirs) > 1:  # the same game can appear twice if overlapping inputs were passed
        _, first = np.unique(G.game_id, return_index=True)
        keep = np.sort(first)
        for k in parts:
            setattr(G, k, getattr(G, k)[keep])
        G.n = len(keep)
    return G


def _bool(arr):
    return pc.fill_null(arr, False).to_numpy(zero_copy_only=False)


def build_pairs(G, cutoff_s, min_gap_s):
    """Return a DataFrame of valid (previous win, current game) pairs.

    Rows are (game, colour); row i < n is White in game i and row n + i is
    Black, so a row's colour follows from its position in the sort.
    """
    n = G.n
    t0 = int(G.start.min()) if n else 0
    start_rel = (G.start - t0).astype(np.int32)
    end_rel = start_rel.astype(np.int64) + G.duration.astype(np.int64)

    player_code = np.concatenate([G.white, G.black])
    gidx = np.concatenate([np.arange(n, dtype=np.int32), np.arange(n, dtype=np.int32)])
    order = np.lexsort((gidx, start_rel[gidx], player_code))
    p = player_code[order]
    g = gidx[order]
    c = (order >= n).astype(np.int8)  # 0 white, 1 black
    del order, gidx, player_code

    prev_g, cur_g, prev_c = g[:-1], g[1:], c[:-1]
    mask = p[1:] == p[:-1]
    mask &= G.eligible[prev_g]
    mask &= G.eligible[cur_g]
    mask &= G.win_type[prev_g] > 0
    mask &= G.winner[prev_g] == prev_c + 1
    k = np.flatnonzero(mask)
    del mask
    gap = start_rel[cur_g[k]].astype(np.int64) - end_rel[prev_g[k]]
    ok = (gap >= min_gap_s) & (gap <= cutoff_s)
    k, gap = k[ok], gap[ok]

    cg, pg = cur_g[k], prev_g[k]
    cc, pc_ = c[1:][k], prev_c[k]
    labels = np.array(["", "time", "checkmate", "resign"], dtype=object)
    winner_name = np.array(["", "white", "black"], dtype=object)
    opp_cur = np.where(cc == 0, G.black[cg], G.white[cg])
    opp_prev = np.where(pc_ == 0, G.black[pg], G.white[pg])
    return pd.DataFrame({
        "player": G.names[p[1:][k]],
        "color": np.where(cc == 0, "white", "black"),
        "game_id": G.game_id[cg].astype(str),
        "prev_game_id": G.game_id[pg].astype(str),
        "prev_win_type": labels[G.win_type[pg]],
        "prev_color": np.where(pc_ == 0, "white", "black"),
        "gap_s": gap,
        "rematch": opp_cur == opp_prev,
        "start_ts": start_rel[cg].astype(np.int64) + t0,
        "time_control": [f"{b}+{i}" for b, i in zip(G.tc_base[cg], G.tc_inc[cg])],
        "elo": np.where(cc == 0, G.white_elo[cg], G.black_elo[cg]).astype(np.float64),
        "opp_elo": np.where(cc == 0, G.black_elo[cg], G.white_elo[cg]).astype(np.float64),
        "result_for_player": _result_for(winner_name[G.winner[cg]], cc),
        "n_ply": G.n_ply[cg],
        "has_eval": G.has_eval[cg],
    })


def _result_for(winner, color):
    # Draws have an empty winner, which reads back as null.
    winner = np.array(["" if w is None else w for w in winner], dtype=object)
    side = np.where(color == 0, "white", "black")
    return np.where(winner == "", "draw", np.where(winner == side, "win", "loss"))


def cell_counts(pairs, min_ply):
    lines = []

    def block(title, df):
        counts = df.groupby("prev_win_type").size().reindex(WIN_TYPES, fill_value=0)
        per_player = df.groupby(["player", "prev_win_type"]).size().unstack(fill_value=0)
        per_player = per_player.reindex(columns=WIN_TYPES, fill_value=0)
        complete = int((per_player > 0).all(axis=1).sum())
        lines.append(f"## {title}")
        lines.append(f"pairs: " + ", ".join(f"{t}={counts[t]:,}" for t in WIN_TYPES))
        lines.append(f"players with any pair: {len(per_player):,}")
        lines.append(f"players with all three conditions: {complete:,}")
        lines.append("")

    block("All pairs", pairs)
    long_enough = pairs[pairs["n_ply"] >= min_ply]
    block(f"Current game reaches ply {min_ply}", long_enough)

    lines.append("## By time control (current game reaches ply %d), top 10" % min_ply)
    for tc, df in sorted(long_enough.groupby("time_control"), key=lambda kv: -len(kv[1]))[:10]:
        per_player = df.groupby(["player", "prev_win_type"]).size().unstack(fill_value=0)
        per_player = per_player.reindex(columns=WIN_TYPES, fill_value=0)
        counts = per_player.sum()
        lines.append(f"{tc:>8}: " + ", ".join(f"{t}={counts[t]:,}" for t in WIN_TYPES)
                     + f", complete players={int((per_player > 0).all(axis=1).sum()):,}")
    lines.append("")

    lines.append("## By Elo band of the player (current game reaches ply %d)" % min_ply)
    bands = pd.cut(long_enough["elo"], bins=list(range(400, 3201, 200)), right=False)
    for band, df in long_enough.groupby(bands, observed=True):
        per_player = df.groupby(["player", "prev_win_type"]).size().unstack(fill_value=0)
        per_player = per_player.reindex(columns=WIN_TYPES, fill_value=0)
        counts = per_player.sum()
        lines.append(f"{str(band):>14}: " + ", ".join(f"{t}={counts[t]:,}" for t in WIN_TYPES)
                     + f", complete players={int((per_player > 0).all(axis=1).sum()):,}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="+", help="fetch_month.py output directories")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cutoff-min", type=float, default=30.0,
                    help="max minutes between previous game's end and this game's start")
    ap.add_argument("--min-gap-s", type=float, default=-60.0,
                    help="tolerance for clock-based end times running slightly late")
    ap.add_argument("--allow-partial", action="store_true",
                    help="accept inputs whose download did not finish (pilot runs only)")
    ap.add_argument("--min-ply", type=int, default=30,
                    help="plies the current game must reach for moves 15-30 to exist")
    args = ap.parse_args()

    check_complete(args.dirs, args.allow_partial)
    os.makedirs(args.out, exist_ok=True)
    table = read_games(args.dirs)
    pairs = build_pairs(table, args.cutoff_min * 60, args.min_gap_s)
    pairs.to_parquet(os.path.join(args.out, "pairs.parquet"), index=False)

    report = (f"# Cell counts\n\ninputs: {', '.join(args.dirs)}\n"
              f"games read: {table.n:,}\nsession cutoff: {args.cutoff_min} min\n\n"
              + cell_counts(pairs, args.min_ply))
    with open(os.path.join(args.out, "cell_counts.txt"), "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
