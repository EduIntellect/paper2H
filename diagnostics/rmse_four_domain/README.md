# RMSE sensitivity, four domains — traceable recomputation (2026-10-01)

Re-ran the four-domain LightGBM producers unchanged (wind/traffic/pm25 via `experiments/*_predictability.py`
and `pm25_lightgbm_full.py` with `mean_absolute_error` wrapped to also record RMSE; load via an exact copy of
`uci_energy_lightgbm.py`'s loop in `rmse_load.py`). Output: `{wind,traffic,pm25,load}_mae_rmse.csv`.
Nothing under results/ or experiments/ was modified.

Check: MAE equals the saved MAE (wind, pm25, load exactly; traffic to 7e-15) and reproduces the PDF tuples
wind 48/48 [1,48]; traffic 72/7 [46,52] (19 sign changes); PM2.5 48/22 [27,48] (5); Load 1/1 [1,1].
RMSE: wind 48/48 [1,48]; traffic 72/63 [10,72] (2); PM2.5 48/23 [26,48] (3); Load 3/3 [1,3] (1).
The inherited PM2.5 RMSE row (48/18 [31,48]) came from the moving-average experiment and is corrected.
Note: the stored results/*_predictions_all.csv belong to the six-domain version (different support) and
were not used.
