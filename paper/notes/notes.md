## PM2.5 XGBoost methodological note

To ensure computational tractability and reduce the influence of non-stationary historical regimes, XGBoost models were trained on a sliding window of the 720 most recent observations (30 days) preceding each forecast origin. Forecast origins were sampled with daily stride. Temporal causality was preserved throughout the evaluation, and no future information was used in feature construction, training, or prediction.
PM2.5 full LightGBM result: formal H^*=48, but with negative short-horizon skill and positive long-horizon skill, confirming both empirical viability and the need to distinguish formal horizon from operational usefulness.
Resumen ejecutivo
	•	H^*_{\text{formal}} = 48
	•	primer skill positivo = 8
	•	positividad sostenida real = desde 27 hasta 48
	•	hallazgo metodológico fuerte:
H^* formal y utilidad operativa no coinciden necesariamente
PM2.5 provides a clear example where the formal horizon H^* equals 48, yet positive skill is not contiguous from short horizons. Instead, the model only achieves sustained superiority over persistence from approximately h=27 onward. This shows that raw H^* alone can overstate operational usefulness unless the contiguity structure of the skill curve is also considered.