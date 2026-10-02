#!/usr/bin/env python3
"""Generate the manuscript table from verified baseline-sensitivity outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DOMAIN_ORDER = ["pm25", "load", "wind", "traffic"]
DOMAIN_LABEL = {"pm25": r"PM$_{2.5}$", "load": "Load", "wind": "Wind", "traffic": "Traffic"}
BASELINE_LABEL = {"persistence": "Persistence", "seasonal_persistence": "Seasonal persistence"}


def generate(results: Path, destination: Path) -> None:
    hstar = pd.read_csv(results / "hstar_summary.csv")
    support = pd.read_csv(results / "support_audit.csv")
    if not support["verified"].all():
        raise RuntimeError("Cannot generate table: common support is not verified")
    if (support[["dropped_a", "dropped_b"]] != 0).any().any():
        raise RuntimeError("Cannot generate table: forecasts were dropped during pairwise alignment")

    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{@{}llcccl@{}}",
        r"\toprule",
        r"Domain & Baseline & Common $n_h$ & $H^*_{\mathrm{relax}}$ & $H^*_{\mathrm{strict}}$ & Longest interval \\",
        r"\midrule",
    ]
    for domain in DOMAIN_ORDER:
        for baseline in ["persistence", "seasonal_persistence"]:
            row = hstar[(hstar["domain"] == domain) & (hstar["baseline"] == baseline)].iloc[0]
            counts = support[(support["domain"] == domain) & (support["baseline"] == baseline)]["n_common"]
            count_text = str(int(counts.min())) if counts.min() == counts.max() else f"{int(counts.min())}--{int(counts.max())}"
            lines.append(
                f"{DOMAIN_LABEL[domain]} & {BASELINE_LABEL[baseline]} & {count_text} & "
                f"{int(row.h_relax)} & {int(row.h_strict)} & "
                f"$[{int(row.h_start)},{int(row.h_end)}]$ \\\\"
            )
        if domain != DOMAIN_ORDER[-1]:
            lines.append(r"\addlinespace[2pt]")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\caption{Baseline sensitivity on exact common support. $n_h$ is the number of aligned forecast origins at each horizon (a range is shown when it varies with $h$). The persistence rows in this table are recomputed on the same support as seasonal persistence and therefore need not equal the primary full-support persistence descriptors.}",
            r"\label{tab:baseline-sensitivity}",
            r"\end{table}",
        ]
    )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    generate(args.results, args.destination)


if __name__ == "__main__":
    main()
