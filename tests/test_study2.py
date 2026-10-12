import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from study2 import LUCKY_CP, matched_take, one_per_player, stratum, winner_view  # noqa: E402


def test_winner_view_flips_for_black_and_caps():
    assert winner_view(-250, "white") == -250   # White won but was losing
    assert winner_view(-250, "black") == 250    # Black won and was winning
    assert winner_view(100_000, "black") == -1000
    assert winner_view(-150, "white") < LUCKY_CP < winner_view(-50, "white")


def test_one_per_player_keeps_one_each():
    df = pd.DataFrame({"player": list("aabbbc"), "x": range(6)})
    out = one_per_player(df, np.random.default_rng(0))
    assert sorted(out.player) == ["a", "b", "c"]


def test_matched_take_copies_strata():
    rng = np.random.default_rng(1)
    n = 5000
    pool = pd.DataFrame({"elo": rng.integers(1200, 2000, n).astype(float),
                         "time_control": rng.choice(["600+0", "600+5"], n), "player": range(n)})
    target = pool.sample(300, random_state=2)
    got = matched_take(pool.drop(target.index), target, rng)
    assert stratum(got).value_counts().sort_index().equals(stratum(target).value_counts().sort_index())
