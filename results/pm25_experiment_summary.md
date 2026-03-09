# PM2.5 Beijing Experiment Summary

- **Dataset used:** Beijing PM2.5 dataset (`data/beijingpm25data.csv`, variable `pm2.5`).
- **Frequency:** Hourly observations.
- **Baseline:** Persistence forecast (last observed value).
- **Model:** Moving-average forecast with trailing window `w=3`.
- **Hmax:** `48` forecast horizons (`h=1..48`).
- **Metric:** Mean Absolute Error (MAE), with relative forecast skill
  \(\mathrm{Skill}(h)=1-E_{\mathrm{model}}(h)/E_{\mathrm{baseline}}(h)\).
- **Observed Skill(h) behavior:** Skill is negative for short-to-medium horizons (approximately `h=1..35`) and becomes positive at longer horizons (`h=36..48`).
- **Current H\*** (under \(\max(h:\mathrm{Skill}(h)>0)\)): `48`.
- **Operational note:** Because late-horizon positive recoveries may be stochastic, the first zero-crossing of `Skill(h)` is a potentially more robust operational definition of the predictability horizon.
