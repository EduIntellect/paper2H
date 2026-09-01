#!/usr/bin/env python3
"""Freeze hashes and protocol metadata for a completed revision run."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path

import lightgbm
import pandas as pd
import sklearn


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_value(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def freeze(directory: Path) -> None:
    directory = directory.resolve()
    required = [
        *(directory / f"predictions_{name}.csv" for name in ["pm25", "load", "wind", "traffic"]),
        directory / "metrics_by_horizon.csv",
        directory / "support_audit.csv",
        directory / "hstar_summary.csv",
        ROOT / "experiments" / "run_revision_baseline_sensitivity.py",
        ROOT / "src" / "baselines.py",
        ROOT / "src" / "common_support.py",
        ROOT / "src" / "hstar.py",
        ROOT / "src" / "summarize_baseline_sensitivity.py",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Cannot freeze incomplete run; missing: {missing}")
    rows = [
        {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "size_bytes": path.stat().st_size}
        for path in required
    ]
    pd.DataFrame(rows).to_csv(directory / "artifact_manifest.tsv", sep="\t", index=False)
    metadata = {
        "git_branch": git_value("branch", "--show-current"),
        "git_base_head": git_value("rev-parse", "HEAD"),
        "python": platform.python_version(),
        "pandas": pd.__version__,
        "scikit_learn": sklearn.__version__,
        "lightgbm": lightgbm.__version__,
        "primary_metric": "MAE",
        "baselines": {
            "persistence": "y_t",
            "seasonal_persistence": "y_(t+h-ceil(h/s)*s)",
            "season_hourly": 24,
            "season_daily_load": 7,
        },
        "common_support_keys": ["origin", "target_timestamp", "horizon"],
        "target_equality_required": True,
        "selection_note": "seasonal persistence was specified before comparative results were inspected",
    }
    (directory / "run_metadata_verified.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    freeze(args.directory)


if __name__ == "__main__":
    main()
