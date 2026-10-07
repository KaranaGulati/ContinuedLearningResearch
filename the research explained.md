# The research explained

Everything about this project in one file: the question, why it was open, the data, the method, what was done step by step, the result, the checks, the limitations, and how to reproduce it. Work done on 7 October 2026. Every number here comes from files in this repository: `results/confirmatory/report.md`, `results/pilot/report.md`, `results/pilot_cell_counts.txt` and `PREREGISTRATION.md`.

## 1. The question

Does the way a chess game is won change how well the winner plays their next game?

On a player's profile, a win on time, a win by checkmate and a win because the opponent resigned all count the same. They are not the same experience. Winning on time often means you were losing on the board and the opponent's clock ran out first, which is closer to a lucky escape than a victory. Checkmate is the most decisive way to win. If the next game is played differently depending on which of these happened, then "a win" is not one thing, and studies that treat the previous result as simply won or lost are mixing different events together.

## 2. Why nobody had answered it

Two earlier studies came close.

Gee, Seese, Curley and Ward (arXiv:2503.21713) fitted a hierarchical Bayesian model to Lichess games and found almost no winner or loser effects on the chance of winning the next game. Player-level effects ranged from -0.02 to 0.03, and most intervals contained zero. In their own future-directions section they note that they did not separate kinds of win, and that 24% of bullet games in their grandmaster cohort were won on time, which they suggest may affect later play differently.

Chowdhary, Iacopini and Battiston (2023, Scientific Reports 13:2113) found that wins and losses cluster into streaks more than chance would predict, with cold streaks lasting longer than hot ones. Their outcome is the result itself, on blitz games.

So results cluster, the previous result barely predicts the next one, and nobody had measured the quality of the moves in the next game broken down by how the previous game was won. That is the gap this study fills.

## 3. The three competing ideas

The original brief listed three theories with no favourite.

1. Lucky escape. A win on time is unearned, the arousal carries over, and the next game is played worst after a win on time.
2. Earned confidence. Checkmate is the most decisive win, so if overconfidence hurts play, the next game is played worst after checkmate.
3. A win is a win. Players do not distinguish between kinds of win, and next-game play is the same after all three.

## 4. Data

### Source

The Lichess open database (https://database.lichess.org/), which publishes every rated game played on Lichess each month under a CC0 licence. One month is about 30 GB compressed and about 90 million games.

### Months used and why

Lichess keeps a list of known problems in its data. Some of them attack this design directly: on 9 February 2021 games were recorded as resigned after they had already ended (fake resignations), on 12 March 2021 a datacenter fire left some games with wrong results, and in June 2020 and before March 2016 players could play themselves in rated games. The list was checked on 7 October 2026. Nothing after March 2021 affects standard chess (the later entries are about Chess960 and Antichess), so the two most recent months were chosen: August and September 2026.

The download script streams each month and never stores the full 30 GB file, because the cloud machine had about 29 GB of disk. A restart of the machine cut both downloads partway through. What had been read by then covers 1 August 00:00 to 5 August 04:04 UTC (12,258,314 games) and 1 September 00:00 to 5 September 00:55 UTC (12,022,960 games), 24.3 million games in total. Within those windows every rated game is present, so each player's sequence of games is complete. This turned out to be far more data than the study needed, so the rest of the months were not downloaded.

### Which games count

- Rated games of standard chess, with no custom starting position.
- Rapid games only, using Lichess's own rule: base time plus 40 times the increment is at least 8 minutes and under 25 minutes. Bullet and blitz were left out on purpose. In fast games, time pressure and move quality are tangled together (Sunde, Zegners and Strittmatter showed the time-pressure effect flips sign depending on how you condition on decision time), so a cleaner comparison needed slower games.
- Games involving accounts with the BOT title were removed.
- Players rated 1200 to 2000 in the next game.

## 5. Turning games into pairs

The unit of the study is a pair: a rapid win, followed by the same player's next rated game. A pair counts only if:

- the player's immediately previous rated game, of any speed, was the rapid win, so a blitz game played in between breaks the link;
- the next game is also an eligible rapid game;
- the next game started no more than 30 minutes after the win ended. The end of a game is estimated from its start time plus the clock time both players used. The point of the cutoff is that any carry-over effect is about what happens right after a win, not three days later. In the data the median gap was about 1 minute.
- the next game lasted at least 30 plies, so there are moves in the scoring window.

## 6. Classifying how a game was won

This is harder than it looks. The PGN `Termination` tag has the values `Normal`, `Time forfeit`, `Abandoned`, `Rules infraction` and `Unterminated`. `Normal` covers both checkmate and resignation, so the tag alone cannot separate two of the three groups.

The rule used:

- `Time forfeit` and the player won: won on time.
- `Normal`, and the last move of the game carries the checkmate symbol `#`: won by checkmate. Comments are stripped first, because Lichess writes engine evaluations such as `[%eval #3]` inside comments, and those would otherwise be read as a mate.
- `Normal`, decisive, no `#`: won by resignation.
- Abandoned games, rules infractions, unterminated games and draws are never counted as a win.

The `#` rule was checked against a full replay of the game with the python-chess library, which tests whether the final position really is checkmate. On 10,000 real decisive games it agreed every time (3,452 checkmates, 6,548 resignations, 0 mismatches).

## 7. Measuring how well the next game was played

Move quality is measured as average centipawn loss (ACPL), the standard method running from Guid and Bratko (2006) through Backus et al. (2023) to Kuenn, Seel and Zegners. A centipawn is one hundredth of a pawn.

For each move, Stockfish evaluates the position before the move and the position after it, both from the mover's point of view. The loss is the drop between the two. Playing the engine's best move costs zero. A player's score for a game is the average loss over their own moves.

Settings:

- Stockfish 16 at a fixed search depth of 15, one thread per engine. Fixed depth rather than a time limit makes the numbers reproducible on any machine, and depth 15 matches Backus et al.
- Only moves 15 to 30, following Backus et al., to skip memorised opening moves and keep the compute manageable.
- Each position is evaluated once. The position after your move is the position before your opponent's move, so one evaluation serves both, which halves the work.
- Evaluations are flipped for Black. Engines report scores from White's side by convention, and forgetting the flip makes every Black move look like a blunder.
- Losses below zero are set to zero, because nobody can beat the engine's best move and negative values are search noise.
- Mate scores are converted to a large number and every evaluation is capped at plus or minus 1000 centipawns (10 pawns), so a single missed mate cannot swamp a whole game's average.
- A game counts only if at least 5 of the player's moves were scored.

The roughly 19% of Lichess games that already carry engine evaluations were not used as the main source. Those exist only because a user asked Lichess to analyse that game, and people analyse games that felt strange or that they lost. That selection could depend on exactly the thing being studied. They were used only as a side check.

## 8. Design: comparing matched groups of pairs

The original brief planned a within-player design, where each player contributes games in all three categories and is compared with themselves. During the project, before any confirmatory game was scored, the design was changed to comparing three groups of pairs: pairs after a win on time, pairs after a checkmate, and pairs after a resignation. A player can appear in more than one group, but at most once in each.

Comparing different players creates a risk: the people who win on time may differ from the people who win by checkmate, for example in rating or in which time control they play, and two things deal with that.

- Matched sampling. The win-on-time group is drawn at random first. The checkmate and resignation groups are then drawn so that their mix of rating (in 100-point bins) and time control is exactly the same as the win-on-time group's.
- Adjustment. The model also controls for the player's rating, the rating gap to the opponent, colour, and time control.

A simulation tested this. When winners on time were made 300 rating points weaker but the way of winning did nothing, the raw averages showed a false gap of about 12 centipawns and the adjusted model correctly showed none.

## 9. Statistical analysis

- Outcome: the next game's ACPL.
- Model: ordinary least squares regression with the kind of win (checkmate as the reference), rating, rating gap, colour and time control. Standard errors are clustered by player, because the same player can appear in more than one group.
- Overall test: a Wald test of whether the two win-type coefficients are both zero.
- Pairwise differences: time minus checkmate, resignation minus checkmate, and time minus resignation, with Holm correction for testing three pairs.
- Equivalence test: because the prediction was "no difference", a non-significant p-value is not enough. A small sample also gives non-significant results. The study used two one-sided tests (TOST) against a smallest effect of interest of 3 centipawns. A difference counts as equivalent to zero when its 90% confidence interval lies entirely inside plus or minus 3 centipawns.

The analysis code was checked on simulated data before use. It found a planted 6-centipawn effect in the right pair, gave small differences when there was no effect, and removed the rating confound described above. Over 300 simulated datasets with no real effect, it gave a false positive 6.0% of the time at the 5% level, which is within sampling error of the nominal rate.

## 10. What was done, step by step

1. Wrote the brief (`README.md`) and the full pipeline in `src/`, with tests in `tests/`.
2. Fixed design problems found in review before any data was pulled: Tukey's test does not suit repeated measures, there was no limit on the gap between games, and the date rule in the brief did not exclude the 2020 and 2021 problem months.
3. Ran a pilot download of 2 million games to check whether wins on time are common enough in rapid. They were: 5,171 players had all three kinds of win in that small slice. This also showed rematches against the same opponent were three times as common after checkmate (9.4%) as after a win on time (2.9%), so a rematch check was added.
4. Downloaded the main data (the windows in section 4).
5. Ran an exploratory pilot of 200 pairs per group to learn how noisy ACPL is and what the data looked like. Its players were later excluded from the main test.
6. Fixed the plan in `PREREGISTRATION.md` and committed it at 15:22 UTC on 7 October 2026, before any game of the main sample was scored. The prediction, threshold and sample size were chosen by Claude at Karana's request, and the file records that and the reasons.
7. Scored the main sample with Stockfish: 38,852 engine jobs (each next game, plus the final position of each winning game for one of the checks), about five hours across three runs. The scoring resumes where it stopped, so the time limit on background jobs lost nothing.
8. Ran the preregistered analysis.

Problems hit and fixed along the way, each with a test where possible:

- Two compressed output files shared one compressor and corrupted each other.
- Draws were mislabelled as losses because an empty winner field read back as missing.
- A dropped connection let the download script report "done" on a partial month. It now resumes from the exact byte where it stopped and marks incomplete months.
- A leftover copy of the scoring program ran alongside the real one. No data was damaged, and the 38 games both copies scored came out identical, which confirmed the engine setup is reproducible. The scorer now refuses to run twice at once.

## 11. The pilot

200 pairs per group, exploratory only.

| previous game won by | mean ACPL in the next game |
|---|---|
| time | 71.7 |
| checkmate | 75.5 |
| resignation | 70.9 |

After adjustment, every difference was within about 4 centipawns of zero (overall p = 0.65). The direction flipped between rating bands. The main lesson was that ACPL is noisier than assumed: the leftover standard deviation after adjustment was 46.7 centipawns, not the 30 that had been guessed, and that number set the size of the main test.

## 12. The prediction and the sample size

The prediction, fixed before the main data was scored: a win is a win. Next-game ACPL does not differ between the three groups, and every pairwise difference lies within plus or minus 3 centipawns.

It was chosen because Gee et al. found almost no winner effects, and the pilot found no difference either. The threshold of 3 centipawns is about 4% of the typical 72 centipawns of loss per move. The draft had 2 centipawns, but at the pilot's noise level that would have needed about 11,400 pairs per group and 8.5 hours of computing.

Sample size: 6,500 pairs per group. A simulation using the pilot's noise level gave about 85% power for all three equivalence tests to pass when the true differences are zero, after allowing for pairs lost to short games.

The decision rule, also fixed in advance:

- Supported: all three pairwise 90% confidence intervals lie inside plus or minus 3 centipawns.
- Refuted: the overall test is significant and at least one difference is significant after Holm correction and at least 3 centipawns in size.
- Anything else: inconclusive.

## 13. The result

The prediction is supported. The way a rapid game is won does not measurably change how well the winner plays the next game.

19,490 pairs were sampled (6,500 time, 6,493 checkmate, 6,497 resignation, from 17,959 players). 18,002 of them had enough scored moves to count.

| previous game won by | next games | mean ACPL | SD |
|---|---|---|---|
| time | 6,007 | 71.91 | 49.70 |
| checkmate | 5,971 | 70.93 | 51.20 |
| resignation | 6,024 | 71.56 | 50.76 |

Adjusted differences in centipawns:

| difference | estimate | 95% CI | 90% CI | Holm p | TOST p |
|---|---|---|---|---|---|
| time minus checkmate | 0.88 | -0.91 to 2.66 | -0.62 to 2.38 | 1.00 | 0.010 |
| resignation minus checkmate | 0.56 | -1.23 to 2.36 | -0.95 to 2.07 | 1.00 | 0.004 |
| time minus resignation | 0.31 | -1.46 to 2.09 | -1.18 to 1.81 | 1.00 | 0.002 |

Overall Wald test: chi-squared(2) = 0.95, p = 0.62. The largest difference, 0.88 centipawns, is about 1% of the typical loss per move. All three 90% intervals sit inside plus or minus 3 centipawns, so all three equivalence tests pass.

## 14. Checks on the result

None of these produced a significant difference between kinds of win.

| check | what it tests | outcome |
|---|---|---|
| Within 10+0 only (80% of pairs) | whether pooling time controls hides or creates an effect | all three differences inside plus or minus 3 cp (largest 0.49) |
| Adding the final evaluation of the winning game and a rematch flag | whether being lucky on the board, rather than the way of winning, drives anything | every difference under 0.2 cp; the final evaluation itself had no effect (-0.12 cp per pawn, SE 0.11) |
| Only wins where the winner was not losing at the end | removes the "won on time from a lost position" cases | all three inside plus or minus 3 cp |
| Rating 1200 to 1600 | sensitivity to the rating band | all three inside plus or minus 3 cp |
| Rating 1600 to 2000 | sensitivity to the rating band | not significant (Holm p = 0.47), but two upper limits reach 3.4 cp, so equivalence at 3 is not shown in this band |
| Rematches removed | whether replaying the same opponent drives anything | all three inside plus or minus 3 cp |
| Mixed model with a random effect per player | whether the result depends on the model form | same estimates (0.88, 0.56, 0.31) |
| Time controls 10+5 and 15+10 | smaller time controls on their own | too few pairs to show equivalence; no significant difference |
| Games Lichess users had analysed themselves (2,985 pairs) | the evaluations Lichess already stores | too few to show equivalence; no significant difference |

## 15. Limitations

- The data covers about nine days, all from the first days of two months.
- Only rapid games and players rated 1200 to 2000. Bullet and blitz, where wins on time are much more common, were excluded on purpose, so the result says nothing about them.
- ACPL on moves 15 to 30 is one measure of play. An effect could appear later in the game, in how the clock is used, or in the result, none of which were tested.
- Casual games are not in the public database, so a casual game played between two rated games is invisible.
- The design changed from within-player to matched groups, and the threshold moved from 2 to 3 centipawns. Both changes were made before any main-sample game was scored, and both are recorded.
- The prediction was written after the exploratory pilot, which is why the pilot's players were excluded from the main sample. The git history shows the preregistration commit came before the main scoring.
- 1,488 of the 19,490 sampled pairs (7.6%) had too few scored moves to count, slightly more than the 6.5% allowed for.
- Matching was on rating and time control only. Other differences between the people who win on time and those who win by checkmate are handled only by the covariates in the model.

## 16. What it means

For club players in rapid chess, scraping a win on the clock, delivering checkmate and watching the opponent resign lead to the same quality of play in the next game, to within a few centipawns. Studies that code the previous game as simply won or lost are not hiding a large difference between kinds of win, at least for this measure, this population and this kind of chess. Testing bullet and blitz, a full month or more, and other measures such as time use would be the obvious next steps.

## 17. How to reproduce it

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
sudo apt-get install stockfish
.venv/bin/python -m pytest -q tests          # 23 tests

.venv/bin/python src/fetch_month.py 2026-08 --out data/2026-08
.venv/bin/python src/fetch_month.py 2026-09 --out data/2026-09
.venv/bin/python src/build_pairs.py data/2026-08 data/2026-09 --out data/partial-pairs --allow-partial
.venv/bin/python src/centipawn_loss.py --pairs data/partial-pairs/pairs.parquet --pgn data/2026-08 data/2026-09 \
    --out data/pilot-scores --elo-min 1200 --elo-max 2000 --n-per-group 200 --depth 15
.venv/bin/python src/centipawn_loss.py --pairs data/partial-pairs/pairs.parquet --pgn data/2026-08 data/2026-09 \
    --out data/confirm-scores --elo-min 1200 --elo-max 2000 --n-per-group 6500 --depth 15 \
    --exclude data/pilot-scores/sample.parquet
.venv/bin/python src/analyze.py --scores data/confirm-scores --out results/confirmatory
```

The fetch commands read the full months. The study used the first part of each, as described in section 4, so an exact rerun needs `--max-games 12258314` for August and `--max-games 12022960` for September. Samples are drawn with the fixed seed 20261007.

## 18. Files in this repository

| file | what it is |
|---|---|
| `README.md` | the original brief |
| `PREREGISTRATION.md` | the plan fixed before the main data was scored |
| `results/SUMMARY.md` | a two-page summary of the result |
| `results/confirmatory/report.md` | full tables for the main test and every check |
| `results/pilot/report.md` | the exploratory pilot |
| `results/pilot_cell_counts.txt` | sample sizes from the first 2-million-game pilot |
| `src/fetch_month.py` | streams and filters a monthly Lichess file |
| `src/build_pairs.py` | links each win to the player's next game |
| `src/validate_checkmate.py` | checks the `#` rule against a full replay |
| `src/centipawn_loss.py` | samples pairs and scores them with Stockfish |
| `src/engine_eval.py` | the centipawn loss arithmetic |
| `src/analyze.py` | the regression, equivalence tests, checks and decision rule |
| `tests/` | 23 tests covering every stage |

## 19. References

- Backus, P., Cubel, M., Guid, M., Sanchez-Pages, S. and Lopez Manas, E. (2023). Quantitative Economics 14(1). Houdini 1.5a at depth 15, moves 15 to 30.
- Chowdhary, S., Iacopini, I. and Battiston, F. (2023). Scientific Reports 13:2113.
- Gee, Seese, Curley and Ward (2025). arXiv:2503.21713.
- Guid, M. and Bratko, I. (2006). ICGA Journal.
- Kuenn, Seel and Zegners. IZA Discussion Paper 13491.
- Regan, Biswas and Zhou (AAAI-14 workshop). Centipawn values are not comparable across engines.
- Sunde, Zegners and Strittmatter. Cited in the brief for the finding that the time-pressure effect on move quality flips sign depending on whether decision time is conditioned on; full reference to be added.
- Lichess open database, https://database.lichess.org/ (CC0).
