"""Exact common-support validation for forecast comparisons."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


KEYS = ["origin", "target_timestamp", "horizon"]
REQUIRED = [*KEYS, "y_true", "y_pred"]


@dataclass(frozen=True)
class SupportAudit:
    n_a: int
    n_b: int
    n_common: int
    dropped_a: int
    dropped_b: int
    verified: bool


def _validate_frame(frame: pd.DataFrame, label: str) -> None:
    missing = [column for column in REQUIRED if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")
    if frame.duplicated(KEYS).any():
        raise ValueError(f"{label} has duplicate forecast keys")


def align_common_support(
    a: pd.DataFrame,
    b: pd.DataFrame,
    *,
    require_full_support: bool = True,
) -> tuple[pd.DataFrame, SupportAudit]:
    """Inner-join forecasts and verify identical targets at identical keys."""
    _validate_frame(a, "forecast A")
    _validate_frame(b, "forecast B")
    merged = a.merge(b, on=KEYS, how="inner", suffixes=("_a", "_b"), validate="one_to_one")
    if not np.array_equal(merged["y_true_a"].to_numpy(), merged["y_true_b"].to_numpy()):
        raise ValueError("y_true differs on common forecast support")

    audit = SupportAudit(
        n_a=len(a),
        n_b=len(b),
        n_common=len(merged),
        dropped_a=len(a) - len(merged),
        dropped_b=len(b) - len(merged),
        verified=(len(merged) == len(a) == len(b)),
    )
    if require_full_support and not audit.verified:
        raise ValueError(f"forecast support mismatch: {audit}")
    return merged, audit


def mae_skill_on_common_support(a: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    """Compute horizon-wise MAE skill only after full-support verification."""
    merged, _ = align_common_support(a, baseline, require_full_support=True)
    merged = merged.assign(
        abs_error_model=np.abs(merged["y_true_a"] - merged["y_pred_a"]),
        abs_error_baseline=np.abs(merged["y_true_b"] - merged["y_pred_b"]),
    )
    grouped = merged.groupby("horizon", sort=True).agg(
        n_common=("horizon", "size"),
        model_mae=("abs_error_model", "mean"),
        baseline_mae=("abs_error_baseline", "mean"),
    )
    if (grouped["baseline_mae"] <= 0).any():
        raise ValueError("baseline MAE must be strictly positive")
    grouped["skill"] = 1.0 - grouped["model_mae"] / grouped["baseline_mae"]
    return grouped.reset_index()
