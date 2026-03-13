# PM2.5 LightGBM Full Result

- **Domain:** PM2.5 Beijing
- **Model:** LightGBM with lag features
- **Protocol:** direct multi-horizon, rolling-origin, daily stride, 30-day sliding training window, last 365 daily origins per horizon
- **Computational protocol:** ORIGIN_STRIDE=24, MAX_TRAIN_SIZE=720, MAX_ORIGINS_PER_HORIZON=365, n_estimators=50
- **Formal H\*:** 48
- **First positive horizon:** 8
- **First sustained positive horizon:** 27
- **Interpretation:** persistence dominates short horizons; sustained positive skill appears only from h=27 onward; therefore raw H* overstates operational usefulness unless the contiguity structure of the skill curve is also considered.

LightGBM achieves consistently positive forecast skill only beyond h=27, with skill ranging from 0.03 to 0.17 for h in [27,48]. At shorter horizons, persistence dominates, consistent with the high autocorrelation of PM2.5 at sub-daily scales.
