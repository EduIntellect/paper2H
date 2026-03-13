from pathlib import Path
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
except ImportError as exc:
    SARIMAX = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

DATA_PATH = Path("data/beijingpm25data.csv")
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
MAX_HORIZON = 48
MIN_TRAIN_SIZE = 24 * 14
MIN_EFFECTIVE_TRAIN = 24 * 7
SARIMA_ORDER = (1, 1, 1)
SARIMA_SEASONAL_ORDER = (1, 1, 1, 24)


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
    # Keep negatives as missing and avoid any global imputation.
    series = series.where(series >= 0)
    series = series.reset_index(drop=True)
    return series


def evaluate_rolling_origin(series: pd.Series, max_horizon: int):
    horizons = np.arange(1, max_horizon + 1)
    baseline_mae = []
    model_mae = []
    valid_counts = []

    n = len(series)

    for h in horizons:
        y_true = []
        y_baseline = []
        y_model = []

        last_origin = n - h - 1
        for origin in range(MIN_TRAIN_SIZE - 1, last_origin + 1):
            target = float(series.iloc[origin + h])
            persistence_pred = float(series.iloc[origin])

            # Skip windows with missing target or baseline predictor.
            if not np.isfinite(target) or not np.isfinite(persistence_pred):
                continue

            train = series.iloc[: origin + 1]
            # Train uses only data available up to origin; no future values.
            train_clean = train.dropna()
            if len(train_clean) < MIN_EFFECTIVE_TRAIN:
                continue

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fitted = SARIMAX(
                        train_clean,
                        order=SARIMA_ORDER,
                        seasonal_order=SARIMA_SEASONAL_ORDER,
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                    ).fit(disp=False)
                forecast = fitted.forecast(steps=h)
                sarima_pred = float(forecast.iloc[-1])
            except Exception:
                # Skip failing windows without breaking the full experiment.
                continue

            if np.isfinite(sarima_pred):
                y_true.append(target)
                y_baseline.append(persistence_pred)
                y_model.append(sarima_pred)

        valid_counts.append(len(y_true))
        if y_true:
            baseline_mae.append(mean_absolute_error(y_true, y_baseline))
            model_mae.append(mean_absolute_error(y_true, y_model))
        else:
            baseline_mae.append(np.nan)
            model_mae.append(np.nan)

    return horizons, np.array(baseline_mae), np.array(model_mae), np.array(valid_counts)


def main():
    if SARIMAX is None:
        print(
            "statsmodels is not available. Install it with 'pip install statsmodels' and rerun.",
            file=sys.stderr,
        )
        print(f"Import error detail: {IMPORT_ERROR}", file=sys.stderr)
        raise SystemExit(1)

    series = load_real_pm25(DATA_PATH)
    horizons, baseline_mae, model_mae, valid_counts = evaluate_rolling_origin(series, MAX_HORIZON)

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
    ).to_csv(RESULTS_DIR / "pm25_sarima_errors.csv", index=False)

    pd.DataFrame({"horizon": horizons, "skill": skill}).to_csv(
        RESULTS_DIR / "pm25_sarima_skill.csv", index=False
    )

    pd.DataFrame({"horizon": horizons, "n_valid_windows": valid_counts}).to_csv(
        RESULTS_DIR / "pm25_sarima_counts.csv", index=False
    )

    (RESULTS_DIR / "pm25_sarima_hstar.txt").write_text(f"H*={h_star}\n", encoding="utf-8")

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, baseline_mae, label="Baseline (Persistence)", linewidth=2)
    plt.plot(
        horizons,
        model_mae,
        label=(
            "Model (SARIMA "
            f"order={SARIMA_ORDER}, seasonal_order={SARIMA_SEASONAL_ORDER})"
        ),
        linewidth=2,
    )
    plt.xlabel("Horizon")
    plt.ylabel("MAE")
    plt.title("PM2.5 SARIMA Error vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_sarima_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, skill, color="darkgreen", linewidth=2)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Horizon")
    plt.ylabel("Forecast Skill")
    plt.title("PM2.5 SARIMA Skill vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_sarima_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H*: {h_star}")
    print("Skill array:", skill)
    print("Baseline MAE array:", baseline_mae)
    print("Model MAE array:", model_mae)


if __name__ == "__main__":
    main()
