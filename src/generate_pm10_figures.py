"""Generate PM10-specific figures and rebuild H* heatmap (Step 4 of PM10 add-on)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path("results")
FIG_DIR = Path("figures/overleaf_export")
FIG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_COLORS = {
    "lightgbm":   "#1f77b4",
    "ridge":      "#ff7f0e",
    "extratrees": "#2ca02c",
    "arima":      "#9467bd",
}
MODEL_LABELS = {
    "lightgbm":   "LightGBM",
    "ridge":      "Ridge",
    "extratrees": "ExtraTrees",
    "arima":      "ARIMA",
}


def plot_skill_pm10():
    skill_df = pd.read_csv(RESULTS_DIR / "pm10_skill_all.csv")
    hstar_df = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm_df = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for model in sorted(skill_df["model"].unique()):
        sub = skill_df[skill_df["model"] == model].sort_values("horizon")
        horizons = sub["horizon"].values
        skill = sub["skill"].values
        color = MODEL_COLORS.get(model, "#333333")
        label = MODEL_LABELS.get(model, model)

        dm_sub = dm_df[(dm_df["domain"] == "pm10") & (dm_df["model"] == model)].set_index("horizon")
        sig = [
            bool(dm_sub.loc[h, "significant_bh"])
            if h in dm_sub.index and pd.notna(dm_sub.loc[h, "significant_bh"])
            else False
            for h in horizons
        ]
        sig_arr = np.array(sig)

        ax.plot(horizons, skill, color=color, lw=1.5, label=label, zorder=3)
        if sig_arr.any():
            ax.scatter(horizons[sig_arr], skill[sig_arr], color=color, marker="o", s=28, zorder=4)
        if (~sig_arr).any():
            ax.scatter(horizons[~sig_arr], skill[~sig_arr], edgecolors=color,
                       facecolors="none", marker="o", s=28, zorder=4)

        hs_row = hstar_df[(hstar_df["domain"] == "pm10") & (hstar_df["model"] == model)]
        if not hs_row.empty and hs_row.iloc[0]["h_strict"] > 0:
            ax.axvspan(hs_row.iloc[0]["h_start"] - 0.3, hs_row.iloc[0]["h_end"] + 0.3,
                       alpha=0.07, color=color, zorder=1)

    ax.axhline(0, color="black", lw=1, ls="--", label="Persistence baseline")
    ax.set_xlabel("Forecast horizon (days)")
    ax.set_ylabel("Skill score")
    ax.set_title("PM10 (Madrid, daily)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(1, 8))

    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"fig_skill_pm10.{ext}", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved fig_skill_pm10.pdf/.png")


def rebuild_heatmap():
    hstar_df = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm_df = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    sig_pct = (
        dm_df.groupby(["domain", "model"])["significant_bh"]
        .mean().mul(100).rename("pct_sig").reset_index()
    )
    df = hstar_df.merge(sig_pct, on=["domain", "model"], how="left")

    # Order domains
    domain_order = ["pm25", "load", "wind", "traffic", "pm10"]
    df["domain_order"] = df["domain"].map({d: i for i, d in enumerate(domain_order)})
    df = df.sort_values(["domain_order", "model"]).drop(columns="domain_order")

    df["row_label"] = df["domain"] + " / " + df["model"]
    cols = ["h_relax", "h_strict", "pct_sig"]
    col_labels = ["H*(relax)", "H*(strict)", "% sign. DM"]
    data = df[cols].values.astype(float)

    fig, ax = plt.subplots(figsize=(6, max(3, len(df) * 0.45 + 1.5)))
    vmax = np.nanmax(data) if not np.all(np.isnan(data)) else 1
    im = ax.imshow(data, aspect="auto", cmap="YlGn", vmin=0, vmax=vmax)

    ax.set_xticks(range(3))
    ax.set_xticklabels(col_labels, fontsize=10)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["row_label"].values, fontsize=9)

    for i in range(len(df)):
        for j in range(3):
            val = data[i, j]
            txt = f"{val:.0f}" if not np.isnan(val) else "—"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9,
                    color="black" if val < 0.6 * vmax else "white")

    ax.set_title("H* descriptors & DM significance — all domains")
    plt.colorbar(im, ax=ax, fraction=0.04)
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"fig_hstar_heatmap.{ext}", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved fig_hstar_heatmap.pdf/.png")


if __name__ == "__main__":
    plot_skill_pm10()
    rebuild_heatmap()
    print("Done.")
