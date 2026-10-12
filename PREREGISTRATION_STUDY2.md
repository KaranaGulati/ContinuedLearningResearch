# Preregistration, study 2

Status: draft for Karana's review. Nothing below is fixed until the date line is filled in and the file is committed. After that commit the file is not edited; any later change goes in a dated amendment at the bottom.

Study 1 and its own preregistration are in `PREREGISTRATION.md` and `results/`. This study uses new data and asks one new question.

Prediction RQ1: a win is a win. Next-game ACPL does not differ between pairs after a win on time, by checkmate and by resignation; every pairwise difference lies within plus or minus 3 cp.
Prediction RQ2: players reset after every game. Next-game ACPL does not differ between lucky and deserved wins on time; the difference lies within plus or minus 2 cp.
Date fixed:

Both predictions are Karana's.

## Questions

- RQ1: does the way a rapid game is won (on time, by checkmate, by resignation) change how accurately the winner plays the next game? This repeats study 1 on new data.
- RQ2: among wins on time, does it matter whether the win was deserved? A lucky time win is one where the winner was losing on the board when the opponent's clock ran out.

## What has been looked at before fixing this

- Study 1 (1 to 5 August and 1 to 5 September 2026), including an exploratory split of its 6,500 time wins: the 1,288 lucky ones played 2.2 cp worse in the next game than checkmate winners (95% CI -0.8 to 5.3, p = 0.15). That hint is why RQ2 exists, and it is not evidence for or against it.
- An exploratory classifier on 1 to 5 September games with Lichess's own evaluations, predicting how a game ended from its evaluation graph. It did not touch next-game play.
- For 6 to 30 September, only sample sizes: 454,791 win-on-time pairs from 148,277 players, 1,266,944 checkmate pairs and 2,942,985 resignation pairs in the rating band. No engine has been run on any 6 to 30 September game and no move-quality number has been computed on them.

## Data

The full Lichess dump of rated standard games for September 2026 (89,616,462 games, download marked complete). Only pairs whose next game starts between 6 September 00:00 and 30 September 23:59 UTC are used, so no game overlaps study 1.

## Pairs

Same rules as study 1: a rapid win, then the same player's next rated game of any speed, which must be an eligible rapid game, start within 30 minutes of the win ending, and reach at least ply 30. Eligible means rated, standard, rapid by Lichess's rule, and no BOT accounts. The player's rating in the next game is in [1200, 2000). At most one pair per player per group.

## Classifying wins

- Time, checkmate and resignation exactly as in study 1 (Termination tag plus the "#" on the last move).
- Lucky time win: Stockfish 16 at depth 15 scores the final position of the winning game, and from the winner's side it is below -100 cp (losing by more than a pawn). Mate scores count as plus or minus 1000.
- Deserved time win: the same score is -100 cp or better.

## Sampling (seed 20261012)

1. Win-on-time pairs are put in random order, and their final positions are scored in that order until there are 13,000 lucky pairs.
2. RQ1 time group: the first 6,500 scored time wins, which keep the natural mix of lucky and deserved wins.
3. RQ1 checkmate and resignation groups: 6,500 each, matched to the RQ1 time group's mix of rating (100-point bins) and time control.
4. RQ2 lucky group: the 13,000 lucky pairs. RQ2 deserved group: 13,000 deserved pairs from the scored time wins, matched to the lucky group's mix of rating and time control.

A pair can be in both an RQ1 and an RQ2 group, because the two questions are analysed separately.

## Measuring the next game

Unchanged from study 1: Stockfish 16, depth 15, one thread, moves 15 to 30, each position evaluated once, losses clipped at zero, evaluations capped at plus or minus 1000 cp, and a game counts if at least 5 of the player's moves were scored.

## Analysis

The model for both questions is the one from study 1: OLS of next-game ACPL on group, the player's rating, the rating gap to the opponent, colour and time control, with standard errors clustered by player. All tests two-tailed, alpha 0.05.

RQ1 decision rule, as in study 1:
- Supported: all three pairwise 90% confidence intervals inside plus or minus 3 cp.
- Refuted: the omnibus Wald test is significant and at least one pairwise difference is significant after Holm correction and at least 3 cp in size.
- Otherwise inconclusive.

RQ2 decision rule:
- Supported: the 90% confidence interval of lucky minus deserved lies inside plus or minus 2 cp (two one-sided tests at alpha 0.05).
- Refuted: the 95% confidence interval excludes zero and the difference is at least 2 cp in size. The report says which direction: worse after a lucky win, or better.
- Otherwise inconclusive.

## Sample size

Study 1's residual SD of ACPL was 49.8 cp. For RQ2, an equivalence test against plus or minus 2 cp with 80% power when the true difference is zero needs about 10,700 pairs per group; 13,000 allows for the 7.6% of pairs study 1 lost to short games. RQ1 keeps study 1's 6,500 per group, which passed its equivalence test there.

## Checks

These do not change the decisions above. They test whether a result depends on one choice.

1. RQ1 and RQ2 within 10+0 only.
2. RQ1 and RQ2 with rematches removed.
3. RQ1 and RQ2 in the rating bands [1200, 1600) and [1600, 2000).
4. RQ2 with a stricter lucky threshold: winner losing by more than 3 pawns at the end.
5. RQ1 and RQ2 with a mixed model (random intercept per player) in place of clustered standard errors.

## Amendments

None yet.
