## Domain
traffic (METR-LA traffic-speed series, sensor `773869`)

## Models compared
- Existing run: LightGBM (`results/traffic_skill.csv`, `results/traffic_errors.csv`)
- Second model: ARIMA `(2,0,0)` in canonical pipeline (`results/traffic_arima_skill.csv`, `results/traffic_arima_errors.csv`, `results/traffic_arima_hstar.txt`)

Runtime note:
- ARIMA `(2,0,0)` canonical run completed successfully in this environment.
- Observed runtime for the full run: ~4 min 24 s.

## Same protocol confirmation
The second-model run reuses the canonical traffic evaluation codepath from `experiments/traffic_predictability.py` by injecting only the estimator class and keeping the same evaluation function (`evaluate_rolling_origin_lightgbm(...)`), with horizon-aligned ARIMA forecasting (`steps=h` for each evaluated horizon).

Explicit parity checks (LightGBM vs ARIMA run):
- same target series loader: yes (`load_traffic_series(...)`)
- same horizon set: yes (`h=1..72`)
- same origin generation and slicing: yes (same `first_origin`, `last_origin`, `ORIGIN_STRIDE`, `MAX_ORIGINS_PER_HORIZON`, train-window slicing)
- same baseline: yes (persistence at origin)
- same metric and skill formula: yes (`MAE`, `Skill(h)=1-MAE_model/MAE_persistence`)
- same output semantics: yes (`errors.csv`, `skill.csv`, `hstar.txt`, horizon plots)

## Result summary
LightGBM (existing artifact truth):
- H*(relax) = 72
- H*(strict) = 7
- Longest contiguous positive interval = [46, 52]
- First positive interval = [17, 18]
- Sign changes = 19
- Positive-skill intervals: [17,18], [21,22], [24,28], [34,37], [39,42], [46,52], [56,56], [58,60], [64,67], [69,72]

ARIMA (new robustness run):
- H*(relax) = 72
- H*(strict) = 6
- Longest contiguous positive interval = [38, 43]
- First positive interval = [17, 17]
- Sign changes = 13

Descriptor comparison:
- H*(relax): equal (72 vs 72)
- H*(strict): close but different (7 vs 6)
- Longest interval location: shifted ([46,52] vs [38,43])
- Fragmentation: reduced but still present (19 sign changes vs 13)

## Does the morphotype replicate?
Partial.

Replicates:
- both runs still show eventual positive skill up to long horizons (`H*(relax)=72`).

Does not replicate:
- strict contiguous reach differs (`H*(strict)` shifts from 7 to 6).
- longest positive interval location shifts (`[46,52]` to `[38,43]`).
- fragmentation remains model-sensitive (sign changes drop from 19 to 13, but are still substantial).
- therefore, exact descriptor-space morphotype is not preserved.

## Interpretation for Paper 2
In traffic, relaxed reach is stable under model substitution (LightGBM -> ARIMA: `H*(relax)=72` in both runs), but strict continuity and interval placement are model-sensitive. This supports keeping dual horizon descriptors (`H*(relax)` and `H*(strict)`) plus interval locations and sign-change diagnostics in Paper 2.

## Reviewer-facing takeaway
Using the canonical traffic pipeline with ARIMA `(2,0,0)` as second model, `H*(relax)` is stable (72) while strict continuity remains model-sensitive: `H*(strict)` shifts from 7 (LightGBM) to 6 (ARIMA), longest positive interval shifts from `[46,52]` to `[38,43]`, and sign changes decrease from 19 to 13. This is a partial replication and indicates that relaxed reach can be stable even when strict interval structure and fragmentation differ by model class.
