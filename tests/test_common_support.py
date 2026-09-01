import pandas as pd
import pytest

from src.common_support import align_common_support, mae_skill_on_common_support


def forecasts(model, rows):
    return pd.DataFrame(rows, columns=["origin", "target_timestamp", "horizon", "y_true", "y_pred"]).assign(model=model)


def test_exact_support_is_verified_and_skill_is_computed():
    model = forecasts("model", [("t0", "t1", 1, 10.0, 9.0), ("t1", "t2", 1, 12.0, 10.0)])
    baseline = forecasts("baseline", [("t0", "t1", 1, 10.0, 8.0), ("t1", "t2", 1, 12.0, 9.0)])
    _, audit = align_common_support(model, baseline)
    assert audit.verified
    result = mae_skill_on_common_support(model, baseline)
    assert result.loc[0, "n_common"] == 2
    assert result.loc[0, "skill"] == pytest.approx(0.4)


def test_mismatched_origins_are_rejected():
    model = forecasts("model", [("t0", "t1", 1, 10.0, 9.0)])
    baseline = forecasts("baseline", [("other", "t1", 1, 10.0, 9.0)])
    with pytest.raises(ValueError, match="support mismatch"):
        align_common_support(model, baseline)


def test_mismatched_target_timestamp_is_rejected():
    model = forecasts("model", [("t0", "t1", 1, 10.0, 9.0)])
    baseline = forecasts("baseline", [("t0", "t2", 1, 10.0, 9.0)])
    with pytest.raises(ValueError, match="support mismatch"):
        align_common_support(model, baseline)


def test_mismatched_horizon_is_rejected():
    model = forecasts("model", [("t0", "t1", 1, 10.0, 9.0)])
    baseline = forecasts("baseline", [("t0", "t1", 2, 10.0, 9.0)])
    with pytest.raises(ValueError, match="support mismatch"):
        align_common_support(model, baseline)


def test_mismatched_y_true_is_rejected():
    model = forecasts("model", [("t0", "t1", 1, 10.0, 9.0)])
    baseline = forecasts("baseline", [("t0", "t1", 1, 11.0, 9.0)])
    with pytest.raises(ValueError, match="y_true differs"):
        align_common_support(model, baseline)


def test_duplicate_keys_are_rejected():
    model = forecasts("model", [("t0", "t1", 1, 10.0, 9.0), ("t0", "t1", 1, 10.0, 9.5)])
    baseline = forecasts("baseline", [("t0", "t1", 1, 10.0, 8.0)])
    with pytest.raises(ValueError, match="duplicate"):
        align_common_support(model, baseline)
