"""Stream one Lichess monthly dump and keep only what the study needs.

The dump is ~30 GB compressed, so it is never written to disk. It is
decompressed on the fly and split into two outputs:

  games.tsv.zst  one row for every rated game in the month. Non-rapid games
                 keep only the fields needed for sequencing (id, players,
                 start time, speed). They are there so a blitz game played
                 between two rapid games breaks the "next game" link
                 instead of being invisible.
  rapid.pgn.zst  full PGN text for eligible games (rated, standard, rapid,
                 no BOT accounts), used later for Stockfish scoring.

Usage:
  python src/fetch_month.py 2025-03 --out data/2025-03
  python src/fetch_month.py 2025-03 --out data/pilot --max-games 2000000
  python src/fetch_month.py path/to/local.pgn.zst --out data/x
"""

import argparse
import csv
import io
import json
import os
import sys
import time

import zstandard

sys.path.insert(0, os.path.dirname(__file__))
from features import game_features, speed_class, start_timestamp  # noqa: E402
from pgn_stream import iter_games  # noqa: E402
from resumable import ResumableReader  # noqa: E402

DUMP_URL = "https://database.lichess.org/standard/lichess_db_standard_rated_{month}.pgn.zst"

# Months touched by entries on https://database.lichess.org/#known-issues that
# matter for this design. Refuse them outright rather than rely on memory.
BAD_MONTHS = {"2016-12", "2020-06", "2020-07", "2020-08", "2021-02", "2021-03"}

INDEX_COLUMNS = ["game_id", "white", "black", "start_ts", "speed", "eligible"]
RAPID_COLUMNS = [
    "tc_base", "tc_inc", "white_elo", "black_elo", "result", "termination", "winner",
    "win_type", "n_ply", "duration_s", "white_first_clk", "black_first_clk",
    "has_clk", "has_eval",
]
COLUMNS = INDEX_COLUMNS + RAPID_COLUMNS


def open_source(source):
    """(decompressed PGN stream, raw reader) for a month, a URL or a local file."""
    if len(source) == 7 and source[4] == "-":
        if source in BAD_MONTHS or source < "2017-04":
            sys.exit(f"{source} overlaps a Lichess known issue or predates clock data; pick another month")
        source = DUMP_URL.format(month=source)
    if source.startswith("http"):
        # curl already knows the proxy and CA bundle, so let it do the transfer.
        raw = ResumableReader(source)
    else:
        raw = open(source, "rb")
    if source.endswith(".zst"):
        return zstandard.ZstdDecompressor().stream_reader(raw, read_size=1 << 20), raw
    return raw, raw


def is_eligible(headers, speed):
    if speed != "rapid" or not headers.get("Event", "").startswith("Rated"):
        return False
    if headers.get("Variant", "Standard") != "Standard" or "FEN" in headers:
        return False
    if headers.get("WhiteTitle") == "BOT" or headers.get("BlackTitle") == "BOT":
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="YYYY-MM, a URL, or a local .pgn / .pgn.zst file")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--max-games", type=int, default=None, help="stop after this many games (pilot runs)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    # One compressor per output: a ZstdCompressor holds stream state and must
    # not be shared between two open writers.
    def compressor():
        return zstandard.ZstdCompressor(level=6, threads=2)

    tsv_raw = open(os.path.join(args.out, "games.tsv.zst"), "wb")
    pgn_raw = open(os.path.join(args.out, "rapid.pgn.zst"), "wb")
    tsv_out = io.TextIOWrapper(compressor().stream_writer(tsv_raw), encoding="utf-8", newline="")
    pgn_out = io.TextIOWrapper(compressor().stream_writer(pgn_raw), encoding="utf-8")
    writer = csv.writer(tsv_out, delimiter="\t", lineterminator="\n")
    writer.writerow(COLUMNS)

    n_total = n_eligible = 0
    t0 = time.time()
    stream, raw = open_source(args.source)
    complete, error = False, None
    try:
        for n_total, eligible_added in _process(stream, writer, pgn_out, args.max_games):
            n_eligible += eligible_added
            if n_total % 1_000_000 == 0:
                rate = n_total / (time.time() - t0)
                print(f"{n_total:,} games, {n_eligible:,} eligible rapid, {rate:,.0f} games/s", flush=True)
        complete = not args.max_games or n_total < args.max_games
    except IOError as exc:
        error = str(exc)

    tsv_out.close()
    pgn_out.close()
    meta = {
        "source": args.source, "games": n_total, "eligible_rapid": n_eligible,
        "complete": complete, "max_games": args.max_games, "error": error,
        "bytes_read": getattr(raw, "offset", None), "bytes_total": getattr(raw, "total", None),
        "resumes": getattr(raw, "resumes", 0), "seconds": round(time.time() - t0),
    }
    with open(os.path.join(args.out, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    status = "complete" if complete else ("stopped at --max-games" if not error else "INCOMPLETE")
    print(f"{status}: {n_total:,} games, {n_eligible:,} eligible rapid, {meta['seconds']:,}s, "
          f"{meta['resumes']} resumes")
    if error:
        sys.exit(f"error: {error}")


def _process(stream, writer, pgn_out, max_games):
    """Write one row per game; yield (games so far, 1 if this game was eligible)."""
    n_total = 0
    for headers, movetext, raw_text in iter_games(stream):
        n_total += 1
        speed, _, _ = speed_class(headers.get("TimeControl"))
        eligible = is_eligible(headers, speed)
        row = [
            headers.get("Site", "").rsplit("/", 1)[-1],
            headers.get("White", ""),
            headers.get("Black", ""),
            start_timestamp(headers),
            speed,
            int(eligible),
        ]
        if eligible:
            feats = game_features(headers, movetext)
            row += [feats[c] for c in RAPID_COLUMNS]
            pgn_out.write(raw_text)
            pgn_out.write("\n")
        else:
            row += [""] * len(RAPID_COLUMNS)
        writer.writerow(["" if v is None else v for v in row])
        yield n_total, int(eligible)
        if max_games and n_total >= max_games:
            return


if __name__ == "__main__":
    main()
