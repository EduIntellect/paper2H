# Traffic Experiment Plan (PeMS / METR-LA)

- Dataset: PeMS / METR-LA
- Target: traffic speed (mph)
- Source variable in raw data: speed (METR-LA sensor readings)
- Frequency: 5-min
- Baseline: persistence
- Initial simple model: moving average
- Hmax: 72
- Metric: MAE
- Goal: generate Error vs Horizon, Skill(h), and H* under leakage-free time-ordered evaluation
- Note: Hmax=72 is domain-specific; cross-domain comparison will use h=1..48 as common range
