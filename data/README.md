# DMKD replication inputs: one local entry point

Status (2026-09-30): local review package; public release and final manuscript
version are not confirmed. Do not describe this directory as a published cache.

`MANIFEST.tsv` identifies all six exact processed inputs read by the current
tabular scripts, with their frozen SHA-256 hashes. The build script assembles
them unchanged into `revision/dmkd_2026-09-30/replication_inputs.zip`.

Run the read-only verification before any new analysis:

```bash
/home/fede/repos/hstar/.venv-lightgbm-validation/bin/python src/verify_dmkd_freeze.py
```

Important scientific gates:

- Beijing `pm25_series.csv` is exactly the non-missing raw subsequence. Its row
  steps are not uniformly hours. The raw hourly file is also retained.
- Barcelona omits dates; its row steps are not uniformly days.
- The PM10 input named `pm10_elx_daily.csv` is historically labelled Madrid,
  Casa de Campo. Observed values match an independently located Madrid raw
  record, but its exact missing-value producer is still not established.
- The Load aggregate sums 15-minute kW readings; divide by four for kWh under
  UCI's documented convention. The very small final-day value needs a coverage
  audit. The file is retained without rescaling or truncation.
- Wind and Traffic have verified regular hourly axes and exact canonical
  linkage. Wind/Traffic files currently exist locally but are Git-ignored.

The recovered September four-domain revision is preserved separately in
`revision/recovered_dmkd_bb9c375/`. Its data manifest, retrieval script and
forecast evidence use a different experimental version. Do not mix its numbers
or support with the six-domain frozen artifacts.

Original sources:

- PM2.5: https://doi.org/10.24432/C5JS49 (CC BY 4.0).
- Load: https://doi.org/10.24432/C58C86 (CC BY 4.0).
- Wind: NREL/WTK-LED CONUS, 2019, site 1673080, 100 m speed.
- Traffic: DCRNN/METR-LA, sensor 773869, 5-minute speed aggregated hourly.
- PM10: Madrid and Catalan monitoring sources as documented in the manuscript;
  complete producer-level lineage and redistribution verification remain open.

Before publishing, resolve provenance and redistribution terms, publish the
approved replication package to an author-controlled location, verify access
from a clean environment, and replace the manuscript's release-pending wording
with that verified link. No publication, Git commit or push is performed by
the local build.
