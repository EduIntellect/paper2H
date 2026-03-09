from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

DATA_PATH = Path("data/pjm_load_hourly.csv")
RESULTS_DIR = Path("results")
FIGURES_DIR = Path("figures")
MAX_HORIZON = 72
MA_WINDOW = 3


def compute_mae_by_horizon(series: pd.Series, max_horizon: int, window: int):
    horizons = np.arange(1, max_horizon + 1)
    baseline_mae = []
    model_mae = []

    baseline_pred = series
    model_pred = series.rolling(window=window).mean()

    for h in horizons:
        target = series.shift(-h)
        valid = target.notna() & baseline_pred.notna() & model_pred.notna()

        y_true = target[valid]
        y_baseline = baseline_pred[valid]
        y_model = model_pred[valid]

        baseline_mae.append(mean_absolute_error(y_true, y_baseline))
        model_mae.append(mean_absolute_error(y_true, y_model))

    return horizons, np.array(baseline_mae), np.array(model_mae)


def load_pjm_series(path: Path) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path)
    if "load" in df.columns:
        series = pd.to_numeric(df["load"], errors="coerce")
    elif "LOAD" in df.columns:
        series = pd.to_numeric(df["LOAD"], errors="coerce")
    else:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            raise ValueError("Expected a numeric load column (e.g., 'load' or 'LOAD').")
        series = pd.to_numeric(df[numeric_cols[0]], errors="coerce")

    return series.interpolate(method="linear", limit_direction="both")


def main():
    series = load_pjm_series(DATA_PATH)

    horizons, baseline_mae, model_mae = compute_mae_by_horizon(
        series=series,
        max_horizon=MAX_HORIZON,
        window=MA_WINDOW,
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        skill = 1.0 - (model_mae / baseline_mae)
    skill = np.where(np.isfinite(skill), skill, np.nan)

    valid_horizons = horizons[skill > 0]
    h_star = int(valid_horizons.max()) if valid_horizons.size > 0 else 0

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        {
            "horizon": horizons,
            "baseline_mae": baseline_mae,
            "model_mae": model_mae,
        }
    ).to_csv(RESULTS_DIR / "pjm_load_errors.csv", index=False)

    pd.DataFrame({"horizon": horizons, "skill": skill}).to_csv(
        RESULTS_DIR / "pjm_load_skill.csv", index=False
    )

    (RESULTS_DIR / "pjm_load_hstar.txt").write_text(f"H*={h_star}\n", encoding="utf-8")

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, baseline_mae, label="Baseline (Persistence)", linewidth=2)
    plt.plot(horizons, model_mae, label=f"Model (Moving Average, w={MA_WINDOW})", linewidth=2)
    plt.xlabel("Horizon")
    plt.ylabel("MAE")
    plt.title("PJM Load Error vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pjm_load_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(horizons, skill, color="darkgreen", linewidth=2)
    plt.axhline(0.0, color="black", linestyle="--", linewidth=1)
    plt.xlabel("Horizon")
    plt.ylabel("Forecast Skill")
    plt.title("PJM Load Skill vs Horizon")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pjm_load_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H*: {h_star}")
    print("Skill array:", skill)
    print("Baseline MAE array:", baseline_mae)
    print("Model MAE array:", model_mae)


if __name__ == "__main__":
    main()
