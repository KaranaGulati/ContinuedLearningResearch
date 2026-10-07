# Does how you won change how you play next?

A study of whether the manner in which a chess game ends affects the quality of the player's
following game, using the Lichess open database and engine-scored move quality.

Status: pipeline written and tested on synthetic data. No Lichess data has been pulled yet, and the
preregistration is waiting on a dated directional prediction. This file is the brief.

## The question

Winning on time, winning by checkmate, and winning because your opponent resigned all record
the same thing on your profile. They are not the same experience. Flagging someone while you
were losing on the board is closer to a lucky escape than a victory.

If next-game move quality differs by how the previous game was won, then "a win" is not one
thing, and every study that treats previous-game result as a binary has been collapsing a real
distinction.

## Why this is open

Gee, Seese, Curley and Ward fitted a hierarchical Bayesian model to Lichess games and found
little evidence for winner-loser effects, with player-level effects on next-game win probability
between -0.02 and 0.03 and most intervals containing zero. Extending the history from one prior
game to ten changed nothing.

Two things in their own Summary and Future Directions section leave this open. They write that
they did not attempt to separate winner and loser effects or allow them different magnitudes.
And they note that 24% of bullet games in their grandmaster cohort are won on time, adding that
results of this form may have a different impact on future performance than other endings.

Separately, Chowdhary, Iacopini and Battiston found wins and losses cluster more than chance
against a within-player shuffle null, with cold streaks longer than hot ones. Their outcome is
the win or loss itself, measured on blitz games and openings only.

So outcomes cluster, the previous result does not predict the next one, and nobody has measured
the thing in between: how well the moves were actually played. The cell "previous game's manner
of ending, by this game's move quality" is empty.

## Hypotheses

Unit of analysis is the player, not the game and not the move.

Independent variable: how that player's previous game was won. Three levels, won on time, won
by checkmate, won by opponent resignation.

Dependent variable: that player's mean centipawn loss in the game immediately following.

Design: within-subjects. Each player contributes all three numbers, so only players with games
in all three categories enter the test.

H0: mu_time = mu_checkmate = mu_resign. The manner of winning has no effect on next-game mean
centipawn loss.

H1: at least one pair of means differs.

H1 is not "all three differ". The omnibus F test says something differs somewhere and cannot
say what, which is what the post-hoc test is for. The likeliest outcome is a significant F with
only one pair clearing the Holm-corrected post-hoc threshold.

### Directional prediction, to be fixed before looking at data

Three live theories, no obvious favourite:

1. Lucky escape. Winning on time often means you were losing on the board, so the win is
   unearned and the arousal carries into the next game, putting the highest error after a win
   on time.
2. Earned confidence. Checkmate is the most decisive win, so if overconfidence is what degrades
   play then checkmate should do the most damage, which reverses the ordering in prediction 1.
3. A win is a win. Players do not distinguish between the three, and the result is a null.

Pick one and write it in `PREREGISTRATION.md` with a date before touching the data, keeping all
tests two-tailed, and do not revise it afterwards. `src/analyze.py` refuses to run until it is filled in.

## Data

Lichess monthly PGN dumps from https://database.lichess.org/, released CC0.

Roughly 30 GB compressed per month and about 90 million games per month in recent years, so
you want one or two months, filtered hard, not the whole archive.

### Filters to apply

Rapid time controls only. The reason is not that fast games have worse moves, it is that in
bullet and blitz, time pressure and move quality are entangled. Sunde, Zegners and Strittmatter
showed the time-pressure coefficient flips sign depending on whether you condition on decision
time, so separating them cleanly matters.

Rated games only. Standard chess only, no variants.

An Elo band, fixed in advance and reported with a sensitivity check.

Only players with at least one game in each of the three win categories, since the design is
within-subjects.

Watch the cell counts after filtering. Wins on time concentrate in fast time controls, so the
rapid filter may thin that group badly. Check this before anything else.

### Dates to exclude, from the Lichess known-issues list

These are not optional, and three of them attack this design specifically.

- 2021-02-09. Games were recorded as resigned after the game had already ended. Manufactures
  fake resignations, which is one of our three groups.
- 2021-03-12. Datacenter fire left some games with incorrect results. The result and termination
  are the whole independent variable here.
- 2020-06, and everything before 2016-03. Players could play themselves in rated games. Poison
  for a design that tracks consecutive games by one player.
- 2016-12, and before 2016 generally. Incorrect evaluations, and mate scores that may not be
  forced in the stated number of moves.
- 2020-07 especially the 31st, and 2020-08 up to the 16th. Incorrect evaluations in the opening
  up to 15 plies. We drop the first 15 moves anyway, so this mostly misses us, but say so in the
  methods.

Sampling from April 2017 or later guarantees clock data, since `%clk` comments only exist from then,
but it does not clear the 2020 and 2021 entries above. `src/fetch_month.py` refuses every month
listed here and anything before 2017-04.

## Classifying the win

This is less free than it first looks. The PGN `Termination` tag has values `Normal`,
`Time forfeit`, `Abandoned`, `Rules infraction` and `Unterminated`. **`Normal` covers both
checkmate and resignation**, so the tag alone cannot separate two of our three groups.

The classification is:

- `Termination == "Time forfeit"` and the player won, so won on time.
- Otherwise replay the game to the final position and test `board.is_checkmate()`. True means
  won by checkmate.
- Otherwise, for a decisive game, the opponent resigned.
- Drop `Abandoned`, `Rules infraction` and `Unterminated` entirely.
- Drop draws, since this study is about manner of winning.

Replaying costs no engine time, just python-chess.

## Measuring move quality

Mean centipawn loss, following the convention that runs from Guid and Bratko (2006) through
Backus et al. (2023) to Kuenn, Seel and Zegners.

For each of your moves, the loss is the engine evaluation of the position before you moved,
minus the evaluation after the move you actually played, both from your own point of view.
Playing the engine's choice gives zero, and the player's score for the game is the average
across their own moves.

Kuenn et al. give a worked example in this form: -0.13 before the move, -1.09 after, so
-0.13 - (-1.09) = 0.96 pawns.

### Settings

- Moves 15 to 30 only, in games of at least 15 moves. This is Backus et al.'s convention, chosen
  to skip prepared openings and to limit compute. Kuenn et al. drop the first 15 "as in Backus
  et al.", so the convention is established and citable.
- Fixed search depth, never a time limit. Guid and Bratko used fixed depth so that complex
  positions automatically get more computation and results reproduce on another machine.
  Depth 15 matches Backus et al. and is defensible by citation.
- Clip losses at zero. You cannot beat the engine's best move, so negatives are search noise.
- Convert mate scores to a large finite value rather than letting them become zero.

### Two things that will silently break the numbers

Perspective. Engine evaluations are from White's point of view by convention, including the
`[%eval]` comments in the Lichess PGN. If you do not flip the sign for Black, every Black move
looks like a catastrophe. In python-chess, `info["score"].pov(colour)` handles it.

Double evaluation. The position after your move is the position before your opponent's move.
It is the same position. Evaluate each position once, store the sequence, and compute losses by
differencing consecutive evaluations with a sign flip. This halves your compute before you
change anything else. For moves 15 to 30 that is about 33 positions per game, not 64.

### Do not use the pre-analysed games

About 6% of Lichess games carry `[%eval]` comments, and only because a user clicked "request
computer analysis". That is not a random 6%. People analyse games they lost, games that felt
strange, games that mattered to them.

For this design the bias points straight at the hypothesis. Our independent variable is how the
previous game ended, and our dependent variable needs an evaluation on the next game. If a
frustrating loss on time makes someone more likely to request analysis on what follows, then
whether the dependent variable exists at all depends on the independent variable.

So run Stockfish on a random sample instead, and use the pre-analysed subset only as a
robustness check. If the result holds in both, the selection objection is answered.

Lichess also publishes a separate position-keyed evaluation database,
`lichess_db_eval.jsonl.zst`, holding about 416 million positions with centipawn scores, depth
and principal variations. Coverage is partial and itself correlated with game type, so treat it
as an optimisation to explore, not the primary source.

## Analysis

Collapse to one number per player per condition before testing anything. Moves from the same
player are not independent observations, and a test run on raw moves will return p-values like
1e-300 on effects of no consequence. After collapsing, n is the number of players, each player
acts as their own control, and the remaining observations are genuinely independent.

One-way repeated-measures ANOVA across the three groups, with Mauchly's test and the
Greenhouse-Geisser correction when sphericity fails. Then paired t-tests on the three pairs with
Holm correction to find which pairs differ. Tukey's HSD assumes independent groups, so it does not
fit a within-subjects design. Report eta squared alongside F. With thousands of players a difference of half a
centipawn will be significant and irrelevant.

### The two checks that decide whether this is real

Time control composition. Wins on time concentrate in faster play, and faster play has higher
error rates generally. Pooling across time controls will manufacture a difference that is pure
composition. **Run the analysis separately within each time control.** If the effect appears only
in pooled data and vanishes inside each control, you have found a confound, not an effect.

Previous-position quality. A player who wins on time was frequently losing on the board.
Condition on the engine evaluation at the end of the previous game. If the effect disappears,
the mechanism is position quality rather than manner of ending, which is a different and less
interesting paper.

### Known artifact to watch

If you plot anything against time remaining, there is a spike at exactly 50% of the starting
clock. Those are tournament players who "berserked", halving their clock for double points, so
their games begin at the 50% mark. Documented by the chess-blunders project, which also puts
games carrying both clock and eval data at 2 to 5%, consistent with the 6% Lichess states.

## Pipeline

1. Download one or two months of rapid-filtered Lichess PGN, 2017 or later.
2. Parse, apply filters, exclude the bad dates.
3. Classify each win as time, checkmate or resignation, using Termination plus a checkmate test
   on the final position.
4. Sort each player's games by UTC timestamp. Shift the win-classification column down one row
   so each game carries how the previous game ended.
5. Keep players with games in all three categories.
6. Benchmark Stockfish on 20 games at depths 12, 15 and 18 before committing to a sample size.
7. Score move quality on a random sample.
8. Aggregate to one mean centipawn loss per player per condition.
9. Repeated-measures ANOVA, Holm-corrected paired t-tests, eta squared. Rerun within each time control.
10. Robustness: previous-position evaluation as a covariate, Elo band sensitivity, and the
    pre-analysed 6% subset as a comparison.

## Files

- `PREREGISTRATION.md` is the analysis plan. It is a draft until the prediction and date are
  filled in and committed.
- `src/fetch_month.py` streams one monthly dump without saving it, and writes a sequencing index
  of every rated game plus the full PGN of eligible rapid games.
- `src/build_pairs.py` links each eligible game to how the same player's previous game ended,
  within a 30-minute session cutoff, and writes the cell counts. It never touches move quality.
- `src/validate_checkmate.py` replays real games to confirm the "#" checkmate rule.
- `src/benchmark_stockfish.py` measures seconds per position on this machine and projects the
  wall-clock time for several sample sizes. Run it before choosing N.
- `src/centipawn_loss.py` samples players, runs Stockfish on moves 15 to 30 with one evaluation per
  position, and appends results to a file so a stopped run resumes.
- `src/analyze.py` runs the primary test and the five checks and writes `results/report.md`.
- `tests/` covers win classification, pairing, the eval arithmetic and the analysis on simulated
  data with a planted effect.

## Running it

    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
    sudo apt-get install stockfish          # Stockfish 16 on Debian/Ubuntu
    .venv/bin/python -m pytest -q tests

    # pilot: first 2 million games of a month, to see cell counts quickly
    .venv/bin/python src/fetch_month.py 2025-03 --out data/pilot --max-games 2000000
    .venv/bin/python src/build_pairs.py data/pilot --out data/pilot-pairs

    # full run on two consecutive months
    .venv/bin/python src/fetch_month.py 2025-03 --out data/2025-03
    .venv/bin/python src/fetch_month.py 2025-04 --out data/2025-04
    .venv/bin/python src/build_pairs.py data/2025-03 data/2025-04 --out data/pairs
    .venv/bin/python src/validate_checkmate.py data/2025-03 --n 10000
    .venv/bin/python src/benchmark_stockfish.py data/2025-03

    # after PREREGISTRATION.md is dated and committed
    .venv/bin/python src/centipawn_loss.py --pairs data/pairs/pairs.parquet \
        --pgn data/2025-03 data/2025-04 --out data/scores \
        --elo-min 1200 --elo-max 2000 --n-players N --depth 15
    .venv/bin/python src/analyze.py --scores data/scores --out results

The months above are examples. Check them against the Lichess known-issues list first.

## Reporting template

> A one-way repeated-measures ANOVA showed a significant effect of manner of winning on
> next-game mean centipawn loss, F(2, df) = _, p = _, eta squared = _. Holm-corrected paired
> t-tests indicated that games following a win on time were played significantly worse than
> games following checkmate; no other pair differed.

## Related work worth citing

- Guid and Bratko (2006), ICGA Journal. Origin of the method, using CRAFTY.
- Backus, Cubel, Guid, Sanchez-Pages and Lopez Manas (2023), Quantitative Economics 14(1).
  Houdini 1.5a at depth 15, moves 15 to 30, mean error 16.5.
- Kuenn, Seel and Zegners, IZA DP 13491. Stockfish 11 at depth 25, drops the first 15 moves.
- Gee, Seese, Curley and Ward, arXiv:2503.21713. The null this study is built against.
- Chowdhary, Iacopini and Battiston (2023), Scientific Reports 13:2113. Streak clustering.
- Regan, Biswas and Zhou (AAAI-14 workshop). Centipawn units are not comparable across engines;
  Stockfish runs about 1.5 times higher in magnitude than most programs.

A full verified literature review, with 221 source-traced claims, is in
`research/chess-behavioral-lit/REPORT.md`.
