import os
import shutil
import sys

import chess
import chess.engine
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from engine_eval import MATE_CP, engine_evals, lichess_evals, move_losses, window_plies  # noqa: E402


def test_window_plies():
    assert window_plies(15, 30, 100) == (28, 60)  # 33 positions, 32 moves
    assert window_plies(15, 30, 40) == (28, 40)


def test_white_blunder_is_charged_to_white():
    # position 28 then White's 15th move (ply 29) drops from +0.20 to -3.00
    losses = move_losses([20, -300], lo=28, cap=1000)
    assert losses == {"white": [320], "black": []}


def test_black_blunder_is_charged_to_black():
    # ply 29 White improves slightly, ply 30 Black hands over 3.7 pawns
    losses = move_losses([20, 30, 400], lo=28, cap=1000)
    assert losses == {"white": [0], "black": [370]}


def test_improvements_clip_to_zero():
    # every move improves the mover's position: White 0->50, Black 50->20, White 20->70
    losses = move_losses([0, 50, 20, 70], lo=28, cap=1000)
    assert losses == {"white": [0, 0], "black": [0]}


def test_missed_mate_is_large_but_finite():
    losses = move_losses([MATE_CP, 0], lo=28, cap=1000)
    assert losses["white"] == [1000]


def test_lichess_eval_parsing():
    movetext = ("1. e4 { [%eval 0.18] [%clk 0:10:00] } 1... e5 { [%eval 0.25] [%clk 0:10:00] } "
                "2. Qh5 { [%eval #-3] [%clk 0:09:58] } 2... Nc6 { [%clk 0:09:57] } 1-0")
    assert lichess_evals(movetext) == [None, 18, 25, -MATE_CP, None]


STOCKFISH = shutil.which("stockfish") or ("/usr/games/stockfish" if os.path.exists("/usr/games/stockfish") else None)


@pytest.mark.skipif(STOCKFISH is None, reason="Stockfish not installed")
def test_engine_sees_hanging_queen_once_per_position():
    board = chess.Board()
    moves = [board.push_san(s) for s in ["e4", "e5", "Qh5", "Nc6", "Qxe5+"]] and list(board.move_stack)
    # 3. Qxe5+?? hangs the queen to 3...Nxe5
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH)
    try:
        evals = engine_evals(engine, moves, 0, len(moves), depth=10, game_key="t")
    finally:
        engine.quit()
    assert len(evals) == len(moves) + 1
    losses = move_losses(evals, lo=0, cap=1000)
    assert losses["white"][-1] > 500
    assert max(losses["black"]) < 150
