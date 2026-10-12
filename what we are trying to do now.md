# What we are trying to do now

Handoff note, last updated 2026-10-07. Read this, then `PREREGISTRATION.md` (the current plan) and `README.md` (the original brief).

## The study in two lines

Does the way a chess game is won (on time, by checkmate, by resignation) change how well the winner plays their next game? Move quality is Stockfish mean centipawn loss (ACPL) on moves 15 to 30 of the next game, on Lichess rapid games.

## Design (changed from the README)

Karana chose a matched pairs design on 2026-10-07. The unit is a pair: a rapid win, then the same player's next rapid game, started within 30 minutes of the win ending with no other rated game in between. Three groups: pairs after a win on time, by checkmate, by resignation. A player can be in several groups but only once per group. The checkmate and resignation groups are drawn to match the win-on-time group's mix of Elo (100-point bins) and time control. The analysis is OLS on the next game's ACPL with Elo, rating gap, colour and time control, standard errors clustered by player, a Wald omnibus test and Holm-corrected pairwise differences. The README's within-player repeated-measures ANOVA is no longer the plan.

## Where things stand

Study 1 is finished (prediction "a win is a win" supported; `results/SUMMARY.md`, `the research explained.md`, deck in `slides/`).

Study 2 is running. Its plan is fixed in `PREREGISTRATION_STUDY2.md` (commit 26b887d, 2026-10-12 11:02 UTC). Karana's predictions: RQ1 a win is a win (+-3 cp), RQ2 players reset after lucky and deserved time wins alike (+-2 cp). Karana approved automatic restarts of long jobs. His teacher has not approved the plan yet; Karana chose to run it anyway.

Progress files are committed to `results/study2-progress/` at each step so a new session can resume:
- `screen.jsonl`: final-position scores of time wins (lucky = winner below -100 cp).
- `sample.parquet`: the five groups.
- `scores.jsonl`: next-game Stockfish scores so far.

## Resuming study 2 in a new session

1. Set up the venv and Stockfish (below).
2. If `data/full-2026-09` is gone: `python src/fetch_month.py 2026-09 --out data/full-2026-09` (about 90 min alone), then `python src/build_pairs.py data/full-2026-09 --out data/full-pairs-09` (about 15 min, needs about 12 GB RAM).
3. Copy the files from `results/study2-progress/` into `data/study2/` (screen.jsonl, and sample.parquet if present) and `data/study2-scores/` (scores.jsonl, sample.parquet).
4. Screening, if not finished: `python src/study2.py screen --pairs data/full-pairs-09/pairs.parquet --pgn data/full-2026-09 --out data/study2 --block 70000`
5. Groups: `python src/study2.py sample --pairs data/full-pairs-09/pairs.parquet --out data/study2`
6. Scoring, repeat until "games to score: 0" (each run stops at the 2 h background limit and resumes):
   `python -u src/centipawn_loss.py --sample data/study2/sample.parquet --pgn data/full-2026-09 --out data/study2-scores --no-final --depth 15`
7. `python src/analyze_study2.py --scores data/study2-scores --out results/study2`, then write up.

## Settings already agreed

Elo band 1200 to 2000, 30-minute session cutoff, Stockfish 16 at depth 15 with one thread per engine, evals capped at plus or minus 1000 cp, a game counts if at least 5 of the player's moves are scored, smallest effect of interest 3 cp (study 1); study 2 uses 3 cp for RQ1 and 2 cp for RQ2.

## Environment setup (the container starts clean)

```
python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip setuptools wheel
.venv/bin/pip install -q -r requirements.txt
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq stockfish   # /usr/games/stockfish
.venv/bin/python -m pytest -q tests
```

The cloud environment's network access is set to Full, so Lichess is reachable. Install python-chess inside the venv; the system pip cannot build it.

## Gotchas already hit

- Two zstd writers must not share one `ZstdCompressor`.
- `fetch_month.py` now resumes a dropped connection with an HTTP Range request and writes `meta.json`; `build_pairs.py` refuses incomplete months unless `--allow-partial`.
- Draws read back with a null winner; `result_for_player` handles that.
- Background jobs started with `&` or `nohup` inside a Bash call get killed when the call returns. Use the Bash tool's background mode.
- Collecting the sampled PGNs scans every rapid game in both months, which takes a few minutes before Stockfish starts.

## How Karana wants to work

- Commit and push straight to `main`. No branches or pull requests unless he asks.
- Casual chat is fine. Prose in the repo follows his human-voice skill: plain, specific, no em dashes.
- He wants serious research, so flag design problems plainly.
