# DMKD results freeze manifest

Date: 2026-09-30

## Status

The six-domain numerical evidence package is frozen after the deterministic
Traffic A1 serialization repair. This freeze did not fit, tune, or retrain any
model. The approximately 25,872 prospective fits remain unauthorized and were
not executed.

This is a numerical-artifact freeze, NOT an end-to-end scientific protocol
certification or clearance for submission. See
`docs/dmkd_revision_status_2026-09-30.md` for the calendar, preprocessing and
manuscript-version gates discovered by the later read-only audit.

The verification command is:

```bash
/home/fede/repos/hstar/.venv-lightgbm-validation/bin/python \
  src/verify_dmkd_freeze.py
```

Expected result: `DMKD freeze verification: PASS`.

## Acceptance results

- Domains: PM2.5, electric load, wind, traffic, PM10 Madrid, and PM10 Barcelona.
- Primary models: Ridge, LightGBM, ExtraTrees, KNN, and MLP.
- Historical ARIMA artifacts for wind and traffic are preserved but excluded
  from the revised empirical comparisons; order selection and matched support
  are not established.
- Duplicate `(model, horizon, origin_idx)` prediction keys: 0 in every domain.
- Traffic exact canonical `y_true` mismatches: 0.
- Traffic canonical timestamp and persistence-baseline mismatches: 0.
- Traffic `y_pred` changes caused by the repair: 0, byte-for-byte and numerically.
- All aggregate descendants (`traffic_skill_all.csv`, `dm_tests_all.csv`,
  `hstar_all_domains.csv`, `hstar_summary.csv`, and
  `unified_results_table.csv`): byte-identical before/after repair.
- H* descriptors, profile classifications, and BH significance decisions: unchanged.
- Traffic figure comparison: the pre/post PNGs generated in the same environment
  were byte-identical and had no differing pixels; no figure was rewritten.

## Frozen dimensions and hashes

| Artifact | Rows | Columns | SHA-256 |
|---|---:|---:|---|
| `data/pm25_series.csv` | 41,757 | 1 | `09e4164af5159c21ca9bd1b09399173c8e7ab67c1445903a126722e4d576abdf` |
| `results/uci_electricity_daily_aggregate.csv` | 667 | 2 | `7a5675255e1de1cedc1d026004cad13052382843aed9c00d429f186c0f5216d3` |
| `data/wind_hourly_clean.csv` | 8,760 | 2 | `8f094e6437b50b5fd6837bfe43ad6f8a262bf5a9eec84472f2062eaac780a309` |
| `data/traffic_hourly_clean.csv` | 2,856 | 2 | `50fb3f411b7521cf72fc87e5660ce2809df67c9507619a6578d4d42e925d479c` |
| `data/pm10_elx_daily.csv` | 2,922 | 2 | `3d8fff43108c5cbc0480ed9f21173e21e89613cef4c99da5636a3ecd90d6bea0` |
| `data/pm10_bcn_daily.csv` | 2,827 | 2 | `d6ccc9c61b1e8fdec68daa6839645ad8cd01016f1f4cd0f65dc04798fc74bfb3` |
| `results/pm25_predictions_all.csv` | 87,600 | 10 | `ddeea697561d181241e36475aae58c05c81616d6f62c2984bc01f0af4ed055f6` |
| `results/load_predictions_all.csv` | 9,730 | 10 | `98b3cbd4f2b416b24c341e5117863f6a01ee23092a9a5ecf1e3caf1b47451625` |
| `results/wind_predictions_all.csv` | 84,290 | 10 | `dad533f3d7da121b02eb945f757d683add66c1acb47b59db87eb49f55bc0f319` |
| `results/traffic_predictions_all.csv` | 37,335 | 10 | `7820e5a8ee98cbdcb6f881982bf04fea8547681de2b2eba2e8fc3b8b6c3e685d` |
| `results/pm10_predictions_all.csv` | 88,655 | 10 | `20481ab50fff854b8c5eb4924de888110c095e982bea75773d17116565874e75` |
| `results/pm10_bcn_predictions_all.csv` | 85,330 | 10 | `c0b1bf8da9dfa59462f6b422e0856e1cf8aa7989a6813dc6cfccc22865bcbc17` |
| `results/pm25_skill_all.csv` | 240 | 7 | `439f21d475882ddb30488c6e9447374cabd393d927419046dc1842db8eb29fd8` |
| `results/load_skill_all.csv` | 35 | 7 | `2527401d4ec1a612d86c61f89961529a6f540606857bb130931d5276246f443c` |
| `results/wind_skill_all.csv` | 240 | 7 | `740f3f39d364274d6f50d17a2da41a709afe91b4bbca41814d6972c1a7f777cd` |
| `results/traffic_skill_all.csv` | 360 | 7 | `3ad87393c7bbda1c534092817c70a67c2d6011af16706730b7868ad162b057f2` |
| `results/pm10_skill_all.csv` | 35 | 7 | `46e646208708ba31ee254c52a46eb8998852a928d9aab3ca07b1fa2a3a6be738` |
| `results/pm10_bcn_skill_all.csv` | 35 | 7 | `3f011a1a9167862e0d5dcdfcd34b40f41a86acf824afa1999c13e9a86628c7b9` |
| `results/dm_tests_all.csv` | 1,065 | 8 | `ac1a91a7d14dcf49fdd2e11bb25bbb6b4b191f1a557acef0f66b9294831283e8` |
| `results/hstar_all_domains.csv` | 32 | 7 | `ed56873d51ded1bab7c6ab467143e7e3a99b4abe227ead150b6d703af39b109f` |
| `results/hstar_summary.csv` | 32 | 9 | `3d0aa069ec0fb82cbfc19ba6b460f645a45d18dba4b696dbc976e9953a40fdcd` |
| `results/unified_results_table.csv` | 1,065 | 17 | `eac03818b5f61651b6e1d4af7969ee4bcac385951b4dbb2ea3a62263b11ee056` |

Submission figures remain frozen. In particular:

- `fig_skill_traffic.pdf`: `d614c943eabe7185d0bbf147d6a5429c5aa361a8fceac020fcb9017b4467de1b`
- `fig_skill_traffic.png`: `bfe272693367931d302570e2efad44a698b35f0d1e90f6e4a0de2c3e74c90a98`
- `fig_hstar_heatmap.pdf`: `d41281b1c1eef3c925407e31fadab5c73e553dec4787255ab5be51c8622c7acd`
- `fig_hstar_heatmap.png`: `20ed16f920462bf5853892bb372f88f40d5aeb2c8ed3fcf77518e8966af47489`

## Change-control rule

Any later change to a frozen hash must be treated as a new evidence version and
must include a documented reason, a fresh verification report, and explicit
authorization if it involves fitting or tuning. Editorial synchronization may
change prose and packaging, but it must not silently replace these artifacts.
