# Study 2 results

Pairs with a scored ACPL: 41,957

## RQ1: does the way you win matter?

### Time vs checkmate vs resignation

Pairs: time 6,055, checkmate 5,955, resign 5,952 (17,600 players). Wald chi2(2) = 2.672, p = 0.2629.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.76 | 51.04 |
| checkmate | 72.32 | 53.17 |
| resign | 73.22 | 52.15 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | -0.54 | [-2.39, 1.31] | [-2.09, 1.01] | -0.57 | 0.6186 | 0.004581 | -0.010 |
| resign minus checkmate | 0.97 | [-0.90, 2.84] | [-0.60, 2.54] | 1.02 | 0.6186 | 0.01658 | 0.019 |
| time minus resign | -1.51 | [-3.34, 0.32] | [-3.05, 0.03] | -1.62 | 0.3177 | 0.05529 | -0.029 |

Decision: **inconclusive: neither equivalence nor a difference of at least the smallest effect of interest**

## RQ2: does a lucky time win matter?

### Lucky vs deserved time wins

Pairs: {'rq2_lucky': 12033, 'rq2_deserved': 11962} (23,995 players). Raw mean ACPL: {'rq2_deserved': 72.278, 'rq2_lucky': 74.379}.

Lucky minus deserved, adjusted: 1.96 cp, 90% CI [0.87, 3.06], 95% CI [0.66, 3.27], p = 0.003183, TOST p = 0.4779.

Decision: **inconclusive**

## Checks

### RQ1, 10+0 only

Pairs: time 4,812, checkmate 4,728, resign 4,727 (13,979 players). Wald chi2(2) = 6.570, p = 0.03744.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.92 | 50.54 |
| checkmate | 72.98 | 53.85 |
| resign | 74.56 | 53.06 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | -1.06 | [-3.13, 1.02] | [-2.80, 0.68] | -1.00 | 0.3175 | 0.03298 | -0.020 |
| resign minus checkmate | 1.63 | [-0.50, 3.76] | [-0.16, 3.41] | 1.50 | 0.2676 | 0.1031 | 0.031 |
| time minus resign | -2.68 | [-4.74, -0.62] | [-4.41, -0.95] | -2.55 | 0.03202 | 0.3819 | -0.051 |

### RQ2, 10+0 only

Pairs: {'rq2_lucky': 9645, 'rq2_deserved': 9635} (19,280 players). Raw mean ACPL: {'rq2_deserved': 73.189, 'rq2_lucky': 75.571}.

Lucky minus deserved, adjusted: 2.29 cp, 90% CI [1.05, 3.53], 95% CI [0.82, 3.76], p = 0.002328, TOST p = 0.6496.

Decision: **refuted: lucky winners play worse by 2.29 cp**

### RQ1, rematches removed

Pairs: time 5,820, checkmate 5,323, resign 5,468 (16,302 players). Wald chi2(2) = 3.690, p = 0.158.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 71.82 | 51.15 |
| checkmate | 72.41 | 53.26 |
| resign | 73.64 | 52.55 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | -0.61 | [-2.53, 1.32] | [-2.22, 1.01] | -0.62 | 0.5364 | 0.007333 | -0.012 |
| resign minus checkmate | 1.23 | [-0.75, 3.20] | [-0.43, 2.88] | 1.22 | 0.4464 | 0.03902 | 0.023 |
| time minus resign | -1.83 | [-3.73, 0.06] | [-3.42, -0.24] | -1.90 | 0.1733 | 0.1133 | -0.035 |

### RQ2, rematches removed

Pairs: {'rq2_deserved': 11585, 'rq2_lucky': 11536} (23,121 players). Raw mean ACPL: {'rq2_deserved': 72.143, 'rq2_lucky': 74.143}.

Lucky minus deserved, adjusted: 1.85 cp, 90% CI [0.74, 2.96], 95% CI [0.53, 3.18], p = 0.006068, TOST p = 0.414.

Decision: **inconclusive**

### RQ1, rating 1200-1600

Pairs: time 3,073, checkmate 3,027, resign 3,012 (8,949 players). Wald chi2(2) = 1.173, p = 0.5564.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 77.89 | 55.18 |
| checkmate | 78.96 | 58.10 |
| resign | 79.48 | 56.76 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | -1.06 | [-3.89, 1.77] | [-3.44, 1.32] | -0.73 | 0.9281 | 0.08958 | -0.019 |
| resign minus checkmate | 0.45 | [-2.44, 3.33] | [-1.98, 2.87] | 0.30 | 0.9281 | 0.04152 | 0.008 |
| time minus resign | -1.50 | [-4.31, 1.30] | [-3.86, 0.85] | -1.05 | 0.8811 | 0.1482 | -0.027 |

### RQ2, rating 1200-1600

Pairs: {'rq2_lucky': 6324, 'rq2_deserved': 6232} (12,556 players). Raw mean ACPL: {'rq2_deserved': 79.005, 'rq2_lucky': 80.897}.

Lucky minus deserved, adjusted: 1.82 cp, 90% CI [0.15, 3.48], 95% CI [-0.17, 3.80], p = 0.07249, TOST p = 0.4287.

Decision: **inconclusive**

### RQ1, rating 1600-2000

Pairs: time 2,982, checkmate 2,928, resign 2,940 (8,665 players). Wald chi2(2) = 2.077, p = 0.354.

| win type | raw mean ACPL | SD |
|---|---|---|
| time | 65.44 | 45.54 |
| checkmate | 65.46 | 46.56 |
| resign | 66.80 | 46.10 |

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | -0.03 | [-2.40, 2.33] | [-2.02, 1.95] | -0.03 | 0.978 | 0.006973 | -0.001 |
| resign minus checkmate | 1.47 | [-0.88, 3.82] | [-0.51, 3.44] | 1.22 | 0.6197 | 0.101 | 0.032 |
| time minus resign | -1.50 | [-3.83, 0.83] | [-3.46, 0.45] | -1.26 | 0.6197 | 0.104 | -0.033 |

### RQ2, rating 1600-2000

Pairs: {'rq2_deserved': 5730, 'rq2_lucky': 5709} (11,439 players). Raw mean ACPL: {'rq2_deserved': 64.961, 'rq2_lucky': 67.159}.

Lucky minus deserved, adjusted: 2.12 cp, 90% CI [0.72, 3.51], 95% CI [0.46, 3.78], p = 0.01241, TOST p = 0.5549.

Decision: **refuted: lucky winners play worse by 2.12 cp**

### RQ2, stricter lucky (losing by > 3 pawns)

Pairs: {'rq2_deserved': 11962, 'rq2_lucky': 8607} (20,569 players). Raw mean ACPL: {'rq2_deserved': 72.278, 'rq2_lucky': 74.351}.

Lucky minus deserved, adjusted: 1.92 cp, 90% CI [0.73, 3.10], 95% CI [0.51, 3.33], p = 0.007772, TOST p = 0.4534.

Decision: **inconclusive**

### RQ1, mixed model

Pairs: time 6,055, checkmate 5,955, resign 5,952 (17,600 players). Wald chi2(2) = 2.645, p = 0.2664.

| difference | adjusted cp | 95% CI | 90% CI | z | Holm p | TOST p | d |
|---|---|---|---|---|---|---|---|
| time minus checkmate | -0.54 | [-2.39, 1.30] | [-2.09, 1.01] | -0.57 | 0.6093 |  |  |
| resign minus checkmate | 0.97 | [-0.88, 2.82] | [-0.58, 2.52] | 1.03 | 0.6093 |  |  |
| time minus resign | -1.51 | [-3.35, 0.33] | [-3.06, 0.04] | -1.61 | 0.3247 |  |  |

### RQ2, mixed model

Pairs: {'rq2_lucky': 12033, 'rq2_deserved': 11962} (23,995 players). Raw mean ACPL: {'rq2_deserved': 72.278, 'rq2_lucky': 74.379}.

Lucky minus deserved, adjusted: 1.96 cp, 90% CI [0.87, 3.06], 95% CI [0.66, 3.27], p = 0.003204, TOST p = 0.4779.

Decision: **(check only)**
