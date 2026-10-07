"""Score move quality with Stockfish on a matched sample of pairs.

A pair is a rapid win followed by the same player's next rapid game. The
unit of analysis is the pair, and the three groups are pairs whose first
game was a win on time, by checkmate or by resignation.

Sampling, all reproducible from --seed:
  1. Keep pairs whose next game is in the Elo band and reaches --min-ply,
     dropping players listed in --exclude (for example the pilot's players,
     so the confirmatory sample never reuses them).
  2. Keep at most one pair per player per group, chosen at random, so a
     player can appear in one, two or all three groups but never twice in one.
  3. Draw --n-per-group win-on-time pairs at random. Then draw the checkmate
     and resignation groups stratum by stratum to match the time group's mix
     of Elo (100-point bins) and time control. The time group is the
     reference because it is the smallest and the most different.

The previous game of every scored pair also gets one evaluation of its final
position (the previous-position covariate).

Output (in --out):
  scores.jsonl   one line per game, appended as games finish, so a stopped
                 run resumes where it left off
  sample.parquet the pairs selected for scoring

Usage:
  python src/centipawn_loss.py --pairs data/partial-pairs/pairs.parquet \
      --pgn data/2026-08 data/2026-09 --out data/pilot-scores \
      --elo-min 1200 --elo-max 2000 --n-per-group 200 --depth 15
"""

import argparse
import fcntl
import io
import json
import multiprocessing as mp
import os
import shutil
import sys
import time

import chess
import chess.engine
import chess.pgn
import numpy as np
import pandas as pd
import zstandard

sys.path.insert(0, os.path.dirname(__file__))
from engine_eval import engine_evals, final_eval, lichess_evals, move_losses, window_plies  # noqa: E402
from pgn_stream import iter_games  # noqa: E402

WIN_TYPES = ["time", "checkmate", "resign"]


def select_sample(pairs, elo_min, elo_max, min_ply, n_per_group, seed, exclude=()):
    rng = np.random.default_rng(seed)
    p = pairs[(pairs.elo >= elo_min) & (pairs.elo < elo_max) & (pairs.n_ply >= min_ply)
              & ~pairs.player.isin(set(exclude))].copy()
    p["_r"] = rng.random(len(p))
    p = p.sort_values("_r").groupby(["player", "prev_win_type"]).head(1)
    p["stratum"] = (p.elo // 100 * 100).astype(int).astype(str) + "|" + p.time_control

    groups = {t: g for t, g in p.groupby("prev_win_type")}
    ref = groups["time"].head(n_per_group)  # already in random order
    target = ref.stratum.value_counts()
    chosen, shortfall = [ref], {}
    for t in ("checkmate", "resign"):
        g = groups[t]
        picked = []
        for stratum, k in target.items():
            avail = g[g.stratum == stratum]
            picked.append(avail.head(k))
            if len(avail) < k:
                shortfall[t] = shortfall.get(t, 0) + k - len(avail)
        chosen.append(pd.concat(picked))
    out = pd.concat(chosen).drop(columns="_r")
    for t, k in shortfall.items():
        print(f"warning: {t} group is {k} pairs short of the time group's strata")
    return out.sort_values(["prev_win_type", "player"]).reset_index(drop=True)


def collect_pgns(pgn_dirs, wanted):
    found = {}
    for d in pgn_dirs:
        stream = zstandard.ZstdDecompressor().stream_reader(open(os.path.join(d, "rapid.pgn.zst"), "rb"))
        for headers, movetext, _ in iter_games(stream):
            gid = headers.get("Site", "").rsplit("/", 1)[-1]
            if gid in wanted and gid not in found:
                found[gid] = movetext
                if len(found) == len(wanted):
                    return found
    return found


_engine = None


def _worker_init(engine_path, hash_mb):
    global _engine
    _engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    # One thread per process: multi-threaded search is not reproducible.
    _engine.configure({"Threads": 1, "Hash": hash_mb})


def score_game(job):
    gid, movetext, need_window, need_final, cfg = job
    game = chess.pgn.read_game(io.StringIO(movetext))
    moves = list(game.mainline_moves())
    n_ply = len(moves)
    row = {"game_id": gid, "n_ply": n_ply, "depth": cfg["depth"]}
    t0 = time.time()
    if need_window:
        lo, hi = window_plies(cfg["first_move"], cfg["last_move"], n_ply)
        if hi > lo:
            evals = engine_evals(_engine, moves, lo, hi, cfg["depth"], gid)
            losses = move_losses(evals, lo, cfg["cap"])
            row.update(window_lo=lo, evals=evals, white_losses=losses["white"], black_losses=losses["black"])
            lich = lichess_evals(movetext)
            if len(lich) > hi and all(e is not None for e in lich[lo:hi + 1]):
                ll = move_losses(lich[lo:hi + 1], lo, cfg["cap"])
                row.update(lichess_white_losses=ll["white"], lichess_black_losses=ll["black"])
    if need_final:
        row["final_eval"] = final_eval(_engine, moves, cfg["depth"], gid + ":final")
    row["seconds"] = round(time.time() - t0, 3)
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--pgn", nargs="+", required=True, help="fetch_month.py output directories")
    ap.add_argument("--out", required=True)
    ap.add_argument("--elo-min", type=int, required=True)
    ap.add_argument("--elo-max", type=int, required=True)
    ap.add_argument("--min-ply", type=int, default=30)
    ap.add_argument("--n-per-group", type=int, required=True, help="pairs per win type")
    ap.add_argument("--exclude", nargs="*", default=[],
                    help="sample.parquet files whose players must not be reused")
    ap.add_argument("--depth", type=int, default=15)
    ap.add_argument("--first-move", type=int, default=15)
    ap.add_argument("--last-move", type=int, default=30)
    ap.add_argument("--cap", type=int, default=1000, help="eval cap in centipawns")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--hash-mb", type=int, default=64)
    ap.add_argument("--seed", type=int, default=20261007)
    ap.add_argument("--engine", default=shutil.which("stockfish") or "/usr/games/stockfish")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    # One scorer per output directory: two copies appending to the same file
    # waste half the CPU and can interleave partial lines.
    lock = open(os.path.join(args.out, ".lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit(f"another centipawn_loss.py is already scoring into {args.out}")
    pairs = pd.read_parquet(args.pairs)
    exclude = set()
    for path in args.exclude:
        exclude |= set(pd.read_parquet(path, columns=["player"]).player)
    sample_path = os.path.join(args.out, "sample.parquet")
    if os.path.exists(sample_path):
        # Resuming: never redraw, or a rerun with different inputs would mix samples.
        sample = pd.read_parquet(sample_path)
    else:
        sample = select_sample(pairs, args.elo_min, args.elo_max, args.min_ply,
                               args.n_per_group, args.seed, exclude)
        sample.to_parquet(sample_path, index=False)
    counts = sample.prev_win_type.value_counts().to_dict()
    print(f"sample: {len(sample):,} pairs {counts}, {sample.player.nunique():,} players, "
          f"{len(exclude):,} players excluded")

    window_ids = set(sample.game_id)
    final_ids = set(sample.prev_game_id)
    out_path = os.path.join(args.out, "scores.jsonl")
    done = set()
    if os.path.exists(out_path):
        with open(out_path) as f:
            done = {json.loads(line)["game_id"] for line in f if line.strip()}
    todo = (window_ids | final_ids) - done
    print(f"games to score: {len(todo):,} ({len(done):,} already done)")
    if not todo:
        return

    pgns = collect_pgns(args.pgn, todo)
    missing = todo - set(pgns)
    if missing:
        print(f"warning: {len(missing):,} games not found in the PGN inputs")

    cfg = {k: getattr(args, k) for k in ("depth", "first_move", "last_move", "cap")}
    jobs = [(gid, pgns[gid], gid in window_ids, gid in final_ids, cfg) for gid in sorted(pgns)]
    t0 = time.time()
    fd = os.open(out_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    with mp.Pool(args.workers, initializer=_worker_init, initargs=(args.engine, args.hash_mb)) as pool:
        for i, row in enumerate(pool.imap_unordered(score_game, jobs, chunksize=4), 1):
            # One write per line, so a crash never leaves half a line behind.
            os.write(fd, (json.dumps(row) + "\n").encode())
            if i % 200 == 0 or i == len(jobs):
                rate = i / (time.time() - t0)
                eta = (len(jobs) - i) / rate / 3600
                print(f"{i:,}/{len(jobs):,} games, {rate:.2f} games/s, {eta:.1f} h left", flush=True)
    os.close(fd)


if __name__ == "__main__":
    main()
