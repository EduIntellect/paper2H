"""Read-only content checks and page contact sheets for the editorial PDFs.

Rendering PNGs must already exist from pdftoppm. Contact sheets are QA
derivatives only; no source figure or PDF is edited. Human visual acceptance
is recorded separately after inspecting every sheet and relevant full pages.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "revision/overleaf_2026-10-01/output"
QA = OUTPUT / "qa"


def main() -> None:
    page_texts = {}
    for name in ("manuscript", "response"):
        reader = PdfReader(OUTPUT / f"{name}_working.pdf")
        page_texts[name] = [p.extract_text() for p in reader.pages]
        pictures = sorted(QA.glob(f"{name}-*.png"))
        if len(pictures) != len(reader.pages):
            raise AssertionError(f"Page rendering incomplete: {name}")
        for start in range(0, len(pictures), 6):
            sheet = Image.new("RGB", (1260, 1230), "#e8e8e8")
            draw = ImageDraw.Draw(sheet)
            for index, path in enumerate(pictures[start:start + 6]):
                picture = Image.open(path).convert("RGB")
                picture.thumbnail((400, 570))
                x, y = (index % 3) * 420 + 10, (index // 3) * 615 + 28
                sheet.paste(picture, (x, y))
                draw.text((x, y - 20), path.name, fill="black")
            sheet.save(QA / f"{name}_sheet_{start // 6 + 1}.jpg", quality=94)
    text = "\n".join(page_texts["manuscript"])
    forbidden = ("13 h &", "support effect and the sensitivity", "365-day rolling training",
                 "claims of model invariance", "H ∗(strict) = 63")
    for phrase in forbidden:
        if phrase in text:
            raise AssertionError(f"Superseded claim remains: {phrase}")
    terms = ("Operational Predictability Horizon", "Operational interpretation",
             "Conceptual illustration", "Schematic of the leakage-free",
             "LightGBM skill curve", "Models", "Comparison of predictability",
             "Baseline sensitivity on exact common support", "Metric sensitivity",
             "Data Availability")
    locations = {term: [i + 1 for i, page in enumerate(page_texts["manuscript"])
                        if term in page] for term in terms}
    report = {"page_counts": {name: len(pages) for name, pages in page_texts.items()},
              "locations": locations, "all_pages_rendered": True,
              "superseded_phrases_checked": list(forbidden),
              "visual_acceptance": "PENDING_HUMAN_INSPECTION"}
    (OUTPUT / "pdf_qa_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
