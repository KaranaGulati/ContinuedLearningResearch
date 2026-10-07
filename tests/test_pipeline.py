import io
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import chess
import pandas as pd
import pytest
import zstandard

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from features import classify_win, game_features, san_moves, speed_class  # noqa: E402
from pgn_stream import iter_games  # noqa: E402

MATE = ["e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6", "Qxf7#"]
SHORT = ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"]
T0 = datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)


def pgn(game_id, white, black, result, termination, moves, start, tc="600+0",
        event="Rated Rapid game", extra_tags=(), eval_comment=None):
    base, inc = map(int, tc.split("+"))
    tags = {
        "Event": event, "Site": f"https://lichess.org/{game_id}", "Date": start.strftime("%Y.%m.%d"),
        "White": white, "Black": black, "Result": result,
        "UTCDate": start.strftime("%Y.%m.%d"), "UTCTime": start.strftime("%H:%M:%S"),
        "WhiteElo": "1500", "BlackElo": "1550", "TimeControl": tc, "Termination": termination,
    }
    tags.update(dict(extra_tags))
    parts = []
    for i, san in enumerate(moves):
        clk = base - 20 * (i // 2 + 1)  # each side spends 20s per move
        h, rem = divmod(clk, 3600)
        m, s = divmod(rem, 60)
        comment = f"[%clk {h}:{m:02d}:{s:02d}]"
        if eval_comment and i == len(moves) - 1:
            comment = f"[%eval {eval_comment}] " + comment
        prefix = f"{i // 2 + 1}. " if i % 2 == 0 else f"{i // 2 + 1}... "
        parts.append(f"{prefix}{san} {{ {comment} }}")
    header = "\n".join(f'[{k} "{v}"]' for k, v in tags.items())
    return f"{header}\n\n{' '.join(parts)} {result}\n\n"


def test_speed_class():
    assert speed_class("600+0")[0] == "rapid"
    assert speed_class("180+2")[0] == "blitz"
    assert speed_class("300+0")[0] == "blitz"
    assert speed_class("900+10")[0] == "rapid"
    assert speed_class("1800+0")[0] == "classical"
    assert speed_class("-")[0] == "correspondence"


def test_classify_win():
    assert classify_win("Time forfeit", "1-0", "a6") == "time"
    assert classify_win("Normal", "1-0", "Qxf7#") == "checkmate"
    assert classify_win("Normal", "0-1", "a6") == "resign"
    assert classify_win("Normal", "1/2-1/2", "a6") == "draw"
    assert classify_win("Abandoned", "1-0", "a6") == "drop"
    assert classify_win("Rules infraction", "0-1", "a6") == "drop"


def test_mate_score_in_comment_is_not_checkmate():
    text = pgn("g1", "a", "b", "1-0", "Normal", SHORT, T0, eval_comment="#3")
    (headers, movetext, _), = iter_games(io.BytesIO(text.encode()))
    assert san_moves(movetext)[-1] == "a6"
    assert game_features(headers, movetext)["win_type"] == "resign"


def test_hash_rule_matches_board_replay():
    for moves, expected in [(MATE, True), (SHORT, False)]:
        board = chess.Board()
        for san in moves:
            board.push_san(san)
        assert board.is_checkmate() is expected
        assert classify_win("Normal", "1-0", moves[-1]) == ("checkmate" if expected else "resign")


def test_features_clock_and_duration():
    text = pgn("g1", "a", "b", "1-0", "Normal", MATE, T0)
    (headers, movetext, _), = iter_games(io.BytesIO(text.encode()))
    f = game_features(headers, movetext)
    assert f["n_ply"] == 7
    assert f["white_first_clk"] == 580
    # White moved 4 times (60s used between first and last reading), Black 3 (40s).
    assert f["duration_s"] == 100
    assert f["has_clk"] == 1 and f["has_eval"] == 0


@pytest.fixture
def month_dir(tmp_path):
    m = lambda minutes: T0 + timedelta(minutes=minutes)  # noqa: E731
    games = [
        # alice: checkmate win, then a rapid game 5 minutes later -> pair (checkmate)
        pgn("a1", "alice", "bob", "1-0", "Normal", MATE, m(0)),
        pgn("a2", "carol", "alice", "1-0", "Normal", SHORT, m(10)),
        # alice: time win, then a blitz game, then rapid -> no pair (blitz in between)
        pgn("a3", "alice", "dave", "1-0", "Time forfeit", SHORT, m(30)),
        pgn("a4", "alice", "erin", "0-1", "Normal", SHORT, m(45), tc="180+0", event="Rated Blitz game"),
        pgn("a5", "alice", "frank", "1-0", "Normal", SHORT, m(55)),
        # alice won a5 by resignation; next game 3 hours later -> no pair (cutoff)
        pgn("a6", "alice", "gina", "1-0", "Normal", SHORT, m(240)),
        # alice won a6 by resignation; next game against a BOT -> not eligible
        pgn("a7", "alice", "botty", "1-0", "Normal", SHORT, m(250), extra_tags=[("BlackTitle", "BOT")]),
        # bob lost a1, then wins on time and plays again -> pair (time)
        pgn("b1", "bob", "hank", "1-0", "Time forfeit", SHORT, m(20)),
        pgn("b2", "ivy", "bob", "0-1", "Abandoned", SHORT, m(32)),
        # bob's b2 was abandoned, so it cannot be a previous win
        pgn("b3", "bob", "ivy", "0-1", "Normal", SHORT, m(40)),
        # carol won a2 by resignation, then draws a rematch against alice -> pair (resign), draw
        pgn("c1", "carol", "alice", "1/2-1/2", "Normal", SHORT, m(14)),
    ]
    raw = "".join(games).encode()
    src = tmp_path / "month.pgn.zst"
    src.write_bytes(zstandard.ZstdCompressor().compress(raw))
    out = tmp_path / "out"
    subprocess.run([sys.executable, os.path.join(ROOT, "src", "fetch_month.py"), str(src), "--out", str(out)],
                   check=True, capture_output=True)
    return out


def test_fetch_month_outputs(month_dir):
    stream = zstandard.ZstdDecompressor().stream_reader(open(month_dir / "games.tsv.zst", "rb"))
    games = pd.read_csv(stream, sep="\t")
    assert len(games) == 11
    assert set(games.loc[games.eligible == 0, "game_id"]) == {"a4", "a7"}
    by_id = games.set_index("game_id")
    assert by_id.loc["a1", "win_type"] == "checkmate"
    assert by_id.loc["a3", "win_type"] == "time"
    assert by_id.loc["a5", "win_type"] == "resign"
    assert by_id.loc["b2", "win_type"] == "drop"

    pgn_stream = zstandard.ZstdDecompressor().stream_reader(open(month_dir / "rapid.pgn.zst", "rb"))
    ids = [h["Site"].rsplit("/", 1)[-1] for h, _, _ in iter_games(pgn_stream)]
    assert len(ids) == 9 and "a4" not in ids and "a7" not in ids


def test_build_pairs(month_dir, tmp_path):
    out = tmp_path / "pairs"
    subprocess.run([sys.executable, os.path.join(ROOT, "src", "build_pairs.py"), str(month_dir),
                    "--out", str(out), "--min-ply", "1"], check=True, capture_output=True)
    pairs = pd.read_parquet(out / "pairs.parquet")
    got = {(r.player, r.prev_game_id, r.game_id, r.prev_win_type) for r in pairs.itertuples()}
    assert got == {
        ("alice", "a1", "a2", "checkmate"),
        ("bob", "b1", "b2", "time"),
        ("carol", "a2", "c1", "resign"),
    }
    row = pairs.set_index("game_id").loc["a2"]
    assert row.color == "black" and row.elo == 1550 and row.opp_elo == 1500
    assert row.result_for_player == "loss"
    # a1 lasted 100s by the clocks, a2 started 10 minutes after a1 started
    assert row.gap_s == 500
    assert not row.rematch  # alice played bob, then carol
    carol = pairs.set_index("game_id").loc["c1"]
    assert carol.rematch and carol.result_for_player == "draw"
