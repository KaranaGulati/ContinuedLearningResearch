"""Primary test and robustness checks, as fixed in PREREGISTRATION.md.

Refuses to run until PREREGISTRATION.md exists and its directional
prediction and date are filled in.

Design: the unit is a pair (a rapid win, then the same player's next rapid
game), and the three groups are pairs after a win on time, by checkmate and
by resignation. A player can sit in more than one group, so observations
from one player are not independent.

Primary: OLS of the next game's ACPL on the win type (checkmate as the
reference), adjusting for the player's Elo, the rating gap to the opponent,
colour and time control, with standard errors clustered by player. The
omnibus test is a Wald test that both win-type coefficients are zero. The
three pairwise differences are tested from the same model with Holm
correction, with 95% confidence intervals. Effect sizes are the adjusted
differences in centipawns and as a fraction of the pooled SD of ACPL.
All tests are two-tailed.

Checks:
  1. the primary test within each time control that has enough pairs
  2. the primary model plus the previous game's final evaluation (player's
     view) and a rematch indicator
  3. the primary test restricted to previous wins where the player was not
     losing on the board at the end
  4. Elo band sensitivity
  5. the same test using Lichess's own [%eval] comments on the
     pre-analysed subset
  6. the primary test without rematches (next game against the same opponent)
  7. a mixed model with a random intercept per player instead of clustered
     standard errors

Usage:
  python src/analyze.py --scores data/scores --out results
  python src/analyze.py --scores data/pilot-scores --out results/pilot --exploratory
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
from statsmodels.stats.multitest import multipletests

WIN_TYPES = ["time", "checkmate", "resign"]
CONTRASTS = [("time", "checkmate"), ("resign", "checkmate"), ("time", "resign")]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_preregistration(path):
    if not os.path.exists(path):
        sys.exit("PREREGISTRATION.md is missing. Write it before running the analysis.")
    text = open(path).read()
    m = re.search(r"^Prediction:\s*(.+)$", text, re.M)
    d = re.search(r"^Date fixed:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    if not m or "TBD" in m.group(1) or not d:
        sys.exit("PREREGISTRATION.md has no dated directional prediction yet. Fill in "
                 "'Prediction:' and 'Date fixed:' before running the analysis.")
    return m.group(1).strip(), d.group(1)


def load(scores_dir, cap, min_moves):
    sample = pd.read_parquet(os.path.join(scores_dir, "sample.parquet"))
    rows = [json.loads(line) for line in open(os.path.join(scores_dir, "scores.jsonl")) if line.strip()]
    scores = {r["game_id"]: r for r in rows}

    def acpl(r, color, key=""):
        losses = r.get(f"{key}{color}_losses") if r else None
        return float(np.mean(losses)) if losses and len(losses) >= min_moves else np.nan

    def prev_final(gid, color):
        r = scores.get(gid)
        if not r or r.get("final_eval") is None:
            return np.nan
        v = max(-cap, min(cap, r["final_eval"]))
        return v if color == "white" else -v

    s = sample.copy()
    s["acpl"] = [acpl(scores.get(g), c) for g, c in zip(s.game_id, s.color)]
    s["lichess_acpl"] = [acpl(scores.get(g), c, "lichess_") for g, c in zip(s.game_id, s.color)]
    s["prev_final_eval"] = [prev_final(g, c) for g, c in zip(s.prev_game_id, s.prev_color)]
    return s


def _prepare(games, dv):
    g = games.dropna(subset=[dv]).copy()
    g["y"] = g[dv]
    g["elo_100"] = (g.elo - 1600) / 100
    g["elo_gap_100"] = (g.opp_elo - g.elo) / 100
    g["rematch"] = g["rematch"].astype(int)
    g["prev_final_eval_pawns"] = g.prev_final_eval / 100
    g["win"] = pd.Categorical(g.prev_win_type, categories=["checkmate", "time", "resign"])
    return g


def _formula(g, extra=()):
    terms = ["C(win)", "elo_100", "elo_gap_100", "C(color)"]
    if g.time_control.nunique() > 1:
        terms.append("C(time_control)")
    return "y ~ " + " + ".join(terms + list(extra))


def _contrasts(params, cov):
    """Wald omnibus and the three pairwise differences from win-type coefficients."""
    names = {"time": "C(win)[T.time]", "resign": "C(win)[T.resign]"}
    b = params[[names["time"], names["resign"]]].to_numpy()
    v = cov.loc[[names["time"], names["resign"]], [names["time"], names["resign"]]].to_numpy()
    wald = float(b @ np.linalg.solve(v, b))

    def est(a, ref):
        vec = np.array([float(a == "time") - float(ref == "time"),
                        float(a == "resign") - float(ref == "resign")])
        return float(vec @ b), float(np.sqrt(vec @ v @ vec))

    rows = []
    for a, ref in CONTRASTS:
        e, se = est(a, ref)
        rows.append({"A": a, "B": ref, "diff": e, "se": se,
                     "ci95": [e - 1.96 * se, e + 1.96 * se],
                     "ci90": [e - 1.645 * se, e + 1.645 * se],
                     "se_for_tost": se,
                     "z": e / se, "p": float(2 * stats.norm.sf(abs(e / se)))})
    holm = multipletests([r["p"] for r in rows], method="holm")[1]
    for r, ph in zip(rows, holm):
        r["p_holm"] = float(ph)
    return {"wald_chi2": wald, "df": 2, "p": float(stats.chi2.sf(wald, 2)), "pairs": rows}


def equivalence(r, sesoi):
    """TOST against +-sesoi for each pair; adds tost_p and equivalent in place."""
    for x in r.get("pairs", []):
        se = x["se_for_tost"]
        p_low = stats.norm.sf((x["diff"] + sesoi) / se)    # H0: diff <= -sesoi
        p_high = stats.norm.cdf((x["diff"] - sesoi) / se)  # H0: diff >= +sesoi
        x["tost_p"] = float(max(p_low, p_high))
        x["equivalent"] = bool(-sesoi < x["ci90"][0] and x["ci90"][1] < sesoi)
    return r


def decide(r, sesoi, alpha=0.05):
    """The preregistered decision rule for the prediction "a win is a win"."""
    pairs = r.get("pairs", [])
    if not pairs:
        return "not tested"
    if all(x["equivalent"] for x in pairs):
        return (f"supported: every pairwise difference is inside +-{sesoi} cp "
                f"(90% CIs, TOST at alpha .05)")
    real = [x for x in pairs if x["p_holm"] < alpha and abs(x["diff"]) >= sesoi]
    if r["p"] < alpha and real:
        names = ", ".join(f"{x['A']} minus {x['B']} = {x['diff']:.2f} cp" for x in real)
        return f"refuted: the omnibus test is significant and {names} (Holm p < .05, at least {sesoi} cp)"
    return "inconclusive: neither equivalence nor a difference of at least the smallest effect of interest"


def primary_test(games, dv="acpl", extra=(), min_per_group=30):
    g = _prepare(games, dv)
    if extra:
        g = g.dropna(subset=[c for c in extra if c in g])
    counts = g.prev_win_type.value_counts().reindex(WIN_TYPES, fill_value=0)
    out = {"n": {t: int(counts[t]) for t in WIN_TYPES}, "n_players": int(g.player.nunique())}
    if counts.min() < min_per_group:
        out["note"] = f"fewer than {min_per_group} pairs in a group"
        return out
    formula = _formula(g, extra)
    groups = pd.factorize(g.player)[0]
    fit = smf.ols(formula, g).fit(cov_type="cluster", cov_kwds={"groups": groups})
    sd = float(g.y.std(ddof=1))
    res = _contrasts(fit.params, fit.cov_params())
    for r in res["pairs"]:
        r["d"] = r["diff"] / sd
    out.update(res)
    out.update({
        "formula": formula,
        "raw_means": {t: float(g.y[g.prev_win_type == t].mean()) for t in WIN_TYPES},
        "raw_sds": {t: float(g.y[g.prev_win_type == t].std(ddof=1)) for t in WIN_TYPES},
        "pooled_sd": sd,
        "resid_sd": float(np.sqrt(fit.mse_resid)),
        "covariates": {k: [float(fit.params[k]), float(fit.bse[k])] for k in fit.params.index
                       if not k.startswith(("C(win)", "C(time_control)", "Intercept"))},
    })
    return out


def n_per_group_needed(resid_sd, delta=2.0, alpha=0.05, power=0.80, comparisons=3):
    """Pairs per group for a two-group difference of delta cp, Bonferroni-level alpha.

    Holm's first step uses alpha / comparisons, so this is the conservative case.
    """
    z = stats.norm.ppf(1 - alpha / comparisons / 2) + stats.norm.ppf(power)
    return int(np.ceil(2 * (z * resid_sd / delta) ** 2))


def mixed_check(games, dv="acpl"):
    g = _prepare(games, dv)
    fit = smf.mixedlm(_formula(g), g, groups=g["player"]).fit(reml=True)
    fe = [k for k in fit.params.index if k != "Group Var"]
    res = _contrasts(fit.params[fe], fit.cov_params().loc[fe, fe])
    counts = g.prev_win_type.value_counts().reindex(WIN_TYPES, fill_value=0)
    res["n"] = {t: int(counts[t]) for t in WIN_TYPES}
    res["n_players"] = int(g.player.nunique())
    return res


def fmt(title, r):
    lines = [f"### {title}", ""]
    if "pairs" not in r:
        return "\n".join(lines + [f"n = {r['n']}: {r.get('note', '')}", ""])
    n = r["n"]
    lines.append(f"Pairs: time {n['time']:,}, checkmate {n['checkmate']:,}, resign {n['resign']:,} "
                 f"({r['n_players']:,} players). Wald chi2({r['df']}) = {r['wald_chi2']:.3f}, "
                 f"p = {r['p']:.4g}.")
    if "raw_means" in r:
        lines += ["", "| win type | raw mean ACPL | SD |", "|---|---|---|"]
        lines += [f"| {t} | {r['raw_means'][t]:.2f} | {r['raw_sds'][t]:.2f} |" for t in WIN_TYPES]
    lines += ["", "| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |",
              "|---|---|---|---|---|---|---|---|"]
    for x in r["pairs"]:
        d = f"{x['d']:.3f}" if "d" in x else ""
        tost = f"{x['tost_p']:.4g}" if "tost_p" in x else ""
        lines.append(f"| {x['A']} minus {x['B']} | {x['diff']:.2f} | [{x['ci95'][0]:.2f}, {x['ci95'][1]:.2f}] | "
                     f"[{x['ci90'][0]:.2f}, {x['ci90'][1]:.2f}] | {x['z']:.2f} | {x['p_holm']:.4g} | {tost} | {d} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scores", required=True, help="centipawn_loss.py output directory")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=int, default=1000)
    ap.add_argument("--min-moves", type=int, default=5,
                    help="minimum scored moves for a game's ACPL to count")
    ap.add_argument("--not-losing-cp", type=int, default=-100,
                    help="check 3: previous final eval (player's view) must be at least this")
    ap.add_argument("--min-tc-pairs", type=int, default=100,
                    help="check 1: pairs per group a time control needs to be tested on its own")
    ap.add_argument("--elo-bands", nargs="+", default=["1200-1600", "1600-2000"])
    ap.add_argument("--sesoi", type=float, default=3.0, help="smallest effect of interest, cp")
    ap.add_argument("--prereg", default=os.path.join(ROOT, "PREREGISTRATION.md"))
    ap.add_argument("--exploratory", action="store_true",
                    help="pilot only: skip the preregistration gate and label the report exploratory")
    args = ap.parse_args()

    if args.exploratory:
        prediction, date = "none (exploratory pilot, not a test of any hypothesis)", "n/a"
    else:
        prediction, date = check_preregistration(args.prereg)
    games = load(args.scores, args.cap, args.min_moves)
    os.makedirs(args.out, exist_ok=True)

    results = {"prediction": prediction, "prediction_date": date,
               "n_scored": int(games.acpl.notna().sum()),
               "primary": primary_test(games)}
    results["by_time_control"] = {
        tc: primary_test(df, min_per_group=args.min_tc_pairs)
        for tc, df in games.groupby("time_control")
        if df.prev_win_type.value_counts().reindex(WIN_TYPES, fill_value=0).min() >= args.min_tc_pairs
    }
    results["previous_position"] = primary_test(games, extra=("prev_final_eval_pawns", "rematch"))
    results["not_losing_at_end"] = primary_test(games[games.prev_final_eval >= args.not_losing_cp])
    results["elo_bands"] = {}
    for band in args.elo_bands:
        lo, hi = map(int, band.split("-"))
        results["elo_bands"][band] = primary_test(games[(games.elo >= lo) & (games.elo < hi)])
    results["lichess_eval_subset"] = primary_test(games, dv="lichess_acpl")
    results["no_rematch"] = primary_test(games[~games.rematch.astype(bool)])
    results["mixed_model"] = mixed_check(games)

    for key, val in list(results.items()):
        if isinstance(val, dict) and "pairs" in val:
            equivalence(val, args.sesoi)
        elif isinstance(val, dict):
            for sub in val.values():
                if isinstance(sub, dict) and "pairs" in sub:
                    equivalence(sub, args.sesoi)
    results["decision"] = decide(results["primary"], args.sesoi)
    if "resid_sd" in results["primary"]:
        rsd = results["primary"]["resid_sd"]
        results["sample_size"] = {"resid_sd": rsd, "delta_cp": 2.0,
                                  "n_per_group_80": n_per_group_needed(rsd),
                                  "n_per_group_90": n_per_group_needed(rsd, power=0.90)}
    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    header = ("# Exploratory pilot\n\nThis sample is used to form the prediction and size the "
              "confirmatory test. None of its p-values are evidence for or against any hypothesis.\n"
              if args.exploratory else
              f"# Results\n\nPreregistered prediction ({date}): {prediction}\n")
    md = [header,
          f"Pairs with a scored ACPL: {results['n_scored']:,}\n",
          "## Primary test\n", fmt("All time controls", results["primary"]),
          f"Decision under the preregistered rule: **{results['decision']}**\n",
          f"Model: `{results['primary'].get('formula', '')}`, OLS with standard errors clustered by player.\n",
          "## Check 1: within each time control\n"]
    md += [fmt(tc, r) for tc, r in results["by_time_control"].items()] or ["No time control had enough pairs.\n"]
    md.append("## Check 2: adding the previous game's final evaluation and rematch\n")
    md.append(fmt("Previous position", results["previous_position"]))
    cov = results["previous_position"].get("covariates", {})
    if "prev_final_eval_pawns" in cov:
        b, se = cov["prev_final_eval_pawns"]
        md.append(f"Previous final evaluation: {b:.2f} cp of ACPL per pawn (SE {se:.2f}).\n")
    md.append(f"## Check 3: previous win where the player was not losing (final eval >= {args.not_losing_cp} cp)\n")
    md.append(fmt("Not losing at the end", results["not_losing_at_end"]))
    md.append("## Check 4: Elo band sensitivity\n")
    md += [fmt(b, r) for b, r in results["elo_bands"].items()]
    md.append("## Check 5: Lichess pre-analysed subset\n")
    md.append(fmt("Lichess [%eval]", results["lichess_eval_subset"]))
    md.append("## Check 6: rematches removed\n")
    md.append(fmt("Next game against a different opponent", results["no_rematch"]))
    if "sample_size" in results:
        ss = results["sample_size"]
        md.append("## Sample size for a 2 cp difference\n")
        md.append(f"Residual SD of ACPL after the covariates: {ss['resid_sd']:.2f} cp. Pairs per group "
                  f"needed at alpha .05 / 3 (Holm's first step), two-tailed: {ss['n_per_group_80']:,} "
                  f"for 80% power, {ss['n_per_group_90']:,} for 90%.\n")
    md.append("## Check 7: mixed model with a random intercept per player\n")
    md.append(fmt("Mixed model", results["mixed_model"]))
    with open(os.path.join(args.out, "report.md"), "w") as f:
        f.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
