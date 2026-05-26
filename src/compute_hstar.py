"""Compute H*(relax) and H*(strict) descriptors from a skill curve."""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path


def compute_hstar(skill_series: pd.Series, horizons: list[int]) -> dict:
    """
    Compute H* descriptors from a skill curve.

    Parameters
    ----------
    skill_series : pd.Series
        Skill values indexed by horizon (or aligned to horizons list).
    horizons : list[int]
        Ordered list of horizon values.

    Returns
    -------
    dict with keys:
        h_relax, h_strict, h_start, h_end, n_sign_changes
    """
    s = np.asarray(skill_series, dtype=float)
    h = np.asarray(horizons, dtype=int)
    positive = s > 0

    # h_relax: max horizon with skill > 0 (allowing gaps)
    pos_indices = np.where(positive)[0]
    h_relax = int(h[pos_indices[-1]]) if len(pos_indices) > 0 else 0

    # Find all contiguous positive intervals
    best_len = 0
    best_start = 0
    best_end = 0
    cur_len = 0
    cur_start = 0
    for i, p in enumerate(positive):
        if p:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            if cur_len > best_len:
                best_len = cur_len
                best_start = cur_start
                best_end = i
        else:
            cur_len = 0

    h_strict = int(h[best_end] - h[best_start] + 1) if best_len > 0 else 0
    h_start = int(h[best_start]) if best_len > 0 else 0
    h_end = int(h[best_end]) if best_len > 0 else 0

    # Sign changes: count transitions positive→non-positive or vice versa
    n_sign_changes = int(np.sum(np.diff(positive.astype(int)) != 0))

    return {
        "h_relax": h_relax,
        "h_strict": h_strict,
        "h_start": h_start,
        "h_end": h_end,
        "n_sign_changes": n_sign_changes,
    }


def compute_hstar_from_skill_csv(
    skill_csv: Path | str,
    horizon_col: str = "horizon",
    skill_col: str = "skill",
    group_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Load skill CSV and compute H* for each group.

    Returns DataFrame with one row per group plus H* columns.
    """
    df = pd.read_csv(skill_csv)
    if group_cols is None:
        group_cols = [c for c in ["domain", "model"] if c in df.columns]

    rows = []
    if group_cols:
        for keys, g in df.groupby(group_cols):
            g_sorted = g.sort_values(horizon_col)
            horizons = g_sorted[horizon_col].tolist()
            skill = g_sorted[skill_col]
            result = compute_hstar(skill, horizons)
            key_dict = dict(zip(group_cols, keys if isinstance(keys, tuple) else [keys]))
            rows.append({**key_dict, **result})
    else:
        df_sorted = df.sort_values(horizon_col)
        result = compute_hstar(df_sorted[skill_col], df_sorted[horizon_col].tolist())
        rows.append(result)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    RESULTS_DIR = Path("results")

    skill_files = [
        ("pm25_skill_all.csv", "pm25"),
        ("load_skill_all.csv", "load"),
        ("wind_skill_all.csv", "wind"),
        ("traffic_skill_all.csv", "traffic"),
        # Legacy ARIMA results (single model, no domain col → add manually)
        ("wind_arima_skill.csv", "wind"),
        ("traffic_arima_skill.csv", "traffic"),
    ]

    all_rows = []
    for fname, domain in skill_files:
        fpath = RESULTS_DIR / fname
        if not fpath.exists():
            print(f"  SKIP (not found): {fpath}")
            continue

        df = pd.read_csv(fpath)
        # Ensure domain column
        if "domain" not in df.columns:
            df["domain"] = domain
        # Ensure model column
        if "model" not in df.columns:
            if "arima" in fname:
                df["model"] = "arima"
            else:
                df["model"] = "unknown"

        for (dom, model), g in df.groupby(["domain", "model"]):
            g_sorted = g.sort_values("horizon")
            horizons = g_sorted["horizon"].tolist()
            skill = g_sorted["skill"]
            result = compute_hstar(skill, horizons)
            all_rows.append({"domain": dom, "model": model, **result})

    out = pd.DataFrame(all_rows)
    out_path = RESULTS_DIR / "hstar_all_domains.csv"
    out.to_csv(out_path, index=False)
    print(f"Saved {len(out)} rows to {out_path}")
    print(out.to_string(index=False))
