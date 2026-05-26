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

DATA_PATH = Path("data/wind_hourly_clean.csv")
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
HORIZONS = list(range(1, 49))
MIN_TRAIN_SAMPLES = 200
ORIGIN_STRIDE = 24
MAX_TRAIN_SIZE = 24 * 30
MAX_ORIGINS_PER_HORIZON = 365

# Fixed minimal classical reference model (no tuning sweep).
SARIMA_ORDER = (1, 0, 0)
SARIMA_SEASONAL_ORDER = (0, 0, 0, 24)


def load_wind_series(path: Path) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path, parse_dates=["timestamp"]).sort_values("timestamp")
    if "value" in df.columns:
        series = pd.to_numeric(df["value"], errors="coerce")
    elif "wind_speed" in df.columns:
        series = pd.to_numeric(df["wind_speed"], errors="coerce")
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            raise ValueError("Expected a numeric wind-speed column (e.g., 'value').")
        series = pd.to_numeric(df[numeric_cols[0]], errors="coerce")

    return series.interpolate(method="linear", limit_direction="both").reset_index(drop=True)


def evaluate_rolling_origin_sarima(series: pd.Series, horizons: list[int]):
    horizons_arr = np.array(horizons)
    baseline_mae = []
    model_mae = []

    n = len(series)

    for h in horizons_arr:
        y_true_list = []
        y_baseline_list = []
        y_model_list = []

        first_origin = 0
        last_origin = n - h - 1

        origins = list(range(first_origin, last_origin + 1, ORIGIN_STRIDE))
        if len(origins) > MAX_ORIGINS_PER_HORIZON:
            origins = origins[-MAX_ORIGINS_PER_HORIZON:]

        for origin in origins:
            target = series.iloc[origin + h]
            persistence_pred = series.iloc[origin]
            if pd.isna(target) or pd.isna(persistence_pred):
                continue

            train_end = origin - h
            if train_end < 0:
                continue

            train_start = max(0, train_end - MAX_TRAIN_SIZE + 1)
            train = series.iloc[train_start : train_end + 1].dropna()
            if len(train) < MIN_TRAIN_SAMPLES:
                continue

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fitted = SARIMAX(
                        train,
                        order=SARIMA_ORDER,
                        seasonal_order=SARIMA_SEASONAL_ORDER,
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                    ).fit(disp=False)
                forecast = fitted.forecast(steps=h)
                model_pred = float(forecast.iloc[-1])
            except Exception:
                continue

            if np.isfinite(model_pred):
                y_true_list.append(float(target))
                y_baseline_list.append(float(persistence_pred))
                y_model_list.append(float(model_pred))

        print(f"Horizon {h}: valid windows={len(y_true_list)}")
        if y_true_list:
            baseline_mae.append(mean_absolute_error(y_true_list, y_baseline_list))
            model_mae.append(mean_absolute_error(y_true_list, y_model_list))
        else:
            baseline_mae.append(np.nan)
            model_mae.append(np.nan)

    return horizons_arr, np.array(baseline_mae), np.array(model_mae)


def compute_hstar_descriptors(horizons: np.ndarray, skill: np.ndarray):
    positive = np.isfinite(skill) & (skill > 0)

    if positive.any():
        h_relax = int(horizons[positive].max())
    else:
        h_relax = 0

    best_len = 0
    best_start = 0
    best_end = 0
    cur_start = None

    for h, is_pos in zip(horizons, positive):
        if is_pos:
            if cur_start is None:
                cur_start = int(h)
        elif cur_start is not None:
            cur_end = int(h - 1)
            cur_len = cur_end - cur_start + 1
            if cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
                best_end = cur_end
            cur_start = None

    if cur_start is not None:
        cur_end = int(horizons[-1])
        cur_len = cur_end - cur_start + 1
        if cur_len > best_len:
            best_len = cur_len
            best_start = cur_start
            best_end = cur_end

    h_strict = best_len
    return h_relax, h_strict, best_start, best_end


def main():
    if SARIMAX is None:
        print(
            "statsmodels is not available. Install it with 'pip install statsmodels' and rerun.",
            file=sys.stderr,
        )
        print(f"Import error detail: {IMPORT_ERROR}", file=sys.stderr)
        raise SystemExit(1)

    series = load_wind_series(DATA_PATH)
    horizons, baseline_mae, model_mae = evaluate_rolling_origin_sarima(
        series=series,
        horizons=HORIZONS,
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        skill = 1.0 - (model_mae / baseline_mae)
    skill = np.where(np.isfinite(skill), skill, np.nan)

    h_relax, h_strict, h_start, h_end = compute_hstar_descriptors(horizons, skill)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        {
            "horizon": horizons,
            "baseline_mae": baseline_mae,
            "model_mae": model_mae,
        }
    ).to_csv(RESULTS_DIR / "wind_sarima_errors.csv", index=False)

    pd.DataFrame({"horizon": horizons, "skill": skill}).to_csv(
        RESULTS_DIR / "wind_sarima_skill.csv", index=False
    )

    (RESULTS_DIR / "wind_sarima_hstar.txt").write_text(
        (
            f"H*(relax)={h_relax}\n"
            f"H*(strict)={h_strict}\n"
            f"Longest positive interval=[{h_start}, {h_end}]\n"
        ),
        encoding="utf-8",
    )

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
    plt.title("Wind SARIMA Error vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "wind_sarima_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, skill, color="darkgreen", linewidth=2)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Horizon")
    plt.ylabel("Forecast Skill")
    plt.title("Wind SARIMA Skill vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "wind_sarima_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H*(relax): {h_relax}")
    print(f"H*(strict): {h_strict}")
    print(f"Longest positive interval: [{h_start}, {h_end}]")
    print("Skill array:", skill)


if __name__ == "__main__":
    main()
