"""Link submitted Figure 3's vector coordinates to stored skill CSVs.

This is document verification, not a forecast experiment. Requires the bundled
Python with pdfplumber. Original PDF/CSV files are opened read-only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF = Path("/home/fede/Descargas/paper2_H_-1.pdf")
OUT = ROOT / "revision/submitted_pdf_2026-10-01/submitted_pm25_figure_linkage.json"


def main() -> None:
    if hashlib.sha256(PDF.read_bytes()).hexdigest() != "464916a0b2f8d780343cc4721eee338623aee52fa3a8b292f914a2c13bd629f8":
        raise AssertionError("Submitted reference PDF changed")
    with pdfplumber.open(PDF) as document:
        page = document.pages[11]
        curves = [c for c in page.curves if len(c.get("pts", [])) == 48]
        if len(curves) != 1:
            raise AssertionError("Expected a unique 48-point curve on submitted PDF page 12")
        points = curves[0]["pts"]
        if any(abs((points[i + 1][0] - points[i][0]) - (points[1][0] - points[0][0])) > 1e-5 for i in range(47)):
            raise AssertionError("Figure horizon spacing is not uniform")
        zero_lines = [l for l in page.lines if l.get("dash") and l["width"] > 200 and abs(l["top"] - l["bottom"]) < 1e-6]
        if len(zero_lines) != 1:
            raise AssertionError("Cannot identify submitted zero-skill reference line")
        zero_y = zero_lines[0]["top"]
    ordinate = [p[1] for p in points]
    comparisons = []
    for relative in ("results/pm25_lightgbm_full_skill.csv", "results/pm25_real_skill.csv"):
        path = ROOT / relative
        with path.open() as stream:
            rows = list(csv.DictReader(stream))
        if [int(r["horizon"]) for r in rows] != list(range(1, 49)):
            raise AssertionError(f"Unexpected horizons: {relative}")
        values = [float(r["skill"]) for r in rows]
        xm, ym = sum(values) / 48, sum(ordinate) / 48
        slope = sum((x - xm) * (y - ym) for x, y in zip(values, ordinate)) / sum((x - xm) ** 2 for x in values)
        intercept = ym - slope * xm
        residual = [abs(y - (slope * x + intercept)) for x, y in zip(values, ordinate)]
        comparisons.append({"csv": relative, "csv_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "pdf_points": 48, "max_residual_points": max(residual),
                            "rmse_residual_points": math.sqrt(sum(r * r for r in residual) / 48),
                            "zero_line_residual_points": abs(intercept - zero_y),
                            "slope": slope, "matches_vector_geometry": slope < 0 and max(residual) < 1e-3 and abs(intercept - zero_y) < 1e-3})
    if not comparisons[0]["matches_vector_geometry"] or comparisons[1]["matches_vector_geometry"]:
        raise AssertionError("Submitted Figure 3 does not uniquely match the located LightGBM skill curve")
    result = {"status": "VERIFIED_PM25_TEXT_FIGURE_INCONSISTENCY", "date": "2026-10-01",
              "pdf": str(PDF), "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
              "figure_number": 3, "pdf_page": 12,
              "text_descriptors_page_11": {"h_relax": 48, "h_strict": 13, "h_start": 36, "h_end": 48},
              "figure_csv_descriptors": {"h_relax": 48, "h_strict": 22, "h_start": 27, "h_end": 48},
              "comparisons": comparisons, "model_fits": 0, "prediction_changes": 0,
              "required_action": "Reconcile text/table to the confirmed evidence version; do not invent a support-effect explanation"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
