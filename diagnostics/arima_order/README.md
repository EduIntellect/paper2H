# ARIMA order diagnostic (wind, traffic) — diagnostic only

Date: 2026-10-01. Nothing here modifies the manuscript, production scripts or saved results.
Environment: local venv `.venv` (not tracked intentionally; numpy 2.5.3, pandas 3.0.6,
statsmodels 0.15.0, pmdarima 2.1.1). Recreate with
`python3 -m venv --without-pip .venv && pip --python .venv/bin/python install numpy pandas scipy matplotlib statsmodels pmdarima`.

## What produced the (2,0,0) figures in the submitted PDF
- Submitted PDF: `paper2_H_-1.pdf`, SHA-256 `464916a0b2f8d780343cc4721eee338623aee52fa3a8b292f914a2c13bd629f8`.
- Eq. (9) wind LightGBM 48/48 [1,48]; wind ARIMA same tuple (§9.2).
- Eq. (10) traffic LightGBM 72/7 [46,52]; Eq. (11) traffic ARIMA 72/6 [38,43], 13 sign changes.
- Matches **pipeline A** (`experiments/{wind,traffic}_arima_canonical_predictability.py`,
  results `results/{wind,traffic}_arima_hstar.txt`). Pipeline B (`src/run_arima_rolling_origin.py`,
  `results/hstar_all_domains.csv`) gives traffic 70/9 [52,60] and does NOT match the PDF.
- The order `(2, 0, 0)` is hardcoded (line 21 of each A script). No record of ACF/PACF, AIC/BIC
  or auto-ARIMA selection exists in the repo.

## WARNING
`paper/paper2_submission.tex` at HEAD is the six-domain expansion, not the submitted paper. Its ARIMA
rows come from pipeline B (traffic 70/9/[52,60]). Recompiling HEAD does not reproduce the submitted
traffic ARIMA numbers (72/6/[38,43]). Settle which pipeline is cited before editorial changes.

## Window reconstruction (pipeline A, h=1)
- Candidate origins: 48, 72, ... step 24; "last N" (365 wind / 180 traffic) never truncates
  (363 / 117 candidates).
- A discards origins with `train_end < 48` and with fewer than 200 valid train samples, so the first
  evaluated origin is **264** (216 training points, not 720). 354 valid origins in wind, 108 in traffic.
- `y_train = series.shift(-h)[train_start..train_end]`, `train_start = max(48, train_end-719)`.
- A fits `statsmodels ARIMA(order=(2,0,0))` with the default constant (`trend='c'`).

## Pitfall found
`pmdarima.auto_arima(..., with_intercept='auto')` dropped the constant for d=0 and inflated AICs by
12-55 points (so the (2,0,0) entry in the search list disagreed with a direct fit). Use
`with_intercept=True`; then auto_arima, `pm.ARIMA` and statsmodels give identical AIC
(check: `check_aic_consistency.py`). AIC values are only comparable within the same d.

## Files
- `arima_order_diagnostic.py`, `run_output.txt`: first/last valid origin, ACF/PACF (lags 1-10 printed,
  PNGs to lag 48), ADF, auto_arima AIC (d free and d=0).
- `*_acf_pacf.png`: ACF/PACF figures.
- `order_stability.py`, `order_stability.csv`, `order_stability_output.txt`: auto_arima (d=0, p,q<=5,
  AIC) at 20 evenly spaced valid origins per domain.
- `check_aic_consistency.py`: AIC agreement check between engines.

## Results (no interpretation)
First/last origin (d=0 search): see `run_output.txt`. Summary over 20 origins:

| Domain | Distinct best orders | Median ΔAIC (2,0,0)−best | Max ΔAIC | (2,0,0) rank median | within ΔAIC≤2 | ADF p>0.05 |
|---|---|---|---|---|---|---|
| wind | 10 | 3.67 | 34.29 | 5 | 10/20 | 2/20 |
| traffic | 8 | 28.04 | 68.49 | 14 | 4/20 | 1/20 |

Most frequent best orders: wind (1,0,0) 6/20, (1,0,1) 4/20; traffic (3,0,1) 5/20, (1,0,3) 3/20,
(2,0,2) 3/20. Not tested: effect of the order on H*(relax)/H*(strict) (would need refitting pipeline A).
