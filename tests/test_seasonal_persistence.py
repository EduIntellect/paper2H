import math

import pytest

from src.baselines import seasonal_index


@pytest.mark.parametrize("season", [7, 24])
@pytest.mark.parametrize("horizon", [1, 2, 7, 23, 24, 25, 48, 49, 72])
def test_seasonal_reference_is_available_at_origin(season, horizon):
    origin = 500
    index = seasonal_index(origin, horizon, season)
    assert index <= origin
    assert (origin + horizon - index) % season == 0
    assert index == origin + horizon - math.ceil(horizon / season) * season


def test_one_day_ahead_uses_previous_daily_phase():
    assert seasonal_index(origin=100, horizon=1, season=24) == 77


def test_exact_season_uses_origin():
    assert seasonal_index(origin=100, horizon=24, season=24) == 100


def test_beyond_one_season_never_uses_future_data():
    assert seasonal_index(origin=100, horizon=25, season=24) == 77


@pytest.mark.parametrize("horizon,season", [(0, 24), (1, 0)])
def test_invalid_parameters_are_rejected(horizon, season):
    with pytest.raises(ValueError):
        seasonal_index(origin=100, horizon=horizon, season=season)
