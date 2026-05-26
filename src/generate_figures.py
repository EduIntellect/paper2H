"""Regenerate main figures from unified results (Steps 9 of Plan B)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

RESULTS_DIR = Path("results")
FIG_DIR = Path("figures/overleaf_export")
FIG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_COLORS = {
    "lightgbm":  "#1f77b4",
    "ridge":     "#ff7f0e",
    "extratrees":"#2ca02c",
    "arima":     "#9467bd",
    "unknown":   "#8c564b",
}
MODEL_LABELS = {
    "lightgbm":   "LightGBM",
    "ridge":      "Ridge",
    "extratrees": "ExtraTrees",
    "arima":      "ARIMA",
}

DOMAIN_LABELS = {
    "pm25":    "PM2.5",
    "load":    "Electric Load",
    "wind":    "Wind Speed",
    "traffic": "Traffic Flow",
}


def _load_skill(domain: str) -> pd.DataFrame | None:
    path = RESULTS_DIR / f"{domain}_skill_all.csv"
    if path.exists():
        df = pd.read_csv(path)
        if "domain" not in df.columns:
            df["domain"] = domain
        return df
    return None


def _load_hstar(domain: str, model: str, hstar_df: pd.DataFrame) -> dict:
    row = hstar_df[(hstar_df["domain"] == domain) & (hstar_df["model"] == model)]
    if row.empty:
        return {}
    return row.iloc[0].to_dict()


def plot_skill_domain(domain: str, skill_df: pd.DataFrame, hstar_df: pd.DataFrame,
                      dm_df: pd.DataFrame | None) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))

    models = skill_df["model"].unique()

    for model in sorted(models):
        sub = skill_df[skill_df["model"] == model].sort_values("horizon")
        horizons = sub["horizon"].values
        skill = sub["skill"].values
        color = MODEL_COLORS.get(model, "#333333")
        label = MODEL_LABELS.get(model, model)

        # DM significance markers
        if dm_df is not None:
            dm_sub = dm_df[(dm_df["domain"] == domain) & (dm_df["model"] == model)]
            dm_sub = dm_sub.set_index("horizon")
            sig = [
                dm_sub.loc[h, "significant_bh"]
                if h in dm_sub.index and pd.notna(dm_sub.loc[h, "significant_bh"])
                else False
                for h in horizons
            ]
        else:
            sig = [False] * len(horizons)

        sig_arr = np.array(sig, dtype=bool)
        ax.plot(horizons, skill, color=color, lw=1.5, label=label, zorder=3)

        if sig_arr.any():
            ax.scatter(horizons[sig_arr], skill[sig_arr],
                       color=color, marker="o", s=28, zorder=4)
        if (~sig_arr).any():
            ax.scatter(horizons[~sig_arr], skill[~sig_arr],
                       edgecolors=color, facecolors="none", marker="o", s=28, zorder=4)

        # H*(strict) shaded band per model
        hs = _load_hstar(domain, model, hstar_df)
        if hs.get("h_strict", 0) > 0:
            ax.axvspan(hs["h_start"] - 0.5, hs["h_end"] + 0.5,
                       alpha=0.07, color=color, zorder=1)

    ax.axhline(0, color="black", lw=1, ls="--", label="Persistence baseline")
    ax.set_xlabel("Forecast horizon (h)")
    ax.set_ylabel("Skill score")
    ax.set_title(DOMAIN_LABELS.get(domain, domain))
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)

    for ext in ["pdf", "png"]:
        fpath = FIG_DIR / f"fig_skill_{domain}.{ext}"
        fig.savefig(fpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved fig_skill_{domain}.pdf/.png")


def plot_hstar_heatmap(hstar_df: pd.DataFrame, dm_df: pd.DataFrame | None) -> None:
    if dm_df is not None:
        sig_pct = (
            dm_df.groupby(["domain", "model"])["significant_bh"]
            .mean()
            .mul(100)
            .rename("pct_sig")
            .reset_index()
        )
        df = hstar_df.merge(sig_pct, on=["domain", "model"], how="left")
    else:
        df = hstar_df.copy()
        df["pct_sig"] = np.nan

    df["row_label"] = df["domain"] + " / " + df["model"]
    df = df.sort_values(["domain", "model"])

    cols = ["h_relax", "h_strict", "pct_sig"]
    col_labels = ["H*(relax)", "H*(strict)", "% sign. DM"]
    data = df[cols].values.astype(float)

    fig, ax = plt.subplots(figsize=(6, max(3, len(df) * 0.5 + 1.5)))
    vmax_col = [data[:, i].max() for i in range(3)]

    im = ax.imshow(data, aspect="auto", cmap="YlGn",
                   vmin=0, vmax=max(vmax_col) if max(vmax_col) > 0 else 1)

    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(col_labels, fontsize=10)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["row_label"].values, fontsize=9)

    for i in range(len(df)):
        for j in range(len(cols)):
            val = data[i, j]
            txt = f"{val:.0f}" if not np.isnan(val) else "—"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9,
                    color="black" if val < 0.6 * (vmax_col[j] or 1) else "white")

    ax.set_title("H* descriptors & DM significance by domain × model")
    plt.colorbar(im, ax=ax, fraction=0.04)
    fig.tight_layout()

    for ext in ["pdf", "png"]:
        fpath = FIG_DIR / f"fig_hstar_heatmap.{ext}"
        fig.savefig(fpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  Saved fig_hstar_heatmap.pdf/.png")


if __name__ == "__main__":
    # Load shared tables
    hstar_path = RESULTS_DIR / "hstar_all_domains.csv"
    hstar_df = pd.read_csv(hstar_path) if hstar_path.exists() else pd.DataFrame()

    dm_path = RESULTS_DIR / "dm_tests_all.csv"
    dm_df = pd.read_csv(dm_path) if dm_path.exists() else None

    domains = ["pm25", "load", "wind", "traffic"]
    for domain in domains:
        skill_df = _load_skill(domain)
        if skill_df is None:
            print(f"  SKIP {domain}: no skill CSV found")
            continue
        print(f"Plotting {domain}...")
        plot_skill_domain(domain, skill_df, hstar_df, dm_df)

    print("Plotting H* heatmap...")
    if not hstar_df.empty:
        plot_hstar_heatmap(hstar_df, dm_df)
    else:
        print("  SKIP heatmap: no H* data")

    print("\nAll figures done.")
