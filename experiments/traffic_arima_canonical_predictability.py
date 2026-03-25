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

TRAFFIC_SCRIPT_PATH = Path("experiments/traffic_predictability.py")
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
ARIMA_ORDER = (2, 0, 0)


def load_traffic_module():
    spec = spec_from_file_location("traffic_predictability", TRAFFIC_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {TRAFFIC_SCRIPT_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ARIMAAdapter:
    """Drop-in replacement for the LightGBM estimator interface in traffic pipeline."""

    def __init__(self, horizon=1, **kwargs):
        self._fitted = None
        self.horizon = max(1, int(horizon))

    def fit(self, x_train, y_train):
        y = pd.Series(y_train).dropna().astype(float)
        if len(y) < 10:
            raise ValueError("Not enough samples for ARIMA fitting")
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
            forecast = self._fitted.forecast(steps=self.horizon)
        return np.array([float(forecast.iloc[-1])])


def _arima_factory_for_horizon(h: int):
    def _factory(**kwargs):
        return ARIMAAdapter(horizon=h, **kwargs)

    return _factory


def evaluate_horizon_aligned_arima(traffic, series: pd.Series):
    """Reuse canonical evaluator per horizon while injecting ARIMA with matching forecast step."""
    horizons_out = []
    baseline_out = []
    model_out = []

    original_estimator = traffic.LGBMRegressor
    try:
        for h in traffic.HORIZONS:
            h = int(h)
            traffic.LGBMRegressor = _arima_factory_for_horizon(h)
            h_arr, baseline_h, model_h = traffic.evaluate_rolling_origin_lightgbm(
                series=series,
                horizons=[h],
                lags=traffic.LAGS,
            )
            horizons_out.extend(h_arr.tolist())
            baseline_out.extend(baseline_h.tolist())
            model_out.extend(model_h.tolist())
    finally:
        traffic.LGBMRegressor = original_estimator

    return np.array(horizons_out), np.array(baseline_out), np.array(model_out)


def compute_descriptors(horizons: np.ndarray, skill: np.ndarray):
    positive = np.isfinite(skill) & (skill > 0)
    h_relax = int(horizons[positive].max()) if positive.any() else 0

    intervals = []
    cur_start = None
    for h, is_pos in zip(horizons, positive):
        h = int(h)
        if is_pos:
            if cur_start is None:
                cur_start = h
        elif cur_start is not None:
            intervals.append((cur_start, h - 1))
            cur_start = None
    if cur_start is not None:
        intervals.append((cur_start, int(horizons[-1])))

    if intervals:
        longest = max(intervals, key=lambda t: (t[1] - t[0] + 1, -t[0]))
        h_start, h_end = longest
        h_strict = h_end - h_start + 1
        first_start, first_end = intervals[0]
    else:
        h_start = h_end = 0
        h_strict = 0
        first_start = first_end = 0

    sign_changes = []
    for i in range(1, len(skill)):
        prev = skill[i - 1]
        cur = skill[i]
        if not (np.isfinite(prev) and np.isfinite(cur)):
            continue
        prev_sign = 1 if prev > 0 else (-1 if prev < 0 else 0)
        cur_sign = 1 if cur > 0 else (-1 if cur < 0 else 0)
        if prev_sign != 0 and cur_sign != 0 and prev_sign != cur_sign:
            sign_changes.append((int(horizons[i - 1]), int(horizons[i])))

    return {
        "h_relax": h_relax,
        "h_strict": h_strict,
        "h_start": h_start,
        "h_end": h_end,
        "first_start": first_start,
        "first_end": first_end,
        "intervals": intervals,
        "sign_changes": sign_changes,
    }


def main():
    if ARIMA is None:
        print(
            "statsmodels is not available. Install it with 'pip install statsmodels' and rerun.",
            file=sys.stderr,
        )
        print(f"Import error detail: {IMPORT_ERROR}", file=sys.stderr)
        raise SystemExit(1)

    traffic = load_traffic_module()

    series = traffic.load_traffic_series(traffic.DATA_PATH)
    horizons, baseline_mae, model_mae = evaluate_horizon_aligned_arima(
        traffic=traffic,
        series=series,
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        skill = 1.0 - (model_mae / baseline_mae)
    skill = np.where(np.isfinite(skill), skill, np.nan)

    desc = compute_descriptors(horizons, skill)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        {
            "horizon": horizons,
            "baseline_mae": baseline_mae,
            "model_mae": model_mae,
        }
    ).to_csv(RESULTS_DIR / "traffic_arima_errors.csv", index=False)

    pd.DataFrame({"horizon": horizons, "skill": skill}).to_csv(
        RESULTS_DIR / "traffic_arima_skill.csv", index=False
    )

    (RESULTS_DIR / "traffic_arima_hstar.txt").write_text(
        (
            f"H*(relax)={desc['h_relax']}\n"
            f"H*(strict)={desc['h_strict']}\n"
            f"Longest positive interval=[{desc['h_start']}, {desc['h_end']}]\n"
            f"First positive interval=[{desc['first_start']}, {desc['first_end']}]\n"
            f"Sign changes={len(desc['sign_changes'])}\n"
            f"Sign change locations={desc['sign_changes']}\n"
            f"Model=ARIMA order={ARIMA_ORDER}\n"
        ),
        encoding="utf-8",
    )

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, baseline_mae, label="Baseline (Persistence)", linewidth=2)
    plt.plot(horizons, model_mae, label=f"Model (ARIMA order={ARIMA_ORDER})", linewidth=2)
    plt.xlabel("Horizon")
    plt.ylabel("MAE")
    plt.title("Traffic ARIMA Error vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "traffic_arima_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, skill, color="darkgreen", linewidth=2)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Horizon")
    plt.ylabel("Forecast Skill")
    plt.title("Traffic ARIMA Skill vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "traffic_arima_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H*(relax): {desc['h_relax']}")
    print(f"H*(strict): {desc['h_strict']}")
    print(f"Longest positive interval: [{desc['h_start']}, {desc['h_end']}]")
    print(f"First positive interval: [{desc['first_start']}, {desc['first_end']}]")
    print(f"Sign changes: {len(desc['sign_changes'])}")


if __name__ == "__main__":
    main()
