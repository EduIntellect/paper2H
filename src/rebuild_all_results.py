"""Rebuild hstar_summary, unified table, and all figures after adding new models.

Run this once all domains have completed with the new models.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from compute_hstar import compute_hstar

RESULTS_DIR = Path("results")
FIG_DIR = Path("figures/overleaf_export")
FIG_DIR.mkdir(parents=True, exist_ok=True)

DOMAINS_ORDER = ["pm25", "load", "wind", "traffic", "pm10", "pm10_bcn"]

H_MAX_MAP = {"pm25": 48, "load": 7, "wind": 48, "traffic": 72,
             "pm10": 7, "pm10_bcn": 7}

COLORS = {
    "ridge":      "#E07B39",
    "lightgbm":   "#3B7DD8",
    "extratrees": "#4CAF50",
    "knn":        "#9C27B0",
    "mlp":        "#F44336",
    "tcn":        "#795548",
    "arima":      "#9467bd",
}
LINESTYLES = {
    "ridge": "-", "lightgbm": "-", "extratrees": "-",
    "knn": "--", "mlp": "--", "tcn": "-.", "arima": ":",
}
LABELS = {
    "ridge": "Ridge", "lightgbm": "LightGBM", "extratrees": "ExtraTrees",
    "knn": "KNN", "mlp": "MLP", "tcn": "TCN", "arima": "ARIMA(2,0,0)",
}
DOMAIN_TITLES = {
    "pm25":     "PM2.5 (Beijing, hourly)",
    "load":     "Electric Load (UCI, daily)",
    "wind":     "Wind Speed (NREL, hourly)",
    "traffic":  "Traffic (METR-LA, hourly)",
    "pm10":     "PM10 Madrid (Casa de Campo, daily)",
    "pm10_bcn": "PM10 Barcelona (Eixample, daily)",
}

MODEL_ORDER = ["ridge", "lightgbm", "extratrees", "knn", "mlp", "tcn", "arima"]


def classify(row):
    h_max = H_MAX_MAP.get(row["domain"], 48)
    hr, hs = row["h_relax"], row["h_strict"]
    if hr <= 1:
        return "IMMEDIATE_COLLAPSE"
    if hs == hr == h_max:
        return "SUSTAINED"
    if hs >= hr * 0.5 and row["h_start"] >= h_max * 0.25:
        return "DELAYED_CONTIGUOUS"
    return "FRAGMENTED"


def rebuild_hstar_summary():
    hstar = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    sig_pct = (dm.groupby(["domain", "model"])["significant_bh"]
               .mean().mul(100).rename("pct_horizons_significant").reset_index())
    summary = hstar.merge(sig_pct, on=["domain", "model"], how="left")
    summary["profile_type"] = summary.apply(classify, axis=1)
    summary.to_csv(RESULTS_DIR / "hstar_summary.csv", index=False)
    print(f"hstar_summary.csv: {len(summary)} rows")

    # Print Table 3 equivalent
    dom_ord = {d: i for i, d in enumerate(DOMAINS_ORDER)}
    mod_ord = {m: i for i, m in enumerate(MODEL_ORDER)}
    summary["_do"] = summary["domain"].map(dom_ord)
    summary["_mo"] = summary["model"].map(mod_ord).fillna(99)
    summary = summary.sort_values(["_do", "_mo"]).drop(columns=["_do", "_mo"])

    print(f"\n{'='*95}")
    print("TABLE 3 EQUIVALENT — H* ALL DOMAINS × ALL MODELS")
    print('='*95)
    cols = ["domain", "model", "h_relax", "h_strict", "h_start", "h_end",
            "pct_horizons_significant", "profile_type"]
    print(summary[cols].to_string(index=False))
    return summary


def rebuild_unified_table():
    skill_dfs = []
    for d in DOMAINS_ORDER:
        p = RESULTS_DIR / f"{d}_skill_all.csv"
        if p.exists():
            df = pd.read_csv(p)
            if "domain" not in df.columns:
                df["domain"] = d
            skill_dfs.append(df)

    # Add ARIMA skill (from predictions files)
    for domain in ["wind", "traffic"]:
        arima_path = RESULTS_DIR / f"{domain}_arima_predictions_all.csv"
        if arima_path.exists():
            arima_pred = pd.read_csv(arima_path)
            rows = []
            for h, g in arima_pred.groupby("horizon"):
                mae_m = g["abs_error_model"].mean()
                mae_b = g["abs_error_baseline"].mean()
                sk = 1 - mae_m / mae_b if mae_b > 0 else np.nan
                rows.append({"domain": domain, "model": "arima", "horizon": h,
                             "n_origins": len(g), "mae_model": mae_m,
                             "mae_baseline": mae_b, "skill": sk})
            if rows:
                skill_dfs.append(pd.DataFrame(rows))

    skill_all = pd.concat(skill_dfs, ignore_index=True)
    hstar = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    merged = skill_all.merge(
        dm[["domain", "model", "horizon", "n_origins", "dm_stat",
            "p_value", "p_value_bh", "significant_bh"]],
        on=["domain", "model", "horizon"], how="left",
    ).merge(
        hstar[["domain", "model", "h_relax", "h_strict",
               "h_start", "h_end", "n_sign_changes"]],
        on=["domain", "model"], how="left",
    )
    merged.to_csv(RESULTS_DIR / "unified_results_table.csv", index=False)
    print(f"unified_results_table.csv: {len(merged)} rows")
    return skill_all


def regenerate_figures(skill_all: pd.DataFrame):
    hstar_df = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm_df = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    for domain in DOMAINS_ORDER:
        skill_df = skill_all[skill_all["domain"] == domain]
        if skill_df.empty:
            continue

        fig, ax = plt.subplots(figsize=(9, 5))
        # Plot in fixed order: original 3 solid, new models dashed
        models_present = [m for m in MODEL_ORDER if m in skill_df["model"].unique()]
        for model in models_present:
            sub = skill_df[skill_df["model"] == model].sort_values("horizon")
            hs = sub["horizon"].values
            sk = sub["skill"].values
            color = COLORS.get(model, "#888")
            ls = LINESTYLES.get(model, "-")
            label = LABELS.get(model, model)

            dm_sub = (dm_df[(dm_df["domain"] == domain) & (dm_df["model"] == model)]
                      .set_index("horizon"))
            sig = np.array([
                bool(dm_sub.loc[h, "significant_bh"])
                if h in dm_sub.index and pd.notna(dm_sub.loc[h, "significant_bh"])
                else False
                for h in hs
            ])

            ax.plot(hs, sk, color=color, lw=1.5, ls=ls, label=label, zorder=3)
            if sig.any():
                ax.scatter(hs[sig], sk[sig], color=color, marker="o", s=22, zorder=4)
            if (~sig).any():
                ax.scatter(hs[~sig], sk[~sig], edgecolors=color,
                           facecolors="none", marker="o", s=22, zorder=4)

            hs_row = hstar_df[(hstar_df["domain"] == domain) &
                              (hstar_df["model"] == model)]
            if not hs_row.empty and hs_row.iloc[0]["h_strict"] > 0:
                ax.axvspan(hs_row.iloc[0]["h_start"] - 0.3,
                           hs_row.iloc[0]["h_end"] + 0.3,
                           alpha=0.06, color=color, zorder=1)

        ax.axhline(0, color="black", lw=1, ls="--", label="Persistence")
        ax.set_xlabel("Forecast horizon")
        ax.set_ylabel("Skill score")
        ax.set_title(DOMAIN_TITLES.get(domain, domain))
        ax.legend(fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
        if domain in ("pm10", "pm10_bcn", "load"):
            ax.set_xticks(range(1, 8))
        # Clamp y-axis to [-1.5, 1] to prevent MLP/Load numerical instability from
        # collapsing the scale (MLP skill reaches -38 on Load due to unscaled targets)
        ymin, ymax = ax.get_ylim()
        if ymin < -1.5:
            ax.set_ylim(bottom=-1.5)
            ax.text(0.02, 0.03, "MLP axis clamped (min skill ≤ −16)",
                    transform=ax.transAxes, fontsize=7, color="gray")

        for ext in ["pdf", "png"]:
            fig.savefig(FIG_DIR / f"fig_skill_{domain}.{ext}",
                        dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  fig_skill_{domain}.pdf/.png")

    # H* heatmap — all models
    dm = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")
    hstar = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    sig_pct = (dm.groupby(["domain", "model"])["significant_bh"]
               .mean().mul(100).rename("pct_sig").reset_index())
    df = hstar.merge(sig_pct, on=["domain", "model"], how="left")
    dom_ord = {d: i for i, d in enumerate(DOMAINS_ORDER)}
    mod_ord = {m: i for i, m in enumerate(MODEL_ORDER)}
    df["_do"] = df["domain"].map(dom_ord)
    df["_mo"] = df["model"].map(mod_ord).fillna(99)
    df = df.sort_values(["_do", "_mo"]).drop(columns=["_do", "_mo"])
    df["row_label"] = df["domain"] + " / " + df["model"]
    data = df[["h_relax", "h_strict", "pct_sig"]].values.astype(float)
    col_labels = ["H*(relax)", "H*(strict)", "% sign. DM"]

    fig, ax = plt.subplots(figsize=(6.5, max(3, len(df) * 0.38 + 1.5)))
    vmax = np.nanmax(data) if not np.all(np.isnan(data)) else 1
    im = ax.imshow(data, aspect="auto", cmap="YlGn", vmin=0, vmax=vmax)
    ax.set_xticks(range(3))
    ax.set_xticklabels(col_labels, fontsize=10)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["row_label"].values, fontsize=7.5)
    for i in range(len(df)):
        for j in range(3):
            v = data[i, j]
            txt = f"{v:.0f}" if not np.isnan(v) else "—"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                    color="black" if v < 0.6 * vmax else "white")
    ax.set_title("H* descriptors & DM significance — all domains")
    plt.colorbar(im, ax=ax, fraction=0.04)
    fig.tight_layout()
    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"fig_hstar_heatmap.{ext}", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  fig_hstar_heatmap.pdf/.png")


if __name__ == "__main__":
    print("=== Rebuilding all results ===\n")
    summary = rebuild_hstar_summary()
    print()
    skill_all = rebuild_unified_table()
    print("\n=== Regenerating figures ===")
    regenerate_figures(skill_all)
    print("\nDone.")
