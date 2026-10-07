"""Check the "#" checkmate rule against a full replay on real games.

Takes up to --n decisive games with Termination "Normal" from a
fetch_month.py output, replays each with python-chess, and compares
board.is_checkmate() on the final position with the "#" rule used by
features.classify_win. Prints the confusion counts and up to 10
disagreements. Run it before scoring; any disagreement means the rule is
not safe to use as it stands.

Usage:
  python src/validate_checkmate.py data/2025-03 --n 10000
"""

import argparse
import io
import os
import sys

import chess.pgn
import zstandard

sys.path.insert(0, os.path.dirname(__file__))
from features import san_moves  # noqa: E402
from pgn_stream import iter_games  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pgn_dir")
    ap.add_argument("--n", type=int, default=10_000)
    args = ap.parse_args()

    stream = zstandard.ZstdDecompressor().stream_reader(open(os.path.join(args.pgn_dir, "rapid.pgn.zst"), "rb"))
    counts = {(True, True): 0, (True, False): 0, (False, True): 0, (False, False): 0}
    disagreements = []
    checked = 0
    for headers, movetext, _ in iter_games(stream):
        if headers.get("Termination") != "Normal" or headers.get("Result") not in ("1-0", "0-1"):
            continue
        moves = san_moves(movetext)
        by_rule = bool(moves) and moves[-1].endswith("#")
        board = chess.pgn.read_game(io.StringIO(movetext)).end().board()
        by_replay = board.is_checkmate()
        counts[(by_rule, by_replay)] += 1
        if by_rule != by_replay and len(disagreements) < 10:
            disagreements.append(headers.get("Site"))
        checked += 1
        if checked >= args.n:
            break

    print(f"checked {checked:,} decisive Normal games")
    print(f"  rule mate, replay mate:      {counts[(True, True)]:,}")
    print(f"  rule resign, replay resign:  {counts[(False, False)]:,}")
    print(f"  rule mate, replay not mate:  {counts[(True, False)]:,}")
    print(f"  rule resign, replay mate:    {counts[(False, True)]:,}")
    for site in disagreements:
        print(f"  disagreement: {site}")
    sys.exit(1 if disagreements else 0)


if __name__ == "__main__":
    main()
