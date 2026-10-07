# Exploratory pilot

This sample is used to form the prediction and size the confirmatory test. None of its p-values are evidence for or against any hypothesis.

Pairs with a scored ACPL: 560

## Primary test

### All time controls

Pairs: time 189, checkmate 184, resign 187 (553 players). Wald chi2(2) = 0.876, p = 0.6455.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.69 | 41.20 |
| checkmate | 75.46 | 51.32 |
| resign | 70.92 | 48.72 |

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | -3.99 | [-13.22, 5.24] | -0.85 | 1 | -0.085 |
| resign minus checkmate | -4.07 | [-14.12, 5.98] | -0.79 | 1 | -0.086 |
| time minus resign | 0.08 | [-9.19, 9.34] | 0.02 | 1 | 0.002 |

Model: `y ~ C(win) + elo_100 + elo_gap_100 + C(color) + C(time_control)`, OLS with standard errors clustered by player.

## Check 1: within each time control

### 600+0

Pairs: time 153, checkmate 149, resign 148 (448 players). Wald chi2(2) = 0.871, p = 0.6468.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 74.21 | 42.13 |
| checkmate | 76.72 | 50.85 |
| resign | 71.23 | 50.90 |

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | -2.68 | [-13.01, 7.65] | -0.51 | 1 | -0.056 |
| resign minus checkmate | -5.43 | [-16.83, 5.97] | -0.93 | 1 | -0.113 |
| time minus resign | 2.75 | [-7.86, 13.36] | 0.51 | 1 | 0.057 |

## Check 2: adding the previous game's final evaluation and rematch

### Previous position

Pairs: time 189, checkmate 184, resign 187 (553 players). Wald chi2(2) = 1.970, p = 0.3734.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.69 | 41.20 |
| checkmate | 75.46 | 51.32 |
| resign | 70.92 | 48.72 |

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | -7.99 | [-19.58, 3.60] | -1.35 | 0.5298 | -0.169 |
| resign minus checkmate | -5.61 | [-15.94, 4.72] | -1.06 | 0.5738 | -0.119 |
| time minus resign | -2.38 | [-12.79, 8.03] | -0.45 | 0.6542 | -0.050 |

Previous final evaluation: -0.52 cp of ACPL per pawn (SE 0.49).

## Check 3: previous win where the player was not losing (final eval >= -100 cp)

### Not losing at the end

Pairs: time 154, checkmate 184, resign 186 (517 players). Wald chi2(2) = 1.157, p = 0.5607.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 70.34 | 41.39 |
| checkmate | 75.46 | 51.32 |
| resign | 70.86 | 48.84 |

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | -5.11 | [-14.85, 4.63] | -1.03 | 0.911 | -0.107 |
| resign minus checkmate | -4.11 | [-14.20, 5.98] | -0.80 | 0.911 | -0.086 |
| time minus resign | -1.00 | [-10.77, 8.77] | -0.20 | 0.911 | -0.021 |

## Check 4: Elo band sensitivity

### 1200-1600

Pairs: time 89, checkmate 87, resign 87 (261 players). Wald chi2(2) = 3.160, p = 0.206.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 74.30 | 38.28 |
| checkmate | 86.77 | 54.80 |
| resign | 74.87 | 47.32 |

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | -11.87 | [-25.59, 1.86] | -1.69 | 0.2703 | -0.250 |
| resign minus checkmate | -11.15 | [-26.39, 4.10] | -1.43 | 0.3035 | -0.235 |
| time minus resign | -0.72 | [-13.90, 12.45] | -0.11 | 0.9145 | -0.015 |

### 1600-2000

Pairs: time 100, checkmate 97, resign 100 (292 players). Wald chi2(2) = 0.361, p = 0.8349.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 69.37 | 43.70 |
| checkmate | 65.32 | 45.95 |
| resign | 67.49 | 49.89 |

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | 3.76 | [-8.69, 16.21] | 0.59 | 1 | 0.081 |
| resign minus checkmate | 2.62 | [-11.07, 16.32] | 0.38 | 1 | 0.056 |
| time minus resign | 1.14 | [-12.20, 14.47] | 0.17 | 1 | 0.024 |

## Check 5: Lichess pre-analysed subset

### Lichess [%eval]

n = {'time': 35, 'checkmate': 28, 'resign': 28}: fewer than 30 pairs in a group

## Check 6: rematches removed

### Next game against a different opponent

Pairs: time 182, checkmate 166, resign 174 (517 players). Wald chi2(2) = 2.054, p = 0.358.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.88 | 41.60 |
| checkmate | 77.90 | 52.88 |
| resign | 70.30 | 48.97 |

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | -6.16 | [-15.94, 3.62] | -1.23 | 0.5901 | -0.129 |
| resign minus checkmate | -7.00 | [-17.63, 3.63] | -1.29 | 0.5901 | -0.146 |
| time minus resign | 0.84 | [-8.82, 10.50] | 0.17 | 0.8644 | 0.018 |

## Sample size for a 2 cp difference

Residual SD of ACPL after the covariates: 46.73 cp. Pairs per group needed at alpha .05 / 3 (Holm's first step), two-tailed: 11,432 for 80% power, 14,752 for 90%.

## Check 7: mixed model with a random intercept per player

### Mixed model

Pairs: time 189, checkmate 184, resign 187 (553 players). Wald chi2(2) = 0.904, p = 0.6364.

| difference | adjusted cp | 95% CI | z | Holm p | d |
|---|---|---|---|---|---|
| time minus checkmate | -3.99 | [-13.49, 5.52] | -0.82 | 1 |  |
| resign minus checkmate | -4.05 | [-13.65, 5.54] | -0.83 | 1 |  |
| time minus resign | 0.07 | [-9.43, 9.57] | 0.01 | 1 |  |
