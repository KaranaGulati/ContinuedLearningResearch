# Results

Preregistered prediction (2026-10-07): a win is a win. Next-game ACPL does not differ between pairs after a win on time, by checkmate and by resignation; every pairwise difference lies within plus or minus 3 cp.

Pairs with a scored ACPL: 18,002

## Primary test

### All time controls

Pairs: time 6,007, checkmate 5,971, resign 6,024 (16,671 players). Wald chi2(2) = 0.950, p = 0.6219.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.91 | 49.70 |
| checkmate | 70.93 | 51.20 |
| resign | 71.56 | 50.76 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.88 | [-0.91, 2.66] | [-0.62, 2.38] | 0.96 | 1 | 0.009871 | 0.017 |
| resign minus checkmate | 0.56 | [-1.23, 2.36] | [-0.95, 2.07] | 0.61 | 1 | 0.003931 | 0.011 |
| time minus resign | 0.31 | [-1.46, 2.09] | [-1.18, 1.81] | 0.35 | 1 | 0.001523 | 0.006 |

Decision under the preregistered rule: **supported: every pairwise difference is inside +-3.0 cp (90% CIs, TOST at alpha .05)**

Model: `y ~ C(win) + elo_100 + elo_gap_100 + C(color) + C(time_control)`, OLS with standard errors clustered by player.

## Check 1: within each time control

### 600+0

Pairs: time 4,825, checkmate 4,781, resign 4,814 (13,298 players). Wald chi2(2) = 0.284, p = 0.8674.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 72.97 | 50.39 |
| checkmate | 72.45 | 52.02 |
| resign | 72.46 | 51.53 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.49 | [-1.54, 2.51] | [-1.22, 2.19] | 0.47 | 1 | 0.007522 | 0.009 |
| resign minus checkmate | 0.02 | [-2.02, 2.07] | [-1.69, 1.74] | 0.02 | 1 | 0.002179 | 0.000 |
| time minus resign | 0.46 | [-1.55, 2.48] | [-1.23, 2.15] | 0.45 | 1 | 0.006777 | 0.009 |

### 600+5

Pairs: time 696, checkmate 705, resign 715 (2,025 players). Wald chi2(2) = 1.026, p = 0.5987.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 68.73 | 48.11 |
| checkmate | 66.24 | 49.03 |
| resign | 68.62 | 46.59 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 2.23 | [-2.77, 7.22] | [-1.96, 6.42] | 0.87 | 1 | 0.3809 | 0.047 |
| resign minus checkmate | 2.21 | [-2.68, 7.10] | [-1.89, 6.32] | 0.89 | 1 | 0.376 | 0.046 |
| time minus resign | 0.02 | [-4.87, 4.90] | [-4.09, 4.12] | 0.01 | 1 | 0.1157 | 0.000 |

### 900+10

Pairs: time 120, checkmate 121, resign 123 (355 players). Wald chi2(2) = 0.823, p = 0.6627.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 66.72 | 47.82 |
| checkmate | 61.90 | 40.11 |
| resign | 64.19 | 44.61 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 5.06 | [-5.87, 15.99] | [-4.12, 14.23] | 0.91 | 1 | 0.644 | 0.114 |
| resign minus checkmate | 2.12 | [-8.50, 12.75] | [-6.79, 11.04] | 0.39 | 1 | 0.4358 | 0.048 |
| time minus resign | 2.93 | [-8.51, 14.38] | [-6.67, 12.54] | 0.50 | 1 | 0.4955 | 0.066 |

## Check 2: adding the previous game's final evaluation and rematch

### Previous position

Pairs: time 6,007, checkmate 5,971, resign 6,024 (16,671 players). Wald chi2(2) = 0.056, p = 0.9723.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.91 | 49.70 |
| checkmate | 70.93 | 51.20 |
| resign | 71.56 | 50.76 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.01 | [-2.35, 2.38] | [-1.97, 2.00] | 0.01 | 1 | 0.006613 | 0.000 |
| resign minus checkmate | 0.19 | [-1.73, 2.11] | [-1.42, 1.80] | 0.20 | 1 | 0.00207 | 0.004 |
| time minus resign | -0.18 | [-2.16, 1.80] | [-1.84, 1.48] | -0.18 | 1 | 0.002649 | -0.004 |

Previous final evaluation: -0.12 cp of ACPL per pawn (SE 0.11).

## Check 3: previous win where the player was not losing (final eval >= -100 cp)

### Not losing at the end

Pairs: time 4,719, checkmate 5,971, resign 5,963 (15,517 players). Wald chi2(2) = 0.473, p = 0.7894.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.42 | 49.43 |
| checkmate | 70.93 | 51.20 |
| resign | 71.54 | 50.66 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.52 | [-1.37, 2.41] | [-1.07, 2.10] | 0.53 | 1 | 0.004984 | 0.010 |
| resign minus checkmate | 0.58 | [-1.22, 2.38] | [-0.93, 2.09] | 0.64 | 1 | 0.004252 | 0.012 |
| time minus resign | -0.07 | [-1.95, 1.82] | [-1.65, 1.51] | -0.07 | 1 | 0.001146 | -0.001 |

## Check 4: Elo band sensitivity

### 1200-1600

Pairs: time 2,939, checkmate 2,913, resign 2,931 (8,217 players). Wald chi2(2) = 0.175, p = 0.9164.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 78.32 | 53.28 |
| checkmate | 78.24 | 57.49 |
| resign | 77.73 | 54.15 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.13 | [-2.70, 2.96] | [-2.25, 2.50] | 0.09 | 1 | 0.02338 | 0.002 |
| resign minus checkmate | -0.43 | [-3.27, 2.40] | [-2.82, 1.95] | -0.30 | 1 | 0.03814 | -0.008 |
| time minus resign | 0.56 | [-2.19, 3.31] | [-1.74, 2.87] | 0.40 | 1 | 0.04094 | 0.010 |

### 1600-2000

Pairs: time 3,068, checkmate 3,058, resign 3,093 (8,510 players). Wald chi2(2) = 2.534, p = 0.2816.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 65.76 | 45.17 |
| checkmate | 63.97 | 43.26 |
| resign | 65.71 | 46.58 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 1.60 | [-0.61, 3.80] | [-0.25, 3.44] | 1.42 | 0.4672 | 0.1057 | 0.035 |
| resign minus checkmate | 1.49 | [-0.75, 3.73] | [-0.39, 3.37] | 1.31 | 0.4672 | 0.09358 | 0.033 |
| time minus resign | 0.10 | [-2.18, 2.38] | [-1.81, 2.01] | 0.09 | 0.9301 | 0.006314 | 0.002 |

## Check 5: Lichess pre-analysed subset

### Lichess [%eval]

Pairs: time 997, checkmate 964, resign 1,024 (2,945 players). Wald chi2(2) = 0.383, p = 0.8256.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.27 | 53.09 |
| checkmate | 71.98 | 56.40 |
| resign | 72.10 | 50.75 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.46 | [-4.38, 5.29] | [-3.60, 4.52] | 0.18 | 1 | 0.1512 | 0.009 |
| resign minus checkmate | 1.43 | [-3.28, 6.14] | [-2.52, 5.38] | 0.60 | 1 | 0.2569 | 0.027 |
| time minus resign | -0.98 | [-5.51, 3.56] | [-4.78, 2.83] | -0.42 | 1 | 0.1906 | -0.018 |

## Check 6: rematches removed

### Next game against a different opponent

Pairs: time 5,788, checkmate 5,322, resign 5,523 (15,467 players). Wald chi2(2) = 0.640, p = 0.7262.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.90 | 49.60 |
| checkmate | 71.11 | 51.02 |
| resign | 71.67 | 50.69 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.75 | [-1.10, 2.60] | [-0.81, 2.30] | 0.79 | 1 | 0.008528 | 0.015 |
| resign minus checkmate | 0.50 | [-1.39, 2.38] | [-1.09, 2.08] | 0.51 | 1 | 0.004636 | 0.010 |
| time minus resign | 0.25 | [-1.58, 2.08] | [-1.29, 1.79] | 0.27 | 1 | 0.001636 | 0.005 |

## Sample size for a 2 cp difference

Residual SD of ACPL after the covariates: 49.84 cp. Pairs per group needed at alpha .05 / 3 (Holm's first step), two-tailed: 13,003 for 80% power, 16,780 for 90%.

## Check 7: mixed model with a random intercept per player

### Mixed model

Pairs: time 6,007, checkmate 5,971, resign 6,024 (16,671 players). Wald chi2(2) = 0.950, p = 0.6217.

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | 0.88 | [-0.91, 2.66] | [-0.62, 2.38] | 0.96 | 1 | 0.009961 |  |
| resign minus checkmate | 0.56 | [-1.22, 2.35] | [-0.94, 2.06] | 0.62 | 1 | 0.003735 |  |
| time minus resign | 0.31 | [-1.47, 2.10] | [-1.18, 1.81] | 0.35 | 1 | 0.001569 |  |
