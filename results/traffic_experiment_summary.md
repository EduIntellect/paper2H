# Traffic Experiment Summary

- **Dataset used:** PeMS / METR-LA (`data/metr-la.h5`)
- **Cleaned canonical input:** `data/traffic_hourly_clean.csv`
- **Target variable:** traffic speed (mph), sensor `773869`
- **Frequency:** hourly (derived from 5-min source by hourly mean)
- **Baseline:** persistence
- **Model:** LightGBM (LAGS=[0,1,2,3,6,12,24,48], ORIGIN_STRIDE=24, n_estimators=50, rolling-origin)
- **Hmax:** `72`
- **Metric:** MAE, with skill relative to persistence

## H* Reporting

- **H*(relax):** `72`
- **H*(strict):** `7`
- **[h_start, h_end] (longest contiguous positive interval):** `[46, 52]`
- **First positive interval:** `[17, 18]`
- **H*(time):** `7 h`

## Correction Note

The LightGBM traffic experiment was corrected by adding `lag_0 = y[t]` to align model and persistence baseline information at prediction origin `t`.

This corrected LightGBM result is the official comparable traffic-domain result for the cross-domain analysis.

## Interpretation

The fragmented `Skill(h)` profile persists after correction, suggesting limited contiguous operational predictability in the 119-day METR-LA traffic-speed series.
