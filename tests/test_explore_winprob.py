import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from explore_winprob import win_losses, win_pct  # noqa: E402


def test_win_pct_is_symmetric_and_capped():
    assert win_pct(0) == pytest.approx(50)
    assert win_pct(300) + win_pct(-300) == pytest.approx(100)
    assert win_pct(5000) == win_pct(1000)
    assert 97 < win_pct(1000) < 98


def test_same_cp_drop_costs_less_when_already_winning():
    level = win_pct(50) - win_pct(-50)
    won = win_pct(800) - win_pct(700)
    assert level > 4 * won


def test_win_losses_sides_and_clipping():
    # lo = 28: the first move scored is ply 29, a White move.
    out = win_losses([0, -100, -100, 200], 28)
    assert out["white"] == [pytest.approx(win_pct(0) - win_pct(-100)), 0.0]
    assert out["black"] == [0.0]
