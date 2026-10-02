# Traffic A1 deterministic serialization repair

Date: 2026-09-18

Scope: normalization of the 15 verified Traffic A1 `y_true` cells and regeneration of their tabular descendants only. No model was fitted; no prediction, hyperparameter, split, temporal support, or protocol setting was changed. The ~25,872 fits remain unauthorized.

- Canonical target: `2012-04-06 09:00:00`; parsed value `22.253009259259255`; CSV token `22.253009259259258`.
- Modified truth cells: 15.
- Maximum pre-repair absolute difference: 3.5527136788005009e-15.
- Post-repair exact canonical mismatches: 0.
- `domain`, `model`, `horizon`, `origin_idx`, `origin_timestamp`, `y_pred`, and `y_pred_baseline`: byte-for-byte identical by CSV field.
- `y_pred` and `y_pred_baseline`: numerically identical (`numpy.array_equal`).

## Updated artifact

- `results/traffic_predictions_all.csv`

All tabular descendants (`traffic_skill_all.csv`, `dm_tests_all.csv`, `hstar_all_domains.csv`, `hstar_summary.csv`, and `unified_results_table.csv`) were recomputed/validated and remained byte-identical. Therefore no aggregate metric, H* descriptor, profile, figure input, or protocol conclusion changed.


## Audit files

- `docs/traffic_a1_serialization_repair_cells_2026-09-18.csv`: all 15 cells, old/canonical values, absolute differences, and old/new errors.
- `docs/traffic_a1_serialization_repair_metrics_2026-09-18.csv`: affected model/horizon metrics before and after.

## SHA-256 before / after

| Artifact | Before | After |
|---|---|---|
| `traffic_predictions_all.csv` | `1c37b99cf7b03496e3ba23b923e5eca4cf96105c9c64c210b3779ac61d8c3886` | `7820e5a8ee98cbdcb6f881982bf04fea8547681de2b2eba2e8fc3b8b6c3e685d` |
| `traffic_skill_all.csv` | `3ad87393c7bbda1c534092817c70a67c2d6011af16706730b7868ad162b057f2` | `3ad87393c7bbda1c534092817c70a67c2d6011af16706730b7868ad162b057f2` |
| `dm_tests_all.csv` | `ac1a91a7d14dcf49fdd2e11bb25bbb6b4b191f1a557acef0f66b9294831283e8` | `ac1a91a7d14dcf49fdd2e11bb25bbb6b4b191f1a557acef0f66b9294831283e8` |
| `hstar_all_domains.csv` | `ed56873d51ded1bab7c6ab467143e7e3a99b4abe227ead150b6d703af39b109f` | `ed56873d51ded1bab7c6ab467143e7e3a99b4abe227ead150b6d703af39b109f` |
| `hstar_summary.csv` | `3d0aa069ec0fb82cbfc19ba6b460f645a45d18dba4b696dbc976e9953a40fdcd` | `3d0aa069ec0fb82cbfc19ba6b460f645a45d18dba4b696dbc976e9953a40fdcd` |
| `unified_results_table.csv` | `eac03818b5f61651b6e1d4af7969ee4bcac385951b4dbb2ea3a62263b11ee056` | `eac03818b5f61651b6e1d4af7969ee4bcac385951b4dbb2ea3a62263b11ee056` |
