"""Verify the recovered September four-domain sensitivity, without fitting."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from compute_hstar import compute_hstar

ROOT = Path(__file__).resolve().parents[1]
RECOVERED = ROOT / "revision/recovered_dmkd_bb9c375"
EVIDENCE = RECOVERED / "results/revision_baseline_sensitivity"
OUT = ROOT / "results/dmkd_revision_audit_2026-09-30/recovered_revision_verification.json"


def main() -> None:
    manifest = pd.read_csv(EVIDENCE / "artifact_manifest.tsv", sep="\t")
    hashes_verified = 0
    for row in manifest.itertuples(index=False):
        path = RECOVERED / row.path
        if not path.is_file():
            raise AssertionError(f"Recovered manifest file missing: {row.path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != row.sha256:
            raise AssertionError(f"Recovered hash mismatch: {row.path}")
        if path.stat().st_size != row.size_bytes:
            raise AssertionError(f"Recovered size mismatch: {row.path}")
        hashes_verified += 1
    metrics = pd.read_csv(EVIDENCE / "metrics_by_horizon.csv")
    summary = pd.read_csv(EVIDENCE / "hstar_summary.csv")
    checks = []
    for domain in ("pm25", "load", "wind", "traffic"):
        p = pd.read_csv(EVIDENCE / f"predictions_{domain}.csv")
        keys = ["origin", "target_timestamp", "horizon"]
        if p.duplicated(["model", *keys]).any():
            raise AssertionError(f"Duplicate recovered key: {domain}")
        unit = pd.Timedelta(days=1) if domain == "load" else pd.Timedelta(hours=1)
        elapsed = (pd.to_datetime(p.target_timestamp) - pd.to_datetime(p.origin)) / unit
        if not np.array_equal(elapsed, p.horizon):
            raise AssertionError(f"Recovered elapsed-time mismatch: {domain}")
        model = p.loc[p.model == "lightgbm", keys + ["y_true", "y_pred"]]
        for baseline in ("persistence", "seasonal_persistence"):
            b = p.loc[p.model == baseline, keys + ["y_true", "y_pred"]]
            paired = model.merge(b, on=keys, validate="one_to_one", suffixes=("_model", "_baseline"))
            if len(paired) != len(model) or len(paired) != len(b):
                raise AssertionError(f"Recovered support loss: {domain}/{baseline}")
            if not np.array_equal(paired.y_true_model, paired.y_true_baseline):
                raise AssertionError(f"Recovered truth mismatch: {domain}/{baseline}")
            calculated = []
            for h, g in paired.groupby("horizon"):
                em = np.abs(g.y_true_model - g.y_pred_model).mean()
                eb = np.abs(g.y_true_model - g.y_pred_baseline).mean()
                calculated.append({"horizon": int(h), "n_common": len(g),
                                   "model_mae": em, "baseline_mae": eb, "skill": 1 - em / eb})
            c = pd.DataFrame(calculated).sort_values("horizon")
            stored = metrics.query("domain == @domain and baseline == @baseline").sort_values("horizon")
            for col in ("horizon", "n_common", "model_mae", "baseline_mae", "skill"):
                if not np.allclose(c[col], stored[col], rtol=1e-12, atol=1e-12):
                    raise AssertionError(f"Recovered metric mismatch: {domain}/{baseline}/{col}")
            hs = compute_hstar(c.skill, c.horizon.tolist())
            stored_hs = summary.query("domain == @domain and baseline == @baseline").iloc[0]
            for key, value in hs.items():
                col = "sign_changes" if key == "n_sign_changes" else key
                if int(stored_hs[col]) != value:
                    raise AssertionError(f"Recovered H* mismatch: {domain}/{baseline}/{col}")
            checks.append({"domain": domain, "baseline": baseline, "rows": len(paired),
                           "exact_common_support": True, "calendar_horizons_verified": True,
                           "metrics_verified": True, "hstar_verified": True})
    pdf = RECOVERED / "paper/revised/revised_manuscript.pdf"
    reference_pdf = Path("/home/fede/forense_paper2H/revised_manuscript.pdf")
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest != hashlib.sha256(reference_pdf.read_bytes()).hexdigest():
        raise AssertionError("Recovered PDF is not the forensic September PDF")
    result = {"status": "PASS_SENSITIVITY_ARTIFACTS_ONLY", "model_fits": 0,
              "commit": "bb9c375ead2fe1f313127b77849296a144270f68",
              "pdf_sha256": digest, "matches_forensic_pdf": True,
              "manifest_files_verified": hashes_verified, "checks": checks,
              "not_verified": ["identity against Editorial Manager", "current Overleaf state",
                               "primary historical preprocessing", "primary RMSE appendix provenance",
                               "author-list change", "public cache completeness"]}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
