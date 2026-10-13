# Study 2: lucky wins and the next game

Results of the study fixed in `PREREGISTRATION_STUDY2.md` on 12 October 2026, before any of its games were scored. Full tables are in `results/study2/report.md`.

## Data

Lichess rated rapid games from 6 to 30 September 2026, none of which overlap study 1. 70,000 wins on time were screened in a fixed random order: in 14,284 of them (20.4%) the winner was losing by more than a pawn when the opponent's clock ran out. 42,851 next games were scored with Stockfish 16 at depth 15 on moves 15 to 30, and 41,957 had enough moves to count.

## RQ2: does a lucky time win change the next game?

Prediction (Karana's): no. Players reset after every game, so lucky and deserved time winners play the next game equally well, within plus or minus 2 cp.

| next game after | pairs | mean ACPL |
|---|---|---|
| deserved time win | 11,962 | 72.28 |
| lucky time win | 12,033 | 74.38 |

After adjusting for rating, opponent rating, colour and time control, lucky winners lost 1.96 cp more per move in their next game (95% CI 0.66 to 3.27, p = 0.003).

The prediction is not supported: the 90% confidence interval (0.87 to 3.06) reaches past the 2 cp limit, so the two groups cannot be called equal. The preregistered rule also says a difference only counts as refuting the prediction if it is at least 2 cp, and this one is 1.96. Under the rule fixed in advance, the result is therefore inconclusive, by 0.04 cp.

What the numbers say plainly is that lucky winners played slightly worse in their next game, the difference is unlikely to be chance, and its size sits right on the threshold chosen beforehand for "big enough to matter". Using study 1's estimate that 100 rating points are worth about 3.7 cp, 1.96 cp is roughly the accuracy gap between players 50 rating points apart.

The direction matches the hint from study 1, where the 1,288 lucky time winners played 2.2 cp worse than checkmate winners (p = 0.15). Study 2 used new games, a deserved-time-win comparison group, and nine times as many lucky wins.

Checks, none of which change the decision:

| check | lucky minus deserved | 95% CI | p |
|---|---|---|---|
| 10+0 only | 2.29 | 0.82 to 3.76 | 0.002 |
| rematches removed | 1.85 | 0.53 to 3.18 | 0.006 |
| rating 1200 to 1600 | 1.82 | -0.17 to 3.80 | 0.07 |
| rating 1600 to 2000 | 2.12 | 0.46 to 3.78 | 0.01 |
| lucky = losing by more than 3 pawns | 1.92 | 0.51 to 3.33 | 0.008 |
| mixed model | 1.96 | 0.66 to 3.27 | 0.003 |

Every check points the same way, between 1.8 and 2.3 cp.

## RQ1: does the way you win matter?

Prediction (Karana's): no. Time, checkmate and resignation wins lead to the same next-game accuracy, within plus or minus 3 cp.

| next game after | pairs | mean ACPL |
|---|---|---|
| time | 6,055 | 71.76 |
| checkmate | 5,955 | 72.32 |
| resignation | 5,952 | 73.22 |

No difference was significant (omnibus p = 0.26). Two of the three comparisons were shown equivalent within 3 cp. The third, time minus resignation, was -1.51 cp with a 90% CI of -3.05 to 0.03, which misses the equivalence zone by 0.05 cp. Under the preregistered rule RQ1 is inconclusive. Study 1, on different games, found all three inside the zone. Taken together, the two studies put any difference between the three kinds of win at no more than about 3 cp.

In the 10+0 check, time minus resignation was -2.68 cp (Holm p = 0.03): players played slightly better after a time win than after the opponent resigned. This is a check, not a test of the prediction, and it points the opposite way from the lucky-win effect.

## Limits

- The deserved group has 11,962 scored pairs from 12,942 sampled; 58 fewer than planned were sampled because a few rating and time-control slots had more lucky than deserved wins.
- One month, rapid only, players rated 1200 to 2000.
- ACPL on moves 15 to 30 only.
- The study was run before Karana's teacher approved the plan.

## What it means

The original question, whether the way you win matters, still comes out as "very little": both studies keep the gaps between time, checkmate and resignation wins within about 3 cp. The sharper question is different. When the win was undeserved, players did a little worse in the next game, about 2 cp, consistently across every check. Whether 2 cp is big enough to matter is the question this study set out to answer with a fixed threshold, and the effect landed on it. A larger preregistered test, or one in blitz where lucky time wins are far more common, would settle which side of the line it falls.
