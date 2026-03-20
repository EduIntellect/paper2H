# Wind Experiment Summary

- **Dataset used:** NREL Wind Toolkit (WTK LED CONUS download, 2019, point sample).
- **Cleaned canonical input:** `data/wind_hourly_clean.csv`.
- **Target variable:** wind speed at 100m, represented as canonical `value`.
- **Frequency:** hourly.
- **Baseline:** persistence.
- **Model:** moving average (`window=3`).
- **Hmax:** `48` (`h=1..48`).
- **Metric:** MAE with skill relative to persistence.
- **Observed Skill(h) behavior:** Skill is negative at `h=1,2` and positive from `h=3` onward.

## H* Reporting

- **H*(relax):** `48`
- **H*(strict):** `46`
- **[h_start, h_end]:** `[3, 48]`
- **H*(time):** `46 h`

## Interpretation

The wind domain shows early negative skill at `h=1,2`, followed by a long contiguous positive-skill interval (`h=3..48`), indicating sustained operational predictability after the shortest lead times.

The reported time-based horizon corresponds to H*(strict), i.e., to the contiguous positive-skill interval, rather than to H*(relax).
