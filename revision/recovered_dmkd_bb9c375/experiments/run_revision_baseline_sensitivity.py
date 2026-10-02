#!/usr/bin/env python3
"""Protocol-matched persistence vs seasonal-persistence sensitivity.

The baseline family was specified before this script was executed. Every
comparison is computed from per-origin predictions on exact common support.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path

import lightgbm
import numpy as np
import pandas as pd
import sklearn
from lightgbm import LGBMRegressor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.baselines import seasonal_index
from src.summarize_baseline_sensitivity import summarize_domain


OUTPUT_COLUMNS = ["domain", "model", "origin", "target_timestamp", "horizon", "y_true", "y_pred"]
LAGS = [0, 1, 2, 3, 6, 12, 24, 48]


@dataclass(frozen=True)
class Domain:
    name: str
    input_path: Path
    horizons: tuple[int, ...]
    season: int
    max_origins: int


DOMAINS = {
    "pm25": Domain("pm25", ROOT / "data" / "beijingpm25data.csv", tuple(range(1, 49)), 24, 365),
    "load": Domain("load", ROOT / "results" / "uci_electricity_daily_aggregate.csv", (1,), 7, 365),
    "wind": Domain("wind", ROOT / "data" / "wind_hourly_clean.csv", tuple(range(1, 49)), 24, 365),
    "traffic": Domain("traffic", ROOT / "data" / "traffic_hourly_clean.csv", tuple(range(1, 73)), 24, 180),
}


def load_series(domain: Domain) -> pd.Series:
    frame = pd.read_csv(domain.input_path)
    if domain.name == "pm25":
        timestamps = pd.to_datetime(
            {"year": frame["year"], "month": frame["month"], "day": frame["day"], "hour": frame["hour"]},
            errors="coerce",
        )
        values = pd.to_numeric(frame["pm2.5"], errors="coerce").where(lambda x: x >= 0)
    else:
        timestamps = pd.to_datetime(frame["timestamp"], errors="coerce")
        values = pd.to_numeric(frame["value"], errors="coerce")
    order = np.argsort(timestamps.to_numpy())
    return pd.Series(values.to_numpy()[order], index=pd.DatetimeIndex(timestamps.to_numpy()[order]), name="value")


def rows_for_prediction(
    domain: str,
    origin_timestamp: pd.Timestamp,
    target_timestamp: pd.Timestamp,
    horizon: int,
    y_true: float,
    model_prediction: float,
    persistence_prediction: float,
    seasonal_prediction: float,
) -> list[dict[str, object]]:
    common = {
        "domain": domain,
        "origin": origin_timestamp.isoformat(),
        "target_timestamp": target_timestamp.isoformat(),
        "horizon": horizon,
        "y_true": y_true,
    }
    return [
        {**common, "model": "lightgbm", "y_pred": model_prediction},
        {**common, "model": "persistence", "y_pred": persistence_prediction},
        {**common, "model": "seasonal_persistence", "y_pred": seasonal_prediction},
    ]


def evaluate_hourly_domain(domain: Domain, series: pd.Series) -> pd.DataFrame:
    lag_frame = pd.DataFrame({f"lag_{lag}": series.shift(lag).to_numpy() for lag in LAGS})
    values = series.to_numpy()
    rows: list[dict[str, object]] = []
    for horizon in domain.horizons:
        target = pd.Series(values).shift(-horizon)
        origins = list(range(max(LAGS), len(values) - horizon, 24))[-domain.max_origins :]
        accepted = 0
        for origin in origins:
            season_idx = seasonal_index(origin, horizon, domain.season)
            if season_idx < 0 or season_idx > origin:
                continue
            y_true = target.iloc[origin]
            persistence = values[origin]
            seasonal = values[season_idx]
            x_origin = lag_frame.iloc[origin]
            if pd.isna([y_true, persistence, seasonal]).any() or x_origin.isna().any():
                continue

            train_end = origin - horizon
            if train_end < max(LAGS):
                continue
            train_start = max(max(LAGS), train_end - 24 * 30 + 1)
            train_index = np.arange(train_start, train_end + 1)
            x_train = lag_frame.iloc[train_index]
            y_train = target.iloc[train_index]
            valid = (~x_train.isna().any(axis=1)) & (~y_train.isna())
            x_train = x_train.loc[valid]
            y_train = y_train.loc[valid]
            if len(x_train) < 200:
                continue

            estimator = LGBMRegressor(
                n_estimators=50,
                learning_rate=0.05,
                num_leaves=31,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
                n_jobs=4,
                verbose=-1,
            )
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                estimator.fit(x_train, y_train)
                prediction = float(estimator.predict(x_origin.to_frame().T)[0])
            if not np.isfinite(prediction):
                continue
            rows.extend(
                rows_for_prediction(
                    domain.name,
                    series.index[origin],
                    series.index[origin + horizon],
                    horizon,
                    float(y_true),
                    prediction,
                    float(persistence),
                    float(seasonal),
                )
            )
            accepted += 1
        print(f"{domain.name} h={horizon}: common origins={accepted}", flush=True)
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def evaluate_load(domain: Domain, series: pd.Series) -> pd.DataFrame:
    values = series.to_numpy()
    rows: list[dict[str, object]] = []
    max_lag = 14
    for horizon in domain.horizons:
        for test_index in range(365, len(values) - horizon):
            origin = test_index - 1
            season_idx = seasonal_index(test_index - 1, horizon, domain.season)
            train_rows = []
            for index in range(max_lag, test_index - horizon + 1):
                features = [values[index - lag] for lag in range(1, max_lag + 1)]
                train_rows.append([*features, index % 7, values[index + horizon - 1]])
            columns = [*(f"lag_{lag}" for lag in range(1, max_lag + 1)), "day_of_week", "target"]
            train = pd.DataFrame(train_rows, columns=columns).dropna()
            if len(train) < 10:
                continue
            feature_columns = columns[:-1]
            x_test = pd.DataFrame(
                [[*(values[test_index - lag] for lag in range(1, max_lag + 1)), test_index % 7]],
                columns=feature_columns,
            )
            y_true = values[test_index + horizon - 1]
            persistence = values[origin]
            seasonal = values[season_idx]
            if pd.isna([y_true, persistence, seasonal]).any() or x_test.isna().any(axis=None):
                continue
            estimator = LGBMRegressor(
                n_estimators=100,
                learning_rate=0.05,
                num_leaves=15,
                random_state=42,
                verbosity=-1,
            )
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                estimator.fit(train[feature_columns], train["target"])
                prediction = float(estimator.predict(x_test)[0])
            rows.extend(
                rows_for_prediction(
                    domain.name,
                    series.index[origin],
                    series.index[test_index + horizon - 1],
                    horizon,
                    float(y_true),
                    prediction,
                    float(persistence),
                    float(seasonal),
                )
            )
    print(f"load h=1: common origins={len(rows) // 3}", flush=True)
    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domains", nargs="+", choices=sorted(DOMAINS), default=sorted(DOMAINS))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "revision_baseline_sensitivity")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    all_metrics = []
    all_support = []
    all_hstar = []
    started = time.perf_counter()
    for name in args.domains:
        domain = DOMAINS[name]
        if not domain.input_path.exists():
            raise FileNotFoundError(domain.input_path)
        series = load_series(domain)
        predictions = evaluate_load(domain, series) if name == "load" else evaluate_hourly_domain(domain, series)
        predictions.to_csv(args.output_dir / f"predictions_{name}.csv", index=False)
        metrics, support, hstar = summarize_domain(predictions, name)
        all_metrics.append(metrics)
        all_support.append(support)
        all_hstar.append(hstar)

    pd.concat(all_metrics, ignore_index=True).to_csv(args.output_dir / "metrics_by_horizon.csv", index=False)
    pd.concat(all_support, ignore_index=True).to_csv(args.output_dir / "support_audit.csv", index=False)
    pd.concat(all_hstar, ignore_index=True).to_csv(args.output_dir / "hstar_summary.csv", index=False)
    metadata = {
        "elapsed_seconds": time.perf_counter() - started,
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
        "lightgbm": lightgbm.__version__,
        "domains": args.domains,
        "baseline_decision": "seasonal persistence specified before result execution",
    }
    (args.output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
