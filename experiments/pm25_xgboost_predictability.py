from pathlib import Path
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

try:
    from xgboost import XGBRegressor
except ImportError as exc:
    XGBRegressor = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

DATA_PATH = Path("data/beijingpm25data.csv")
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
HORIZONS = [1, 3, 6, 12, 24, 36, 48]
LAGS = [1, 2, 3, 6, 12, 24, 48]
MIN_TRAIN_SAMPLES = 200
ORIGIN_STRIDE = 24
MAX_TRAIN_SIZE = 24 * 30
MAX_ORIGINS_PER_HORIZON = 60


def load_real_pm25(path: Path) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path)
    if "pm2.5" not in df.columns:
        raise ValueError("Expected column 'pm2.5' in Beijing dataset")

    if {"year", "month", "day", "hour"}.issubset(df.columns):
        time_index = pd.to_datetime(
            {
                "year": df["year"],
                "month": df["month"],
                "day": df["day"],
                "hour": df["hour"],
            },
            errors="coerce",
        )
        df = df.assign(_time=time_index).sort_values("_time")

    series = pd.to_numeric(df["pm2.5"], errors="coerce")
    # Conservative cleaning: keep negatives as missing and avoid global imputation.
    series = series.where(series >= 0)
    series = series.reset_index(drop=True)
    return series


def build_lag_features(series: pd.Series, lags: list[int]) -> pd.DataFrame:
    lag_df = pd.DataFrame(index=series.index)
    for lag in lags:
        lag_df[f"lag_{lag}"] = series.shift(lag)
    return lag_df


def evaluate_rolling_origin_xgboost(series: pd.Series, horizons: list[int], lags: list[int]):
    horizons_arr = np.array(horizons)
    baseline_mae = []
    model_mae = []
    valid_counts = []

    lag_df = build_lag_features(series, lags)
    max_lag = max(lags)
    n = len(series)

    for h in horizons_arr:
        y_true_list = []
        y_baseline_list = []
        y_model_list = []

        target_series = series.shift(-h)
        first_origin = max_lag
        last_origin = n - h - 1

        # Daily stride is an explicit computational choice to keep rolling-origin
        # evaluation tractable without altering temporal causality.
        origins = list(range(first_origin, last_origin + 1, ORIGIN_STRIDE))
        if len(origins) > MAX_ORIGINS_PER_HORIZON:
            origins = origins[-MAX_ORIGINS_PER_HORIZON:]

        for origin in origins:
            target = target_series.iloc[origin]
            persistence_pred = series.iloc[origin]

            # Skip if the scored pair is missing.
            if pd.isna(target) or pd.isna(persistence_pred):
                continue

            x_origin = lag_df.iloc[origin]
            if x_origin.isna().any():
                continue

            train_end = origin - h
            if train_end < max_lag:
                continue

            train_start = max(max_lag, train_end - MAX_TRAIN_SIZE + 1)
            train_idx = np.arange(train_start, train_end + 1)
            x_train = lag_df.iloc[train_idx]
            y_train = target_series.iloc[train_idx]

            valid_train_mask = (~x_train.isna().any(axis=1)) & (~y_train.isna())
            x_train = x_train.loc[valid_train_mask]
            y_train = y_train.loc[valid_train_mask]

            if len(x_train) < MIN_TRAIN_SAMPLES:
                continue

            model = XGBRegressor(
                n_estimators=50,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="reg:squarederror",
                random_state=42,
                n_jobs=-1,
            )

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model.fit(x_train, y_train)
                model_pred = float(model.predict(x_origin.to_frame().T)[0])
            except Exception:
                # Skip fitting/prediction failures and continue evaluation.
                continue

            if np.isfinite(model_pred):
                y_true_list.append(float(target))
                y_baseline_list.append(float(persistence_pred))
                y_model_list.append(model_pred)

        valid_counts.append(len(y_true_list))
        print(f"Horizon {h}: valid windows={len(y_true_list)}")
        if y_true_list:
            baseline_mae.append(mean_absolute_error(y_true_list, y_baseline_list))
            model_mae.append(mean_absolute_error(y_true_list, y_model_list))
        else:
            baseline_mae.append(np.nan)
            model_mae.append(np.nan)

    return horizons_arr, np.array(baseline_mae), np.array(model_mae), np.array(valid_counts)


def main():
    if XGBRegressor is None:
        print(
            "xgboost is not available. Install it with 'pip install xgboost' and rerun.",
            file=sys.stderr,
        )
        print(f"Import error detail: {IMPORT_ERROR}", file=sys.stderr)
        raise SystemExit(1)

    series = load_real_pm25(DATA_PATH)
    horizons, baseline_mae, model_mae, valid_counts = evaluate_rolling_origin_xgboost(
        series=series,
        horizons=HORIZONS,
        lags=LAGS,
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        skill = 1.0 - (model_mae / baseline_mae)
    skill = np.where(np.isfinite(skill), skill, np.nan)

    positive_horizons = horizons[skill > 0]
    h_star = int(positive_horizons.max()) if positive_horizons.size > 0 else 0

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        {
            "horizon": horizons,
            "baseline_mae": baseline_mae,
            "model_mae": model_mae,
        }
    ).to_csv(RESULTS_DIR / "pm25_xgboost_screen_errors.csv", index=False)

    pd.DataFrame({"horizon": horizons, "skill": skill}).to_csv(
        RESULTS_DIR / "pm25_xgboost_screen_skill.csv", index=False
    )

    pd.DataFrame({"horizon": horizons, "n_valid_windows": valid_counts}).to_csv(
        RESULTS_DIR / "pm25_xgboost_screen_counts.csv", index=False
    )

    (RESULTS_DIR / "pm25_xgboost_screen_hstar.txt").write_text(f"H*={h_star}\n", encoding="utf-8")

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, baseline_mae, label="Baseline (Persistence)", linewidth=2)
    plt.plot(horizons, model_mae, label="Model (XGBoost)", linewidth=2)
    plt.xlabel("Horizon")
    plt.ylabel("MAE")
    plt.title("PM2.5 XGBoost Screening Error vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_xgboost_screen_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, skill, color="darkgreen", linewidth=2)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Horizon")
    plt.ylabel("Forecast Skill")
    plt.title("PM2.5 XGBoost Screening Skill vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_xgboost_screen_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H*: {h_star}")
    print("Skill array:", skill)
    print("Baseline MAE array:", baseline_mae)
    print("Model MAE array:", model_mae)
    print("Valid window counts:", valid_counts)
    print("Horizons used:", HORIZONS)
    print("Max origins per horizon:", MAX_ORIGINS_PER_HORIZON)
    print("Origin stride:", ORIGIN_STRIDE)
    print("Max train size:", MAX_TRAIN_SIZE)


if __name__ == "__main__":
    main()
