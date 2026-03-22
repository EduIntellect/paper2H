# Wind Experiment Summary

- **Dataset used:** NREL Wind Toolkit (WTK LED CONUS download, 2019, point sample).
- **Cleaned canonical input:** `data/wind_hourly_clean.csv`.
- **Target variable:** wind speed at 100m, represented as canonical `value`.
- **Frequency:** hourly.
- **Baseline:** persistence.
- **Model:** LightGBM (LAGS=[0,1,2,3,6,12,24,48], ORIGIN_STRIDE=24, n_estimators=50, rolling-origin).
- **Hmax:** `48` (`h=1..48`).
- **Metric:** MAE with skill relative to persistence.
- **Observed Skill(h) behavior:** Skill is positive across the full evaluated range (`h=1..48`).

## H* Reporting

- **H*(relax):** `48`
- **H*(strict):** `48`
- **[h_start, h_end]:** `[1, 48]`
- **H*(time):** `48 h`

## Correction Note

The official comparable wind-domain result is produced with the canonical LightGBM protocol used across comparable domains.

## Interpretation

The wind domain shows sustained positive skill across all evaluated horizons, indicating a full-range contiguous interval of useful operational predictability relative to persistence.

The reported time-based horizon corresponds to H*(strict), i.e., to the contiguous positive-skill interval, rather than to H*(relax).
