"""Measure Stockfish seconds per position on this machine and project run time.

Takes the first --n-games eligible games that reach --min-ply from a
fetch_month.py output, evaluates the moves 15-30 window at each depth, and
prints the projected wall-clock time for several sample sizes, counting
one window per scored game plus one final-position eval per previous game.

Usage:
  python src/benchmark_stockfish.py data/2025-03 --depths 12 15 18
"""

import argparse
import io
import os
import shutil
import sys
import time

import chess.engine
import chess.pgn
import zstandard

sys.path.insert(0, os.path.dirname(__file__))
from engine_eval import engine_evals, window_plies  # noqa: E402
from pgn_stream import iter_games  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pgn_dir")
    ap.add_argument("--n-games", type=int, default=20)
    ap.add_argument("--depths", type=int, nargs="+", default=[12, 15, 18])
    ap.add_argument("--min-ply", type=int, default=30)
    ap.add_argument("--workers", type=int, default=os.cpu_count(),
                    help="parallel engine processes assumed for the projection")
    ap.add_argument("--engine", default=shutil.which("stockfish") or "/usr/games/stockfish")
    args = ap.parse_args()

    stream = zstandard.ZstdDecompressor().stream_reader(open(os.path.join(args.pgn_dir, "rapid.pgn.zst"), "rb"))
    games = []
    for headers, movetext, _ in iter_games(stream):
        moves = list(chess.pgn.read_game(io.StringIO(movetext)).mainline_moves())
        if len(moves) >= args.min_ply:
            games.append((headers["Site"].rsplit("/", 1)[-1], moves))
        if len(games) == args.n_games:
            break

    engine = chess.engine.SimpleEngine.popen_uci(args.engine)
    engine.configure({"Threads": 1, "Hash": 64})
    print(f"{engine.id.get('name')}, {len(games)} games, 1 thread per engine, {args.workers} workers assumed\n")
    print(f"{'depth':>5} {'positions':>9} {'s/position':>10} {'s/game':>7}   projected hours for N scored games")
    sizes = [10_000, 30_000, 100_000]
    for depth in args.depths:
        n_pos, t0 = 0, time.time()
        for gid, moves in games:
            lo, hi = window_plies(15, 30, len(moves))
            n_pos += len(engine_evals(engine, moves, lo, hi, depth, f"{gid}:{depth}"))
        spp = (time.time() - t0) / n_pos
        per_game = spp * (n_pos / len(games) + 1)  # + one final-position eval of the previous game
        proj = "  ".join(f"N={n:,}: {per_game * n / args.workers / 3600:.1f}h" for n in sizes)
        print(f"{depth:>5} {n_pos:>9} {spp:>10.4f} {per_game:>7.2f}   {proj}")
    engine.quit()


if __name__ == "__main__":
    main()
