# Exploratory: move quality as lost winning chances

Not preregistered. Same games, same Stockfish 16 evaluations and same models as the main analysis; only the unit changes, from centipawns to Win% (Win% = 50 + 50 * (2 / (1 + exp(-0.00368208 * cp)) - 1), cp capped at +-1000).

## Lucky minus deserved time wins (RQ2)

| measure | lucky minus deserved | 95% CI | p | in SDs |
|---|---|---|---|---|
| centipawns (preregistered) | 1.96 cp | 0.66 to 3.27 | 0.00318 | 0.038 |
| Win% lost per move | 0.060 points | -0.024 to 0.144 | 0.161 | 0.018 |

Raw means, Win% lost per move: {'rq2_deserved': 4.554, 'rq2_lucky': 4.62}

## Time vs checkmate vs resignation (RQ1)

| measure | omnibus p | pair | difference | 95% CI | Holm p | in SDs |
|---|---|---|---|---|---|---|
| centipawns | 0.263 | time - checkmate | -0.541 cp | -2.390 to 1.309 | 0.619 | -0.010 |
| centipawns | 0.263 | resign - checkmate | 0.969 cp | -0.899 to 2.838 | 0.619 | 0.019 |
| centipawns | 0.263 | time - resign | -1.510 cp | -3.340 to 0.320 | 0.318 | -0.029 |
| win_pct | 0.646 | time - checkmate | 0.008 points | -0.111 to 0.127 | 1 | 0.002 |
| win_pct | 0.646 | resign - checkmate | 0.053 points | -0.067 to 0.173 | 1 | 0.016 |
| win_pct | 0.646 | time - resign | -0.045 points | -0.162 to 0.073 | 1 | -0.013 |
