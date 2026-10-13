"""Study 2 analysis, as fixed in PREREGISTRATION_STUDY2.md (2026-10-12).

RQ1: rq1_time vs rq1_checkmate vs rq1_resign, same model and decision rule
     as study 1, smallest effect of interest 3 cp.
RQ2: rq2_lucky vs rq2_deserved. OLS of next-game ACPL on group, rating,
     rating gap, colour and time control, standard errors clustered by
     player. Supported if the 90% CI lies inside +-2 cp; refuted if the 95%
     CI excludes zero and the difference is at least 2 cp; else inconclusive.

Checks (do not change the decisions): 10+0 only, rematches removed, two
rating bands, a stricter lucky threshold (losing by more than 3 pawns) and
a mixed model.

Usage:
  python src/analyze_study2.py --scores data/study2-scores --out results/study2
"""

import argparse
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from analyze import decide, equivalence, fmt, mixed_check, primary_test  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RQ1_MAP = {"rq1_time": "time", "rq1_checkmate": "checkmate", "rq1_resign": "resign"}


def check_preregistration(path):
    text = open(path).read()
    if not re.search(r"^Date fixed:\s*\d{4}-\d{2}-\d{2}\s*$", text, re.M):
        sys.exit("PREREGISTRATION_STUDY2.md is not dated yet.")


def load(scores_dir, cap, min_moves):
    sample = pd.read_parquet(os.path.join(scores_dir, "sample.parquet"))
    scores = {}
    for line in open(os.path.join(scores_dir, "scores.jsonl")):
        r = json.loads(line)
        scores[r["game_id"]] = r

    def acpl(gid, color):
        losses = (scores.get(gid) or {}).get(f"{color}_losses")
        return float(np.mean(losses)) if losses and len(losses) >= min_moves else np.nan

    sample["acpl"] = [acpl(g, c) for g, c in zip(sample.game_id, sample.color)]
    sample["prev_final_eval"] = 0.0  # not used in study 2; keeps primary_test's columns
    return sample


def rq2_test(g, sesoi):
    g = g.dropna(subset=["acpl"]).copy()
    if g.group.value_counts().min() < 30:
        return {"note": "too few pairs", "n": g.group.value_counts().to_dict()}
    g["lucky"] = (g.group == "rq2_lucky").astype(int)
    g["elo_100"] = (g.elo - 1600) / 100
    g["gap_100"] = (g.opp_elo - g.elo) / 100
    terms = ["lucky", "elo_100", "gap_100", "C(color)"] + (["C(time_control)"] if g.time_control.nunique() > 1 else [])
    fit = smf.ols("acpl ~ " + " + ".join(terms), g).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(g.player)[0]})
    d, se = float(fit.params["lucky"]), float(fit.bse["lucky"])
    ci90 = [d - 1.645 * se, d + 1.645 * se]
    ci95 = [d - 1.96 * se, d + 1.96 * se]
    tost = float(max(stats.norm.sf((d + sesoi) / se), stats.norm.cdf((d - sesoi) / se)))
    if -sesoi < ci90[0] and ci90[1] < sesoi:
        decision = f"supported: lucky minus deserved is inside +-{sesoi} cp (90% CI)"
    elif (ci95[0] > 0 or ci95[1] < 0) and abs(d) >= sesoi:
        decision = f"refuted: lucky winners play {'worse' if d > 0 else 'better'} by {abs(d):.2f} cp"
    else:
        decision = "inconclusive"
    return {"n": g.group.value_counts().to_dict(), "n_players": int(g.player.nunique()),
            "raw_means": g.groupby("group").acpl.mean().round(3).to_dict(),
            "diff": d, "se": se, "ci90": ci90, "ci95": ci95, "p": float(fit.pvalues["lucky"]),
            "tost_p": tost, "decision": decision}


def rq1_test(g, sesoi):
    g = g[g.group.isin(RQ1_MAP)].assign(prev_win_type=lambda d: d.group.map(RQ1_MAP))
    r = equivalence(primary_test(g), sesoi)
    if "pairs" in r:
        r["decision"] = decide(r, sesoi)
    return r


def rq2_mixed(g):
    g = g.dropna(subset=["acpl"]).copy()
    g["lucky"] = (g.group == "rq2_lucky").astype(int)
    g["elo_100"] = (g.elo - 1600) / 100
    g["gap_100"] = (g.opp_elo - g.elo) / 100
    fit = smf.mixedlm("acpl ~ lucky + elo_100 + gap_100 + C(color) + C(time_control)", g, groups=g["player"]).fit(reml=True)
    d, se = float(fit.params["lucky"]), float(fit.bse["lucky"])
    return {"n": g.group.value_counts().to_dict(), "n_players": int(g.player.nunique()),
            "raw_means": g.groupby("group").acpl.mean().round(3).to_dict(), "diff": d, "se": se,
            "ci90": [d - 1.645 * se, d + 1.645 * se], "ci95": [d - 1.96 * se, d + 1.96 * se],
            "p": float(fit.pvalues["lucky"]),
            "tost_p": float(max(stats.norm.sf((d + 2) / se), stats.norm.cdf((d - 2) / se))),
            "decision": "(check only)"}


def fmt_rq2(title, r):
    if "diff" not in r:
        return f"### {title}\n\n{r.get('note')}: {r.get('n')}\n"
    return (f"### {title}\n\nPairs: {r['n']} ({r['n_players']:,} players). Raw mean ACPL: {r['raw_means']}.\n\n"
            f"Lucky minus deserved, adjusted: {r['diff']:.2f} cp, 90% CI [{r['ci90'][0]:.2f}, {r['ci90'][1]:.2f}], "
            f"95% CI [{r['ci95'][0]:.2f}, {r['ci95'][1]:.2f}], p = {r['p']:.4g}, TOST p = {r['tost_p']:.4g}.\n\n"
            f"Decision: **{r['decision']}**\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=int, default=1000)
    ap.add_argument("--min-moves", type=int, default=5)
    ap.add_argument("--prereg", default=os.path.join(ROOT, "PREREGISTRATION_STUDY2.md"))
    args = ap.parse_args()
    check_preregistration(args.prereg)

    s = load(args.scores, args.cap, args.min_moves)
    rq2 = s[s.group.isin(["rq2_lucky", "rq2_deserved"])]
    res = {"n_scored": int(s.acpl.notna().sum()),
           "rq1": rq1_test(s, 3.0), "rq2": rq2_test(rq2, 2.0), "checks": {}}
    subsets = {
        "10+0 only": lambda d: d[d.time_control == "600+0"],
        "rematches removed": lambda d: d[~d.rematch.astype(bool)],
        "rating 1200-1600": lambda d: d[(d.elo >= 1200) & (d.elo < 1600)],
        "rating 1600-2000": lambda d: d[(d.elo >= 1600) & (d.elo < 2000)],
    }
    for name, f in subsets.items():
        res["checks"][name] = {"rq1": rq1_test(f(s), 3.0), "rq2": rq2_test(f(rq2), 2.0)}
    strict = rq2[(rq2.group == "rq2_deserved") | (rq2.final_eval_winner < -300)]
    res["checks"]["stricter lucky (losing by > 3 pawns)"] = {"rq2": rq2_test(strict, 2.0)}
    rq1g = s[s.group.isin(RQ1_MAP)].assign(prev_win_type=lambda d: d.group.map(RQ1_MAP))
    res["checks"]["mixed model"] = {"rq1": mixed_check(rq1g), "rq2": rq2_mixed(rq2)}

    os.makedirs(args.out, exist_ok=True)
    json.dump(res, open(os.path.join(args.out, "results.json"), "w"), indent=2, default=float)
    md = ["# Study 2 results\n", f"Pairs with a scored ACPL: {res['n_scored']:,}\n",
          "## RQ1: does the way you win matter?\n", fmt("Time vs checkmate vs resignation", res["rq1"]),
          f"Decision: **{res['rq1'].get('decision', 'not tested')}**\n",
          "## RQ2: does a lucky time win matter?\n", fmt_rq2("Lucky vs deserved time wins", res["rq2"]),
          "## Checks\n"]
    for name, c in res["checks"].items():
        if "rq1" in c:
            md.append(fmt(f"RQ1, {name}", c["rq1"]))
        md.append(fmt_rq2(f"RQ2, {name}", c["rq2"]))
    open(os.path.join(args.out, "report.md"), "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
