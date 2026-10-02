"""Read-only audit of the four-domain paper supplied by its author.

Recomputes descriptors from historical aggregate MAE only, not predictions.
Does not reconstruct RMSE from MAE, fit models, or alter frozen results.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from compute_hstar import compute_hstar

ROOT = Path(__file__).resolve().parents[1]
PDF = Path("/home/fede/Descargas/paper2_H_-1.pdf")
OUT = ROOT / "revision/submitted_pdf_2026-10-01"
EXPECTED_PDF = "464916a0b2f8d780343cc4721eee338623aee52fa3a8b292f914a2c13bd629f8"
DOMAINS = {
    "pm25": ("pm25_lightgbm_full", (48, 13, 36, 48), "experiments/pm25_lightgbm_full.py"),
    "load": ("uci_energy_lightgbm", (1, 1, 1, 1), "experiments/uci_energy_lightgbm.py"),
    "wind": ("wind", (48, 48, 1, 48), "experiments/wind_predictability.py"),
    "traffic": ("traffic", (72, 7, 46, 52), "experiments/traffic_predictability.py"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if digest(PDF) != EXPECTED_PDF:
        raise AssertionError("Author-supplied PDF changed")
    before = {}
    checks = []
    for domain, (stem, expected, producer) in DOMAINS.items():
        paths = [ROOT / "results" / f"{stem}_{suffix}.csv" for suffix in ("errors", "skill")]
        for p in paths:
            before[str(p.relative_to(ROOT))] = digest(p)
        errors, skill = [pd.read_csv(p).sort_values("horizon") for p in paths]
        calculated = 1 - errors.model_mae / errors.baseline_mae
        if not np.array_equal(errors.horizon, skill.horizon) or not np.allclose(calculated, skill.skill, rtol=1e-12, atol=1e-12):
            raise AssertionError(f"Historical MAE linkage failed: {domain}")
        primary = errors.loc[errors.horizon == 1] if domain == "load" else errors
        primary_skill = 1 - primary.model_mae / primary.baseline_mae
        hs = compute_hstar(primary_skill, primary.horizon.tolist())
        descriptor_match = tuple(hs[k] for k in ("h_relax", "h_strict", "h_start", "h_end")) == expected
        historic_source = subprocess.check_output([
            "git", "--git-dir=/home/fede/forense_paper2H/paper2H.git", "show",
            "bb9c375ead2fe1f313127b77849296a144270f68:" + producer,
        ])
        source = ROOT / producer
        checks.append({"domain": domain, "submitted_primary_tuple": list(expected),
                       "historical_mae_descriptors_match": descriptor_match, "hstar": hs,
                       "primary_horizons": primary.horizon.tolist(),
                       "source_matches_recovered_revision": historic_source == source.read_bytes(),
                       "producer": producer, "producer_sha256": digest(source),
                       "warning": "Aggregate agreement does not prove exact manuscript-source or every historical forecast"})
    loader_checks = []
    for domain in ("wind", "traffic"):
        data = ROOT / f"data/{domain}_hourly_clean.csv"
        f = pd.read_csv(data)
        times = pd.to_datetime(f.timestamp)
        values = pd.to_numeric(f.value, errors="coerce")
        if not np.array_equal(values, values.interpolate(method="linear", limit_direction="both")):
            raise AssertionError(f"Interpolation is not a no-op: {domain}")
        if times.duplicated().any() or not ((times.diff().dropna()) == pd.Timedelta(hours=1)).all():
            raise AssertionError(f"Nonregular canonical hourly grid: {domain}")
        loader_checks.append({"domain": domain, "input_sha256": digest(data),
                              "rows": len(f), "missing_values": int(values.isna().sum()),
                              "global_loader_interpolation_is_noop": True,
                              "regular_hourly_grid": True})
    raw = pd.read_csv(ROOT / "data/beijingpm25data.csv")
    raw_times = pd.to_datetime(raw[["year", "month", "day", "hour"]])
    if len(raw) != 43824 or not (raw_times.diff().dropna() == pd.Timedelta(hours=1)).all():
        raise AssertionError("Primary raw PM2.5 calendar is not complete hourly")
    after = {p: digest(ROOT / p) for p in before}
    if before != after:
        raise AssertionError("Historical primary artifacts changed")
    result = {"audit_date": "2026-10-01", "status": "VERIFIED_PDF_IDENTITY_PARTIAL_PRIMARY_MAE_LINKAGE",
              "pdf": str(PDF), "pdf_sha256": EXPECTED_PDF,
              "pdf_md5": hashlib.md5(PDF.read_bytes()).hexdigest(),
              "source_of_identity": "Author identifies this supplied PDF as the reviewers' manuscript",
              "independent_editorial_manager_access": False,
              "domains": 4, "authors": ["Federico Garcia Crespi", "Julio Alberto Ramos Martinez"],
              "primary_checks": checks, "loader_checks": loader_checks,
              "pm25_primary_raw_rows": len(raw), "pm25_primary_grid_regular": True,
              "pm25_primary_missing_values_preserved_by_producer": True,
              "six_domain_compressed_pm25_audit_applies_to_submitted_input": False,
              "model_fits": 0, "prediction_changes": 0,
              "historical_artifacts_before": before, "historical_artifacts_after": after,
              "remaining_gates": ["current Overleaf ZIP/PDF and submitted-source identity",
                                  "PM2.5 submitted 48/13 [36,48] versus located MAE artifact 48/22 [27,48]",
                                  "primary RMSE per-origin or squared-error provenance",
                                  "Load extended figure provenance and final-day coverage",
                                  "Load implementation/configuration reporting",
                                  "reviewer-specific equation clarification and metadata sync",
                                  "author-controlled public data cache and redistribution verification"],
              "submission_clearance": False}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "evidence_identity.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
