# Wind ARIMA(2,0,0) rerun with a true h-step forecast — diagnostic only (2026-10-01)

Why: `experiments/wind_arima_canonical_predictability.py:55` calls `forecast(steps=1)` at every horizon
(traffic's script uses `steps=self.horizon`). For h>1 the saved wind ARIMA therefore predicts t+1, not t+h.
Here: identical evaluator (`experiments/wind_predictability.py`), windows, origins, order (2,0,0);
only `steps=h`. Script: `wind_arima_hstep.py` (12 processes, 10m34s). Output: `wind_arima_hstep_errors.csv`.
Nothing under results/ or experiments/ was touched.

Checks: baseline MAE identical to `results/wind_arima_errors.csv`; h=1 model MAE equal (2.13347 vs 2.13347).

Result (h-step): skill > 0 at 48/48 horizons, 0 sign changes -> H*(relax)=48, H*(strict)=48, [1,48].
Skill amplitude differs from the saved (steps=1) artifact: new range 0.068-0.291, saved 0.068-0.123;
largest model-MAE difference 0.79 at h=38.
