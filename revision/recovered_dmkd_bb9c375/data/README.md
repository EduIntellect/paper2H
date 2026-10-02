# Reproducing the four submitted experimental inputs

This directory is the single entry point for the four-domain manuscript. The
revision covers Beijing PM2.5, electric load, wind, and METR-LA traffic only.
Later PM10 experiments are outside its scope.

`MANIFEST.tsv` records the source identifier, exact experimental file,
SHA-256 checksum, preprocessing producer, and redistribution status for every
domain. A checksum mismatch is a hard failure; do not run an experiment on a
different input under the same filename.

## Inputs already versioned

- Beijing PM2.5: `data/beijingpm25data.csv`.
- Electric load: `results/uci_electricity_daily_aggregate.csv`.

Verify either file with `shasum -a 256 <path>` and compare it with
`data/MANIFEST.tsv`.

## Wind

The exact submitted point is independently documented as WTK-LED CONUS,
2019, `POINT(-105.0 40.0)`, 60-minute UTC data, attribute
`windspeed_100m`. The API resolves this request to site 1673080 at longitude
-105.00313 and latitude 39.99677.

Run:

```bash
python src/retrieve_external_inputs.py wind \
  --api-key DEMO_KEY \
  --email YOUR_EMAIL
```

The command downloads the raw CSV, verifies its SHA-256, runs the historical
preprocessor, and verifies `data/wind_hourly_clean.csv` (8,760 hourly rows).
Use a personal NLR key if `DEMO_KEY` is rate-limited; never commit the key.

## Traffic / METR-LA

The raw HDF5 file is the DCRNN `metr-la.h5` object identified by SHA-256
`64784b76d6fb8ec9bff4b6decafb354da2bb37840468fdccee5044e511277c05`.
The original DCRNN Google Drive folder is the dataset identifier; the retrieval
script uses a byte-identical public mirror because the folder endpoint is not
reliably scriptable.

Run:

```bash
python src/retrieve_external_inputs.py traffic
```

This verifies the raw object, selects sensor `773869`, aggregates 5-minute
speed observations to hourly means, and verifies the 2,856-row canonical file
`data/traffic_hourly_clean.csv`. Reading the HDF5 file requires PyTables.

## Verification evidence

The reconstructed wind and traffic inputs reproduce every submitted
persistence MAE by horizon within floating-point tolerance (`4.44e-16` for
wind and `3.56e-15` for traffic). This baseline fingerprint is independent of
LightGBM and is recorded in the forensic audit workspace.
