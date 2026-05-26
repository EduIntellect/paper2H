"""
Rolling-origin ARIMA evaluator with per-origin predictions saved in standard format.
Produces predictions_all.csv compatible with dm_tests.py and compute_hstar.py.

Usage:
    python src/run_arima_rolling_origin.py wind
    python src/run_arima_rolling_origin.py traffic
"""
from __future__ import annotations

import sys
import warnings
import time
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))
from dm_tests import dm_test, benjamini_hochberg
from compute_hstar import compute_hstar

RESULTS_DIR = Path("results")

DOMAIN_CONFIG = {
    "wind": {
        "data_file": "data/wind_hourly_clean.csv",
        "arima_order": (2, 0, 0),
        "horizons": list(range(1, 49)),
        "lags": [0, 1, 2, 3, 6, 12, 24, 48],
        "stride": 24,
        "min_train": 200,
        "max_train": 720,
        "max_origins": 365,
    },
    "traffic": {
        "data_file": "data/traffic_hourly_clean.csv",
        "arima_order": (2, 0, 0),
        "horizons": list(range(1, 73)),
        "lags": [0, 1, 2, 3, 6, 12, 24, 48],
        "stride": 24,
        "min_train": 200,
        "max_train": 720,
        "max_origins": 180,
    },
}


def fit_and_forecast(train_values: np.ndarray, order: tuple, h_max: int) -> np.ndarray | None:
    """Fit ARIMA on train_values and return forecasts for steps 1..h_max."""
    try:
        from statsmodels.tsa.arima.model import ARIMA as StatsARIMA
        y = pd.Series(train_values.astype(float))
        y = y.dropna()
        if len(y) < max(order[0] + order[2] + 5, 20):
            return None
        y.index = pd.RangeIndex(len(y))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fitted = StatsARIMA(y, order=order).fit()
            forecasts = fitted.forecast(steps=h_max)
        return np.array(forecasts, dtype=float)
    except Exception:
        return None


def run_arima_rolling_origin(domain: str) -> pd.DataFrame:
    cfg = DOMAIN_CONFIG[domain]
    df = pd.read_csv(cfg["data_file"], parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    series = df["value"].values
    timestamps = df["timestamp"].values
    n = len(series)

    horizons = cfg["horizons"]
    h_max = max(horizons)
    stride = cfg["stride"]
    min_train = cfg["min_train"]
    max_train = cfg["max_train"]
    max_origins = cfg["max_origins"]
    order = cfg["arima_order"]

    rows = []
    origin_count = 0
    t0 = time.time()

    for origin_idx in range(min_train, n - h_max, stride):
        # training window
        train_start = max(0, origin_idx - max_train) if max_train else 0
        train_vals = series[train_start:origin_idx]

        if len(train_vals) < min_train:
            continue

        # fit ARIMA and get forecasts for all horizons at once
        forecasts = fit_and_forecast(train_vals, order, h_max)
        if forecasts is None:
            continue

        # baseline = persistence (last known value)
        baseline_val = series[origin_idx - 1]

        for h in horizons:
            target_idx = origin_idx + h - 1
            if target_idx >= n:
                break
            y_true = series[target_idx]
            y_pred = float(forecasts[h - 1])
            y_base = float(baseline_val)

            rows.append({
                "domain": domain,
                "model": "arima",
                "horizon": h,
                "origin_idx": origin_idx,
                "origin_timestamp": timestamps[origin_idx],
                "y_true": y_true,
                "y_pred": y_pred,
                "y_pred_baseline": y_base,
                "abs_error_model": abs(y_true - y_pred),
                "abs_error_baseline": abs(y_true - y_base),
            })

        origin_count += 1
        if origin_count % 50 == 0:
            elapsed = time.time() - t0
            print(f"  {domain} ARIMA: {origin_count} origins done in {elapsed:.0f}s")
        if max_origins and origin_count >= max_origins:
            break

    elapsed = time.time() - t0
    print(f"  {domain} ARIMA done: {origin_count} origins, {len(rows)} rows in {elapsed:.0f}s")
    return pd.DataFrame(rows)


def compute_skill_from_predictions(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (domain, model, h), g in df.groupby(["domain", "model", "horizon"]):
        mae_m = g["abs_error_model"].mean()
        mae_b = g["abs_error_baseline"].mean()
        skill = 1 - mae_m / mae_b if mae_b > 0 else np.nan
        rows.append({"domain": domain, "model": model, "horizon": h,
                     "n_origins": len(g), "mae_model": mae_m,
                     "mae_baseline": mae_b, "skill": skill})
    return pd.DataFrame(rows).sort_values(["domain", "model", "horizon"])


def run_dm_tests(pred_df: pd.DataFrame, domain: str) -> pd.DataFrame:
    from dm_tests import dm_test, benjamini_hochberg
    rows = []
    for (model, h), g in pred_df.groupby(["model", "horizon"]):
        dm_stat, p_val = dm_test(g["abs_error_model"].values,
                                 g["abs_error_baseline"].values, h=int(h))
        rows.append({"domain": domain, "model": model, "horizon": h,
                     "n_origins": len(g), "dm_stat": dm_stat, "p_value": p_val})
    dm_df = pd.DataFrame(rows)
    pvals = dm_df["p_value"].values
    mask = np.isfinite(pvals)
    bh = np.full(len(pvals), np.nan)
    if mask.sum() > 0:
        bh[mask] = benjamini_hochberg(pvals[mask])
    dm_df["p_value_bh"] = bh
    dm_df["significant_bh"] = bh < 0.05
    sig_pct = dm_df["significant_bh"].mean() * 100
    print(f"  {domain} ARIMA DM: {sig_pct:.1f}% horizons significant (BH)")
    return dm_df


def update_results_tables(domain: str, skill_df: pd.DataFrame,
                          dm_df: pd.DataFrame) -> None:
    # Update hstar_all_domains.csv
    hstar_rows = []
    for (dom, model), g in skill_df.groupby(["domain", "model"]):
        g_sorted = g.sort_values("horizon")
        result = compute_hstar(g_sorted["skill"], g_sorted["horizon"].tolist())
        hstar_rows.append({"domain": dom, "model": model, **result})
    new_hstar = pd.DataFrame(hstar_rows)

    hstar_path = RESULTS_DIR / "hstar_all_domains.csv"
    existing_h = pd.read_csv(hstar_path)
    existing_h = existing_h[~((existing_h["domain"] == domain) &
                               (existing_h["model"] == "arima"))]
    combined_h = pd.concat([existing_h, new_hstar], ignore_index=True)
    combined_h.to_csv(hstar_path, index=False)
    print(f"  hstar_all_domains.csv updated ({len(combined_h)} rows)")
    print(new_hstar.to_string(index=False))

    # Update dm_tests_all.csv
    dm_path = RESULTS_DIR / "dm_tests_all.csv"
    existing_dm = pd.read_csv(dm_path)
    existing_dm = existing_dm[~((existing_dm["domain"] == domain) &
                                 (existing_dm["model"] == "arima"))]
    combined_dm = pd.concat([existing_dm, dm_df], ignore_index=True)
    combined_dm.to_csv(dm_path, index=False)
    print(f"  dm_tests_all.csv updated ({len(combined_dm)} rows)")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in DOMAIN_CONFIG:
        print(f"Usage: python {sys.argv[0]} <domain>")
        print(f"Available: {list(DOMAIN_CONFIG.keys())}")
        sys.exit(1)

    domain = sys.argv[1]
    print(f"=== ARIMA rolling-origin: {domain} ===")

    pred_df = run_arima_rolling_origin(domain)
    pred_df.to_csv(RESULTS_DIR / f"{domain}_arima_predictions_all.csv", index=False)
    print(f"Saved {domain}_arima_predictions_all.csv ({len(pred_df)} rows)")

    skill_df = compute_skill_from_predictions(pred_df)
    print("\nSkill by horizon:")
    print(skill_df[["horizon", "n_origins", "mae_model", "mae_baseline", "skill"]].to_string(index=False))

    dm_df = run_dm_tests(pred_df, domain)
    update_results_tables(domain, skill_df, dm_df)
    print(f"\nDone: {domain} ARIMA.")
