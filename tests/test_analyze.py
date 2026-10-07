import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from analyze import check_preregistration, primary_test  # noqa: E402

WIN_TYPES = ["time", "checkmate", "resign"]


def simulate(effect, n_players=300, games_per_cell=3, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for p in range(n_players):
        skill = rng.normal(40, 12)
        for t in WIN_TYPES:
            for _ in range(games_per_cell):
                rows.append({"player": f"p{p}", "prev_win_type": t,
                             "acpl": skill + effect.get(t, 0) + rng.normal(0, 15)})
    return pd.DataFrame(rows)


def test_planted_effect_is_found_in_the_right_pair():
    r = primary_test(simulate({"time": 5.0}))
    assert r["n_players"] == 300 and r["df1"] == 2 and r["df2"] == 598
    assert r["p"] < 1e-6
    assert r["means"]["time"] - r["means"]["checkmate"] == pytest.approx(5.0, abs=1.5)
    by_pair = {frozenset((x["A"], x["B"])): x for x in r["posthoc"]}
    assert abs(by_pair[frozenset(("checkmate", "resign"))]["mean_diff"]) < 1.5
    assert by_pair[frozenset(("checkmate", "time"))]["p_holm"] < 0.001
    assert 0 < r["eta2"] < r["partial_eta2"] < 1


def test_null_is_not_significant():
    r = primary_test(simulate({}, seed=3))
    assert r["p"] > 0.05


def test_incomplete_players_are_dropped():
    df = simulate({}, n_players=10)
    df = df[~((df.player == "p0") & (df.prev_win_type == "time"))]
    assert primary_test(df)["n_players"] == 9


def test_preregistration_gate(tmp_path):
    path = tmp_path / "PREREGISTRATION.md"
    path.write_text("Prediction: TBD\nDate fixed:\n")
    with pytest.raises(SystemExit):
        check_preregistration(str(path))
    path.write_text("Prediction: lucky escape\nDate fixed: 2026-10-08\n")
    assert check_preregistration(str(path)) == ("lucky escape", "2026-10-08")
