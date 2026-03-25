from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.arima.model import ARIMA
except ImportError as exc:
    ARIMA = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None

WIND_SCRIPT_PATH = Path("experiments/wind_predictability.py")
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
ARIMA_ORDER = (2, 0, 0)


def load_wind_module():
    spec = spec_from_file_location("wind_predictability", WIND_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {WIND_SCRIPT_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ARIMAAdapter:
    """Drop-in replacement for the LightGBM estimator interface used in wind pipeline."""

    def __init__(self, **kwargs):
        self._fitted = None

    def fit(self, x_train, y_train):
        y = pd.Series(y_train).dropna().astype(float)
        if len(y) < 10:
            raise ValueError("Not enough samples for ARIMA fitting")
        # Use a regular hourly index to avoid forecast-index warnings in statsmodels.
        y.index = pd.date_range("2000-01-01", periods=len(y), freq="h")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._fitted = ARIMA(y, order=ARIMA_ORDER).fit()
        return self

    def predict(self, x):
        if self._fitted is None:
            raise ValueError("Model not fitted")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            forecast = self._fitted.forecast(steps=1)
        return np.array([float(forecast.iloc[-1])])


def compute_hstar_descriptors(horizons: np.ndarray, skill: np.ndarray):
    positive = np.isfinite(skill) & (skill > 0)
    h_relax = int(horizons[positive].max()) if positive.any() else 0

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
    if ARIMA is None:
        print(
            "statsmodels is not available. Install it with 'pip install statsmodels' and rerun.",
            file=sys.stderr,
        )
        print(f"Import error detail: {IMPORT_ERROR}", file=sys.stderr)
        raise SystemExit(1)

    wind = load_wind_module()

    # Canonical protocol reuse: swap model class only, keep evaluation function intact.
    wind.LGBMRegressor = ARIMAAdapter

    series = wind.load_wind_series(wind.DATA_PATH)
    horizons, baseline_mae, model_mae = wind.evaluate_rolling_origin_lightgbm(
        series=series,
        horizons=wind.HORIZONS,
        lags=wind.LAGS,
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
    ).to_csv(RESULTS_DIR / "wind_arima_errors.csv", index=False)

    pd.DataFrame({"horizon": horizons, "skill": skill}).to_csv(
        RESULTS_DIR / "wind_arima_skill.csv", index=False
    )

    (RESULTS_DIR / "wind_arima_hstar.txt").write_text(
        (
            f"H*(relax)={h_relax}\n"
            f"H*(strict)={h_strict}\n"
            f"Longest positive interval=[{h_start}, {h_end}]\n"
            f"Model=ARIMA order={ARIMA_ORDER}\n"
        ),
        encoding="utf-8",
    )

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, baseline_mae, label="Baseline (Persistence)", linewidth=2)
    plt.plot(horizons, model_mae, label=f"Model (ARIMA order={ARIMA_ORDER})", linewidth=2)
    plt.xlabel("Horizon")
    plt.ylabel("MAE")
    plt.title("Wind ARIMA Error vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "wind_arima_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, skill, color="darkgreen", linewidth=2)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Horizon")
    plt.ylabel("Forecast Skill")
    plt.title("Wind ARIMA Skill vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "wind_arima_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H*(relax): {h_relax}")
    print(f"H*(strict): {h_strict}")
    print(f"Longest positive interval: [{h_start}, {h_end}]")


if __name__ == "__main__":
    main()
