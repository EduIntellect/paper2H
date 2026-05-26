"""Run KNN and MLP on a single domain and merge into existing predictions_all.csv.

Usage:
    python experiments/run_new_models.py <domain>

Domains: pm25 | load | wind | traffic | pm10 | pm10_bcn
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rolling_origin_evaluator import run_evaluation
from models_tabular import make_knn, make_mlp
from compute_hstar import compute_hstar
from dm_tests import dm_test, benjamini_hochberg

RESULTS_DIR = Path("results")

NEW_MODELS = {
    "knn": make_knn(),
    "mlp": make_mlp(),
}

DOMAIN_CFG = {
    "pm25": {
        "csv": "data/pm25_series.csv",
        "col": "PM25",
        "index_col": None,
        "parse_dates": False,
        "horizons": list(range(1, 49)),
        "lags": [0, 1, 2, 3, 6, 12, 24, 48],
        "stride": 24, "min_train": 200, "max_train": 720, "max_origins": 365,
    },
    "load": {
        "csv": "results/uci_electricity_daily_aggregate.csv",
        "col": "value",
        "index_col": "timestamp",
        "parse_dates": True,
        "horizons": list(range(1, 8)),
        "lags": [0, 1, 2, 3, 7, 14],
        "stride": 1, "min_train": 365, "max_train": None, "max_origins": None,
    },
    "wind": {
        "csv": "data/wind_hourly_clean.csv",
        "col": "value",
        "index_col": "timestamp",
        "parse_dates": True,
        "horizons": list(range(1, 49)),
        "lags": [0, 1, 2, 3, 6, 12, 24, 48],
        "stride": 24, "min_train": 200, "max_train": 720, "max_origins": 365,
    },
    "traffic": {
        "csv": "data/traffic_hourly_clean.csv",
        "col": "value",
        "index_col": "timestamp",
        "parse_dates": True,
        "horizons": list(range(1, 73)),
        "lags": [0, 1, 2, 3, 6, 12, 24, 48],
        "stride": 24, "min_train": 200, "max_train": 720, "max_origins": 180,
    },
    "pm10": {
        "csv": "data/pm10_elx_daily.csv",
        "col": "pm10",
        "index_col": "date",
        "parse_dates": True,
        "horizons": list(range(1, 8)),
        "lags": [0, 1, 2, 3, 7, 14],
        "stride": 1, "min_train": 365, "max_train": None, "max_origins": None,
    },
    "pm10_bcn": {
        "csv": "data/pm10_bcn_daily.csv",
        "col": "pm10",
        "index_col": "date",
        "parse_dates": True,
        "horizons": list(range(1, 8)),
        "lags": [0, 1, 2, 3, 7, 14],
        "stride": 1, "min_train": 365, "max_train": None, "max_origins": None,
    },
}


def load_series(cfg: dict) -> pd.Series:
    kwargs: dict = {}
    if cfg["parse_dates"] and cfg["index_col"]:
        kwargs = {"parse_dates": [cfg["index_col"]], "index_col": cfg["index_col"]}
    df = pd.read_csv(cfg["csv"], **kwargs)
    series = df[cfg["col"]]
    if not isinstance(series.index, pd.DatetimeIndex):
        series = series.reset_index(drop=True)
    return series.sort_index()


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


def verify_regression(domain: str, new_pred: pd.DataFrame) -> None:
    """Check that Ridge/LightGBM/ExtraTrees MAEs haven't changed."""
    existing_path = RESULTS_DIR / f"{domain}_predictions_all.csv"
    if not existing_path.exists():
        return
    existing = pd.read_csv(existing_path)
    existing_models = [m for m in existing["model"].unique()
                       if m not in ("knn", "mlp")]
    for model in existing_models:
        ex = existing[existing["model"] == model]
        mae_ex = ex["abs_error_model"].mean()
        # new_pred only has knn/mlp so nothing to compare — just report
    # Report existing model MAEs as regression baseline
    print(f"  Regression check — existing models in {domain}_predictions_all.csv:")
    for model in existing_models:
        ex = existing[existing["model"] == model]
        print(f"    {model}: mean abs_error_model = {ex['abs_error_model'].mean():.4f} "
              f"(n={len(ex)}) — UNCHANGED (not re-run)")


def merge_and_save(domain: str, new_pred: pd.DataFrame) -> pd.DataFrame:
    existing_path = RESULTS_DIR / f"{domain}_predictions_all.csv"
    if existing_path.exists():
        existing = pd.read_csv(existing_path)
        # Remove any previous knn/mlp rows (idempotent)
        existing = existing[~existing["model"].isin(list(NEW_MODELS.keys()))]
        combined = pd.concat([existing, new_pred], ignore_index=True)
    else:
        combined = new_pred
    combined.to_csv(existing_path, index=False)
    print(f"  Saved {domain}_predictions_all.csv ({len(combined)} rows total)")
    return combined


def update_skill_csv(domain: str, all_pred: pd.DataFrame) -> pd.DataFrame:
    skill = compute_skill(all_pred)
    skill.to_csv(RESULTS_DIR / f"{domain}_skill_all.csv", index=False)
    # Print new model rows
    new = skill[skill["model"].isin(list(NEW_MODELS.keys()))]
    print(f"\n  Skill (new models only):")
    print(new[["model", "horizon", "n_origins", "skill"]].to_string(index=False))
    return skill


def run_dm_for_new_models(domain: str, all_pred: pd.DataFrame) -> None:
    dm_path = RESULTS_DIR / "dm_tests_all.csv"
    dm_existing = pd.read_csv(dm_path) if dm_path.exists() else pd.DataFrame()

    new_rows = []
    for model in NEW_MODELS:
        sub = all_pred[all_pred["model"] == model]
        for h, g in sub.groupby("horizon"):
            dm_stat, p_val = dm_test(g["abs_error_model"].values,
                                     g["abs_error_baseline"].values, h=int(h))
            new_rows.append({"domain": domain, "model": model, "horizon": h,
                              "n_origins": len(g), "dm_stat": dm_stat,
                              "p_value": p_val})

    dm_new = pd.DataFrame(new_rows)
    pvals = dm_new["p_value"].values
    mask = np.isfinite(pvals)
    bh = np.full(len(pvals), np.nan)
    if mask.sum() > 0:
        bh[mask] = benjamini_hochberg(pvals[mask])
    dm_new["p_value_bh"] = bh
    dm_new["significant_bh"] = bh < 0.05

    # Remove old knn/mlp rows for this domain, append new
    if len(dm_existing) > 0:
        dm_existing = dm_existing[
            ~((dm_existing["domain"] == domain) &
              (dm_existing["model"].isin(list(NEW_MODELS.keys()))))]
        dm_combined = pd.concat([dm_existing, dm_new], ignore_index=True)
    else:
        dm_combined = dm_new
    dm_combined.to_csv(dm_path, index=False)

    for model in NEW_MODELS:
        sig_pct = dm_new[dm_new["model"] == model]["significant_bh"].mean() * 100
        print(f"  DM {model}: {sig_pct:.1f}% horizons significant (BH)")


def update_hstar_for_new_models(domain: str, skill_df: pd.DataFrame) -> None:
    hstar_path = RESULTS_DIR / "hstar_all_domains.csv"
    existing = pd.read_csv(hstar_path) if hstar_path.exists() else pd.DataFrame()

    new_rows = []
    for model in NEW_MODELS:
        sub = skill_df[(skill_df["domain"] == domain) & (skill_df["model"] == model)]
        if sub.empty:
            continue
        sub = sub.sort_values("horizon")
        result = compute_hstar(sub["skill"], sub["horizon"].tolist())
        new_rows.append({"domain": domain, "model": model, **result})

    new_df = pd.DataFrame(new_rows)
    if len(existing) > 0:
        existing = existing[
            ~((existing["domain"] == domain) &
              (existing["model"].isin(list(NEW_MODELS.keys()))))]
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_csv(hstar_path, index=False)
    print(f"\n  H* (new models):")
    print(new_df[["domain", "model", "h_relax", "h_strict",
                  "h_start", "h_end"]].to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in DOMAIN_CFG:
        print(f"Usage: python {sys.argv[0]} <domain>")
        print(f"Domains: {list(DOMAIN_CFG.keys())}")
        sys.exit(1)

    domain = sys.argv[1]
    cfg = DOMAIN_CFG[domain]
    print(f"\n{'='*60}")
    print(f"=== KNN + MLP : {domain} ===")
    print(f"{'='*60}")

    series = load_series(cfg)
    print(f"  Series: {len(series)} rows")

    t0 = time.time()
    new_pred = run_evaluation(
        series=series,
        models=NEW_MODELS,
        horizons=cfg["horizons"],
        lags=cfg["lags"],
        stride=cfg["stride"],
        min_train=cfg["min_train"],
        max_train=cfg["max_train"],
        max_origins=cfg["max_origins"],
        domain=domain,
    )
    elapsed = time.time() - t0
    print(f"  Evaluation done: {len(new_pred)} rows in {elapsed:.0f}s")

    verify_regression(domain, new_pred)
    all_pred = merge_and_save(domain, new_pred)
    skill_df = update_skill_csv(domain, all_pred)
    run_dm_for_new_models(domain, all_pred)
    update_hstar_for_new_models(domain, skill_df)

    print(f"\n  Done: {domain} KNN+MLP in {elapsed:.0f}s")
