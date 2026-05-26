"""Build unified results table joining skill + H* + DM test results."""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

RESULTS_DIR = Path("results")


def classify_profile(row: pd.Series, h_max: int) -> str:
    """Classify domain×model into predictability profile."""
    h_relax = row["h_relax"]
    h_strict = row["h_strict"]

    if h_relax == 0 and h_strict == 0:
        return "IMMEDIATE_COLLAPSE"
    if h_relax <= 1:
        return "IMMEDIATE_COLLAPSE"
    if h_strict == h_relax == h_max:
        return "SUSTAINED"
    if (h_strict >= h_relax * 0.5
            and row["h_start"] >= h_max * 0.25):
        return "DELAYED_CONTIGUOUS"
    return "FRAGMENTED"


if __name__ == "__main__":
    # ── Load skill tables ────────────────────────────────────────────────
    skill_files = {
        "pm25": RESULTS_DIR / "pm25_skill_all.csv",
        "load": RESULTS_DIR / "load_skill_all.csv",
        "wind": RESULTS_DIR / "wind_skill_all.csv",
        "traffic": RESULTS_DIR / "traffic_skill_all.csv",
    }
    skill_dfs = []
    for domain, fpath in skill_files.items():
        if fpath.exists():
            df = pd.read_csv(fpath)
            if "domain" not in df.columns:
                df["domain"] = domain
            skill_dfs.append(df)
        else:
            print(f"  MISSING skill: {fpath}")

    skill_all = pd.concat(skill_dfs, ignore_index=True) if skill_dfs else pd.DataFrame()

    # ── Load H* table ────────────────────────────────────────────────────
    hstar_path = RESULTS_DIR / "hstar_all_domains.csv"
    hstar = pd.read_csv(hstar_path) if hstar_path.exists() else pd.DataFrame()

    # ── Load DM tests ────────────────────────────────────────────────────
    dm_path = RESULTS_DIR / "dm_tests_all.csv"
    dm = pd.read_csv(dm_path) if dm_path.exists() else pd.DataFrame()

    # ── Join ─────────────────────────────────────────────────────────────
    if not skill_all.empty and not dm.empty:
        merged = skill_all.merge(
            dm[["domain", "model", "horizon", "n_origins", "dm_stat",
                "p_value", "p_value_bh", "significant_bh"]],
            on=["domain", "model", "horizon"], how="left",
        )
    elif not skill_all.empty:
        merged = skill_all.copy()
    else:
        merged = pd.DataFrame()

    if not merged.empty and not hstar.empty:
        merged = merged.merge(
            hstar[["domain", "model", "h_relax", "h_strict",
                   "h_start", "h_end", "n_sign_changes"]],
            on=["domain", "model"], how="left",
        )

    if not merged.empty:
        out_path = RESULTS_DIR / "unified_results_table.csv"
        merged.to_csv(out_path, index=False)
        print(f"Unified table: {len(merged)} rows → {out_path}")

    # ── H* summary with taxonomy ─────────────────────────────────────────
    if not hstar.empty and not dm.empty:
        # pct_horizons_significant per domain×model
        sig_pct = (
            dm.groupby(["domain", "model"])["significant_bh"]
            .mean()
            .mul(100)
            .rename("pct_horizons_significant")
            .reset_index()
        )
        summary = hstar.merge(sig_pct, on=["domain", "model"], how="left")

        # Max horizon per domain
        h_max_map = {
            "pm25": 48, "load": 7, "wind": 48, "traffic": 72,
        }
        summary["profile_type"] = summary.apply(
            lambda r: classify_profile(r, h_max_map.get(r["domain"], 48)),
            axis=1,
        )

        out_path2 = RESULTS_DIR / "hstar_summary.csv"
        summary.to_csv(out_path2, index=False)
        print(f"\nH* summary ({len(summary)} rows) → {out_path2}")
        print(summary.to_string(index=False))

        print("\n=== Profile classification ===")
        for _, row in summary.iterrows():
            print(f"  {row['domain']:10s} {row['model']:12s}  "
                  f"h_relax={row['h_relax']:3d}  h_strict={row['h_strict']:3d}  "
                  f"→ {row['profile_type']}")
    elif not hstar.empty:
        # No DM data yet — just print H*
        h_max_map = {"pm25": 48, "load": 7, "wind": 48, "traffic": 72}
        hstar["pct_horizons_significant"] = np.nan
        hstar["profile_type"] = hstar.apply(
            lambda r: classify_profile(r, h_max_map.get(r["domain"], 48)), axis=1
        )
        out_path2 = RESULTS_DIR / "hstar_summary.csv"
        hstar.to_csv(out_path2, index=False)
        print(hstar.to_string(index=False))
