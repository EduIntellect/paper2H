## Domain
wind

## Models compared
- Existing run: LightGBM (`results/wind_skill.csv`, `results/wind_errors.csv`)
- Robustness run: ARIMA `(2,0,0)` using the canonical wind evaluation codepath (`results/wind_arima_skill.csv`, `results/wind_arima_errors.csv`)

Note: SARIMA was attempted first for this check, but in this repo/runtime it was too heavy/unstable for a practical full 48-horizon rolling run. Per protocol fallback, ARIMA with fixed order `(2,0,0)` was used.

## Same protocol confirmation
The robustness run reused the canonical wind pipeline directly by calling `evaluate_rolling_origin_lightgbm(...)` from `experiments/wind_predictability.py` and only swapping the estimator object (LightGBM -> ARIMA adapter).

Explicit parity checks:
- origins match the LightGBM wind experiment: yes (same `first_origin`, `last_origin`, stride, and max-origins truncation because the same function generated them)
- horizon set matches: yes (`h = 1..48`)
- baseline matches: yes (persistence, `y_hat_baseline = y_t` at each origin)
- skill formula matches: yes (`Skill(h) = 1 - MAE_model(h)/MAE_persistence(h)`)
- output semantics match: yes (`errors.csv` with `baseline_mae/model_mae`, `skill.csv` with `skill` by horizon, horizon-indexed plots, and H* summary text)

## Result summary
LightGBM (existing):
- H*(relax) = 48
- H*(strict) = 48
- Longest contiguous positive interval = [1, 48]
- Sign changes in Skill(h): 0 (none)
- Pattern: contiguous positive regime, no late emergence

ARIMA (new robustness run):
- H*(relax) = 48
- H*(strict) = 48
- Longest contiguous positive interval = [1, 48]
- Sign changes in Skill(h): 0 (none)
- Pattern: contiguous positive regime, no late emergence

Difference observed:
- Magnitude differs (ARIMA skill is generally lower-amplitude than LightGBM), but the qualitative shape/morphotype descriptors are unchanged.

## Does the morphotype replicate?
Yes. The wind-domain morphotype replicates under ARIMA: both models show a single contiguous positive-skill regime across the full horizon range with identical H* descriptors and no sign changes.

## Interpretation for Paper 2
Initial evidence supports that this wind-domain Skill(h) morphotype reflects domain structure more than a LightGBM-specific artifact.

## Reviewer-facing takeaway
Under a strict protocol-matched robustness check (same rolling-origin evaluation, persistence baseline, horizons, and skill definition), replacing LightGBM with a fixed-order ARIMA preserves the wind-domain morphotype exactly in descriptor space: `H*(relax)=48`, `H*(strict)=48`, interval `[1,48]`, and zero sign changes. This supports the claim that the observed wind pattern is domain-driven rather than model-specific, at least across these two model classes.
