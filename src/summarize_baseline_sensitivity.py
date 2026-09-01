#!/usr/bin/env python3
"""Summarize frozen per-origin baseline-sensitivity predictions."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.common_support import align_common_support, mae_skill_on_common_support
from src.hstar import compute_hstar


KEY_COLUMNS = ["origin", "target_timestamp", "horizon", "y_true", "y_pred"]
BASELINES = ["persistence", "seasonal_persistence"]


def model_frame(predictions: pd.DataFrame, name: str) -> pd.DataFrame:
    return predictions.loc[predictions["model"] == name, KEY_COLUMNS]


def summarize_domain(predictions: pd.DataFrame, domain: str):
    model = model_frame(predictions, "lightgbm")
    metric_rows: list[pd.DataFrame] = []
    support_rows: list[dict[str, object]] = []
    hstar_rows: list[dict[str, object]] = []
    for baseline_name in BASELINES:
        baseline = model_frame(predictions, baseline_name)
        for horizon in sorted(model["horizon"].unique()):
            model_h = model.loc[model["horizon"] == horizon]
            baseline_h = baseline.loc[baseline["horizon"] == horizon]
            _, audit = align_common_support(model_h, baseline_h, require_full_support=True)
            support_rows.append(
                {"domain": domain, "baseline": baseline_name, "horizon": int(horizon), **audit.__dict__}
            )
        metrics = mae_skill_on_common_support(model, baseline).assign(
            domain=domain, baseline=baseline_name
        )
        metric_rows.append(metrics)
        result = compute_hstar(metrics["horizon"], metrics["skill"])
        signs = metrics.sort_values("horizon")["skill"].to_numpy() > 0
        hstar_rows.append(
            {
                "domain": domain,
                "baseline": baseline_name,
                **result.__dict__,
                "sign_changes": int(np.sum(signs[1:] != signs[:-1])),
            }
        )
    return pd.concat(metric_rows, ignore_index=True), pd.DataFrame(support_rows), pd.DataFrame(hstar_rows)


def summarize_directory(directory: Path) -> None:
    prediction_files = sorted(directory.glob("predictions_*.csv"))
    if not prediction_files:
        raise FileNotFoundError(f"No predictions_*.csv files in {directory}")
    metrics_all = []
    support_all = []
    hstar_all = []
    for path in prediction_files:
        domain = path.stem.removeprefix("predictions_")
        metrics, support, hstar = summarize_domain(pd.read_csv(path), domain)
        metrics_all.append(metrics)
        support_all.append(support)
        hstar_all.append(hstar)
    pd.concat(metrics_all, ignore_index=True).to_csv(directory / "metrics_by_horizon.csv", index=False)
    pd.concat(support_all, ignore_index=True).to_csv(directory / "support_audit.csv", index=False)
    pd.concat(hstar_all, ignore_index=True).to_csv(directory / "hstar_summary.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    summarize_directory(args.directory)


if __name__ == "__main__":
    main()
