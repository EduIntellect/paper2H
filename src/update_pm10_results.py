"""Append PM10 to H*, DM, unified table, and hstar_summary. Steps 3-4 of PM10 add-on."""
from __future__ import annotations

import sys
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compute_hstar import compute_hstar
from dm_tests import dm_test, benjamini_hochberg

RESULTS_DIR = Path("results")
DOMAIN = "pm10"
H_MAX = 7  # max horizon for PM10


# ── Step 3a: H* for PM10 ────────────────────────────────────────────────────
def update_hstar():
    skill_path = RESULTS_DIR / "pm10_skill_all.csv"
    hstar_path = RESULTS_DIR / "hstar_all_domains.csv"

    df = pd.read_csv(skill_path)
    if "domain" not in df.columns:
        df["domain"] = DOMAIN

    new_rows = []
    for (dom, model), g in df.groupby(["domain", "model"]):
        g_sorted = g.sort_values("horizon")
        result = compute_hstar(g_sorted["skill"], g_sorted["horizon"].tolist())
        new_rows.append({"domain": dom, "model": model, **result})

    new_df = pd.DataFrame(new_rows)

    if hstar_path.exists():
        existing = pd.read_csv(hstar_path)
        existing = existing[existing["domain"] != DOMAIN]
        combined = pd.concat([existing, new_df], ignore_index=True)
    else:
        combined = new_df

    combined.to_csv(hstar_path, index=False)
    print(f"H* updated ({len(combined)} rows) → {hstar_path}")
    print(new_df.to_string(index=False))
    return new_df


# ── Step 3b: DM tests for PM10 ──────────────────────────────────────────────
def update_dm():
    pred_path = RESULTS_DIR / "pm10_predictions_all.csv"
    dm_path = RESULTS_DIR / "dm_tests_all.csv"

    df = pd.read_csv(pred_path)
    print(f"Processing {DOMAIN}: {len(df)} rows")

    domain_rows = []
    for (model, h), g in df.groupby(["model", "horizon"]):
        errs_m = g["abs_error_model"].values
        errs_b = g["abs_error_baseline"].values
        dm_stat, p_val = dm_test(errs_m, errs_b, h=int(h))
        domain_rows.append({
            "domain": DOMAIN, "model": model, "horizon": h,
            "n_origins": len(g), "dm_stat": dm_stat, "p_value": p_val,
        })

    domain_df = pd.DataFrame(domain_rows)
    pvals = domain_df["p_value"].values
    finite_mask = np.isfinite(pvals)
    bh_pvals = np.full(len(pvals), np.nan)
    if finite_mask.sum() > 0:
        bh_pvals[finite_mask] = benjamini_hochberg(pvals[finite_mask])
    domain_df["p_value_bh"] = bh_pvals
    domain_df["significant_bh"] = bh_pvals < 0.05

    if dm_path.exists():
        existing = pd.read_csv(dm_path)
        existing = existing[existing["domain"] != DOMAIN]
        combined = pd.concat([existing, domain_df], ignore_index=True)
    else:
        combined = domain_df

    combined.to_csv(dm_path, index=False)
    print(f"DM tests updated ({len(combined)} rows) → {dm_path}")

    sig_pct = domain_df["significant_bh"].mean() * 100
    print(f"  PM10 % significant DM: {sig_pct:.1f}%")
    return domain_df


# ── Step 3c-d: Rebuild unified table and hstar_summary ──────────────────────
def rebuild_unified():
    # Load all skill tables
    domains = ["pm25", "load", "wind", "traffic", "pm10"]
    skill_dfs = []
    for d in domains:
        p = RESULTS_DIR / f"{d}_skill_all.csv"
        if p.exists():
            df = pd.read_csv(p)
            if "domain" not in df.columns:
                df["domain"] = d
            skill_dfs.append(df)

    skill_all = pd.concat(skill_dfs, ignore_index=True)
    hstar = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    # Join
    merged = skill_all.merge(
        dm[["domain","model","horizon","n_origins","dm_stat","p_value","p_value_bh","significant_bh"]],
        on=["domain","model","horizon"], how="left",
    ).merge(
        hstar[["domain","model","h_relax","h_strict","h_start","h_end","n_sign_changes"]],
        on=["domain","model"], how="left",
    )
    merged.to_csv(RESULTS_DIR / "unified_results_table.csv", index=False)
    print(f"Unified table: {len(merged)} rows → results/unified_results_table.csv")

    # H* summary with taxonomy
    h_max_map = {"pm25": 48, "load": 7, "wind": 48, "traffic": 72, "pm10": 7}
    sig_pct = (
        dm.groupby(["domain","model"])["significant_bh"]
        .mean().mul(100).rename("pct_horizons_significant").reset_index()
    )
    summary = hstar.merge(sig_pct, on=["domain","model"], how="left")

    def classify(row):
        h_max = h_max_map.get(row["domain"], 48)
        h_relax, h_strict = row["h_relax"], row["h_strict"]
        if h_relax <= 1:
            return "IMMEDIATE_COLLAPSE"
        if h_strict == h_relax == h_max:
            return "SUSTAINED"
        if h_strict >= h_relax * 0.5 and row["h_start"] >= h_max * 0.25:
            return "DELAYED_CONTIGUOUS"
        return "FRAGMENTED"

    summary["profile_type"] = summary.apply(classify, axis=1)
    summary.to_csv(RESULTS_DIR / "hstar_summary.csv", index=False)

    print(f"\nH* summary ({len(summary)} rows) → results/hstar_summary.csv")
    print(summary.to_string(index=False))

    print("\n=== Profile classification ===")
    for _, row in summary.iterrows():
        print(f"  {row['domain']:10s} {row['model']:12s}  "
              f"h_relax={row['h_relax']:3d}  h_strict={row['h_strict']:3d}  "
              f"→ {row['profile_type']}")
    return summary


if __name__ == "__main__":
    print("=== Step 3a: H* for PM10 ===")
    update_hstar()
    print("\n=== Step 3b: DM tests for PM10 ===")
    update_dm()
    print("\n=== Step 3c-d: Rebuild unified table ===")
    rebuild_unified()
