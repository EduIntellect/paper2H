"""Transparent forecast baselines used by the revision experiments."""

from __future__ import annotations

import math


def seasonal_index(origin: int, horizon: int, season: int) -> int:
    """Index the latest observed value sharing the target's seasonal phase.

    The returned index is guaranteed to be no later than ``origin`` for
    positive horizons and seasons, including forecasts beyond one season.
    """
    if horizon < 1:
        raise ValueError("horizon must be positive")
    if season < 1:
        raise ValueError("season must be positive")
    return origin + horizon - math.ceil(horizon / season) * season
