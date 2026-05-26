from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
EXPORT_DIR = ROOT / "figures" / "overleaf_export"


def setup_style() -> None:
    plt.style.use("default")
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.edgecolor": "0.15",
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def load_skill(csv_name: str) -> pd.DataFrame:
    df = pd.read_csv(RESULTS_DIR / csv_name)
    if not {"horizon", "skill"}.issubset(df.columns):
        raise ValueError(f"{csv_name} must contain horizon and skill columns")
    df = df.copy()
    df["horizon"] = pd.to_numeric(df["horizon"], errors="raise")
    df["skill"] = pd.to_numeric(df["skill"], errors="raise")
    return df.sort_values("horizon")


def longest_positive_interval(df: pd.DataFrame) -> tuple[int, int] | None:
    intervals: list[tuple[int, int]] = []
    start: int | None = None
    horizons = df["horizon"].astype(int).tolist()
    skills = df["skill"].tolist()
    for h, s in zip(horizons, skills):
        if s > 0 and start is None:
            start = h
        elif s <= 0 and start is not None:
            intervals.append((start, h - 1))
            start = None
    if start is not None:
        intervals.append((start, horizons[-1]))
    if not intervals:
        return None
    return max(intervals, key=lambda t: (t[1] - t[0] + 1, -t[0]))


def hstar_relax(df: pd.DataFrame) -> int:
    positive = df.loc[df["skill"] > 0, "horizon"]
    return int(positive.max()) if not positive.empty else 0


def hstar_strict(df: pd.DataFrame) -> int:
    interval = longest_positive_interval(df)
    return interval[1] - interval[0] + 1 if interval else 0


def plot_skill_curve(
    csv_name: str,
    output_name: str,
    x_label: str,
    annotate_hstar: bool = True,
) -> None:
    df = load_skill(csv_name)
    interval = longest_positive_interval(df)
    relax = hstar_relax(df)

    fig, ax = plt.subplots(figsize=(6.0, 3.7))
    ax.plot(df["horizon"], df["skill"], color="black")
    ax.axhline(0.0, color="0.45", linestyle="--", linewidth=1.0)

    if interval:
        subset = df[(df["horizon"] >= interval[0]) & (df["horizon"] <= interval[1])]
        ax.plot(subset["horizon"], subset["skill"], color="black", linewidth=2.3)
        ax.axvspan(interval[0], interval[1], color="0.92", zorder=0)
        if annotate_hstar:
            y_text = max(df["skill"].max() * 0.82, 0.02)
            ax.text(
                interval[0],
                y_text,
                f"[h_start, h_end] = [{interval[0]}, {interval[1]}]",
                fontsize=8.7,
                ha="left",
                va="center",
            )
            ax.text(
                relax,
                y_text * 0.82,
                r"$H^*_{\mathrm{relax}}$" + f" = {relax}",
                fontsize=8.7,
                ha="right",
                va="center",
            )

    ax.set_xlabel(x_label)
    ax.set_ylabel("Skill(h)")
    ax.set_xlim(df["horizon"].min(), df["horizon"].max())
    y_min = min(df["skill"].min() - 0.05, -0.05)
    y_max = max(df["skill"].max() + 0.05, 0.08)
    ax.set_ylim(y_min, y_max)
    ax.margins(x=0.01)
    fig.tight_layout()
    fig.savefig(EXPORT_DIR / output_name, bbox_inches="tight")
    plt.close(fig)


def plot_hstar_conceptual() -> None:
    horizons = list(range(1, 13))
    skill = [-0.18, 0.14, 0.12, -0.04, 0.10, 0.13, 0.11, -0.03, 0.06, -0.02, 0.08, 0.05]
    df = pd.DataFrame({"horizon": horizons, "skill": skill})
    interval = longest_positive_interval(df)
    relax = hstar_relax(df)
    strict = hstar_strict(df)
    fragmented = [(2, 3), (5, 7), (9, 9), (11, 12)]

    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    ax.plot(df["horizon"], df["skill"], color="black", marker="o", markersize=3.6)
    ax.axhline(0.0, color="0.45", linestyle="--", linewidth=1.0)
    ax.axvspan(interval[0], interval[1], color="0.92", zorder=0)

    for start, end in fragmented:
        if (start, end) != interval:
            ax.hlines(-0.12, start, end, color="0.25", linewidth=2.2)

    ax.annotate(
        r"$H^*_{\mathrm{relax}}$",
        xy=(relax, df.loc[df["horizon"] == relax, "skill"].iloc[0]),
        xytext=(relax - 1.2, 0.19),
        arrowprops={"arrowstyle": "->", "lw": 0.9, "color": "0.2"},
        fontsize=9,
        ha="right",
    )
    ax.annotate(
        "Longest contiguous positive interval",
        xy=((interval[0] + interval[1]) / 2, 0.02),
        xytext=(4.6, 0.26),
        arrowprops={"arrowstyle": "->", "lw": 0.9, "color": "0.2"},
        fontsize=9,
        ha="center",
    )
    ax.annotate(
        r"$H^*_{\mathrm{strict}}$" + f" = {strict}",
        xy=(interval[1], -0.055),
        xytext=(8.5, -0.21),
        arrowprops={"arrowstyle": "->", "lw": 0.9, "color": "0.2"},
        fontsize=9,
        ha="left",
    )
    ax.text(1.05, -0.16, "Fragmented positive intervals", fontsize=8.7, ha="left")
    ax.text(5.0, -0.055, f"[h_start, h_end] = [{interval[0]}, {interval[1]}]", fontsize=8.7, ha="center")

    ax.set_xlabel("Forecast horizon h")
    ax.set_ylabel("Skill(h)")
    ax.set_xlim(1, 12)
    ax.set_ylim(-0.26, 0.31)
    ax.set_xticks(horizons)
    fig.tight_layout()
    fig.savefig(EXPORT_DIR / "fig_hstar_conceptual.pdf", bbox_inches="tight")
    plt.close(fig)


def add_box(ax, x: float, y: float, w: float, h: float, text: str) -> None:
    rect = Rectangle((x, y), w, h, facecolor="white", edgecolor="0.15", linewidth=0.9)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)


def add_arrow(ax, x1: float, y1: float, x2: float, y2: float) -> None:
    arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->", mutation_scale=10, linewidth=0.9, color="0.2")
    ax.add_patch(arrow)


def plot_rolling_origin_protocol() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")

    add_box(ax, 0.5, 1.45, 1.9, 0.6, "Train window")
    add_box(ax, 2.8, 1.45, 2.1, 0.6, "Train-only preprocessing")
    add_box(ax, 5.3, 1.45, 1.5, 0.6, "Forecast origin")
    add_box(ax, 7.2, 1.45, 1.8, 0.6, "h-step prediction")
    add_arrow(ax, 2.4, 1.75, 2.8, 1.75)
    add_arrow(ax, 4.9, 1.75, 5.3, 1.75)
    add_arrow(ax, 6.8, 1.75, 7.2, 1.75)

    ax.text(5.9, 0.8, "Roll origin forward", fontsize=9, ha="center")
    add_arrow(ax, 5.9, 1.2, 5.9, 0.95)
    add_arrow(ax, 5.9, 0.6, 1.45, 0.6)
    add_arrow(ax, 1.45, 0.6, 1.45, 1.35)

    ax.text(1.45, 2.3, "Past only", fontsize=8.7, ha="center")
    ax.text(8.1, 2.3, "Future target at horizon h", fontsize=8.7, ha="center")

    fig.tight_layout()
    fig.savefig(EXPORT_DIR / "fig_rolling_origin_protocol.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_cross_domain_summary() -> None:
    domains = [
        ("PM2.5", "results/pm25_real_skill.csv"),
        ("Load", "results/uci_energy_lightgbm_skill.csv"),
        ("Wind", "results/wind_skill.csv"),
        ("Traffic", "results/traffic_skill.csv"),
    ]
    rows = []
    for label, csv_path in domains:
        df = pd.read_csv(ROOT / csv_path)
        rows.append(
            {
                "domain": label,
                "relax": hstar_relax(df),
                "strict": hstar_strict(df),
            }
        )

    summary = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    x = range(len(summary))
    width = 0.34
    ax.bar([i - width / 2 for i in x], summary["relax"], width=width, color="white", edgecolor="black", linewidth=0.9)
    ax.bar([i + width / 2 for i in x], summary["strict"], width=width, color="0.75", edgecolor="black", linewidth=0.9)
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary["domain"])
    ax.set_ylabel("Horizon length")
    ax.legend([r"$H^*_{\mathrm{relax}}$", r"$H^*_{\mathrm{strict}}$"], frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(EXPORT_DIR / "fig_cross_domain_hstar_summary.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    setup_style()
    plot_hstar_conceptual()
    plot_rolling_origin_protocol()
    plot_skill_curve("pm25_real_skill.csv", "fig_skill_pm25.pdf", "Forecast horizon h")
    plot_skill_curve("uci_energy_lightgbm_skill.csv", "fig_skill_load.pdf", "Forecast horizon h (days)")
    plot_skill_curve("wind_skill.csv", "fig_skill_wind.pdf", "Forecast horizon h")
    plot_skill_curve("traffic_skill.csv", "fig_skill_traffic.pdf", "Forecast horizon h")
    plot_cross_domain_summary()


if __name__ == "__main__":
    main()
