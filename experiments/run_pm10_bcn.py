"""Run rolling-origin evaluation for PM10_BCN domain (Barcelona Eixample)."""
from __future__ import annotations

import sys, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
from rolling_origin_evaluator import run_evaluation
from models_tabular import make_lightgbm, make_ridge, make_extratrees

RESULTS_DIR = Path("results")
DOMAIN = "pm10_bcn"

MODELS = {
    "lightgbm":   make_lightgbm(),
    "ridge":      make_ridge(),
    "extratrees": make_extratrees(),
}


def compute_skill(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (domain, model, h), g in df.groupby(["domain", "model", "horizon"]):
        mae_m = g["abs_error_model"].mean()
        mae_b = g["abs_error_baseline"].mean()
        skill = 1 - mae_m / mae_b if mae_b > 0 else np.nan
        rows.append({"domain": domain, "model": model, "horizon": h,
                     "n_origins": len(g), "mae_model": mae_m,
                     "mae_baseline": mae_b, "skill": skill})
    return pd.DataFrame(rows).sort_values(["domain", "model", "horizon"])


if __name__ == "__main__":
    print(f"=== {DOMAIN} ===")
    df = pd.read_csv("data/pm10_bcn_daily.csv", parse_dates=["date"])
    df = df.sort_values("date").set_index("date")
    series = df["pm10"]

    result = run_evaluation(
        series=series, models=MODELS,
        horizons=list(range(1, 8)),
        lags=[0, 1, 2, 3, 7, 14],
        stride=1, min_train=365, max_train=None, max_origins=None,
        domain=DOMAIN,
    )

    result.to_csv(RESULTS_DIR / f"{DOMAIN}_predictions_all.csv", index=False)
    print(f"Predictions: {len(result)} rows")

    skill = compute_skill(result)
    skill.to_csv(RESULTS_DIR / f"{DOMAIN}_skill_all.csv", index=False)
    print(f"Skill rows: {len(skill)}")
    print(skill.to_string(index=False))
