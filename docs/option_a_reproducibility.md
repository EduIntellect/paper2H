# Option A Reproducibility

## Wind — ARIMA(2,0,0) robustness experiment

```bash
python3 experiments/wind_arima_canonical_predictability.py
```

Expected outputs:
- `results/wind_arima_errors.csv`
- `results/wind_arima_skill.csv`
- `results/wind_arima_hstar.txt` (`H*(relax)=48`, `H*(strict)=48`, `interval=[1,48]`)
- `figures/wind_arima_error_vs_horizon.png`
- `figures/wind_arima_skill_vs_horizon.png`

## Traffic — ARIMA(2,0,0) robustness experiment

```bash
python3 experiments/traffic_arima_canonical_predictability.py
```

Expected outputs:
- `results/traffic_arima_errors.csv`
- `results/traffic_arima_skill.csv`
- `results/traffic_arima_hstar.txt` (`H*(relax)=72`, `H*(strict)=6`, `interval=[38,43]`, `sign_changes=13`)
- `figures/traffic_arima_error_vs_horizon.png`
- `figures/traffic_arima_skill_vs_horizon.png`

## Notes

Both scripts reuse the canonical rolling-origin pipeline.
No hyperparameter tuning.
Persistence baseline.
MAE-based skill.
Approximate runtimes:
- wind: not recorded in this note
- traffic: ~4m 24s
