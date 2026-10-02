"""Audit frozen forecasts and calculate revision diagnostics without model fitting.

Outputs live in a separate evidence directory. Primary data, predictions, MAE,
H*, DM/BH and figures are never overwritten. Seasonal sensitivity is restricted
to inputs whose row steps are verified calendar steps. PM2.5 timestamps are
recovered only after exact equality with the observed raw-data subsequence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from compute_hstar import compute_hstar
from verify_dmkd_freeze import EXPECTED_ARTIFACTS, main as verify_freeze

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/dmkd_revision_audit_2026-09-30"
CONFIG = {
    "pm25": ("data/pm25_series.csv", "PM25", None, "h", 24),
    "load": ("results/uci_electricity_daily_aggregate.csv", "value", "timestamp", "D", 7),
    "wind": ("data/wind_hourly_clean.csv", "value", "timestamp", "h", 24),
    "traffic": ("data/traffic_hourly_clean.csv", "value", "timestamp", "h", 24),
    "pm10": ("data/pm10_elx_daily.csv", "pm10", "date", "D", 7),
    "pm10_bcn": ("data/pm10_bcn_daily.csv", "pm10", "date", "D", 7),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    verify_freeze()
    before = {p: sha(ROOT / p) for p in EXPECTED_ARTIFACTS}
    OUT.mkdir(parents=True, exist_ok=True)
    metrics, summary, temporal, counts, mismatch_rows = [], [], [], [], []
    input_hashes = dict(before)
    for domain, (relative, value_col, time_col, frequency, season) in CONFIG.items():
        frame = pd.read_csv(ROOT / relative)
        values = frame[value_col].to_numpy(dtype=float)
        if time_col is None:
            raw = pd.read_csv(ROOT / "data/beijingpm25data.csv")
            observed = raw.loc[raw["pm2.5"].notna()].reset_index(drop=True)
            if not np.array_equal(observed["pm2.5"].to_numpy(), values):
                raise AssertionError("PM2.5 observed raw subsequence does not match frozen input")
            times = pd.DatetimeIndex(pd.to_datetime(observed[["year", "month", "day", "hour"]]))
            input_hashes["data/beijingpm25data.csv"] = sha(ROOT / "data/beijingpm25data.csv")
        else:
            times = pd.DatetimeIndex(pd.to_datetime(frame[time_col]))
        if not times.is_monotonic_increasing or times.has_duplicates:
            raise AssertionError(f"Unordered or duplicate timestamps: {domain}")
        step = pd.Timedelta(hours=1) if frequency == "h" else pd.Timedelta(days=1)
        regular = bool(((times[1:] - times[:-1]) == step).all())
        predictions = pd.read_csv(ROOT / f"results/{domain}_predictions_all.csv")
        origin = predictions["origin_idx"].to_numpy(dtype=int)
        horizon = predictions["horizon"].to_numpy(dtype=int)
        target = origin + horizon
        elapsed = np.asarray((times[target] - times[origin]) / step, dtype=float)
        mismatch = elapsed != horizon
        if not np.allclose(predictions["y_true"], values[target], rtol=0, atol=1e-12):
            raise AssertionError(f"Truth linkage failed: {domain}")
        if not np.allclose(predictions["y_pred_baseline"], values[origin], rtol=0, atol=1e-12):
            raise AssertionError(f"Persistence linkage failed: {domain}")
        temporal.append({"domain": domain, "input_rows": len(frame),
                         "regular_calendar_grid": regular,
                         "calendar_gap_count": int(((times[1:] - times[:-1]) != step).sum()),
                         "prediction_rows": len(predictions),
                         "mismatched_elapsed_rows": int(mismatch.sum()),
                         "mismatched_unique_keys": int(predictions.loc[mismatch, ["horizon", "origin_idx"]].drop_duplicates().shape[0]),
                         "max_elapsed_steps": float(elapsed.max()),
                         "seasonal_sensitivity_status": "COMPUTED" if regular else "BLOCKED_CALENDAR_GRID"})
        for idx in np.flatnonzero(mismatch):
            r = predictions.iloc[idx]
            mismatch_rows.append({"domain": domain, "model": r["model"], "origin_idx": int(origin[idx]),
                                  "origin_timestamp": times[origin[idx]].isoformat(),
                                  "target_timestamp": times[target[idx]].isoformat(),
                                  "declared_horizon": int(horizon[idx]), "elapsed_steps": float(elapsed[idx])})
        error = predictions["y_true"].to_numpy() - predictions["y_pred"].to_numpy()
        baselines = {"persistence": predictions["y_pred_baseline"].to_numpy()}
        if regular:
            seasonal_idx = target - ((horizon + season - 1) // season) * season
            if np.any(seasonal_idx < 0) or np.any(seasonal_idx > origin):
                raise AssertionError(f"Seasonal baseline unavailable at origin: {domain}")
            baselines["seasonal_persistence"] = values[seasonal_idx]
        for baseline, baseline_values in baselines.items():
            baseline_error = predictions["y_true"].to_numpy() - baseline_values
            for metric in ("MAE", "RMSE"):
                work = predictions[["model", "horizon", "origin_idx"]].copy()
                work["model_loss"] = np.abs(error) if metric == "MAE" else error ** 2
                work["baseline_loss"] = np.abs(baseline_error) if metric == "MAE" else baseline_error ** 2
                rows = []
                for (model, h), g in work.groupby(["model", "horizon"], sort=True):
                    em, eb = g["model_loss"].mean(), g["baseline_loss"].mean()
                    if metric == "RMSE":
                        em, eb = np.sqrt(em), np.sqrt(eb)
                    rows.append({"domain": domain, "model": model, "baseline": baseline,
                                 "metric": metric, "horizon": int(h), "n_origins": len(g),
                                 "error_model": float(em), "error_baseline": float(eb),
                                 "skill": float(1 - em / eb) if eb > 0 else float("nan"),
                                 "horizon_unit": frequency if regular else "observation_steps"})
                result = pd.DataFrame(rows)
                metrics.extend(rows)
                for model, g in result.groupby("model", sort=True):
                    g = g.sort_values("horizon")
                    summary.append({"domain": domain, "model": model, "baseline": baseline,
                                    "metric": metric, "horizon_unit": frequency if regular else "observation_steps",
                                    **compute_hstar(g["skill"], g["horizon"].tolist())})
        for (model, h), g in predictions.groupby(["model", "horizon"]):
            counts.append({"domain": domain, "model": model, "horizon": int(h),
                           "n_origins": len(g), "primary_support_unchanged": True})

    pd.DataFrame(metrics).to_csv(OUT / "metrics_by_horizon.csv", index=False)
    pd.DataFrame(summary).to_csv(OUT / "hstar_sensitivity.csv", index=False)
    pd.DataFrame(temporal).to_csv(OUT / "calendar_audit.csv", index=False)
    pd.DataFrame(mismatch_rows).to_csv(OUT / "calendar_mismatches.csv", index=False)
    pd.DataFrame(counts).to_csv(OUT / "support_audit.csv", index=False)
    after = {p: sha(ROOT / p) for p in EXPECTED_ARTIFACTS}
    if before != after:
        raise AssertionError("A frozen artifact changed during the audit")
    verify_freeze()
    metadata = {"date": "2026-09-30", "model_fits": 0, "model_prediction_changes": 0,
                "frozen_hashes_unchanged": True, "frozen_before": before, "frozen_after": after,
                "input_hashes": input_hashes,
                "seasonal_rule": "y[t+h-ceil(h/s)*s]; s=24 hourly, s=7 daily; observed at or before origin",
                "selection": "fixed before computing this audit; no baseline or model selected on results",
                "support": "all existing primary rows; no rows dropped; no forecasts refitted",
                "warning": "PM2.5 and Barcelona remain observation-index diagnostics, not validated calendar forecasts",
                "outputs": {p.name: sha(p) for p in sorted(OUT.glob("*.csv"))}}
    (OUT / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(pd.DataFrame(temporal).to_string(index=False))
    print(pd.DataFrame(summary).query("model == 'lightgbm'").to_string(index=False))


if __name__ == "__main__":
    main()
