"""Check local working-revision tables and reviewer coverage without fitting.

Passing certifies linkage to the stored evidence, not scientific validity or
identity with the submitted/Overleaf manuscript. The working version remains
blocked for submission until its explicit acceptance gates are resolved.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from verify_dmkd_freeze import main as verify_freeze

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/dmkd_revision_audit_2026-09-30"
DOMAINS = ("pm25", "load", "wind", "traffic", "pm10", "pm10_bcn")
MODELS = ("ridge", "lightgbm", "extratrees", "knn", "mlp")
DESCRIPTORS = ("h_relax", "h_strict", "h_start", "h_end")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def numbers(cells: list[str]) -> list[int]:
    return [0 if c.strip() == "---" else int(c.strip()) for c in cells]


def main() -> None:
    verify_freeze()
    tex = (ROOT / "paper/paper2_submission.tex").read_text()
    frozen = pd.read_csv(ROOT / "results/hstar_summary.csv")
    audit = pd.read_csv(OUT / "hstar_sensitivity.csv")
    metrics = pd.read_csv(OUT / "metrics_by_horizon.csv")
    main_table = tex.split("\\label{tab:results}", 1)[1].split("\\end{table}", 1)[0]
    pattern = re.compile(r"^\s*&\s*(Ridge|LightGBM|ExtraTrees|KNN|MLP)\s*&\s*(\d+)\s*&\s*(\d+)\s*&\s*(\d+|---)\s*&\s*(\d+|---)\s*&\s*([\d.]+)\\%.*?\\textsc\{([^}]+)\}", re.M)
    rows = pattern.findall(main_table)
    require(len(rows) == 30, f"Expected 30 main table rows, found {len(rows)}")
    for i, (label, *cells) in enumerate(rows):
        domain, model = DOMAINS[i // 5], MODELS[i % 5]
        require(label.lower() == model, f"Model/order mismatch: {domain}/{label}")
        stored = frozen.query("domain == @domain and model == @model").iloc[0]
        require(numbers(cells[:4]) == [int(stored[c]) for c in DESCRIPTORS],
                f"Main H* table mismatch: {domain}/{model}")
        require(float(cells[4]) == round(float(stored.pct_horizons_significant), 1),
                f"Main significance table mismatch: {domain}/{model}")
        require(cells[5].replace("\\_", "_").upper() == stored.profile_type,
                f"Main profile mismatch: {domain}/{model}")
        calculated = audit.query("domain == @domain and model == @model and baseline == 'persistence' and metric == 'MAE'").iloc[0]
        for key in (*DESCRIPTORS, "n_sign_changes"):
            require(int(calculated[key]) == int(stored[key]), f"Reaggregated H* mismatch: {domain}/{model}/{key}")
    for domain in DOMAINS:
        stored = pd.read_csv(ROOT / f"results/{domain}_skill_all.csv")
        calculated = metrics.query("domain == @domain and baseline == 'persistence' and metric == 'MAE'")
        paired = stored.merge(calculated, on=["domain", "model", "horizon"], suffixes=("_stored", "_audit"), validate="one_to_one")
        require(len(paired) == len(stored), f"MAE support mismatch: {domain}")
        for left, right in (("skill_stored", "skill_audit"), ("mae_model", "error_model"), ("mae_baseline", "error_baseline")):
            require(np.allclose(paired[left], paired[right], atol=1e-12, rtol=1e-12), f"MAE metric mismatch: {domain}/{left}")
        require(np.array_equal(paired.n_origins_stored, paired.n_origins_audit), f"Origin counts mismatch: {domain}")
    seasonal_tex = (ROOT / "paper/revision_sensitivity_tables.tex").read_text()
    seasonal_rows = re.findall(r"^(Load|Wind|Traffic) & (Persistence|Seasonal) & (\d+) & (\d+) & (\d+|---) & (\d+|---)", seasonal_tex, re.M)
    require(len(seasonal_rows) == 6, "Expected six baseline rows")
    for domain, reference, *cells in seasonal_rows:
        domain = domain.lower()
        baseline = "persistence" if reference == "Persistence" else "seasonal_persistence"
        stored = audit.query("domain == @domain and model == 'lightgbm' and baseline == @baseline and metric == 'MAE'").iloc[0]
        require(numbers(cells) == [int(stored[c]) for c in DESCRIPTORS], f"Seasonal table mismatch: {domain}/{baseline}")
    rmse_tex = (ROOT / "paper/revision_rmse_table.tex").read_text()
    rmse_rows = re.findall(r"^.+? & (MAE|RMSE) & (\d+) & (\d+) & (\d+|---) & (\d+|---)", rmse_tex, re.M)
    require(len(rmse_rows) == 12, "Expected twelve loss-sensitivity rows")
    for i, (metric, *cells) in enumerate(rmse_rows):
        domain = DOMAINS[i // 2]
        stored = audit.query("domain == @domain and model == 'lightgbm' and baseline == 'persistence' and metric == @metric").iloc[0]
        require(numbers(cells) == [int(stored[c]) for c in DESCRIPTORS], f"RMSE table mismatch: {domain}/{metric}")
    expected = {"E1", "E2"} | {f"R1.{i}" for i in range(1, 11)} | {f"R2.{i}" for i in range(1, 8)}
    matrix = pd.read_csv(ROOT / "docs/dmkd_reviewer_response_matrix.csv")
    response = (ROOT / "paper/response_to_reviewers.tex").read_text()
    actual = re.findall(r"\\comment\{(E[12]|R[12]\.\d+):", response)
    require(set(actual) == expected and len(actual) == len(expected), "Response comments incomplete or duplicated")
    require(set(matrix.comment_id) == expected and not matrix.comment_id.duplicated().any(), "Response matrix incomplete")
    require(matrix.notna().all().all(), "Missing response matrix field")
    for label in ("fig:hstar_conceptual", "fig:rolling_origin", "fig:skill-pm25"):
        require(f"\\ref{{{label}}}" in tex and f"\\label{{{label}}}" in tex, f"Missing figure reference: {label}")
    result = {"status": "PASS_EDITORIAL_LINKAGE_ONLY", "checked_on": "2026-10-01",
              "main_table_rows_verified": 30, "baseline_table_rows_verified": 6,
              "loss_table_rows_verified": 12, "reviewer_editor_requests_accounted_for": 19,
              "all_primary_mae_reaggregations_match": True, "model_fits": 0,
              "submission_clearance": False,
              "warning": "Four/six-domain identity and scientific acceptance gates remain open"}
    (OUT / "editorial_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    verify_freeze()


if __name__ == "__main__":
    main()
