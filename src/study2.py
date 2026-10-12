"""Study 2: screen time wins for luck, then draw the five groups.

Follows PREREGISTRATION_STUDY2.md (fixed 2026-10-12).

  screen  Put the eligible win-on-time pairs (one per player) in a random
          order fixed by the seed, and score the final position of each
          winning game with Stockfish in that order until 13,000 are lucky
          (winner losing by more than 1 pawn). Appends to screen.jsonl, so a
          stopped run resumes.
  sample  Build the groups: rq1_time (first 6,500 screened), rq1_checkmate
          and rq1_resign (6,500 each, matched to rq1_time), rq2_lucky (first
          13,000 lucky) and rq2_deserved (13,000 non-lucky, matched to
          rq2_lucky). Writes sample.parquet, one row per pair per group.

Usage:
  python src/study2.py screen --pairs data/full-pairs-09/pairs.parquet --pgn data/full-2026-09 --out data/study2
  python src/study2.py sample --pairs data/full-pairs-09/pairs.parquet --out data/study2
"""

import argparse
import fcntl
import io
import json
import multiprocessing as mp
import os
import shutil
import sys
from datetime import datetime, timezone

import chess.pgn
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from centipawn_loss import collect_pgns  # noqa: E402
import engine_eval  # noqa: E402

SEED = 20261012
START = datetime(2026, 9, 6, tzinfo=timezone.utc).timestamp()
END = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()
ELO_MIN, ELO_MAX, MIN_PLY = 1200, 2000, 30
LUCKY_CP, CAP = -100, 1000
N_RQ1, N_RQ2 = 6500, 13000


def eligible_pairs(pairs):
    return pairs[(pairs.start_ts >= START) & (pairs.start_ts < END) & (pairs.elo >= ELO_MIN)
                 & (pairs.elo < ELO_MAX) & (pairs.n_ply >= MIN_PLY)]


def one_per_player(df, rng):
    """Random order, then the first pair of each player; the order is kept."""
    df = df.assign(_r=rng.random(len(df))).sort_values("_r")
    return df.drop_duplicates("player").drop(columns="_r").reset_index(drop=True)


def stratum(df):
    return (df.elo // 100 * 100).astype(int).astype(str) + "|" + df.time_control


def matched_take(pool, target, rng):
    """From pool, draw at random the same number of pairs per stratum as target has."""
    pool = pool.assign(_s=stratum(pool), _r=rng.random(len(pool))).sort_values("_r")
    need = stratum(target).value_counts()
    taken = [pool[pool._s == s].head(k) for s, k in need.items()]
    out = pd.concat(taken).drop(columns=["_s", "_r"])
    short = int(need.sum() - len(out))
    if short:
        print(f"warning: matched draw is {short} pairs short of the target's strata")
    return out


def winner_view(final_white, prev_color):
    v = max(-CAP, min(CAP, final_white))
    return v if prev_color == "white" else -v


_engine = None


def _init(engine_path):
    global _engine
    import chess.engine
    _engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    _engine.configure({"Threads": 1, "Hash": 64})


def _score(job):
    gid, movetext = job
    moves = list(chess.pgn.read_game(io.StringIO(movetext)).mainline_moves())
    return gid, engine_eval.final_eval(_engine, moves, 15, gid + ":final")


def screen(args):
    os.makedirs(args.out, exist_ok=True)
    lock = open(os.path.join(args.out, ".lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit(f"another study2.py is already running in {args.out}")

    order_path = os.path.join(args.out, "screen_order.parquet")
    if os.path.exists(order_path):
        order = pd.read_parquet(order_path)
    else:
        rng = np.random.default_rng(SEED)
        p = eligible_pairs(pd.read_parquet(args.pairs))
        order = one_per_player(p[p.prev_win_type == "time"], rng)
        order["screen_rank"] = np.arange(len(order))
        order.to_parquet(order_path, index=False)
    print(f"time-win pairs in screening order: {len(order):,}")

    out_path = os.path.join(args.out, "screen.jsonl")
    done = {}
    if os.path.exists(out_path):
        for line in open(out_path):
            r = json.loads(line)
            done[r["prev_game_id"]] = r
    colour = dict(zip(order.prev_game_id, order.prev_color))
    lucky = sum(r["lucky"] for r in done.values())
    print(f"already screened: {len(done):,}, lucky so far: {lucky:,}")

    fd = os.open(out_path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    start = len(done)
    while lucky < N_RQ2 and start < len(order):
        # Screening is strictly in rank order, so "the first N" is well defined.
        block = order.iloc[start:start + args.block]
        todo = [g for g in block.prev_game_id if g not in done]
        pgns = collect_pgns(args.pgn, set(todo))
        jobs = [(g, pgns[g]) for g in todo if g in pgns]
        with mp.Pool(args.workers, initializer=_init, initargs=(args.engine,)) as pool:
            results = dict(pool.imap_unordered(_score, jobs, chunksize=8))
        for g in block.prev_game_id:
            if g in done or g not in results:
                continue
            v = winner_view(results[g], colour[g])
            row = {"prev_game_id": g, "final_eval_winner": v, "lucky": v < LUCKY_CP}
            done[g] = row
            os.write(fd, (json.dumps(row) + "\n").encode())
        lucky = sum(r["lucky"] for r in done.values())
        start += len(block)
        print(f"screened {start:,} in order, lucky {lucky:,} ({100 * lucky / max(1, len(done)):.1f}%)", flush=True)
    os.close(fd)


def sample(args):
    rng = np.random.default_rng(SEED + 1)
    order = pd.read_parquet(os.path.join(args.out, "screen_order.parquet"))
    rows = [json.loads(l) for l in open(os.path.join(args.out, "screen.jsonl"))]
    sc = order.merge(pd.DataFrame(rows), on="prev_game_id").sort_values("screen_rank")
    lucky = sc[sc.lucky]
    if len(lucky) < N_RQ2:
        sys.exit(f"only {len(lucky):,} lucky pairs screened; run screen first")
    lucky = lucky.head(N_RQ2)
    last_rank = lucky.screen_rank.max()
    screened = sc[sc.screen_rank <= last_rank]  # the contiguous screened prefix

    p = eligible_pairs(pd.read_parquet(args.pairs))
    groups = {"rq1_time": screened.head(N_RQ1)}
    for t in ("checkmate", "resign"):
        pool = one_per_player(p[p.prev_win_type == t], rng)
        groups[f"rq1_{t}"] = matched_take(pool, groups["rq1_time"], rng)
    groups["rq2_lucky"] = lucky
    groups["rq2_deserved"] = matched_take(screened[~screened.lucky], lucky, rng)

    out = pd.concat([g.assign(group=name) for name, g in groups.items()], ignore_index=True)
    out.to_parquet(os.path.join(args.out, "sample.parquet"), index=False)
    print(out.group.value_counts().to_dict(), f"unique next games to score: {out.game_id.nunique():,}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=["screen", "sample"])
    ap.add_argument("--pairs", required=True)
    ap.add_argument("--pgn", nargs="+", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--block", type=int, default=20000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--engine", default=shutil.which("stockfish") or "/usr/games/stockfish")
    args = ap.parse_args()
    screen(args) if args.step == "screen" else sample(args)


if __name__ == "__main__":
    main()
