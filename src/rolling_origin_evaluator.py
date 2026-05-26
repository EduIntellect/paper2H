"""Unified rolling-origin evaluator with persistence baseline.

Efficient implementation: lag matrix is built once per horizon, then the
rolling-origin loop only slices and fits — no redundant array construction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import clone


def run_evaluation(
    series: pd.Series,
    models: dict,
    horizons: list[int],
    lags: list[int],
    stride: int,
    min_train: int,
    max_train: int | None,
    max_origins: int | None,
    domain: str = "unknown",
) -> pd.DataFrame:
    """
    Rolling-origin evaluation against a persistence baseline.

    Returns DataFrame with columns:
        domain, model, horizon, origin_idx, origin_timestamp,
        y_true, y_pred, y_pred_baseline,
        abs_error_model, abs_error_baseline
    """
    values = np.asarray(series, dtype=float)
    timestamps = list(series.index)
    n = len(values)
    max_lag = max(lags) if lags else 0

    # Precompute full lag matrix: X[t] = [values[t-lag] for lag in lags]
    # lag=0 → values[t] itself (last known value at origin t)
    n_lags = len(lags)
    X_full = np.full((n, n_lags), np.nan)
    for j, lag in enumerate(lags):
        if lag == 0:
            X_full[:, j] = values
        elif lag < n:
            X_full[lag:, j] = values[:-lag]

    # Collect valid origin indices (cap AFTER filtering by min_train, not before)
    max_h = max(horizons)
    all_candidate_origins = list(range(max_lag, n - max_h, stride))

    records = []
    # Track per-horizon origin count to enforce max_origins uniformly
    origin_counts: dict[int, int] = {}

    for h in horizons:
        origin_counts[h] = 0
        # Target for horizon h: y_t = values[t + h]
        y_full = np.full(n, np.nan)
        y_full[:n - h] = values[h:]

        for origin in all_candidate_origins:
            if max_origins is not None and origin_counts[h] >= max_origins:
                break
            # Training window
            train_start = max(0, origin - max_train) if max_train is not None else 0
            train_end = origin  # exclusive; features at train_end-1, target at train_end-1+h

            # Valid training rows: lag features and target both available,
            # target index must be < origin (no leakage)
            # Row i is valid when: i >= max_lag  AND  i + h <= origin
            row_min = max(train_start, max_lag)
            row_max = origin - h + 1  # i + h - 1 < origin  →  i < origin - h + 1

            if row_max - row_min < min_train:
                continue

            X_train = X_full[row_min:row_max]
            y_train = y_full[row_min:row_max]

            # Drop rows with any NaN (shouldn't happen after max_lag guard, but be safe)
            valid = np.isfinite(X_train).all(axis=1) & np.isfinite(y_train)
            if valid.sum() < min_train:
                continue

            X_tr = X_train[valid]
            y_tr = y_train[valid]

            # Features and truth at origin
            x_origin = X_full[origin]
            if not np.isfinite(x_origin).all():
                continue
            y_true = values[origin + h]
            if not np.isfinite(y_true):
                continue

            # Persistence baseline: last known value
            y_baseline = values[origin]

            ts = timestamps[origin]

            origin_counts[h] += 1

            for model_name, estimator in models.items():
                try:
                    fitted = clone(estimator).fit(X_tr, y_tr)
                    y_pred = float(fitted.predict(x_origin.reshape(1, -1))[0])
                except Exception:
                    continue

                records.append({
                    "domain": domain,
                    "model": model_name,
                    "horizon": h,
                    "origin_idx": origin,
                    "origin_timestamp": ts,
                    "y_true": y_true,
                    "y_pred": y_pred,
                    "y_pred_baseline": y_baseline,
                    "abs_error_model": abs(y_true - y_pred),
                    "abs_error_baseline": abs(y_true - y_baseline),
                })

    return pd.DataFrame(records)
