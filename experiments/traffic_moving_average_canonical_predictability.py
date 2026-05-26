from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TRAFFIC_SCRIPT_PATH = Path("experiments/traffic_predictability.py")
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
MA_WINDOW = 3


def load_traffic_module():
    spec = spec_from_file_location("traffic_predictability", TRAFFIC_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec from {TRAFFIC_SCRIPT_PATH}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MovingAverageAdapter:
    """Drop-in replacement for the LightGBM estimator interface in traffic pipeline."""

    def __init__(self, **kwargs):
        self._last_mean = None

    def fit(self, x_train, y_train):
        y = pd.Series(y_train).dropna().astype(float)
        if len(y) == 0:
            raise ValueError("No samples available for moving-average fitting")
        window = min(MA_WINDOW, len(y))
        self._last_mean = float(y.iloc[-window:].mean())
        return self

    def predict(self, x):
        if self._last_mean is None:
            raise ValueError("Model not fitted")
        return np.array([self._last_mean], dtype=float)


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
    traffic = load_traffic_module()
    traffic.LGBMRegressor = MovingAverageAdapter

    series = traffic.load_traffic_series(traffic.DATA_PATH)
    horizons, baseline_mae, model_mae = traffic.evaluate_rolling_origin_lightgbm(
        series=series,
        horizons=traffic.HORIZONS,
        lags=traffic.LAGS,
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
    ).to_csv(RESULTS_DIR / "traffic_moving_average_errors.csv", index=False)

    pd.DataFrame({"horizon": horizons, "skill": skill}).to_csv(
        RESULTS_DIR / "traffic_moving_average_skill.csv", index=False
    )

    (RESULTS_DIR / "traffic_moving_average_hstar.txt").write_text(
        (
            f"H*(relax)={desc['h_relax']}\n"
            f"H*(strict)={desc['h_strict']}\n"
            f"Longest positive interval=[{desc['h_start']}, {desc['h_end']}]\n"
            f"First positive interval=[{desc['first_start']}, {desc['first_end']}]\n"
            f"Sign changes={len(desc['sign_changes'])}\n"
            f"Sign change locations={desc['sign_changes']}\n"
            f"Model=MovingAverage window={MA_WINDOW}\n"
        ),
        encoding="utf-8",
    )

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, baseline_mae, label="Baseline (Persistence)", linewidth=2)
    plt.plot(horizons, model_mae, label=f"Model (Moving Average w={MA_WINDOW})", linewidth=2)
    plt.xlabel("Horizon")
    plt.ylabel("MAE")
    plt.title("Traffic Moving-Average Error vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "traffic_moving_average_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, skill, color="darkgreen", linewidth=2)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Horizon")
    plt.ylabel("Forecast Skill")
    plt.title("Traffic Moving-Average Skill vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "traffic_moving_average_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H*(relax): {desc['h_relax']}")
    print(f"H*(strict): {desc['h_strict']}")
    print(f"Longest positive interval: [{desc['h_start']}, {desc['h_end']}]")
    print(f"First positive interval: [{desc['first_start']}, {desc['first_end']}]")
    print(f"Sign changes: {len(desc['sign_changes'])}")


if __name__ == "__main__":
    main()
