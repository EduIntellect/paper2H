import pytest

from src.hstar import HStarResult, compute_hstar


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([1, 1, 1, 1], HStarResult(4, 4, 1, 4)),  # all positive
        ([-1, -1, -1], HStarResult(0, 0, 0, 0)),  # all negative
        ([1, 1, -1, 1], HStarResult(4, 2, 1, 2)),  # intermediate gap
        ([-1, -1, 1, 1, 1, -1, 1], HStarResult(7, 3, 3, 5)),  # delayed onset
        ([1, -1, 1, 1, -1, 1], HStarResult(6, 2, 3, 4)),  # multiple islands
        ([-1, -1, -1, 1], HStarResult(4, 1, 4, 4)),  # single endpoint
        ([1, 1, -1, 1, 1], HStarResult(5, 2, 1, 2)),  # tied: earliest wins
        ([1], HStarResult(1, 1, 1, 1)),  # h=1 only
    ],
)
def test_hstar_edge_cases(values, expected):
    assert compute_hstar(range(1, len(values) + 1), values) == expected


def test_unsorted_horizons_are_sorted_before_interval_detection():
    assert compute_hstar([3, 1, 2], [1, 1, 1]) == HStarResult(3, 3, 1, 3)
