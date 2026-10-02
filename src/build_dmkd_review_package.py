"""Build a local DMKD review bundle in a clean directory; never submit it.

No experiments, Git operations, commits, uploads or model fits are run.
The bundle is deliberately marked NOT_READY_FOR_SUBMISSION.
"""
from __future__ import annotations

import difflib
import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
import zipfile
from pathlib import Path

from verify_dmkd_freeze import main as verify_freeze
from verify_dmkd_revision_editorial import main as verify_editorial

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "revision/dmkd_2026-09-30"
STYLES = Path("/home/fede/repos/paper2H_latex")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_tex(directory: Path, name: str) -> None:
    commands = [["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"]]
    if name == "main":
        commands += [["bibtex", name]]
    commands += [["pdflatex", "-interaction=nonstopmode", "-halt-on-error", name + ".tex"]] * 3
    for command in commands:
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise RuntimeError(" ".join(command) + "\n" + result.stdout[-6000:] + result.stderr[-2000:])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-only", action="store_true", help="Refresh archive and hashes after QA without recompiling")
    args = parser.parse_args()
    verify_freeze()
    verify_editorial()
    OUT.mkdir(parents=True, exist_ok=True)
    source = OUT / "sources"
    source.mkdir(exist_ok=True)
    figures = source / "figures"
    figures.mkdir(exist_ok=True)
    for name in ("tables.tex", "revision_sensitivity_tables.tex", "revision_rmse_table.tex", "sn-bibliography.bib",
                 "response_to_reviewers.tex", "dmkd_cover_letter_template.tex"):
        shutil.copy2(ROOT / "paper" / name, source / name)
    shutil.copy2(ROOT / "paper/paper2_submission.tex", source / "main.tex")
    for name in ("sn-jnl.cls", "sn-basic.bst"):
        shutil.copy2(STYLES / name, source / name)
    for name in ("fig_skill_pm25.pdf", "fig_skill_load.pdf", "fig_skill_wind.pdf",
                 "fig_skill_traffic.pdf", "fig_skill_pm10.pdf", "fig_skill_pm10_bcn.pdf", "fig_hstar_heatmap.pdf"):
        shutil.copy2(ROOT / "figures" / name, figures / name)
    for name in ("fig_hstar_conceptual.pdf", "fig_rolling_origin_protocol.pdf"):
        shutil.copy2(ROOT / "revision/recovered_dmkd_bb9c375/paper/revised" / name, figures / name)
    source_hashes = {str(p.relative_to(source)): digest(p) for p in sorted(source.rglob("*")) if p.is_file()}
    compiled_manifest = OUT / "compiled_source_hashes.json"
    if args.package_only:
        if not compiled_manifest.is_file() or json.loads(compiled_manifest.read_text())["source_hashes"] != source_hashes:
            raise AssertionError("Source changed since compilation; rerun without --package-only")
        build = Path(json.loads(compiled_manifest.read_text())["build_directory"])
    else:
        build = Path(tempfile.mkdtemp(prefix="clean_build_", dir=OUT))
        shutil.copytree(source, build, dirs_exist_ok=True)
    for name, target in (("main", "working_manuscript.pdf"),
                         ("response_to_reviewers", "response_working_draft.pdf"),
                         ("dmkd_cover_letter_template", "cover_letter_working_draft.pdf")):
        if not args.package_only:
            compile_tex(build, name)
            shutil.copy2(build / (name + ".pdf"), OUT / target)
        elif not (OUT / target).is_file():
            raise AssertionError(f"Cannot package without existing PDF: {target}")
    if not args.package_only:
        compiled_manifest.write_text(json.dumps({"build_directory": str(build), "source_hashes": source_hashes}, indent=2) + "\n")
    with tarfile.open(ROOT / "revision/pre_edit_2026-09-30/editorial_sources.tar.gz") as archive:
        old = archive.extractfile("paper/paper2_submission.tex").read().decode("utf-8")
    new = (ROOT / "paper/paper2_submission.tex").read_text(encoding="utf-8")
    diff = "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                     fromfile="six_domain_draft_before.tex", tofile="six_domain_working_revision.tex"))
    (OUT / "editorial_changes.diff").write_text(diff, encoding="utf-8")
    import pandas as pd
    inputs = pd.read_csv(ROOT / "data/MANIFEST.tsv", sep="\t")
    with zipfile.ZipFile(OUT / "replication_inputs.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for row in inputs.itertuples(index=False):
            path = ROOT / row.exact_file
            if digest(path) != row.sha256:
                raise AssertionError(f"Input changed: {row.exact_file}")
            archive.write(path, row.exact_file)
        for relative in ("data/README.md", "data/MANIFEST.tsv", "data/beijingpm25data.csv"):
            archive.write(ROOT / relative, relative)
    status = {"status": "NOT_READY_FOR_SUBMISSION", "model_fits": 0,
              "clean_directory_compile": "PASS", "build_directory": str(build), "primary_frozen_artifacts": "UNCHANGED",
              "version": "ARCHIVED six-domain working revision; author-supplied submitted PDF confirms four-domain scope",
              "gates": ["submitted-source identity and Overleaf reconciliation",
                        "PM2.5 compressed time axis", "Barcelona missing-day axis",
                        "Madrid causal preprocessing", "Load final-day coverage",
                        "public data release and redistribution verification",
                        "final reviewer page/line mapping and marked manuscript"]}
    (OUT / "submission_status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    files = list(source.rglob("*")) + [OUT / n for n in
            ("working_manuscript.pdf", "response_working_draft.pdf", "cover_letter_working_draft.pdf",
             "editorial_changes.diff", "replication_inputs.zip", "submission_status.json", "compiled_source_hashes.json",
             "SCOPE_NOTICE.md")]
    manifest = {str(p.relative_to(OUT)): digest(p) for p in sorted(files) if p.is_file()}
    (OUT / "package_hashes.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(OUT / "local_review_bundle.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files + [OUT / "package_hashes.json"]:
            if path.is_file():
                archive.write(path, str(path.relative_to(OUT)))
        for path in sorted((ROOT / "results/dmkd_revision_audit_2026-09-30").glob("*")):
            archive.write(path, "audit/" + path.name)
        for relative in ("docs/dmkd_revision_status_2026-09-30.md", "docs/dmkd_reviewer_response_matrix.csv",
                         "docs/dmkd_submitted_pdf_identity_2026-10-01.md", "docs/dmkd_reviewer_map_four_domains_2026-10-01.md",
                         "docs/dmkd_results_freeze_2026-09-30.md", "docs/overleaf_sync_procedure.md",
                         "docs/traffic_a1_serialization_repair_2026-09-18.md",
                         "src/audit_dmkd_revision.py", "src/verify_dmkd_revision_editorial.py",
                         "src/verify_recovered_dmkd_revision.py", "src/verify_dmkd_freeze.py", "src/compute_hstar.py"):
            archive.write(ROOT / relative, relative)
    verify_freeze()
    print("Clean-directory compilation: PASS. Local bundle: " + str(OUT))
    print("Submission status: NOT_READY_FOR_SUBMISSION; model fits: 0.")


if __name__ == "__main__":
    main()
