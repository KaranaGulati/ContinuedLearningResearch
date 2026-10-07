"""Score move quality with Stockfish on a random sample of players.

Sampling: players are drawn at random from those who, after the Elo band and
game-length filters, have at least one pair in each of the three conditions.
For each sampled player at most --max-per-cell games per condition are
scored, drawn at random. The previous game of every scored pair also gets a
single evaluation of its final position (the previous-position covariate).

Output (in --out):
  scores.jsonl   one line per game, appended as games finish, so a stopped
                 run resumes where it left off
  sample.parquet the pairs that were selected for scoring

Usage:
  python src/centipawn_loss.py --pairs data/pairs/pairs.parquet \
      --pgn data/2025-03 data/2025-04 --out data/scores \
      --elo-min 1200 --elo-max 2000 --n-players 3000 --depth 15
"""

import argparse
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


def select_sample(pairs, elo_min, elo_max, min_ply, n_players, max_per_cell, seed):
    rng = np.random.default_rng(seed)
    p = pairs[(pairs.elo >= elo_min) & (pairs.elo < elo_max) & (pairs.n_ply >= min_ply)]
    cells = p.groupby(["player", "prev_win_type"]).size().unstack(fill_value=0)
    cells = cells.reindex(columns=WIN_TYPES, fill_value=0)
    complete = np.array(sorted(cells.index[(cells > 0).all(axis=1)]))
    chosen = set(rng.permutation(complete)[:n_players]) if n_players else set(complete)
    p = p[p.player.isin(chosen)]
    # Random cap per player x condition, reproducible from the seed.
    p = p.assign(_r=rng.random(len(p))).sort_values("_r")
    p = p.groupby(["player", "prev_win_type"], group_keys=False).head(max_per_cell)
    return p.drop(columns="_r").sort_values(["player", "start_ts"]).reset_index(drop=True)


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
    ap.add_argument("--n-players", type=int, default=0, help="0 = every complete player")
    ap.add_argument("--max-per-cell", type=int, default=5)
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
    pairs = pd.read_parquet(args.pairs)
    sample = select_sample(pairs, args.elo_min, args.elo_max, args.min_ply,
                           args.n_players, args.max_per_cell, args.seed)
    sample.to_parquet(os.path.join(args.out, "sample.parquet"), index=False)
    print(f"sample: {sample.player.nunique():,} players, {len(sample):,} pairs")

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
    with mp.Pool(args.workers, initializer=_worker_init, initargs=(args.engine, args.hash_mb)) as pool, \
            open(out_path, "a") as out:
        for i, row in enumerate(pool.imap_unordered(score_game, jobs, chunksize=4), 1):
            out.write(json.dumps(row) + "\n")
            if i % 200 == 0 or i == len(jobs):
                out.flush()
                rate = i / (time.time() - t0)
                eta = (len(jobs) - i) / rate / 3600
                print(f"{i:,}/{len(jobs):,} games, {rate:.2f} games/s, {eta:.1f} h left", flush=True)


if __name__ == "__main__":
    main()
