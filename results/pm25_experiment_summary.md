# PM2.5 Experiment Summary

- **Dataset used:** Beijing PM2.5 time series (`data/beijingpm25data.csv`, column `pm2.5`, interpolated missing values).
- **Baseline:** Persistence forecast (last observed value).
- **Model:** Moving-average forecaster with window `w=3`.
- **Hmax:** `48` horizons (`h = 1..48`).
- **Skill(h) behavior:** Skill is negative for short and mid horizons (approximately `h=1..35`), crosses near zero around `h≈36`, and remains slightly positive at long horizons (`h=36..48`).
- **Computed H\*:** `48` (using `H* = max(h : Skill(h) > 0)`, from `results/pm25_real_hstar.txt`).
