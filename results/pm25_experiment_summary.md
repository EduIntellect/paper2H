# PM2.5 Experiment Summary

- **Dataset used:** Beijing PM2.5 dataset (`data/beijingpm25data.csv`)
- **Cleaned canonical input:** `data/beijingpm25data.csv` (univariate target extracted as `pm2.5`)
- **Target variable:** PM2.5 concentration (`pm2.5`)
- **Frequency:** hourly
- **Baseline:** persistence
- **Model:** LightGBM (LAGS=[0,1,2,3,6,12,24,48], ORIGIN_STRIDE=24, n_estimators=50, rolling-origin)
- **Hmax:** `48`
- **Metric:** MAE, with skill relative to persistence

## H* Reporting

- **H*(relax):** `48`
- **H*(strict):** `22`
- **[h_start, h_end] (longest contiguous positive interval):** `[27, 48]`
- **H*(time):** `22 h`

## Correction Note

The LightGBM comparable result was updated after adding `lag_0 = y[t]` to align model and persistence baseline information at prediction origin `t`.

This corrected LightGBM result is the official comparable PM2.5-domain result for the cross-domain analysis.

## Interpretation

PM2.5 exhibits a late contiguous positive-skill interval after an extended negative region, indicating delayed emergence of useful operational predictability relative to persistence.
