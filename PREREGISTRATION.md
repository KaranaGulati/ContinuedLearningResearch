# Preregistration

Status: draft. Nothing below is fixed until the prediction and date are filled in and the file is committed. After that commit, this file is not edited. Any later change goes in a dated amendment at the bottom, with the reason, and the report lists every amendment.

`src/analyze.py` will not run until the two lines below are filled in.

Prediction: TBD
Date fixed:

The three options are in the README. Write one of them in a sentence that names the ordering, for example "next-game ACPL is highest after a win on time, and the time vs checkmate and time vs resign differences are both positive". All tests stay two-tailed whichever is chosen.

## What has been looked at before fixing this

A pilot on the first 2,000,000 games of the 2026-09 dump (about 17 hours of play) was run on 2026-10-07. From it the following were seen:

- Sample sizes: 5,171 players with all three conditions once the current game reaches ply 30, and 17,334 / 47,899 / 103,421 pairs after a win on time / checkmate / resignation. 10+0 holds about 80% of rapid pairs.
- The "#" checkmate rule agreed with a full replay on all 10,000 decisive Normal games checked (3,452 mates, 6,548 resignations).
- Session gaps: median about 1 minute, 90th percentile about 10 minutes.
- Rematch share by condition: 2.9% after a win on time, 9.4% after checkmate, 7.3% after resignation.
- 19% of eligible rapid games carry Lichess [%eval] comments, not the 6% stated in the README.
- Next-game result by condition was also printed: the player won 48.8% of next games after a win on time, 50.9% after checkmate and 49.9% after resignation. This is the outcome Gee et al. studied, not this study's dependent variable, but it was seen before the prediction was fixed, so it is recorded here.

No move-quality number has been computed on any study game. No engine has been run on a study game except the 20-game timing benchmark, whose ACPL values are not printed.

## Data

Lichess monthly dumps of rated standard games, two consecutive months: 2026-08 (91,912,325 games) and 2026-09 (89,616,462 games). Both were checked against https://database.lichess.org/#known-issues on 2026-10-07; the only entries after March 2021 concern Chess960 and Antichess, which are not in the standard dump. `fetch_month.py` refuses 2016-12, 2020-06 to 2020-08, 2021-02, 2021-03 and anything before 2017-04.

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

## Players

- The player's rating in the current game is in [1200, 2000).
- The current game reaches at least ply 30, so both players have at least one move inside the scored window.
- The player has at least one qualifying game in each of the three conditions. Players missing any condition are excluded from the test.

## Sampling for the engine

From the complete players, [N players] are drawn at random (seed 20261007). For each sampled player, at most 5 games per condition are scored, drawn at random with the same seed. N is set after the Stockfish benchmark and before any scoring, and is written here.

## Dependent variable

Mean centipawn loss of the player over their own moves 15 to 30 in the current game.

- Stockfish 16, fixed depth 15, 1 thread, 64 MB hash, new game sent before each game.
- Each position from ply 28 to ply 60 (or the end of the game) is evaluated once. A move's loss is the drop in evaluation from the mover's point of view between the position before and the position after, clipped at zero.
- Mate scores become +-100,000 cp and every evaluation is then capped at +-1000 cp. A missed mate therefore costs at most 1000 cp, so one blunder cannot outweigh a whole game.
- A game's ACPL counts only if at least 5 of the player's moves were scored.

## Primary analysis

1. Collapse to one number per player per condition: the mean of that player's game-level ACPL in that condition.
2. One-way repeated-measures ANOVA, three levels, alpha 0.05, two-tailed. Mauchly's test is reported. If sphericity is rejected, the Greenhouse-Geisser corrected p is the one used for the decision.
3. Effect sizes: eta squared and partial eta squared.
4. Post hoc: paired t-tests on all three pairs with Holm correction, with Cohen's dz.
5. Smallest effect of interest: [X] cp difference between two conditions. A significant pair with an absolute difference below this is reported as statistically detectable and practically negligible.

## Decision rule

The prediction is supported if the omnibus test is significant and the post-hoc pairs it names are significant in the predicted direction and at least as large as the smallest effect of interest. The null ("a win is a win") is supported if the omnibus test is not significant and every pair's 95% confidence interval lies inside plus or minus the smallest effect of interest. Anything else is reported as inconclusive.

## Checks that decide whether an effect is real

1. Time control. The primary analysis is rerun separately within each rapid time control that has at least 100 complete players. An effect that appears only in the pooled data is reported as a composition confound.
2. Previous position. A mixed model on game-level ACPL with a random intercept per player, condition (checkmate as the reference), the previous game's final engine evaluation from the player's side, the rating gap, whether the next game is a rematch, colour, and time control. If the condition effect disappears once the final evaluation is in the model, the mechanism is position quality, and the report says so.
3. The primary test restricted to previous wins where the final evaluation from the player's side is at least -100 cp, meaning the player was not losing on the board.
4. Elo band sensitivity: the primary test within [1200, 1600) and [1600, 2000).
5. Pre-analysed games: the primary test using Lichess's own [%eval] comments, for games that have them. This subset is selected by users requesting analysis, so it is a comparison and never the main result.
6. Rematches: the primary test with rematches removed (next game against the same opponent as the winning game). The pilot showed rematches are three times as common after checkmate as after a win on time, so an effect that disappears here is a rematch effect.

## Amendments

None yet.
