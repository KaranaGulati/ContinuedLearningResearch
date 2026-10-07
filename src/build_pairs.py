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
import os

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


def read_games(dirs):
    tables = []
    for d in dirs:
        stream = pa.input_stream(os.path.join(d, "games.tsv.zst"), compression="zstd")
        tables.append(pacsv.read_csv(
            stream,
            parse_options=pacsv.ParseOptions(delimiter="\t", quote_char=False),
            convert_options=pacsv.ConvertOptions(
                column_types=COLUMN_TYPES, strings_can_be_null=True,
                null_values=[""], quoted_strings_can_be_null=True),
        ))
    table = pa.concat_tables(tables)
    table = table.filter(pc.is_valid(table["start_ts"]))
    # The same game can appear twice if overlapping inputs were passed.
    if len(dirs) > 1:
        _, first = np.unique(table["game_id"].to_numpy(zero_copy_only=False), return_index=True)
        table = table.take(np.sort(first))
    return table


def build_pairs(table, cutoff_s, min_gap_s):
    """Return a DataFrame of valid (previous win, current game) pairs."""
    n = table.num_rows
    names = pa.chunked_array(table["white"].chunks + table["black"].chunks)
    player = pc.dictionary_encode(names).combine_chunks()
    player_code = player.indices.to_numpy()
    player_names = player.dictionary
    # Row i < n is White in game i, row n + i is Black in game i, so swapping
    # the halves gives each row's opponent.
    opponent_code = np.concatenate([player_code[n:], player_code[:n]])

    start = table["start_ts"].to_numpy().astype(np.int64)
    duration = np.nan_to_num(table["duration_s"].to_numpy(zero_copy_only=False).astype(float))
    end = start + duration.astype(np.int64)
    game_idx = np.concatenate([np.arange(n), np.arange(n)])
    color = np.concatenate([np.zeros(n, np.int8), np.ones(n, np.int8)])  # 0 white, 1 black
    start2 = np.concatenate([start, start])
    end2 = np.concatenate([end, end])

    order = np.lexsort((game_idx, start2, player_code))
    p, g, c = player_code[order], game_idx[order], color[order]
    o = opponent_code[order]
    s, e = start2[order], end2[order]

    same_player = p[1:] == p[:-1]
    prev_g, prev_c, prev_end = g[:-1], c[:-1], e[:-1]
    cur_g, cur_c, cur_start = g[1:], c[1:], s[1:]
    gap = cur_start - prev_end

    eligible = table["eligible"].to_numpy(zero_copy_only=False).astype(bool)
    winner = table["winner"].to_numpy(zero_copy_only=False)
    win_type = table["win_type"].to_numpy(zero_copy_only=False)
    prev_won = np.where(prev_c == 0, winner[prev_g] == "white", winner[prev_g] == "black")
    prev_type_ok = np.isin(win_type[prev_g], WIN_TYPES)

    keep = (same_player & eligible[prev_g] & eligible[cur_g] & prev_won & prev_type_ok
            & (gap >= min_gap_s) & (gap <= cutoff_s))
    k = np.flatnonzero(keep)
    cg, cc, pg = cur_g[k], cur_c[k], prev_g[k]

    def col(name):
        return table[name].to_numpy(zero_copy_only=False)

    white_elo, black_elo = col("white_elo"), col("black_elo")
    return pd.DataFrame({
        "player": player_names.take(pa.array(p[1:][k])).to_numpy(zero_copy_only=False),
        "color": np.where(cc == 0, "white", "black"),
        "game_id": col("game_id")[cg],
        "prev_game_id": col("game_id")[pg],
        "prev_win_type": win_type[pg],
        "prev_color": np.where(prev_c[k] == 0, "white", "black"),
        "gap_s": gap[k],
        "rematch": o[1:][k] == o[:-1][k],
        "start_ts": cur_start[k],
        "time_control": [f"{int(b)}+{int(i)}" for b, i in zip(col("tc_base")[cg], col("tc_inc")[cg])],
        "elo": np.where(cc == 0, white_elo[cg], black_elo[cg]),
        "opp_elo": np.where(cc == 0, black_elo[cg], white_elo[cg]),
        "result_for_player": _result_for(col("winner")[cg], cc),
        "n_ply": col("n_ply")[cg],
        "has_eval": col("has_eval")[cg],
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
    ap.add_argument("--min-ply", type=int, default=30,
                    help="plies the current game must reach for moves 15-30 to exist")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    table = read_games(args.dirs)
    pairs = build_pairs(table, args.cutoff_min * 60, args.min_gap_s)
    pairs.to_parquet(os.path.join(args.out, "pairs.parquet"), index=False)

    report = (f"# Cell counts\n\ninputs: {', '.join(args.dirs)}\n"
              f"games read: {table.num_rows:,}\nsession cutoff: {args.cutoff_min} min\n\n"
              + cell_counts(pairs, args.min_ply))
    with open(os.path.join(args.out, "cell_counts.txt"), "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
