# PM2.5 Beijing Experiment Summary

- **Dataset used:** Beijing PM2.5 dataset (`data/beijingpm25data.csv`, variable `pm2.5`).
- **Frequency:** Hourly observations.
- **Baseline:** Persistence forecast (last observed value).
- **Model:** Moving-average forecast with trailing window `w=3`.
- **Hmax:** `48` forecast horizons (`h=1..48`).
- **Metric:** Mean Absolute Error (MAE), with skill defined as \(\mathrm{Skill}(h)=1-E_{\mathrm{model}}(h)/E_{\mathrm{baseline}}(h)\).
- **Observed Skill(h) behavior:** Skill is negative at short-to-medium horizons (approximately `h=1..35`) and becomes positive at longer horizons (`h=36..48`).

## H* Definition Used in This Domain

- Reported value uses the original definition \(H^*=\max\{h:\mathrm{Skill}(h)>0\}\).
- For the PM2.5 Beijing experiment, this yields **`H* = 48`**.
- Interpretive caution: late positive skill may reflect long-horizon recovery effects rather than contiguous useful predictability.
- A first-zero-crossing criterion may therefore provide a more robust operational estimate of `H*`.

## Leakage-Free Evaluation Protocol

- Evaluation is strictly time-ordered, with **no random split**.
- Targets are generated as `series.shift(-h)` for each horizon.
- Baseline and model predictions are evaluated on the same valid timestamps via a shared mask.
- This enforces temporally aligned, leakage-free comparison across horizons.
