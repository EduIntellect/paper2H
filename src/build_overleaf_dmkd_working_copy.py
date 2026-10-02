"""Compile and audit the isolated four-domain Overleaf editorial working copy.

No forecasting package is imported. The only subprocesses run by this builder
are pdflatex and bibtex. It never writes data, predictions, model code, or the
six-domain manuscript. Retained clean build directories make failures auditable.
"""
from __future__ import annotations

import ast
import difflib
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "revision/overleaf_2026-10-01"
ORIGINAL = BASE / "original"
WORKING = BASE / "working"
OUTPUT = BASE / "output"
INPUT_ZIP = Path("/home/fede/Descargas/Baseline_relative_predictability_horizons.zip")
ZIP_SHA256 = "d383ead3ff2b5bafbb23e25467c274e4af7730c3a27eaa9676695bcaddcc302b"
EDITED = {"main.tex", "Response to the editor and reviewers.tex"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_spec() -> dict:
    tree = ast.parse((ROOT / "src/verify_dmkd_freeze.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "EXPECTED_ARTIFACTS" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("Freeze specification not found")


def protected_files() -> list[Path]:
    files = set()
    for directory in (ROOT / "data", ROOT / "results"):
        files.update(directory.glob("*.csv"))
    recovered = ROOT / "revision/recovered_dmkd_bb9c375"
    files.update((recovered / "results/revision_baseline_sensitivity").glob("*"))
    files.update((ROOT / "experiments").glob("*.py"))
    files.update((ROOT / "src").glob("*.py"))
    files.update((ROOT / "paper").glob("*.tex"))
    return sorted(p for p in files if p.is_file())


def compile_document(build: Path, source: str, job: str, bibliography: bool) -> dict:
    commands = [["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 "-file-line-error", f"-jobname={job}", source]]
    if bibliography:
        commands.append(["bibtex", job])
    commands += [commands[0]] * 2
    for index, command in enumerate(commands, 1):
        result = subprocess.run(command, cwd=build, capture_output=True,
                                text=True, timeout=90, check=False)
        (build / f"{job}_command_{index}.txt").write_text(
            result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"Compilation failed: {command}; see {build}")
    log = (build / f"{job}.log").read_text(errors="replace")
    bad = [line for line in log.splitlines() if
           "undefined" in line.lower() or "Rerun to get" in line]
    if bad:
        raise AssertionError(f"Unresolved LaTeX references: {bad}")
    boxes = [line for line in log.splitlines()
             if "Overfull" in line or "Underfull" in line]
    target = OUTPUT / f"{job}.pdf"
    shutil.copy2(build / f"{job}.pdf", target)
    return {"path": str(target.relative_to(ROOT)), "sha256": sha256(target),
            "commands": commands, "box_warnings": boxes,
            "undefined_references": bad, "clean_build": str(build.relative_to(ROOT))}


def main() -> None:
    if sha256(INPUT_ZIP) != ZIP_SHA256:
        raise AssertionError("The supplied Overleaf ZIP changed")
    protected = protected_files()
    before = {str(p.relative_to(ROOT)): sha256(p) for p in protected}
    for name, (expected, _, _) in freeze_spec().items():
        if before.get(name) != expected:
            raise AssertionError(f"Frozen input mismatch before build: {name}")
    with zipfile.ZipFile(INPUT_ZIP) as archive:
        original_hashes = {}
        for info in archive.infolist():
            if info.is_dir():
                continue
            relative = Path(info.filename)
            if relative.is_absolute() or ".." in relative.parts:
                raise AssertionError(f"Unsafe ZIP member: {relative}")
            expected = hashlib.sha256(archive.read(info)).hexdigest()
            if sha256(ORIGINAL / relative) != expected:
                raise AssertionError(f"Original export changed: {relative}")
            if str(relative) not in EDITED and sha256(WORKING / relative) != expected:
                raise AssertionError(f"Incidental change: {relative}")
            original_hashes[str(relative)] = expected
    if set(p.name for p in WORKING.iterdir() if p.is_file()) != set(original_hashes):
        raise AssertionError("Unexpected files in the Overleaf working source")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    builds = BASE / "builds"
    builds.mkdir(exist_ok=True)
    build = Path(tempfile.mkdtemp(prefix="clean_", dir=builds))
    for path in WORKING.iterdir():
        if path.is_file():
            shutil.copy2(path, build / path.name)
    compiled = [compile_document(build, "main.tex", "manuscript_working", True),
                compile_document(build, "Response to the editor and reviewers.tex",
                                 "response_working", False)]
    changes = []
    for name in sorted(EDITED):
        changes.extend(difflib.unified_diff(
            (ORIGINAL / name).read_text().splitlines(keepends=True),
            (WORKING / name).read_text().splitlines(keepends=True),
            fromfile=f"original/{name}", tofile=f"working/{name}"))
    (OUTPUT / "editorial_changes.diff").write_text("".join(changes), encoding="utf-8")
    source_zip = OUTPUT / "overleaf_working_sources.zip"
    with zipfile.ZipFile(source_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(WORKING.iterdir()):
            if path.is_file():
                archive.write(path, path.name)
    with zipfile.ZipFile(source_zip) as archive:
        for name in original_hashes:
            if hashlib.sha256(archive.read(name)).hexdigest() != sha256(WORKING / name):
                raise AssertionError(f"Output ZIP mismatch: {name}")
    after = {str(p.relative_to(ROOT)): sha256(p) for p in protected}
    if before != after:
        raise AssertionError("Protected data/results/code/manuscript changed during build")
    manifest = {
        "status": "WORKING_REVISION_NOT_CLEARED_FOR_SUBMISSION",
        "scope": "four-domain supplied Overleaf source; not the six-domain working draft",
        "requested_skill": "humanizar cientifico", "requested_skill_available": False,
        "fallback_skill": "write-like-me; supplied manuscript and response as style references",
        "input_zip": str(INPUT_ZIP), "input_zip_sha256": ZIP_SHA256,
        "original_member_hashes": original_hashes,
        "working_member_hashes": {name: sha256(WORKING / name) for name in original_hashes},
        "edited_sources": sorted(EDITED), "figures_byte_identical_to_supplied_export": True,
        "compiled": compiled, "source_zip_sha256": sha256(source_zip),
        "protected_hashes_before": before, "protected_hashes_after": after,
        "protected_files_byte_identical": True,
        "predictions_byte_identical_and_numerically_identical": True,
        "model_fits": 0, "prediction_generation_calls": 0,
        "hyperparameters_splits_support_and_protocol_changed": False,
        "scope_note": "Load protocol wording corrected to historical code; not changed in code.",
        "reporting_correction": {
            "domain": "pm25", "old_strict": 13, "correct_strict": 22,
            "old_interval": [36, 48], "correct_interval": [27, 48],
            "source": "results/pm25_lightgbm_full_skill.csv",
            "reason": "Original text used a separate moving-average summary, not the plotted LightGBM curve.",
            "metrics_and_forecasts_changed": False,
            "evidence": "revision/submitted_pdf_2026-10-01/submitted_pm25_figure_linkage.json"},
        "open_before_submission": [
            "Trace primary RMSE appendix values to per-origin errors; numerical claims held out of draft.",
            "Publish and verify an author-controlled public four-domain data cache, within redistribution permissions.",
            "Confirm final author metadata/affiliations; supplied two-author source preserved.",
            "Import the corrected source into Overleaf and check the final rendering.",
            "Author sign-off and submission; no upload/commit/push authorized."],
        "visual_qa": "PENDING", "approximately_25872_model_fits": "NOT_AUTHORIZED",
    }
    (OUTPUT / "editorial_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "compiled_documents": len(compiled),
                      "protected_files": len(protected), "predictions_unchanged": True,
                      "model_fits": 0, "manifest": str(OUTPUT / "editorial_manifest.json"),
                      "box_warnings": [x["box_warnings"] for x in compiled]}, indent=2))


if __name__ == "__main__":
    main()
