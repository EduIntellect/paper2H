# Data cache: inputs of the four-domain experiments

Exact inputs used for the PM2.5, electric-load, wind and traffic experiments in "Baseline-Relative Predictability
Horizons for Cross-Domain Forecast Evaluation". Verify with `sha256sum -c SHA256SUMS`. Files are unmodified copies
of the inputs used for the reported results. Please cite the original datasets.

| File | Rows | Source | Lineage | Terms |
|---|---|---|---|---|
| `pm25_beijing_hourly_raw.csv` | 43,824 hourly (missing values kept as NA) | UCI Beijing PM2.5 (Chen, 2015) | unmodified download | CC BY 4.0 |
| `load_uci_daily_aggregate.csv` | 667 daily | UCI ElectricityLoadDiagrams20112014 (Trindade, 2015) | `src/aggregate_uci_electricity.py`: sum of 15-minute kW readings per day (divide by 4 for kWh) | CC BY 4.0 |
| `wind_hourly_clean.csv` | 8,760 hourly | NREL Wind Toolkit, WTK-LED CONUS 2019, one grid point (Draxl et al., 2015) | `src/prepare_nrel_wind_data.py` | NREL open data, CC BY 3.0 US (AWS Open Data registry); attribute NREL |
| `traffic_hourly_clean.csv` | 2,856 hourly | METR-LA (Li et al., 2018), sensor 773869, hourly aggregate | `src/prepare_traffic_data.py` | Derived from Caltrans PeMS loop-detector data distributed with DCRNN; see note |

Columns: `timestamp,value` (PM2.5 raw keeps the original UCI columns).

Note on traffic: the underlying measurements come from the Caltrans Performance Measurement System (PeMS). The
METR-LA benchmark is widely redistributed (for example a CC BY 4.0 copy on Zenodo, record 5146275, uploaded by a
third party), but we did not obtain separate confirmation from PeMS. This file is a single-sensor hourly aggregate
provided only to reproduce the paper. If you hold rights and object to this copy, please open an issue and it will be removed.

Code: https://github.com/EduIntellect/paper2H
