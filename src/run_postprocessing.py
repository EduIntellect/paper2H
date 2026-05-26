"""Run Steps 5–9: H*, DM tests, unified table, and figures."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_step(label: str, script: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print('='*60)
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,
        text=True,
    )
    if result.returncode != 0:
        print(f"  FAILED with exit code {result.returncode}")
        return False
    return True


if __name__ == "__main__":
    src = Path("src")
    steps = [
        ("Step 5: Compute H* descriptors", str(src / "compute_hstar.py")),
        ("Step 6: Diebold-Mariano tests", str(src / "dm_tests.py")),
        ("Step 7: Build unified results table", str(src / "build_unified_results.py")),
        ("Step 9: Generate figures", str(src / "generate_figures.py")),
    ]
    for label, script in steps:
        ok = run_step(label, script)
        if not ok:
            print(f"\nAborted at: {label}")
            sys.exit(1)

    print("\n\nAll post-processing steps complete.")
