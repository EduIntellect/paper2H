#!/usr/bin/env python3
"""Generate the two reviewer-requested conceptual figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


def conceptual_hstar(output: Path) -> None:
    horizons = list(range(1, 13))
    values = [-0.18, 0.14, 0.12, -0.04, 0.10, 0.13, 0.11, -0.03, 0.06, -0.02, 0.08, 0.05]
    longest = (5, 7)

    fig, ax = plt.subplots(figsize=(7.2, 4.25))
    ax.axhspan(0, 0.30, color="0.97", zorder=0)
    ax.axvspan(longest[0] - 0.15, longest[1] + 0.15, color="0.88", zorder=1)
    ax.axhline(0.0, color="0.4", linestyle="--", linewidth=1.0, zorder=2)
    ax.plot(horizons, values, color="black", marker="o", markersize=4, zorder=3)

    label_box = {"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "0.7", "alpha": 0.98}
    ax.annotate(
        r"Relaxed reach: $H^*(\mathrm{relax})=12$",
        xy=(12, values[-1]),
        xytext=(11.7, 0.255),
        ha="right",
        va="center",
        fontsize=9,
        bbox=label_box,
        arrowprops={"arrowstyle": "->", "lw": 0.9, "color": "0.2"},
    )
    ax.annotate(
        r"Longest positive interval $[5,7]$" "\n" r"$H^*(\mathrm{strict})=3$",
        xy=(6, 0.105),
        xytext=(6, 0.255),
        ha="center",
        va="center",
        fontsize=9,
        bbox=label_box,
        arrowprops={"arrowstyle": "->", "lw": 0.9, "color": "0.2"},
    )
    ax.text(
        1.25,
        -0.225,
        "Non-positive gaps may occur inside the relaxed reach;\n"
        "they are not themselves interpreted as skillful.",
        fontsize=8.7,
        ha="left",
        va="center",
        bbox=label_box,
    )

    ax.set_xlabel(r"Forecast horizon $h$")
    ax.set_ylabel(r"Skill$(h)$")
    ax.set_xlim(0.8, 12.2)
    ax.set_ylim(-0.30, 0.33)
    ax.set_xticks(horizons)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def add_box(ax, x: float, width: float, text: str) -> None:
    y, height = 1.35, 0.85
    ax.add_patch(Rectangle((x, y), width, height, facecolor="white", edgecolor="0.15", linewidth=1.0))
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=9, linespacing=1.2)


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=11, linewidth=1.0, color="0.2"))


def rolling_origin(output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 3.25))
    ax.set_xlim(0, 11.6)
    ax.set_ylim(0, 3.2)
    ax.axis("off")

    boxes = [
        (0.4, 2.0, "Past-only\ntraining window"),
        (2.9, 2.4, "Train-only\npreprocessing"),
        (5.8, 1.9, "Forecast\norigin"),
        (8.2, 2.4, "$h$-step model and\nbaseline forecasts"),
    ]
    for x, width, text in boxes:
        add_box(ax, x, width, text)
    for left, right in zip(boxes, boxes[1:]):
        arrow(ax, (left[0] + left[1], 1.775), (right[0], 1.775))

    ax.text(1.4, 2.55, "Information available at origin", fontsize=8.7, ha="center")
    ax.text(9.4, 2.55, "Targets observed only for scoring", fontsize=8.7, ha="center")
    ax.text(5.75, 0.75, "Advance origin and repeat", fontsize=9, ha="center")
    arrow(ax, (6.75, 1.25), (6.75, 0.95))
    arrow(ax, (6.55, 0.55), (1.4, 0.55))
    arrow(ax, (1.4, 0.55), (1.4, 1.25))

    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    conceptual_hstar(args.output_dir / "fig_hstar_conceptual.pdf")
    rolling_origin(args.output_dir / "fig_rolling_origin_protocol.pdf")


if __name__ == "__main__":
    main()
