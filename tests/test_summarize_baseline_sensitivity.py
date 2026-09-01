import pandas as pd

from src.summarize_baseline_sensitivity import summarize_domain


def test_summary_audits_each_horizon_and_baseline():
    rows = []
    truths = {(1, 1): 10.0, (2, 1): 12.0, (1, 2): 14.0}
    predictions = {
        "lightgbm": {(1, 1): 9.0, (2, 1): 11.0, (1, 2): 13.0},
        "persistence": {(1, 1): 8.0, (2, 1): 10.0, (1, 2): 12.0},
        "seasonal_persistence": {(1, 1): 7.0, (2, 1): 9.0, (1, 2): 11.0},
    }
    for model, values in predictions.items():
        for (origin, horizon), y_pred in values.items():
            rows.append(
                {
                    "domain": "synthetic",
                    "model": model,
                    "origin": f"o{origin}",
                    "target_timestamp": f"t{origin}_{horizon}",
                    "horizon": horizon,
                    "y_true": truths[(origin, horizon)],
                    "y_pred": y_pred,
                }
            )
    metrics, support, hstar = summarize_domain(pd.DataFrame(rows), "synthetic")
    assert len(metrics) == 4
    assert len(support) == 4
    assert support["verified"].all()
    assert (support["dropped_a"] == 0).all()
    assert (support["dropped_b"] == 0).all()
    assert len(hstar) == 2
