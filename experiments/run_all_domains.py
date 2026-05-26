"""Run rolling-origin evaluation for all four domains."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd

from rolling_origin_evaluator import run_evaluation
from models_tabular import make_lightgbm, make_ridge, make_extratrees

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

MODELS = {
    "lightgbm": make_lightgbm(),
    "ridge": make_ridge(),
    "extratrees": make_extratrees(),
}


def compute_skill_from_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-origin predictions to skill by model × horizon."""
    rows = []
    for (domain, model, h), g in df.groupby(["domain", "model", "horizon"]):
        mae_m = g["abs_error_model"].mean()
        mae_b = g["abs_error_baseline"].mean()
        skill = 1 - mae_m / mae_b if mae_b > 0 else np.nan
        rows.append({
            "domain": domain, "model": model, "horizon": h,
            "n_origins": len(g),
            "mae_model": mae_m, "mae_baseline": mae_b, "skill": skill,
        })
    return pd.DataFrame(rows).sort_values(["domain", "model", "horizon"])


# ── PM2.5 ──────────────────────────────────────────────────────────────────
def run_pm25():
    print("=== PM2.5 ===")
    df = pd.read_csv("data/pm25_series.csv")
    series = pd.Series(df["PM25"].values, name="PM25")
    result = run_evaluation(
        series=series, models=MODELS,
        horizons=list(range(1, 49)),
        lags=[0, 1, 2, 3, 6, 12, 24, 48],
        stride=24, min_train=200, max_train=720, max_origins=365,
        domain="pm25",
    )
    out_pred = RESULTS_DIR / "pm25_predictions_all.csv"
    result.to_csv(out_pred, index=False)
    print(f"  Predictions rows: {len(result)}")

    skill = compute_skill_from_predictions(result)
    out_skill = RESULTS_DIR / "pm25_skill_all.csv"
    skill.to_csv(out_skill, index=False)
    print(f"  Skill rows: {len(skill)}")
    return result, skill


# ── Load ───────────────────────────────────────────────────────────────────
def run_load():
    print("=== Load ===")
    df = pd.read_csv("results/uci_electricity_daily_aggregate.csv",
                     parse_dates=["timestamp"])
    df = df.sort_values("timestamp").set_index("timestamp")
    series = df["value"]

    result = run_evaluation(
        series=series, models=MODELS,
        horizons=list(range(1, 8)),
        lags=[0, 1, 2, 3, 7, 14],
        stride=1, min_train=365, max_train=None, max_origins=None,
        domain="load",
    )
    out_pred = RESULTS_DIR / "load_predictions_all.csv"
    result.to_csv(out_pred, index=False)
    print(f"  Predictions rows: {len(result)}")

    skill = compute_skill_from_predictions(result)
    out_skill = RESULTS_DIR / "load_skill_all.csv"
    skill.to_csv(out_skill, index=False)
    print(f"  Skill rows: {len(skill)}")
    return result, skill


# ── Wind ───────────────────────────────────────────────────────────────────
def run_wind():
    print("=== Wind ===")
    df = pd.read_csv("data/wind_hourly_clean.csv", parse_dates=["timestamp"])
    df = df.sort_values("timestamp").set_index("timestamp")
    series = df["value"]

    result = run_evaluation(
        series=series, models=MODELS,
        horizons=list(range(1, 49)),
        lags=[0, 1, 2, 3, 6, 12, 24, 48],
        stride=24, min_train=200, max_train=720, max_origins=365,
        domain="wind",
    )
    out_pred = RESULTS_DIR / "wind_predictions_all.csv"
    result.to_csv(out_pred, index=False)
    print(f"  Predictions rows: {len(result)}")

    skill = compute_skill_from_predictions(result)
    out_skill = RESULTS_DIR / "wind_skill_all.csv"
    skill.to_csv(out_skill, index=False)
    print(f"  Skill rows: {len(skill)}")
    return result, skill


# ── Traffic ────────────────────────────────────────────────────────────────
def run_traffic():
    print("=== Traffic ===")
    df = pd.read_csv("data/traffic_hourly_clean.csv", parse_dates=["timestamp"])
    df = df.sort_values("timestamp").set_index("timestamp")
    series = df["value"]

    result = run_evaluation(
        series=series, models=MODELS,
        horizons=list(range(1, 73)),
        lags=[0, 1, 2, 3, 6, 12, 24, 48],
        stride=24, min_train=200, max_train=720, max_origins=180,
        domain="traffic",
    )
    out_pred = RESULTS_DIR / "traffic_predictions_all.csv"
    result.to_csv(out_pred, index=False)
    print(f"  Predictions rows: {len(result)}")

    skill = compute_skill_from_predictions(result)
    out_skill = RESULTS_DIR / "traffic_skill_all.csv"
    skill.to_csv(out_skill, index=False)
    print(f"  Skill rows: {len(skill)}")
    return result, skill


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")

    results_all = []
    skills_all = []

    for fn in [run_pm25, run_load, run_wind, run_traffic]:
        pred, skill = fn()
        results_all.append(pred)
        skills_all.append(skill)

    print("\n=== Done. Summary ===")
    for df in skills_all:
        if len(df) > 0:
            d = df["domain"].iloc[0]
            print(f"{d}: {len(df)} skill rows, models: {df['model'].unique().tolist()}")
