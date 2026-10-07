# What we are trying to do now

Handoff note, last updated 2026-10-07. Read this, then `PREREGISTRATION.md` (the current plan) and `README.md` (the original brief).

## The study in two lines

Does the way a chess game is won (on time, by checkmate, by resignation) change how well the winner plays their next game? Move quality is Stockfish mean centipawn loss (ACPL) on moves 15 to 30 of the next game, on Lichess rapid games.

## Design (changed from the README)

Karana chose a matched pairs design on 2026-10-07. The unit is a pair: a rapid win, then the same player's next rapid game, started within 30 minutes of the win ending with no other rated game in between. Three groups: pairs after a win on time, by checkmate, by resignation. A player can be in several groups but only once per group. The checkmate and resignation groups are drawn to match the win-on-time group's mix of Elo (100-point bins) and time control. The analysis is OLS on the next game's ACPL with Elo, rating gap, colour and time control, standard errors clustered by player, a Wald omnibus test and Holm-corrected pairwise differences. The README's within-player repeated-measures ANOVA is no longer the plan.

## Where things stand

- Data on disk (not committed, lost when the container goes): 1 to 5 August 2026 (12.3M games) and 1 to 5 September 2026 (12.0M games) in `data/2026-08` and `data/2026-09`, pairs in `data/partial-pairs/pairs.parquet` (rebuild with `build_pairs.py data/2026-08 data/2026-09 --out data/partial-pairs --allow-partial`).
- Exploratory pilot done (200 pairs per group): no difference between win types, residual SD 46.7 cp. Report in `results/pilot/report.md`.
- `PREREGISTRATION.md` is fixed and dated 2026-10-07 (commit 6ef4d78). At Karana's request Claude chose the prediction: a win is a win, tested by equivalence within plus or minus 3 cp, 6,500 pairs per group, pilot players excluded.
- Confirmatory scoring started 2026-10-07 about 15:23 UTC into `data/confirm-scores` (about 19,500 pairs, 4.8 hours). The Bash background mode stops a job after 2 hours, so it has to be relaunched with the same command; it resumes from `scores.jsonl` and reuses the saved `sample.parquet`.

## Next steps

1. Keep the confirmatory run going until `games to score: 0`. Relaunch command:
   ```
   .venv/bin/python -u src/centipawn_loss.py --pairs data/partial-pairs/pairs.parquet --pgn data/2026-08 data/2026-09 \
       --out data/confirm-scores --elo-min 1200 --elo-max 2000 --n-per-group 6500 --depth 15 \
       --exclude data/pilot-scores/sample.parquet >> data/confirm-scores.log 2>&1
   ```
2. Run `analyze.py --scores data/confirm-scores --out results/confirmatory` (no `--exploratory`). It prints the preregistered decision.
3. Commit `results/confirmatory/` and write up the result for Karana's teacher.

## Settings already agreed

Elo band 1200 to 2000, 30-minute session cutoff, Stockfish 16 at depth 15 with one thread per engine, evals capped at plus or minus 1000 cp, a game counts if at least 5 of the player's moves are scored, smallest effect of interest 3 cp.

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
