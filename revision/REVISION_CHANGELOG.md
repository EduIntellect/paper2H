# Revision changelog

## Methods and reproducibility

- Recovered and independently verified the exact wind and traffic experimental series by reproducing every submitted persistence and LightGBM horizon error to floating-point tolerance.
- Added canonical H* and exact common-support modules with focused tests.
- Added a pre-specified seasonal-persistence sensitivity producer that stores per-origin forecasts and refuses to calculate Skill on mismatched support.
- Corrected the LightGBM configurations in Methods to match the historical producer scripts; the submitted “remaining parameters are defaults” statement was inaccurate.
- Added a unified data entry point, manifest, expected hashes, and deterministic wind/traffic retrieval and preprocessing.

## Scientific interpretation

- Made the relaxed-gap semantics mathematically explicit.
- Added a dedicated operational interpretation and actionability subsection.
- Added a bounded dynamic-use discussion explaining adaptive selection bias and the need for prospective, prequential, or nested validation.
- Removed causal or invariant language not directly supported by the experiment.
- Removed the ARIMA numerical robustness claims after the audit found no order-selection rationale and a non-horizon-aware wind adapter.

## Presentation

- Regenerated Figures 1 and 2 to eliminate overlap, clipping, and box overflow.
- Added explicit in-text references to Figures 1–3.
- Added verified units and clarified the stored electric-load scale in Table 2.
- Expanded Limitations and rewrote Data Availability around one reproducible entry point.

## Baseline-sensitivity result

- Completed the four-domain seasonal-persistence sensitivity in 2,899.9 seconds on CPU.
- Verified exact common support for every domain, baseline, and horizon, with zero dropped records in every pairwise alignment.
- Reported all outcomes: PM2.5 strict 22→24 on matched support, load 1→1, wind 48→30, and traffic 7→14; relaxed reach is unchanged, with the endpoint-coincidence limitation stated explicitly.

## Final validation

- Passed 39 focused tests covering H* semantics, seasonal information availability, common support, and summary generation.
- Compiled a 23-page revised manuscript with no undefined citations/references or overfull boxes and visually inspected every page.
- Final PDF SHA-256: `bca5fe7cf846be29745f66a16913246e8dce7b98710cf206dd4176d8c7b2bb20`.
