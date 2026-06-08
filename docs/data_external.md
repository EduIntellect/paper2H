# External Datasets Documentation — paper2H

This document records the source, acquisition details, and preprocessing pipeline for the heavy raw datasets that are stored locally but are not committed to the git repository as submission artifacts.

---

## 1. Electric Load (UCI Electricity Load Diagrams 2011–2014)
* **Local Raw Path:** `data/LD2011_2014.txt` (approx. 710 MB)
* **Data Source:** [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/321/electricityloaddiagrams20112014)
* **Description:** Contains electricity consumption measurements (in kW) for 370 clients, sampled at 15-minute intervals from 2011 to 2014.
* **Extraction / Cleaned Path:** `results/uci_electricity_daily_aggregate.csv`
* **Preprocessing:**
  - Aggregated from 15-minute raw measurements to daily sums across the stable coverage client set.
  - Aligned to `(timestamp, value)` columns.
  - Script: `src/aggregate_uci_electricity.py`

---

## 2. Traffic (METR-LA)
* **Local Raw Path:** `data/metr-la.h5` (approx. 57 MB)
* **Data Source:** Public data link from the [DCRNN GitHub Repository](https://github.com/liyaguang/DCRNN)
* **Description:** Contains traffic speed measurements collected by loop detectors in Los Angeles County, sampled at 5-minute intervals during 2012.
* **Extraction / Cleaned Path:** `data/traffic_hourly_clean.csv`
* **Preprocessing:**
  - A single representative sensor trajectory is extracted from the sensor matrix.
  - Resampled from 5-minute to hourly frequency.
  - Columns: `timestamp`, `value`
  - Script: `src/prepare_traffic_data.py`

---

## 3. Traffic Robustness Check (PeMS-BAY)
* **Local Raw Path:** `data/pems-bay.h5` (approx. 136 MB)
* **Data Source:** Public data link from the [DCRNN GitHub Repository](https://github.com/liyaguang/DCRNN)
* **Description:** Contains traffic speed measurements from sensors in the San Francisco Bay Area, sampled at 5-minute intervals.
* **Note:** This dataset is stored locally as part of the traffic-domain data-handling codebase, but METR-LA is the primary traffic domain evaluated in the paper.

---

## 4. Summary of Local Clean Paths (Tracked in Git)
The following preprocessed CSV datasets are small enough to be versioned and are directly read by the domain evaluation scripts:
- `data/pm25_series.csv` (PM2.5 Beijing)
- `data/wind_hourly_clean.csv` (Wind Speed NREL)
- `data/traffic_hourly_clean.csv` (METR-LA extracted)
- `data/pm10_elx_daily.csv` (PM10 Madrid)
- `data/pm10_bcn_daily.csv` (PM10 Barcelona)
- `results/uci_electricity_daily_aggregate.csv` (Electric Load aggregated)
