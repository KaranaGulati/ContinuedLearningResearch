# What we are trying to do now

Handoff note, last updated 2026-10-07. Read this, then `PREREGISTRATION.md` (the current plan) and `README.md` (the original brief).

## The study in two lines

Does the way a chess game is won (on time, by checkmate, by resignation) change how well the winner plays their next game? Move quality is Stockfish mean centipawn loss (ACPL) on moves 15 to 30 of the next game, on Lichess rapid games.

## Design (changed from the README)

Karana chose a matched pairs design on 2026-10-07. The unit is a pair: a rapid win, then the same player's next rapid game, started within 30 minutes of the win ending with no other rated game in between. Three groups: pairs after a win on time, by checkmate, by resignation. A player can be in several groups but only once per group. The checkmate and resignation groups are drawn to match the win-on-time group's mix of Elo (100-point bins) and time control. The analysis is OLS on the next game's ACPL with Elo, rating gap, colour and time control, standard errors clustered by player, a Wald omnibus test and Holm-corrected pairwise differences. The README's within-player repeated-measures ANOVA is no longer the plan.

## Where things stand

- Data on disk (not committed, lost when the container goes): the first part of 2026-08 (1 to 5 August, 12.3M games) and of 2026-09 (1 to 5 September, 12.0M games) in `data/2026-08` and `data/2026-09`. A worker restart cut the full downloads; Karana decided this is enough data. Pairs from both are in `data/partial-pairs/pairs.parquet` (rebuild with `build_pairs.py data/2026-08 data/2026-09 --out data/partial-pairs --allow-partial`).
- In the Elo band 1200 to 2000 there are 146,751 win-on-time pairs, 410,087 checkmate pairs and 950,990 resignation pairs.
- The "#" checkmate rule matched a full replay on 10,000 of 10,000 games.
- Exploratory pilot: 200 pairs per group, being scored into `data/pilot-scores` (about 1,200 Stockfish games at depth 15). Analyse it with `analyze.py --scores data/pilot-scores --out results/pilot --exploratory`.

## Next steps

1. Finish the pilot, analyse it in exploratory mode, and commit `results/pilot/`.
2. Karana writes the prediction from the pilot and dates it in `PREREGISTRATION.md`. Use the pilot's pooled SD of ACPL to set N per group for 80% power on a 2 cp difference after Holm correction, and write N in the preregistration.
3. Update the "What has been looked at" section of `PREREGISTRATION.md` to list the pilot results.
4. Commit the preregistration, then score the confirmatory sample with `--exclude data/pilot-scores/sample.parquet`, then run `analyze.py` without `--exploratory`.

## Settings already agreed

Elo band 1200 to 2000, 30-minute session cutoff, Stockfish 16 at depth 15 with one thread per engine, evals capped at plus or minus 1000 cp, a game counts if at least 5 of the player's moves are scored, smallest effect of interest 2 cp.

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
