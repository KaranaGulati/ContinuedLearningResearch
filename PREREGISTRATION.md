# Preregistration

Status: fixed on 2026-10-07, before any confirmatory pair was scored. This file is not edited after the commit that dates it. Any later change goes in a dated amendment at the bottom, with the reason, and the report lists every amendment.

Prediction: a win is a win. Next-game ACPL does not differ between pairs after a win on time, by checkmate and by resignation; every pairwise difference lies within plus or minus 3 cp.
Date fixed: 2026-10-07

Who chose it and why: Karana asked Claude to choose the prediction and sample size. Claude chose the null because Gee et al. found almost no winner effects on Lichess outcomes, and the exploratory pilot below found no difference between win types (every adjusted gap within 4 cp, with the direction flipping between rating bands). The two directional theories in the README remain the alternatives the test can detect.

## What has been looked at before fixing this

A pilot on the first 2,000,000 games of the 2026-09 dump (about 17 hours of play) was run on 2026-10-07. From it the following were seen:

- Sample sizes: 5,171 players with all three conditions once the current game reaches ply 30, and 17,334 / 47,899 / 103,421 pairs after a win on time / checkmate / resignation. 10+0 holds about 80% of rapid pairs.
- The "#" checkmate rule agreed with a full replay on all 10,000 decisive Normal games checked (3,452 mates, 6,548 resignations).
- Session gaps: median about 1 minute, 90th percentile about 10 minutes.
- Rematch share by condition: 2.9% after a win on time, 9.4% after checkmate, 7.3% after resignation.
- 19% of eligible rapid games carry Lichess [%eval] comments, not the 6% stated in the README.
- Next-game result by condition was also printed: the player won 48.8% of next games after a win on time, 50.9% after checkmate and 49.9% after resignation. This is the outcome Gee et al. studied, not this study's dependent variable, but it was seen before the prediction was fixed, so it is recorded here.

An exploratory pilot was then scored and analysed on 2026-10-07: 200 pairs per group drawn as in the Sampling section (199 checkmate pairs, one short of the matched strata), 560 pairs with a usable ACPL. Its full report is in `results/pilot/report.md`. What it showed:

- Raw mean ACPL 71.7 after a win on time, 75.5 after checkmate, 70.9 after resignation. Adjusted differences: time minus checkmate -4.0 cp (95% CI -13.2 to 5.2), resignation minus checkmate -4.1 cp (-14.1 to 6.0), time minus resignation 0.1 cp (-9.2 to 9.3). Omnibus Wald p = 0.65.
- In the 1200 to 1600 band checkmate was about 12 cp worse than the other two; in 1600 to 2000 the order reversed. Neither was significant.
- Residual SD of ACPL after covariates: 46.7 cp. ACPL is right-skewed (median 62.6, 95th percentile 165.2, skew 1.54).
- 39 of 599 pairs (6.5%) had fewer than 5 scored moves and no ACPL.

The pilot's 592 players are excluded from the confirmatory sample. No confirmatory pair has been scored.

## Data

Lichess monthly dumps of rated standard games for 2026-08 and 2026-09. Both were checked against https://database.lichess.org/#known-issues on 2026-10-07; the only entries after March 2021 concern Chess960 and Antichess, which are not in the standard dump. `fetch_month.py` refuses 2016-12, 2020-06 to 2020-08, 2021-02, 2021-03 and anything before 2017-04.

The study uses the first part of each month, because a worker restart cut the downloads: 2026-08-01 00:00 to 2026-08-05 04:04 UTC (12,258,314 games) and 2026-09-01 00:00 to 2026-09-05 00:55 UTC (12,022,960 games). Within those windows every rated game is present, so a player's sequence of games is complete. The early-month windows are a limitation: they cover about nine days, and the first days of a month are not known to differ from the rest.

## Eligible games

- Rated, standard chess, no custom starting position.
- Rapid, using Lichess's own rule: base + 40 x increment is at least 480 and under 1500 seconds.
- Neither player has the BOT title.

## Pairing a game with the previous one

For each player, all rated games of any speed are sorted by start time. A game enters the study if:

- the player's immediately preceding rated game was an eligible rapid game the player won,
- that win was on time, by checkmate, or by the opponent's resignation (classification below),
- the current game is eligible,
- the current game started no more than 30 minutes after the previous game ended. The end time is estimated from the start time plus the clock time both players used. A gap down to -60 seconds is accepted because the clock estimate can run slightly late.

A blitz or bullet game in between breaks the link. Casual and variant games are not in the rated dump, so an unseen casual game can sit between two linked games. The 30-minute cutoff limits this but does not remove it.

## Classifying the previous win

- Termination "Time forfeit" and the player won: time.
- Termination "Normal" and the last move carries "#": checkmate. Comments are stripped first so that [%eval #3] is not read as a mate.
- Termination "Normal", decisive, no "#": resignation.
- Abandoned, Rules infraction, Unterminated and draws are never a previous win.

`test_hash_rule_matches_board_replay` in the tests checks the "#" rule against python-chess's `board.is_checkmate()`. Before scoring, the rule is also checked on 10,000 real decisive Normal games by replaying them, using `src/validate_checkmate.py`.

## Design

The unit is a pair: a rapid win, then the same player's next rapid game. The three groups are pairs whose first game was a win on time, by checkmate, or by the opponent's resignation. A player can appear in more than one group, but at most once in each.

A pair is kept if the player's rating in the next game is in [1200, 2000) and the next game reaches at least ply 30, so both players have at least one move inside the scored window.

## Sampling

`centipawn_loss.py`, seed 20261007:

1. One pair per player per group, chosen at random.
2. Draw N win-on-time pairs at random.
3. Draw the checkmate and resignation groups stratum by stratum so their mix of Elo (100-point bins) and time control matches the win-on-time group exactly. Winners on time differ in rating and time control from other winners, and matching removes that difference by construction instead of leaving it all to the model.

## Exploratory pilot, then confirmatory test

- Pilot: 200 pairs per group, drawn as above. It is exploratory. Its results are used to choose the prediction below and to estimate the noise for the sample size. It is never reported as the test.
- Confirmatory: N pairs per group, drawn the same way but excluding every player in the pilot (`--exclude data/pilot-scores/sample.parquet`). Only this sample is analysed under the decision rule.
- N: 6,500 pairs per group. The pilot's residual SD of ACPL was 46.7 cp. A simulation with that SD gives 85% power for all three pairwise 90% confidence intervals to fall inside plus or minus 3 cp when the true differences are zero, after allowing for the 6.5% of pairs the pilot lost to games with fewer than 5 scored moves.

## Dependent variable

Mean centipawn loss of the player over their own moves 15 to 30 in the current game.

- Stockfish 16, fixed depth 15, 1 thread, 64 MB hash, new game sent before each game.
- Each position from ply 28 to ply 60 (or the end of the game) is evaluated once. A move's loss is the drop in evaluation from the mover's point of view between the position before and the position after, clipped at zero.
- Mate scores become +-100,000 cp and every evaluation is then capped at +-1000 cp. A missed mate therefore costs at most 1000 cp, so one blunder cannot outweigh a whole game.
- A game's ACPL counts only if at least 5 of the player's moves were scored.

## Primary analysis

1. Outcome: the next game's ACPL for the player.
2. Model: OLS with win type (checkmate as the reference), the player's Elo, the rating gap to the opponent, colour and time control. Standard errors are clustered by player, because a player can appear in more than one group.
3. Omnibus test: Wald test that both win-type coefficients are zero, chi-squared with 2 degrees of freedom, alpha 0.05, two-tailed.
4. Pairwise: time minus checkmate, resignation minus checkmate and time minus resignation, from the same model, with Holm correction and 95% confidence intervals.
5. Effect sizes: the adjusted differences in centipawns, and divided by the pooled SD of ACPL.
6. Smallest effect of interest: 3 cp, about 4% of the pilot's mean ACPL of 72 cp. It was 2 cp in the draft; it moved to 3 cp after the pilot showed the noise was larger than assumed, because 2 cp would have needed about 11,400 pairs per group. A significant difference smaller than 3 cp is reported as detectable and practically negligible.
7. Equivalence: two one-sided tests (TOST) at alpha .05 for each pair against plus or minus 3 cp, which is the same as the 90% confidence interval lying inside plus or minus 3 cp.

## Decision rule

- Supported: all three pairwise 90% confidence intervals lie inside plus or minus 3 cp.
- Refuted: the omnibus Wald test is significant and at least one pairwise difference is significant after Holm correction with an absolute size of at least 3 cp. The report then says which directional theory the pattern matches: higher ACPL after a win on time matches the lucky escape; higher ACPL after checkmate matches earned confidence.
- Anything else is inconclusive.

`analyze.py` applies this rule and prints the decision.

## Checks that decide whether an effect is real

1. Time control. The primary analysis is rerun separately within each rapid time control that has at least 100 pairs in every group. An effect that appears only in the pooled data is reported as a composition confound.
2. Previous position. The primary model plus the previous game's final engine evaluation from the player's side and whether the next game is a rematch. If the win-type effect disappears once the final evaluation is in the model, the mechanism is position quality, and the report says so.
3. The primary test restricted to previous wins where the final evaluation from the player's side is at least -100 cp, meaning the player was not losing on the board.
4. Elo band sensitivity: the primary test within [1200, 1600) and [1600, 2000).
5. Pre-analysed games: the primary test using Lichess's own [%eval] comments, for games that have them. This subset is selected by users requesting analysis, so it is a comparison and never the main result.
6. Rematches: the primary test with rematches removed (next game against the same opponent as the winning game). The pilot showed rematches are three times as common after checkmate as after a win on time, so an effect that disappears here is a rematch effect.
7. Model form: a mixed model with a random intercept per player in place of clustered standard errors.

## Amendments

None yet.
