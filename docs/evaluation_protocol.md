# Evaluation Protocol

The experiments follow a time-ordered forecasting protocol on univariate time series. For each forecast horizon \(h = 1, \ldots, H\), predictions are generated using only information available up to the forecast origin, and errors are computed against the observed future value at \(t+h\).

No random train/test partitioning is used. This avoids temporal leakage and preserves the chronological dependence structure of the data.

Performance is evaluated across multiple horizons using mean absolute error (MAE). For each horizon, model error is compared with a persistence baseline (last-value forecast), and forecast skill is computed as:

\[
\mathrm{Skill}(h) = 1 - \frac{E_{\mathrm{model}}(h)}{E_{\mathrm{baseline}}(h)}.
\]

This protocol quantifies how predictive performance evolves with lead time and supports estimation of the forecast skill horizon \(H^*\).
