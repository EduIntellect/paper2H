# Data cache: PM2.5 and electric load

Inputs used for the PM2.5 and electric-load experiments in "Baseline-Relative Predictability Horizons for
Cross-Domain Forecast Evaluation". Verify with `sha256sum -c SHA256SUMS`. Files are unmodified copies of the
inputs used for the reported results.

| File | Rows | Source | Lineage | Licence |
|---|---|---|---|---|
| `pm25_beijing_hourly_raw.csv` | 43,824 hourly (missing values kept as NA) | UCI Beijing PM2.5 (Chen, 2015) | unmodified download | CC BY 4.0 |
| `load_uci_daily_aggregate.csv` | 667 daily | UCI ElectricityLoadDiagrams20112014 (Trindade, 2015) | `src/aggregate_uci_electricity.py`: sum of 15-minute kW readings per day (divide by 4 for kWh) | CC BY 4.0 |

Please cite the original datasets. Wind (NREL Wind Toolkit) and traffic (METR-LA) are not redistributed here;
obtain them from their original distributors (see the paper's Data Availability section). Code:
https://github.com/EduIntellect/paper2H
