"""Canonical baseline-relative skill and H* descriptors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class HStarResult:
    h_relax: int
    h_strict: int
    h_start: int
    h_end: int


def skill(model_error: Iterable[float], baseline_error: Iterable[float]) -> np.ndarray:
    """Return ``1 - model_error / baseline_error`` horizon by horizon."""
    model = np.asarray(list(model_error), dtype=float)
    baseline = np.asarray(list(baseline_error), dtype=float)
    if model.shape != baseline.shape:
        raise ValueError("model_error and baseline_error must have identical shapes")
    if np.any(baseline <= 0) or np.any(~np.isfinite(baseline)):
        raise ValueError("baseline_error must be finite and strictly positive")
    if np.any(~np.isfinite(model)):
        raise ValueError("model_error must be finite")
    return 1.0 - model / baseline


def compute_hstar(horizons: Iterable[int], skill_values: Iterable[float]) -> HStarResult:
    """Compute relaxed reach and the longest contiguous positive-skill interval.

    ``H*(relax)`` is the last evaluated horizon with strictly positive skill,
    even when non-positive gaps occur earlier. ``H*(strict)`` is the length of
    the longest interval of consecutive integer horizons with positive skill.
    If several intervals tie, the earliest interval is reported.
    """
    h = np.asarray(list(horizons), dtype=int)
    values = np.asarray(list(skill_values), dtype=float)
    if h.shape != values.shape:
        raise ValueError("horizons and skill_values must have identical shapes")
    if h.ndim != 1:
        raise ValueError("horizons and skill_values must be one-dimensional")
    if len(np.unique(h)) != len(h):
        raise ValueError("horizons must be unique")

    order = np.argsort(h)
    h = h[order]
    values = values[order]
    positive = h[np.isfinite(values) & (values > 0)]
    if positive.size == 0:
        return HStarResult(0, 0, 0, 0)

    best_start = best_end = int(positive[0])
    run_start = run_end = int(positive[0])
    for horizon in positive[1:]:
        horizon = int(horizon)
        if horizon == run_end + 1:
            run_end = horizon
        else:
            run_start = run_end = horizon
        if run_end - run_start > best_end - best_start:
            best_start, best_end = run_start, run_end

    return HStarResult(
        h_relax=int(positive.max()),
        h_strict=best_end - best_start + 1,
        h_start=best_start,
        h_end=best_end,
    )
