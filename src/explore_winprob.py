"""Exploratory check for study 2: measure move quality as lost winning chances, not centipawns.

Not part of the preregistered analysis. It answers the objection that a 100 cp
drop matters a lot in a level position and hardly at all in a won one.

Each stored Stockfish 16 evaluation is converted to a winning chance with the
formula Lichess uses for its accuracy score (lichess.org/page/accuracy; the
scalachess source caps evaluations at +-1000 cp before converting):

    Win% = 50 + 50 * (2 / (1 + exp(-0.00368208 * cp)) - 1)

A move's loss is how far it lowered the mover's Win%, clipped at zero, and a
game's score is the average over the player's moves 15 to 30 (at least 5).
The models are the preregistered ones (study 2 RQ2, and RQ1's three win
types) with this score in place of ACPL. No equivalence bounds are set for
this unit, so only the estimates are reported, next to the centipawn results
in standard-deviation units for comparison.

Usage:
  python src/explore_winprob.py --scores results/study2-progress --out results/study2
"""

import argparse
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from analyze import primary_test  # noqa: E402
from analyze_study2 import RQ1_MAP, load, rq2_test  # noqa: E402

CAP = 1000
K = 0.00368208


def win_pct(cp):
    cp = max(-CAP, min(CAP, cp))
    return 50 + 50 * (2 / (1 + math.exp(-K * cp)) - 1)


def win_losses(evals, lo):
    """Per-move Win% losses for both sides from a White-POV eval sequence starting at position lo."""
    out = {"white": [], "black": []}
    for i in range(1, len(evals)):
        before, after = evals[i - 1], evals[i]
        if before is None or after is None:
            continue
        white_moved = (lo + i) % 2 == 1
        w_before, w_after = win_pct(before), win_pct(after)
        drop = (w_before - w_after) if white_moved else (w_after - w_before)
        out["white" if white_moved else "black"].append(max(0.0, drop))
    return out


def add_win_loss(sample, scores_path, min_moves):
    per_game = {}
    for line in open(scores_path):
        r = json.loads(line)
        if r.get("evals") is not None:
            per_game[r["game_id"]] = win_losses(r["evals"], r["window_lo"])

    def avg(gid, color):
        losses = (per_game.get(gid) or {}).get(color)
        return float(np.mean(losses)) if losses and len(losses) >= min_moves else np.nan

    return sample.assign(wloss=[avg(g, c) for g, c in zip(sample.game_id, sample.color)])


def standardised(diff, se, sd):
    return {"diff": diff, "ci95": [diff - 1.96 * se, diff + 1.96 * se], "sd": sd, "d": diff / sd}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scores", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-moves", type=int, default=5)
    args = ap.parse_args()

    s = load(args.scores, CAP, args.min_moves)
    s = add_win_loss(s, os.path.join(args.scores, "scores.jsonl"), args.min_moves)
    res = {"formula": "Win% = 50 + 50 * (2 / (1 + exp(-0.00368208 * cp)) - 1), cp capped at +-1000"}

    rq2 = s[s.group.isin(["rq2_lucky", "rq2_deserved"])]
    for name, col in (("centipawns", "acpl"), ("win_pct", "wloss")):
        g = rq2.assign(acpl=rq2[col])
        r = rq2_test(g, 2.0)
        sd = float(g.dropna(subset=["acpl"]).acpl.std(ddof=1))
        res[f"rq2_{name}"] = {**standardised(r["diff"], r["se"], sd), "p": r["p"], "n": r["n"],
                              "raw_means": r["raw_means"]}

    rq1 = s[s.group.isin(RQ1_MAP)].assign(prev_win_type=lambda d: d.group.map(RQ1_MAP))
    for name, col in (("centipawns", "acpl"), ("win_pct", "wloss")):
        r = primary_test(rq1.assign(acpl=rq1[col]))
        res[f"rq1_{name}"] = {"omnibus_p": r["p"], "raw_means": r["raw_means"], "sd": r["pooled_sd"],
                              "pairs": [{"pair": f"{p['A']} - {p['B']}", "diff": p["diff"], "ci95": p["ci95"],
                                         "p_holm": p["p_holm"], "d": p["d"]} for p in r["pairs"]]}

    os.makedirs(args.out, exist_ok=True)
    json.dump(res, open(os.path.join(args.out, "exploratory_winprob.json"), "w"), indent=2, default=float)

    a, b = res["rq2_centipawns"], res["rq2_win_pct"]
    md = ["# Exploratory: move quality as lost winning chances\n",
          "Not preregistered. Same games, same Stockfish 16 evaluations and same models as the main analysis; "
          "only the unit changes, from centipawns to Win% (" + res["formula"] + ").\n",
          "## Lucky minus deserved time wins (RQ2)\n",
          "| measure | lucky minus deserved | 95% CI | p | in SDs |", "|---|---|---|---|---|",
          f"| centipawns (preregistered) | {a['diff']:.2f} cp | {a['ci95'][0]:.2f} to {a['ci95'][1]:.2f} | {a['p']:.3g} | {a['d']:.3f} |",
          f"| Win% lost per move | {b['diff']:.3f} points | {b['ci95'][0]:.3f} to {b['ci95'][1]:.3f} | {b['p']:.3g} | {b['d']:.3f} |",
          "", f"Raw means, Win% lost per move: {b['raw_means']}\n",
          "## Time vs checkmate vs resignation (RQ1)\n",
          "| measure | omnibus p | pair | difference | 95% CI | Holm p | in SDs |", "|---|---|---|---|---|---|---|"]
    for name, unit in (("centipawns", "cp"), ("win_pct", "points")):
        r = res[f"rq1_{name}"]
        for p in r["pairs"]:
            md.append(f"| {name} | {r['omnibus_p']:.3g} | {p['pair']} | {p['diff']:.3f} {unit} | "
                      f"{p['ci95'][0]:.3f} to {p['ci95'][1]:.3f} | {p['p_holm']:.3g} | {p['d']:.3f} |")
    open(os.path.join(args.out, "exploratory_winprob.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
