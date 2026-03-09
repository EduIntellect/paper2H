# Electric Load Data Contract (PJM)

- **Expected raw input file:** `data/pjm_load_hourly_raw.csv`
- **Expected raw schema:** at least one timestamp column (`timestamp`/`datetime`/`date`/`time`) and one load column (`load`/`LOAD`/`mw`/`MW`/`demand`).
- **Cleaned output file:** `data/pjm_load_hourly_clean.csv`
- **Cleaned output schema (canonical):**
  - `timestamp` (parsed datetime)
  - `load` (numeric electric load target)
- **Frequency:** hourly.
- **Target variable:** electric load.
- **Preparation rules:** parse timestamps, coerce numeric load, drop rows with missing timestamp/load, sort chronologically, and deduplicate by timestamp.
- **Timezone handling:** timestamps are preserved as provided in the raw PJM CSV; no timezone conversion is applied during preparation.
- **Experiment setup (this domain):** persistence baseline, moving-average initial model, `Hmax = 72`, metric `MAE`.
- **Evaluation protocol:** leakage-free time-ordered forecasting with aligned timestamp comparison across horizons.
