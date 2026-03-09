# Electric Load Experiment Plan (PJM)

- **Dataset:** PJM electricity load (`data/pjm_load_hourly.csv`).
- **Frequency:** Hourly.
- **Baseline:** Persistence (last observed load).
- **Initial simple model:** Moving average (`window=3`).
- **Hmax:** 72 horizons (`h=1..72`).
- **Metric:** Mean Absolute Error (MAE), with skill defined relative to persistence.
- **Goal:** Generate `Skill(h)`, `H*`, and Error vs Horizon curves under leakage-free, time-ordered evaluation.
