"""Append PM10_BCN to all results tables and regenerate figures."""
from __future__ import annotations

import sys, numpy as np, pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compute_hstar import compute_hstar
from dm_tests import dm_test, benjamini_hochberg

RESULTS_DIR = Path("results")
DOMAIN = "pm10_bcn"
H_MAX = 7

H_MAX_MAP = {"pm25": 48, "load": 7, "wind": 48, "traffic": 72,
             "pm10": 7, "pm10_bcn": 7}
DOMAINS_ORDER = ["pm25", "load", "wind", "traffic", "pm10", "pm10_bcn"]


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


def update_hstar():
    df = pd.read_csv(RESULTS_DIR / f"{DOMAIN}_skill_all.csv")
    if "domain" not in df.columns:
        df["domain"] = DOMAIN
    new_rows = []
    for (dom, model), g in df.groupby(["domain", "model"]):
        result = compute_hstar(g.sort_values("horizon")["skill"],
                               g.sort_values("horizon")["horizon"].tolist())
        new_rows.append({"domain": dom, "model": model, **result})
    new_df = pd.DataFrame(new_rows)

    existing = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    existing = existing[existing["domain"] != DOMAIN]
    combined = pd.concat([existing, new_df], ignore_index=True)
    combined.to_csv(RESULTS_DIR / "hstar_all_domains.csv", index=False)
    print(f"H* updated ({len(combined)} rows)")
    print(new_df.to_string(index=False))
    return new_df


def update_dm():
    df = pd.read_csv(RESULTS_DIR / f"{DOMAIN}_predictions_all.csv")
    print(f"DM for {DOMAIN}: {len(df)} rows")
    rows = []
    for (model, h), g in df.groupby(["model", "horizon"]):
        dm_stat, p_val = dm_test(g["abs_error_model"].values,
                                 g["abs_error_baseline"].values, h=int(h))
        rows.append({"domain": DOMAIN, "model": model, "horizon": h,
                     "n_origins": len(g), "dm_stat": dm_stat, "p_value": p_val})
    dm_df = pd.DataFrame(rows)
    pvals = dm_df["p_value"].values
    mask = np.isfinite(pvals)
    bh = np.full(len(pvals), np.nan)
    if mask.sum() > 0:
        bh[mask] = benjamini_hochberg(pvals[mask])
    dm_df["p_value_bh"] = bh
    dm_df["significant_bh"] = bh < 0.05

    existing = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")
    existing = existing[existing["domain"] != DOMAIN]
    combined = pd.concat([existing, dm_df], ignore_index=True)
    combined.to_csv(RESULTS_DIR / "dm_tests_all.csv", index=False)
    sig_pct = dm_df["significant_bh"].mean() * 100
    print(f"DM updated ({len(combined)} rows) | PM10_BCN % significant: {sig_pct:.1f}%")
    return dm_df


def rebuild_unified():
    skill_dfs = []
    for d in DOMAINS_ORDER:
        p = RESULTS_DIR / f"{d}_skill_all.csv"
        if p.exists():
            df = pd.read_csv(p)
            if "domain" not in df.columns:
                df["domain"] = d
            skill_dfs.append(df)

    skill_all = pd.concat(skill_dfs, ignore_index=True)
    hstar = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    merged = skill_all.merge(
        dm[["domain","model","horizon","n_origins","dm_stat",
            "p_value","p_value_bh","significant_bh"]],
        on=["domain","model","horizon"], how="left",
    ).merge(
        hstar[["domain","model","h_relax","h_strict","h_start","h_end","n_sign_changes"]],
        on=["domain","model"], how="left",
    )
    merged.to_csv(RESULTS_DIR / "unified_results_table.csv", index=False)
    print(f"Unified table: {len(merged)} rows")

    sig_pct = (dm.groupby(["domain","model"])["significant_bh"]
               .mean().mul(100).rename("pct_horizons_significant").reset_index())
    summary = hstar.merge(sig_pct, on=["domain","model"], how="left")
    summary["profile_type"] = summary.apply(classify, axis=1)
    summary.to_csv(RESULTS_DIR / "hstar_summary.csv", index=False)
    print(f"\n{'='*70}")
    print("H* SUMMARY — ALL DOMAINS")
    print('='*70)
    print(summary.to_string(index=False))
    return summary


def regenerate_figures(summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIG_DIR = Path("figures/overleaf_export")
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    COLORS = {"lightgbm":"#1f77b4","ridge":"#ff7f0e","extratrees":"#2ca02c","arima":"#9467bd"}
    LABELS = {"lightgbm":"LightGBM","ridge":"Ridge","extratrees":"ExtraTrees","arima":"ARIMA"}
    DOMAIN_TITLES = {"pm25":"PM2.5 (Beijing, hourly)","load":"Electric Load (UCI, daily)",
                     "wind":"Wind Speed (NREL, hourly)","traffic":"Traffic (METR-LA, hourly)",
                     "pm10":"PM10 Madrid (Casa de Campo, daily)",
                     "pm10_bcn":"PM10 Barcelona Eixample (daily)"}

    hstar_df = pd.read_csv(RESULTS_DIR / "hstar_all_domains.csv")
    dm_df = pd.read_csv(RESULTS_DIR / "dm_tests_all.csv")

    for domain in DOMAINS_ORDER:
        skill_path = RESULTS_DIR / f"{domain}_skill_all.csv"
        if not skill_path.exists():
            continue
        skill_df = pd.read_csv(skill_path)
        if "domain" not in skill_df.columns:
            skill_df["domain"] = domain

        fig, ax = plt.subplots(figsize=(8, 4.5))
        for model in sorted(skill_df["model"].unique()):
            sub = skill_df[skill_df["model"]==model].sort_values("horizon")
            hs = sub["horizon"].values
            sk = sub["skill"].values
            color = COLORS.get(model,"#333")
            label = LABELS.get(model, model)

            dm_sub = dm_df[(dm_df["domain"]==domain)&(dm_df["model"]==model)].set_index("horizon")
            sig = np.array([bool(dm_sub.loc[h,"significant_bh"])
                            if h in dm_sub.index and pd.notna(dm_sub.loc[h,"significant_bh"])
                            else False for h in hs])

            ax.plot(hs, sk, color=color, lw=1.5, label=label, zorder=3)
            if sig.any():
                ax.scatter(hs[sig], sk[sig], color=color, marker="o", s=28, zorder=4)
            if (~sig).any():
                ax.scatter(hs[~sig], sk[~sig], edgecolors=color, facecolors="none",
                           marker="o", s=28, zorder=4)

            hs_row = hstar_df[(hstar_df["domain"]==domain)&(hstar_df["model"]==model)]
            if not hs_row.empty and hs_row.iloc[0]["h_strict"] > 0:
                ax.axvspan(hs_row.iloc[0]["h_start"]-0.3, hs_row.iloc[0]["h_end"]+0.3,
                           alpha=0.07, color=color, zorder=1)

        ax.axhline(0, color="black", lw=1, ls="--", label="Persistence")
        ax.set_xlabel("Forecast horizon")
        ax.set_ylabel("Skill score")
        ax.set_title(DOMAIN_TITLES.get(domain, domain))
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        if domain in ("pm10","pm10_bcn","load"):
            ax.set_xticks(range(1, 8))

        for ext in ["pdf","png"]:
            fig.savefig(FIG_DIR / f"fig_skill_{domain}.{ext}", dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  fig_skill_{domain}.pdf/.png")

    # H* heatmap
    sig_pct = (dm_df.groupby(["domain","model"])["significant_bh"]
               .mean().mul(100).rename("pct_sig").reset_index())
    df = hstar_df.merge(sig_pct, on=["domain","model"], how="left")
    df["order"] = df["domain"].map({d:i for i,d in enumerate(DOMAINS_ORDER)})
    df = df.sort_values(["order","model"]).drop(columns="order")
    df["row_label"] = df["domain"] + " / " + df["model"]
    data = df[["h_relax","h_strict","pct_sig"]].values.astype(float)
    col_labels = ["H*(relax)","H*(strict)","% sign. DM"]

    fig, ax = plt.subplots(figsize=(6, max(3, len(df)*0.42+1.5)))
    vmax = np.nanmax(data) if not np.all(np.isnan(data)) else 1
    im = ax.imshow(data, aspect="auto", cmap="YlGn", vmin=0, vmax=vmax)
    ax.set_xticks(range(3))
    ax.set_xticklabels(col_labels, fontsize=10)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["row_label"].values, fontsize=8)
    for i in range(len(df)):
        for j in range(3):
            v = data[i,j]
            txt = f"{v:.0f}" if not np.isnan(v) else "—"
            ax.text(j,i,txt,ha="center",va="center",fontsize=8,
                    color="black" if v < 0.6*vmax else "white")
    ax.set_title("H* descriptors & DM significance — all domains")
    plt.colorbar(im, ax=ax, fraction=0.04)
    fig.tight_layout()
    for ext in ["pdf","png"]:
        fig.savefig(FIG_DIR / f"fig_hstar_heatmap.{ext}", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  fig_hstar_heatmap.pdf/.png")


if __name__ == "__main__":
    print("=== H* ==="); update_hstar()
    print("\n=== DM ==="); update_dm()
    print("\n=== Unified table ===")
    summary = rebuild_unified()
    print("\n=== Figures ===")
    regenerate_figures(summary)
    print("\nDone.")
