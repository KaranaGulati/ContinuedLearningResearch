# Does how you win change how you play next?

Summary of the confirmatory result, 7 October 2026. Full tables are in `results/confirmatory/report.md`, the plan fixed before the data was scored is in `PREREGISTRATION.md`, and the code is in `src/`.

## Result

The way a rapid game is won does not measurably change how well the winner plays their next game. Across 18,002 next games, average centipawn loss after a win on time, a checkmate and a resignation differed by less than 1 centipawn, and every difference is pinned inside plus or minus 3 centipawns. This was the preregistered prediction, and it is supported under the preregistered decision rule.

| previous game won by | next games | mean centipawn loss | SD |
|---|---|---|---|
| time | 6,007 | 71.91 | 49.70 |
| checkmate | 5,971 | 70.93 | 51.20 |
| resignation | 6,024 | 71.56 | 50.76 |

Adjusted for the player's rating, the rating gap to the opponent, colour and time control:

| difference | centipawns | 90% CI | TOST p |
|---|---|---|---|
| time minus checkmate | 0.88 | -0.62 to 2.38 | 0.010 |
| resignation minus checkmate | 0.56 | -0.95 to 2.07 | 0.004 |
| time minus resignation | 0.31 | -1.18 to 1.81 | 0.002 |

The omnibus test of any difference between the three groups gave p = 0.62. The largest gap, 0.88 centipawns, is about 1% of the typical 71 centipawns of loss per move.

## Why the question was open

Gee, Seese, Curley and Ward (arXiv:2503.21713) found almost no winner or loser effects on whether a Lichess player wins the next game, but treated every win as the same. Chowdhary, Iacopini and Battiston (2023) found that wins and losses cluster into streaks. Neither measured how well the next game was actually played, or asked whether a win on time, where the winner was often losing on the board, carries over differently from a checkmate.

## Data

Lichess's public database of rated standard games, 1 to 5 August and 1 to 5 September 2026: 24.3 million games. A pair is a rapid win followed by the same player's next rated game, which must also be rapid, must start within 30 minutes of the win ending, and must not have any other rated game in between. Players rated 1200 to 2000 only. Games with BOT accounts were removed.

The checkmate and resignation groups were sampled to match the win-on-time group's mix of rating (100-point bins) and time control exactly, because players who win on time are not a random set of winners. Each player appears at most once per group. The 592 players used in the exploratory pilot were excluded.

## Measuring move quality

Each next game was scored with Stockfish 16 at a fixed depth of 15, on the player's moves 15 to 30, following Backus et al. (2023). A move's loss is how much the engine evaluation dropped from the mover's side, clipped at zero and capped at 10 pawns, and each position was evaluated once. A game counts if at least 5 of the player's moves were scored. Two separate runs that happened to score the same 38 games produced identical numbers, so the scoring is reproducible.

## Checks

Nothing changed the conclusion. No check produced a significant difference between win types.

- Within 10+0, which holds 80% of the pairs, all three differences were inside plus or minus 3 centipawns.
- Adding the final engine evaluation of the winning game, and whether the next game was a rematch, shrank every difference to under 0.2 centipawns.
- Keeping only wins where the winner was not losing on the board at the end gave the same result.
- In the 1200 to 1600 band all three differences were inside plus or minus 3 centipawns. In 1600 to 2000, two upper confidence limits reached 3.4 centipawns, so equivalence at 3 is not shown in that band; neither difference was significant (Holm p = 0.47).
- Removing rematches, and using a mixed model with a random effect per player instead of clustered standard errors, gave the same answer.
- The smaller time controls (10+5, 15+10) and the subset of games Lichess users had analysed themselves had too few pairs to show equivalence, and showed no significant difference either.

## Limitations

- The data covers about nine days, all from the first days of two months.
- Only rapid games and players rated 1200 to 2000. Bullet and blitz, where wins on time are far more common, were left out on purpose because time pressure and move quality are tangled there, so the result says nothing about them.
- Centipawn loss on moves 15 to 30 is one measure of play. An effect could show up later in the game, in time use, or in the result, none of which were tested here.
- Casual games are not in the public database, so a casual game played between two rated games is invisible.
- The design changed during the project, from comparing each player with themselves to comparing matched groups of pairs. The change was made before any confirmatory game was scored.
- The prediction was chosen after an exploratory pilot of 200 pairs per group, which showed no difference. It was written down and committed at 15:22 UTC on 7 October 2026, before any of the confirmatory sample was scored, and the pilot players were excluded from it. The git history shows the order.
- 1,488 of the 19,490 sampled pairs (7.6%) had too few scored moves to count, slightly more than the 6.5% the sample size allowed for.

## What it means

For club players in rapid, scraping a game on the clock, mating, or watching the opponent resign leads to the same quality of play next game, to within a few centipawns. Studies that code the previous result as simply won or lost are not hiding a large difference between kinds of win, at least for this measure and this population.
