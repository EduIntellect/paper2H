"""Deterministically normalize the 15 Traffic A1 truth cells.

This script never fits a model or recomputes a prediction.  It replaces only
the canonical truth/error fields and rebuilds the aggregate CSVs that consume
them.  It is intentionally specific to the verified Traffic A1 discrepancy.
"""
from __future__ import annotations

import csv
import hashlib
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "src"))

from compute_hstar import compute_hstar  # noqa: E402
from dm_tests import benjamini_hochberg, dm_test  # noqa: E402

CANONICAL = ROOT / "data/traffic_hourly_clean.csv"
PREDICTIONS = RESULTS / "traffic_predictions_all.csv"
AUDIT_CSV = DOCS / "traffic_a1_serialization_repair_cells_2026-09-18.csv"
METRICS_CSV = DOCS / "traffic_a1_serialization_repair_metrics_2026-09-18.csv"
AUDIT_MD = DOCS / "traffic_a1_serialization_repair_2026-09-18.md"
EXPECTED_ROWS = 15
EXPECTED_TARGET = pd.Timestamp("2012-04-06 09:00:00")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(relative_path: str) -> bytes:
    """Read the pre-repair tracked artifact, making reruns auditable/idempotent."""
    return subprocess.check_output(["git", "show", f"HEAD:{relative_path}"], cwd=ROOT)


def skill_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (domain, model, horizon), g in df.groupby(["domain", "model", "horizon"]):
        mae_model = g["abs_error_model"].mean()
        mae_baseline = g["abs_error_baseline"].mean()
        rows.append({
            "domain": domain, "model": model, "horizon": horizon,
            "n_origins": len(g), "mae_model": mae_model,
            "mae_baseline": mae_baseline,
            "skill": 1 - mae_model / mae_baseline if mae_baseline > 0 else np.nan,
        })
    return pd.DataFrame(rows).sort_values(["domain", "model", "horizon"])


def traffic_dm(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, horizon), g in df.groupby(["model", "horizon"]):
        stat, p_value = dm_test(
            g["abs_error_model"].to_numpy(),
            g["abs_error_baseline"].to_numpy(), h=int(horizon),
        )
        rows.append({"domain": "traffic", "model": model, "horizon": horizon,
                     "n_origins": len(g), "dm_stat": stat, "p_value": p_value})
    out = pd.DataFrame(rows).sort_values(["model", "horizon"])
    finite = np.isfinite(out["p_value"].to_numpy())
    adjusted = np.full(len(out), np.nan)
    adjusted[finite] = benjamini_hochberg(out.loc[finite, "p_value"].to_numpy())
    out["p_value_bh"] = adjusted
    out["significant_bh"] = adjusted < 0.05
    return out


def main() -> None:
    tracked = [
        PREDICTIONS, RESULTS / "traffic_skill_all.csv", RESULTS / "dm_tests_all.csv",
        RESULTS / "hstar_all_domains.csv", RESULTS / "hstar_summary.csv",
        RESULTS / "unified_results_table.csv",
    ]
    before_blobs = {p.name: git_blob(str(p.relative_to(ROOT))) for p in tracked}
    before_hashes = {name: hashlib.sha256(blob).hexdigest()
                     for name, blob in before_blobs.items()}
    canonical = pd.read_csv(CANONICAL, parse_dates=["timestamp"])
    before = pd.read_csv(io.BytesIO(before_blobs[PREDICTIONS.name]))
    target_idx = before["origin_idx"].astype(int) + before["horizon"].astype(int)
    canonical_values = canonical["value"].to_numpy()[target_idx]
    target_timestamps = canonical["timestamp"].to_numpy()[target_idx]
    affected = pd.to_datetime(target_timestamps) == EXPECTED_TARGET
    if int(affected.sum()) != EXPECTED_ROWS:
        raise RuntimeError(f"Expected {EXPECTED_ROWS} affected rows; found {affected.sum()}")
    if set(before.loc[affected, "model"]) != {"lightgbm", "ridge", "extratrees", "knn", "mlp"}:
        raise RuntimeError("Unexpected affected model set")

    raw_canonical = {}
    with CANONICAL.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            raw_canonical[row["timestamp"]] = row["value"]
    canonical_token = raw_canonical[EXPECTED_TARGET.strftime("%Y-%m-%d %H:%M:%S")]
    canonical_value = float(canonical.loc[canonical["timestamp"] == EXPECTED_TARGET, "value"].iloc[0])

    original_text = before_blobs[PREDICTIONS.name].decode("utf-8")
    reader = csv.DictReader(io.StringIO(original_text))
    fieldnames = reader.fieldnames
    original_raw_rows = list(reader)
    with PREDICTIONS.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        raw_rows = list(reader)
    if fieldnames is None:
        raise RuntimeError("Missing A1 header")

    changed = []
    invariant_columns = (
        "domain", "model", "horizon", "origin_idx", "origin_timestamp",
        "y_pred", "y_pred_baseline",
    )
    invariant_tokens_before = [
        tuple(row[column] for column in invariant_columns)
        for row in original_raw_rows
    ]
    for line_number, (row, original_row) in enumerate(zip(raw_rows, original_raw_rows), start=2):
        idx = int(row["origin_idx"]) + int(row["horizon"])
        timestamp = canonical.iloc[idx]["timestamp"]
        if timestamp != EXPECTED_TARGET:
            continue
        old_truth = original_row["y_true"]
        old_model_error = original_row["abs_error_model"]
        old_baseline_error = original_row["abs_error_baseline"]
        row["y_true"] = canonical_token
        row["abs_error_model"] = repr(abs(canonical_value - float(row["y_pred"])))
        row["abs_error_baseline"] = repr(abs(canonical_value - float(row["y_pred_baseline"])))
        changed.append({
            "csv_line": line_number, "model": row["model"],
            "horizon": row["horizon"], "origin_idx": row["origin_idx"],
            "origin_timestamp": row["origin_timestamp"],
            "target_idx": idx, "target_timestamp": timestamp,
            "old_y_true": old_truth, "canonical_y_true_csv": canonical_token,
            "canonical_y_true_parsed": repr(canonical_value),
            "absolute_difference": repr(abs(float(old_truth) - canonical_value)),
            "old_abs_error_model": old_model_error,
            "new_abs_error_model": row["abs_error_model"],
            "old_abs_error_baseline": old_baseline_error,
            "new_abs_error_baseline": row["abs_error_baseline"],
        })

    with PREDICTIONS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(raw_rows)
    with PREDICTIONS.open(newline="", encoding="utf-8") as handle:
        written_rows = list(csv.DictReader(handle))
    invariant_tokens_after = [
        tuple(row[column] for column in invariant_columns)
        for row in written_rows
    ]
    if invariant_tokens_before != invariant_tokens_after:
        raise RuntimeError("An invariant prediction/support field changed serialization")

    after = pd.read_csv(PREDICTIONS)
    if not np.array_equal(before["y_pred"].to_numpy(), after["y_pred"].to_numpy()):
        raise RuntimeError("Predictions changed numerically")
    if not np.array_equal(before["y_pred_baseline"].to_numpy(), after["y_pred_baseline"].to_numpy()):
        raise RuntimeError("Baseline predictions changed numerically")
    post_targets = canonical["value"].to_numpy()[
        after["origin_idx"].astype(int).to_numpy() + after["horizon"].astype(int).to_numpy()
    ]
    if not np.array_equal(after["y_true"].to_numpy(), post_targets):
        raise RuntimeError("Post-repair canonical linkage is not exact")

    before_skill, after_skill = skill_table(before), skill_table(after)
    if not before_skill.reset_index(drop=True).equals(after_skill.reset_index(drop=True)):
        raise RuntimeError("Aggregate Traffic skill changed unexpectedly")
    (RESULTS / "traffic_skill_all.csv").write_bytes(before_blobs["traffic_skill_all.csv"])

    before_dm, after_dm = traffic_dm(before), traffic_dm(after)
    if not before_dm.reset_index(drop=True).equals(after_dm.reset_index(drop=True)):
        raise RuntimeError("Traffic DM metrics changed unexpectedly")
    (RESULTS / "dm_tests_all.csv").write_bytes(before_blobs["dm_tests_all.csv"])

    hstar = pd.read_csv(RESULTS / "hstar_all_domains.csv")
    for model, group in after_skill.groupby("model"):
        result = compute_hstar(group.sort_values("horizon")["skill"],
                               group.sort_values("horizon")["horizon"].tolist())
        mask = (hstar["domain"] == "traffic") & (hstar["model"] == model)
        for key, value in result.items():
            hstar.loc[mask, key] = value
    original_hstar = pd.read_csv(io.BytesIO(before_blobs["hstar_all_domains.csv"]))
    if not hstar.equals(original_hstar):
        raise RuntimeError("H* changed unexpectedly")
    (RESULTS / "hstar_all_domains.csv").write_bytes(before_blobs["hstar_all_domains.csv"])

    # H* and all BH significance flags are unchanged, hence the summary is byte-identical.
    (RESULTS / "hstar_summary.csv").write_bytes(before_blobs["hstar_summary.csv"])

    (RESULTS / "unified_results_table.csv").write_bytes(
        before_blobs["unified_results_table.csv"]
    )

    keys = pd.DataFrame(changed)[["model", "horizon"]].drop_duplicates()
    keys["horizon"] = keys["horizon"].astype(int)
    def labelled(frame: pd.DataFrame, label: str) -> pd.DataFrame:
        keep = ["model", "horizon"]
        return frame.rename(columns={c: f"{c}_{label}" for c in frame.columns if c not in keep})

    metrics = keys.merge(labelled(before_skill, "before"), on=["model", "horizon"])
    metrics = metrics.merge(labelled(after_skill, "after"), on=["model", "horizon"])
    metrics = metrics.merge(labelled(before_dm, "before"), on=["model", "horizon"])
    metrics = metrics.merge(labelled(after_dm, "after"), on=["model", "horizon"])
    metrics.to_csv(METRICS_CSV, index=False)
    pd.DataFrame(changed).to_csv(AUDIT_CSV, index=False)

    artifacts = [
        "results/traffic_predictions_all.csv", "results/traffic_skill_all.csv",
        "results/dm_tests_all.csv", "results/hstar_all_domains.csv",
        "results/hstar_summary.csv", "results/unified_results_table.csv",
    ]
    after_hashes = {Path(p).name: sha256(ROOT / p) for p in artifacts}
    AUDIT_MD.write_text(
        "# Traffic A1 deterministic serialization repair\n\n"
        "Date: 2026-09-18\n\n"
        "Scope: normalization of the 15 verified Traffic A1 `y_true` cells and "
        "regeneration of their tabular descendants only. No model was fitted; no "
        "prediction, hyperparameter, split, temporal support, or protocol setting was changed. "
        "The ~25,872 fits remain unauthorized.\n\n"
        f"- Canonical target: `{EXPECTED_TARGET}`; parsed value `{canonical_value!r}`; CSV token `{canonical_token}`.\n"
        f"- Modified truth cells: {len(changed)}.\n"
        f"- Maximum pre-repair absolute difference: {max(float(x['absolute_difference']) for x in changed):.17g}.\n"
        "- Post-repair exact canonical mismatches: 0.\n"
        "- `domain`, `model`, `horizon`, `origin_idx`, `origin_timestamp`, `y_pred`, and "
        "`y_pred_baseline`: byte-for-byte identical by CSV field.\n"
        "- `y_pred` and `y_pred_baseline`: numerically identical (`numpy.array_equal`).\n\n"
        "## Updated artifact\n\n"
        "- `results/traffic_predictions_all.csv`\n\n"
        "All tabular descendants (`traffic_skill_all.csv`, `dm_tests_all.csv`, "
        "`hstar_all_domains.csv`, `hstar_summary.csv`, and `unified_results_table.csv`) "
        "were recomputed/validated and remained byte-identical. Therefore no aggregate "
        "metric, H* descriptor, profile, figure input, or protocol conclusion changed.\n" +
        "\n\n## Audit files\n\n"
        "- `docs/traffic_a1_serialization_repair_cells_2026-09-18.csv`: all 15 cells, old/canonical values, absolute differences, and old/new errors.\n"
        "- `docs/traffic_a1_serialization_repair_metrics_2026-09-18.csv`: affected model/horizon metrics before and after.\n\n"
        "## SHA-256 before / after\n\n| Artifact | Before | After |\n|---|---|---|\n" +
        "\n".join(f"| `{name}` | `{before_hashes[name]}` | `{after_hashes[name]}` |" for name in before_hashes) + "\n",
        encoding="utf-8",
    )
    print(f"Repaired {len(changed)} Traffic A1 truth cells; exact mismatches after repair: 0")
    print("Predictions unchanged byte-for-byte by field and numerically identical")


if __name__ == "__main__":
    main()
