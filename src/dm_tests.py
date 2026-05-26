"""Diebold-Mariano test (Harvey-Leybourne-Newbold modified) for forecast evaluation."""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats


def dm_test(
    errors_model: np.ndarray,
    errors_baseline: np.ndarray,
    h: int = 1,
) -> tuple[float, float]:
    """
    Harvey-Leybourne-Newbold modified DM test (two-sided).

    Positive DM statistic → model is better than baseline (lower errors).
    Returns (dm_statistic, p_value).
    """
    errors_model = np.asarray(errors_model, dtype=float)
    errors_baseline = np.asarray(errors_baseline, dtype=float)

    d = errors_baseline - errors_model  # positive when model wins
    n = len(d)
    if n < 2:
        return float("nan"), float("nan")

    d_mean = np.mean(d)
    gamma0 = np.var(d, ddof=0)

    # Autocovariance lags 1..h-1
    gammas = []
    for k in range(1, h):
        gk = np.mean((d[k:] - d_mean) * (d[:-k] - d_mean))
        gammas.append(gk)

    var_d = (gamma0 + 2 * sum(gammas)) / n
    if var_d <= 0:
        return float("nan"), float("nan")

    # HLN correction factor
    correction = np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    dm_stat = (d_mean / np.sqrt(var_d)) * correction
    p_val = 2 * (1 - stats.t.cdf(abs(dm_stat), df=n - 1))
    return float(dm_stat), float(p_val)


def benjamini_hochberg(p_values: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """BH FDR correction. Returns array of adjusted p-values."""
    n = len(p_values)
    if n == 0:
        return np.array([])
    order = np.argsort(p_values)
    ranks = np.empty(n)
    ranks[order] = np.arange(1, n + 1)
    adjusted = p_values * n / ranks
    # Enforce monotonicity (from largest rank down)
    adj = np.copy(adjusted[order])
    for i in range(n - 2, -1, -1):
        adj[i] = min(adj[i], adj[i + 1])
    result = np.empty(n)
    result[order] = adj
    return np.minimum(result, 1.0)


if __name__ == "__main__":
    RESULTS_DIR = Path("results")

    # Load per-origin predictions for all domains
    domains = ["pm25", "load", "wind", "traffic"]
    all_rows = []

    for domain in domains:
        pred_file = RESULTS_DIR / f"{domain}_predictions_all.csv"
        if not pred_file.exists():
            print(f"  SKIP (not found): {pred_file}")
            continue

        df = pd.read_csv(pred_file)
        print(f"Processing {domain}: {len(df)} rows")

        domain_rows = []
        for (model, h), g in df.groupby(["model", "horizon"]):
            errs_m = g["abs_error_model"].values
            errs_b = g["abs_error_baseline"].values
            n_valid = len(errs_m)
            dm_stat, p_val = dm_test(errs_m, errs_b, h=int(h))
            domain_rows.append({
                "domain": domain,
                "model": model,
                "horizon": h,
                "n_origins": n_valid,
                "dm_stat": dm_stat,
                "p_value": p_val,
            })

        # BH correction per domain
        domain_df = pd.DataFrame(domain_rows)
        pvals = domain_df["p_value"].values
        finite_mask = np.isfinite(pvals)
        bh_pvals = np.full(len(pvals), np.nan)
        if finite_mask.sum() > 0:
            bh_pvals[finite_mask] = benjamini_hochberg(pvals[finite_mask])
        domain_df["p_value_bh"] = bh_pvals
        domain_df["significant_bh"] = bh_pvals < 0.05
        all_rows.append(domain_df)

    if all_rows:
        result = pd.concat(all_rows, ignore_index=True)
        out_path = RESULTS_DIR / "dm_tests_all.csv"
        result.to_csv(out_path, index=False)
        print(f"\nSaved {len(result)} rows to {out_path}")
        # Summary
        sig = result.groupby("domain")["significant_bh"].mean() * 100
        print("\n% significant horizons per domain:")
        print(sig.round(1).to_string())
    else:
        print("No prediction files found.")
