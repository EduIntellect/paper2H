# DMKD Overleaf-to-repository synchronization procedure

Status: decision text, local Reviewer 1 text and the author-supplied submitted
PDF received. Its hash confirms the four-domain/two-author reference; see
`docs/dmkd_submitted_pdf_identity_2026-10-01.md`. Waiting for the
final Overleaf-rendered PDF. The supplied source ZIP is preserved in
`revision/overleaf_2026-10-01/original`; its isolated edited copy is in
`revision/overleaf_2026-10-01/working`. See
`docs/dmkd_humanized_working_revision_2026-10-01.md` and its output manifest.
A four-domain September revision has been recovered separately in
`revision/recovered_dmkd_bb9c375`; it is not automatically the current Overleaf
state. The local six-domain working draft must not replace it silently.

## Required inputs

1. The complete Overleaf source ZIP used for the revised manuscript.
2. The PDF compiled by Overleaf from that source.
3. The editor decision letter and every reviewer comment, without omissions.
4. The manuscript identifier and revision deadline.

## Controlled synchronization

1. Record the SHA-256 hash and acquisition date of every supplied file.
2. Expand the Overleaf ZIP into a temporary staging directory, never directly
   over `paper/`.
3. Inventory `.tex`, `.bib`, figure, table, style, and class files.
4. Compare the staged source with `paper/` and classify each difference as
   editorial, formatting, evidence-related, or unexplained.
5. Copy only reviewed differences into the repository with recoverable patches.
6. Preserve the confirmed submitted four-domain scope and both authors unless
   an explicit author decision changes them. Verify every numerical
   claim against that version's artifacts. The six-domain numerical freeze
   does not certify historical preprocessing or calendar validity; consult
   `docs/dmkd_revision_status_2026-09-30.md` before accepting its claims.
7. Verify that all figures and tables map to `docs/figure_table_traceability.md`.
8. Compile the synchronized source and compare the resulting PDF with the
   supplied Overleaf PDF page by page.
9. Populate the four-domain reviewer matrix (keep the six-domain matrix separate) and ensure every reviewer
   comment has a response, manuscript location, evidence source, and verification.
10. Produce clean and marked manuscripts only after the response matrix is complete.

## Safety rules

- Overleaf remains the manuscript source of truth until synchronization is approved.
- Do not overwrite the local manuscript without preserving a recoverable prior state.
- Do not alter frozen numerical artifacts during editorial synchronization.
- Do not claim an experiment, analysis, or robustness check that was not performed.
- Do not commit, push, or upload a submission package without explicit authorization.

## Completion criteria

- Local and Overleaf sources are reconciled and compile successfully.
- The compiled local PDF matches the intended revised manuscript.
- Every numerical claim matches the frozen evidence package.
- Every editor/reviewer comment is accounted for in the response matrix.
- The clean manuscript, marked manuscript, response letter, cover letter, and
  source package pass a clean-directory compilation check.
