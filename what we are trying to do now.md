# What we are trying to do now

Handoff note written at the end of the first working session (2026-10-07). Read this and `README.md` before doing anything.

## The study in two lines

Does the way a chess game is won (on time, by checkmate, by resignation) change how well the winner plays their next game? Data is the Lichess monthly database dumps, move quality is Stockfish mean centipawn loss on moves 15 to 30, and the test is a within-player repeated-measures ANOVA. The full design is in `README.md`; the analysis plan is in `PREREGISTRATION.md`.

## Where things stand

The whole pipeline is written, tested on synthetic data (18 tests pass) and pushed to `main`. No real Lichess data has been pulled yet. The only blocker so far was the cloud environment's network policy, which denied `database.lichess.org` and `lichess.org`. Karana has since set the environment's Network access to Full, and that is why this new session exists: to check that the network now works and start pulling data.

The immediate job is step 1 below. Do not skip ahead to scoring.

## Next steps, in order

1. Check the network: `curl -sS -I https://database.lichess.org/` should return HTTP 200. If it returns a 403 from the proxy, the setting has not applied. Tell Karana, and do not try to work around it.
2. Set up the environment (the container starts clean every session):
   ```
   python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip setuptools wheel
   .venv/bin/pip install -q -r requirements.txt
   DEBIAN_FRONTEND=noninteractive apt-get install -y -qq stockfish   # binary lands at /usr/games/stockfish
   .venv/bin/python -m pytest -q tests                               # expect 18 passed
   ```
   Install python-chess inside the venv. The system pip fails to build it (setuptools `install_layout` error).
3. Read https://database.lichess.org/#known-issues and pick two consecutive recent months that are clear of every listed issue. `src/fetch_month.py` already refuses 2016-12, 2020-06 to 2020-08, 2021-02, 2021-03 and anything before 2017-04, but there may be newer entries. Tell Karana which months you picked and why.
4. Pilot first, to answer the biggest open risk: are wins on time common enough in rapid to fill that group?
   ```
   .venv/bin/python src/fetch_month.py YYYY-MM --out data/pilot --max-games 2000000
   .venv/bin/python src/build_pairs.py data/pilot --out data/pilot-pairs
   ```
   Show Karana `data/pilot-pairs/cell_counts.txt`, and copy it into the repo as `results/pilot_cell_counts.txt` so it survives the container.
5. Check the checkmate rule on real games: `.venv/bin/python src/validate_checkmate.py data/pilot --n 10000`. Any disagreement means the "#" rule needs fixing before going further.
6. If the counts look workable, run the two full months in the background (each is about 90 million games, roughly 90 minutes of parsing plus the download), then `build_pairs.py` on both months together, then `benchmark_stockfish.py`.
7. Stop there. Scoring (`centipawn_loss.py`) and analysis (`analyze.py`) wait until Karana has filled in and committed `PREREGISTRATION.md`. `analyze.py` refuses to run until the `Prediction:` and `Date fixed:` lines are filled in. Do not run any engine scoring of study games before that, apart from the 20-game timing benchmark.

## Decisions Karana still has to make (in PREREGISTRATION.md)

- The directional prediction (lucky escape, earned confidence, or a win is a win) and the date it was fixed.
- The two months.
- The smallest effect of interest, in centipawns.
- N players to score, chosen after the benchmark.

These defaults were proposed and need his confirmation: Elo band 1200 to 2000, a 30-minute session cutoff between games, evals capped at plus or minus 1000 cp, at most 5 scored games per player per condition, and at least 5 scored moves for a game to count.

## Design changes already agreed (they differ from the original brief)

- Holm-corrected paired t-tests replace Tukey's HSD, because Tukey assumes independent groups. Mauchly's test and the Greenhouse-Geisser correction are added.
- "Next game" means the immediately following rated game of any speed, within 30 minutes of the previous game ending. A blitz game in between breaks the link.
- Games with a BOT account are dropped.
- Checkmate is detected from the "#" on the last move after stripping comments (so `[%eval #3]` is not read as mate), instead of replaying every game. `validate_checkmate.py` checks this against a full replay.
- Data comes from the monthly dumps, not the per-user Lichess API, because the API cannot give a random sample of players and is rate limited.

## Files

- `src/fetch_month.py` streams a month without saving the 30 GB file. It writes `games.tsv.zst` (every rated game, for sequencing) and `rapid.pgn.zst` (eligible rapid games only).
- `src/build_pairs.py` links each game to the player's previous win and writes `pairs.parquet` and `cell_counts.txt`.
- `src/validate_checkmate.py`, `src/benchmark_stockfish.py`, `src/centipawn_loss.py`, `src/engine_eval.py` and `src/analyze.py` are described in the README's Files section.
- `data/` is git-ignored. Everything in it is lost when the container is reclaimed, so commit small outputs (cell counts, reports) to `results/`.

## Gotchas already hit

- Two zstd writers must not share one `ZstdCompressor`; that corrupted both outputs. It is fixed, so keep one compressor per output.
- pingouin 0.7 renamed its columns (`p_unc`, `p_corr`, `p_GG_corr`). `analyze.py` handles both spellings.
- Disk allowance is about 31 GB. The full months must be streamed, never downloaded whole.

## How Karana wants to work

- Commit and push straight to `main`. No feature branches, no pull requests unless he asks.
- Casual chat is fine. Any prose that goes into the repo (README, preregistration, reports) follows his human-voice writing skill: plain, specific, no em dashes.
- He wants serious research: flag design problems plainly instead of glossing over them.
