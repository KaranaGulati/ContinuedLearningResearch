"""Primary test and robustness checks, as fixed in PREREGISTRATION.md.

Refuses to run until PREREGISTRATION.md exists and its directional
prediction and date are filled in.

Primary: one mean centipawn loss per player per condition (the mean of that
player's game-level ACPL across the games scored in that condition), then a
one-way repeated-measures ANOVA with Greenhouse-Geisser correction, eta
squared and partial eta squared, and Holm-corrected paired t-tests as
the post-hoc comparisons. All tests are two-tailed.

Checks:
  1. the primary test rerun within each time control
  2. a mixed model on game-level ACPL with a player random intercept,
     adding the previous game's final evaluation (player's view), rating
     gap, colour and time control
  3. the primary test restricted to previous wins where the player was not
     losing on the board at the end
  4. Elo band sensitivity
  5. the same test using Lichess's own [%eval] comments on the
     pre-analysed subset

Usage:
  python src/analyze.py --scores data/scores --out results
"""

import argparse
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats
import statsmodels.formula.api as smf

WIN_TYPES = ["time", "checkmate", "resign"]
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

    def n_moves(r, color):
        return len(r.get(f"{color}_losses") or []) if r else 0

    def prev_final(gid, color):
        r = scores.get(gid)
        if not r or r.get("final_eval") is None:
            return np.nan
        v = max(-cap, min(cap, r["final_eval"]))
        return v if color == "white" else -v

    s = sample.copy()
    s["acpl"] = [acpl(scores.get(g), c) for g, c in zip(s.game_id, s.color)]
    s["n_moves"] = [n_moves(scores.get(g), c) for g, c in zip(s.game_id, s.color)]
    s["lichess_acpl"] = [acpl(scores.get(g), c, "lichess_") for g, c in zip(s.game_id, s.color)]
    s["prev_final_eval"] = [prev_final(g, c) for g, c in zip(s.prev_game_id, s.prev_color)]
    s["elo_gap"] = s.opp_elo - s.elo
    return s


def _col(row, *names):
    """First present column: pingouin renamed p-unc to p_unc and so on in 0.7."""
    for name in names:
        if name in row.index and not pd.isna(row[name]):
            return float(row[name])
    return None


def primary_test(games, dv="acpl"):
    """RM-ANOVA on player x condition means, among players complete on this subset."""
    g = games.dropna(subset=[dv])
    cell = g.groupby(["player", "prev_win_type"])[dv].mean().unstack()
    cell = cell.reindex(columns=WIN_TYPES).dropna()
    n = len(cell)
    if n < 3:
        return {"n_players": n, "note": "too few complete players"}
    long = cell.reset_index().melt(id_vars="player", var_name="prev_win_type", value_name=dv)
    aov = pg.rm_anova(data=long, dv=dv, within="prev_win_type", subject="player",
                      correction=True, detailed=True)
    effect, error = aov.iloc[0], aov.iloc[1]
    ss_total = ((long[dv] - long[dv].mean()) ** 2).sum()
    post = pg.pairwise_tests(data=long, dv=dv, within="prev_win_type", subject="player",
                             padjust="holm", alternative="two-sided")
    pairs = []
    for _, r in post.iterrows():
        diff = cell[r["A"]] - cell[r["B"]]
        half = stats.t.ppf(0.975, n - 1) * diff.std(ddof=1) / np.sqrt(n)
        pairs.append({"A": r["A"], "B": r["B"], "mean_diff": float(diff.mean()),
                      "ci95": [float(diff.mean() - half), float(diff.mean() + half)],
                      "t": float(r["T"]), "df": float(r["dof"]), "p_holm": _col(r, "p_corr", "p-corr"),
                      "dz": float(diff.mean() / diff.std(ddof=1))})
    out = {
        "n_players": n,
        "means": {t: float(cell[t].mean()) for t in WIN_TYPES},
        "sds": {t: float(cell[t].std(ddof=1)) for t in WIN_TYPES},
        "F": float(effect["F"]), "df1": int(effect["DF"]), "df2": int(error["DF"]),
        "p": _col(effect, "p_unc", "p-unc"),
        "eta2": float(effect["SS"] / ss_total),
        "partial_eta2": float(effect["SS"] / (effect["SS"] + error["SS"])),
        "posthoc": pairs,
    }
    for key, names in [("gg_epsilon", ("eps",)), ("p_gg", ("p_GG_corr", "p-GG-corr")),
                       ("mauchly_p", ("p_spher", "p-spher"))]:
        value = _col(effect, *names)
        if value is not None:
            out[key] = value
    return out


def mixed_model(games):
    g = games.dropna(subset=["acpl", "prev_final_eval"]).copy()
    if g.player.nunique() < 10:
        return {"note": "too few players"}
    g["prev_final_eval_pawns"] = g.prev_final_eval / 100
    formula = ("acpl ~ C(prev_win_type, Treatment('checkmate')) + prev_final_eval_pawns"
               " + elo_gap + C(color) + C(time_control)")
    fit = smf.mixedlm(formula, g, groups=g["player"]).fit(reml=True)
    keep = [k for k in fit.params.index if "prev_" in k or k in ("elo_gap", "Intercept")]
    return {
        "n_games": int(len(g)), "n_players": int(g.player.nunique()), "formula": formula,
        "coef": {k: float(fit.params[k]) for k in keep},
        "se": {k: float(fit.bse[k]) for k in keep},
        "p": {k: float(fit.pvalues[k]) for k in keep},
    }


def fmt_primary(title, r):
    if "F" not in r:
        return f"### {title}\n\nn = {r['n_players']} complete players: {r.get('note', '')}\n"
    p_line = f"p = {r['p']:.4g}"
    if "p_gg" in r:
        p_line += f", Greenhouse-Geisser p = {r['p_gg']:.4g} (epsilon {r['gg_epsilon']:.3f})"
    lines = [f"### {title}", "",
             f"n = {r['n_players']:,} players. F({r['df1']}, {r['df2']}) = {r['F']:.3f}, {p_line}, "
             f"eta squared = {r['eta2']:.4f}, partial eta squared = {r['partial_eta2']:.4f}.", "",
             "| condition | mean ACPL | SD |", "|---|---|---|"]
    lines += [f"| {t} | {r['means'][t]:.2f} | {r['sds'][t]:.2f} |" for t in WIN_TYPES]
    lines += ["", "| pair | mean diff | 95% CI | t | df | Holm p | dz |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {x['A']} vs {x['B']} | {x['mean_diff']:.2f} | [{x['ci95'][0]:.2f}, {x['ci95'][1]:.2f}] | "
              f"{x['t']:.3f} | {x['df']:.0f} | {x['p_holm']:.4g} | {x['dz']:.3f} |" for x in r["posthoc"]]
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
    ap.add_argument("--min-tc-players", type=int, default=100,
                    help="check 1: complete players a time control needs to be tested on its own")
    ap.add_argument("--elo-bands", nargs="+", default=["1200-1600", "1600-2000"])
    ap.add_argument("--prereg", default=os.path.join(ROOT, "PREREGISTRATION.md"))
    args = ap.parse_args()

    prediction, date = check_preregistration(args.prereg)
    games = load(args.scores, args.cap, args.min_moves)
    os.makedirs(args.out, exist_ok=True)
    results = {"prediction": prediction, "prediction_date": date,
               "n_games_scored": int(games.acpl.notna().sum())}

    results["primary"] = primary_test(games)
    results["by_time_control"] = {}
    for tc, df in games.groupby("time_control"):
        r = primary_test(df)
        if r["n_players"] >= args.min_tc_players:
            results["by_time_control"][tc] = r
    results["mixed_model"] = mixed_model(games)
    results["not_losing_at_end"] = primary_test(games[games.prev_final_eval >= args.not_losing_cp])
    results["elo_bands"] = {}
    for band in args.elo_bands:
        lo, hi = map(int, band.split("-"))
        results["elo_bands"][band] = primary_test(games[(games.elo >= lo) & (games.elo < hi)])
    results["lichess_eval_subset"] = primary_test(games, dv="lichess_acpl")

    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    md = [f"# Results\n\nPreregistered prediction ({date}): {prediction}\n",
          f"Games with a scored ACPL: {results['n_games_scored']:,}\n",
          "## Primary test\n", fmt_primary("All time controls", results["primary"]),
          "## Check 1: within each time control\n"]
    md += [fmt_primary(tc, r) for tc, r in sorted(results["by_time_control"].items(),
                                                  key=lambda kv: -kv[1]["n_players"])]
    mm = results["mixed_model"]
    md.append("## Check 2: mixed model with previous final evaluation\n")
    if "coef" in mm:
        md.append(f"`{mm['formula']}`, random intercept per player, {mm['n_games']:,} games, "
                  f"{mm['n_players']:,} players.\n")
        md.append("| term | coef | SE | p |\n|---|---|---|---|")
        md += [f"| {k} | {mm['coef'][k]:.3f} | {mm['se'][k]:.3f} | {mm['p'][k]:.4g} |" for k in mm["coef"]]
        md.append("")
    else:
        md.append(mm.get("note", "") + "\n")
    md.append(f"## Check 3: previous win where the player was not losing (final eval >= {args.not_losing_cp} cp)\n")
    md.append(fmt_primary("Not losing at the end", results["not_losing_at_end"]))
    md.append("## Check 4: Elo band sensitivity\n")
    md += [fmt_primary(b, r) for b, r in results["elo_bands"].items()]
    md.append("## Check 5: Lichess pre-analysed subset\n")
    md.append(fmt_primary("Lichess [%eval]", results["lichess_eval_subset"]))
    with open(os.path.join(args.out, "report.md"), "w") as f:
        f.write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
