# Canonical data recovery and A1 linkage audit

Date: 2026-09-18

Scope: recovery and read-only audit of the canonical wind and traffic inputs.
No ARIMA fit was executed and no prediction or result artifact was rewritten.

## Recovery procedure

The raw inputs were recovered from the historical local project copy and the
canonical CSVs were regenerated with the documented preparation scripts:

```bash
python src/prepare_nrel_wind_data.py \
  --input data/nrel_wind_toolkit_hourly_raw.csv \
  --output data/wind_hourly_clean.csv

python src/prepare_traffic_data.py \
  --input data/metr-la.h5 \
  --output data/traffic_hourly_clean.csv \
  --sensor 773869
```

Each regenerated CSV was byte-identical to two independently located local
copies (the historical project copy and its recoverable trash copy).

## Integrity and structure

| Domain | Canonical SHA-256 | Observations | Interval | Frequency | Duplicate timestamps | Missing timestamps | Missing values | Forward fills |
|---|---|---:|---|---|---:|---:|---:|---:|
| Wind | `8f094e6437b50b5fd6837bfe43ad6f8a262bf5a9eec84472f2062eaac780a309` | 8,760 | 2019-01-01 00:00 to 2019-12-31 23:00 | hourly | 0 | 0 | 0 | 0 |
| Traffic | `50fb3f411b7521cf72fc87e5660ce2809df67c9507619a6578d4d42e925d479c` | 2,856 | 2012-03-01 00:00 to 2012-06-27 23:00 | hourly | 0 | 0 | 0 | 0 |

Raw-input checks:

- Wind: 8,760 hourly rows; no invalid or duplicate timestamps, missing target
  values, or non-hourly steps.
- Traffic: 34,272 five-minute rows for sensor `773869`; no invalid or
  duplicate timestamps, missing sensor values, or non-five-minute steps. The
  documented hourly mean produced 2,856 nonempty hourly bins.

Raw-input SHA-256 values observed during recovery:

- `nrel_wind_toolkit_hourly_raw.csv`:
  `92194496784fbacb86ef68856488d1c270f7c339abbfa92e2f2cca6732aa3542`
- `metr-la.h5`:
  `64784b76d6fb8ec9bff4b6decafb354da2bb37840468fdccee5044e511277c05`

## Linkage to A1 predictions

The audit treated `results/wind_predictions_all.csv` and
`results/traffic_predictions_all.csv` as the A1 prediction artifacts. For
every row it checked:

- `origin_timestamp == canonical_timestamp[origin_idx]`;
- `y_true == canonical_value[origin_idx + horizon]`;
- `y_pred_baseline == canonical_value[origin_idx]`;
- indices are in bounds and `(model, horizon, origin_idx)` keys are unique.

| Domain | A1 rows | Models | Timestamp mismatches | Baseline mismatches | Exact `y_true` mismatches |
|---|---:|---:|---:|---:|---:|
| Wind | 84,290 | 5 | 0 | 0 | 0 |
| Traffic | 37,335 | 5 | 0 | 0 | 15 |

The 15 traffic mismatches are repeated appearances (five models at three
origin/horizon pairs) of the same target value. The A1 file serializes it as
`22.25300925925925`, while the recovered canonical CSV parses as
`22.253009259259255`. The maximum absolute difference is
`3.552713678800501e-15`; all 15 pass an absolute tolerance of `1e-12`.
There are no timestamp, support, or source-series ambiguities.

## Decision under the predeclared criterion

Classification: **repairable and documentable difference**.

The canonical inputs are recovered and unambiguously linked to A1. Wind is an
exact match. Traffic has a serialization-only one-ULP discrepancy in 15
`y_true` cells, so the strict byte/numeric-exact criterion is not yet met.
Before freezing the common-support protocol, rebuild or normalize the affected
traffic A1 rows and their directly derived error/summary artifacts from the
recovered canonical CSV. This repair does not require refitting any forecasting
model. ARIMA execution remains unauthorized pending that repair and a final
zero-mismatch linkage check.
