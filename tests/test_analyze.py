import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from analyze import check_preregistration, primary_test  # noqa: E402
from centipawn_loss import select_sample  # noqa: E402

WIN_TYPES = ["time", "checkmate", "resign"]


def simulate(effect, n_per=1600, time_elo_shift=0, seed=0):
    """Pairs from a pool of players; ACPL falls with Elo and carries a player effect."""
    rng = np.random.default_rng(seed)
    pool = 3000
    skill = rng.normal(0, 15, pool)
    rows = []
    for t in WIN_TYPES:
        for i in range(n_per):
            pid = int(rng.integers(pool))
            elo = rng.normal(1600 + (time_elo_shift if t == "time" else 0), 200)
            acpl = 60 - 0.04 * (elo - 1600) + skill[pid] + effect.get(t, 0) + rng.normal(0, 30)
            rows.append({"player": f"p{pid}", "prev_win_type": t, "acpl": acpl,
                         "elo": elo, "opp_elo": elo + rng.normal(0, 100),
                         "color": rng.choice(["white", "black"]), "time_control": "600+0",
                         "rematch": False, "prev_final_eval": 0.0})
    return pd.DataFrame(rows)


def by_pair(r):
    return {(x["A"], x["B"]): x for x in r["pairs"]}


def test_planted_effect_is_found_in_the_right_pair():
    r = primary_test(simulate({"time": 6.0}))
    assert r["p"] < 1e-4
    tc = by_pair(r)[("time", "checkmate")]
    assert tc["diff"] == pytest.approx(6.0, abs=2.5) and tc["p_holm"] < 0.01
    rc = by_pair(r)[("resign", "checkmate")]
    assert rc["ci95"][0] < 0 < rc["ci95"][1] or abs(rc["diff"]) < 2.5


def test_null_gives_small_differences():
    # Calibration was checked separately: 300 null runs gave 6.0% false
    # positives at alpha .05, so a p-value threshold here would fail by chance.
    r = primary_test(simulate({}, seed=3))
    assert all(abs(x["diff"]) < 3 for x in r["pairs"])


def test_elo_confound_is_removed_by_adjustment():
    # Winners on time are 300 points weaker, so their raw ACPL is ~12 cp worse,
    # but win type itself does nothing.
    r = primary_test(simulate({}, time_elo_shift=-300, seed=5))
    assert r["raw_means"]["time"] - r["raw_means"]["checkmate"] > 8
    assert abs(by_pair(r)[("time", "checkmate")]["diff"]) < 3
    assert r["p"] > 0.01


def test_matched_sampler():
    rng = np.random.default_rng(0)
    n = 6000
    pairs = pd.DataFrame({
        "player": [f"p{i}" for i in rng.integers(0, 2500, n)],
        "prev_win_type": rng.choice(WIN_TYPES, n, p=[0.1, 0.3, 0.6]),
        "elo": rng.integers(1200, 2000, n), "n_ply": 80,
        "time_control": rng.choice(["600+0", "600+5"], n, p=[0.8, 0.2]),
    })
    s = select_sample(pairs, 1200, 2000, 30, n_per_group=150, seed=1, exclude={"p1", "p2"})
    counts = s.prev_win_type.value_counts()
    assert (counts == 150).all()
    assert not s.duplicated(["player", "prev_win_type"]).any()
    assert not s.player.isin({"p1", "p2"}).any()
    strata = s.groupby(["prev_win_type", "stratum"]).size().unstack(fill_value=0)
    assert (strata.loc["checkmate"] == strata.loc["time"]).all()
    assert (strata.loc["resign"] == strata.loc["time"]).all()


def test_preregistration_gate(tmp_path):
    path = tmp_path / "PREREGISTRATION.md"
    path.write_text("Prediction: TBD\nDate fixed:\n")
    with pytest.raises(SystemExit):
        check_preregistration(str(path))
    path.write_text("Prediction: lucky escape\nDate fixed: 2026-10-08\n")
    assert check_preregistration(str(path)) == ("lucky escape", "2026-10-08")
