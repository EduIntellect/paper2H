# Response to the Editor and Reviewers

We thank the Editor and both Reviewers for comments that led us to strengthen the manuscript’s reproducibility, operational interpretation, and reporting. We audited the submitted four-domain source and its historical producer artifacts before changing any result. The revised package now preserves per-origin forecasts, verifies exact common support before calculating relative skill, and provides a single data-reproduction entry point.

## Editor

> Please report results precisely, remove overstated conclusions, and explain limitations completely.

Response: We reconstructed and verified the wind and traffic inputs by reproducing every submitted persistence and LightGBM horizon error to floating-point tolerance. We corrected the actual fixed LightGBM configurations in “Models” (pp. 10–11), removed unsupported model-invariance and causal language, and expanded “Limitations” (p. 19) to state baseline, metric, Hmax, dataset, model-configuration, and validation-protocol conditionality. We also state explicitly that a dynamic H* controller was not prospectively evaluated. The new “Alternative-baseline sensitivity” subsection (pp. 16–17) and Table 4 report the additional analysis.

## Reviewer 1

> 1. In the operational definitions, use a colon before the explanations of the relaxed and strict horizons.

Response: We changed both labels from a period to a colon in “Operational Predictability Horizon” (Section 3.1, p. 6).

> 2–3. Equation (5) and the surrounding text should explicitly state that the relaxed horizon permits non-positive skill at intermediate steps.

Response: We now define $\mathcal H^+=\{h\in\mathcal H:\mathrm{Skill}(h)>0\}$ and $H^*(\mathrm{relax})=\max(\mathcal H^+\cup\{0\})$ in Section 3.1 (p. 6). The text explicitly states that intermediate horizons with non-positive skill may lie inside the relaxed reach but are not themselves interpreted as skillful. We verified this semantics with executable tests, including an intermediate gap and delayed onset.

> 4. Maintain units throughout Table 2.

Response: Table 2 (p. 11) now identifies PM2.5 in µg m−3, wind speed in m s−1, and traffic speed in mph. For electric load, we clarify that the stored experimental target is the sum of 15-minute kW readings and that division by four expresses the same daily aggregate in kWh; this follows the source metadata and the actual aggregation script.

> 5. Figures 1–3 are not correctly referenced in the text.

Response: We added explicit textual references to the conceptual H* figure (Fig. 1, p. 7), the rolling-origin protocol figure (Fig. 2, p. 9), and the first empirical skill figure (Fig. 3, p. 12).

> 6. Evaluate baseline choices beyond persistence.

Response: Before inspecting any comparative result, we pre-specified seasonal persistence as a transparent cross-domain sensitivity baseline: 24-hour seasonality for hourly domains and 7-day seasonality for daily load. LightGBM, persistence, and seasonal persistence were regenerated on identical forecast origins, and exact equality of origin, target timestamp, horizon, and y_true was asserted before Skill was calculated. No records were dropped during alignment. On the matched support, seasonal persistence changed Hstrict from 22 to 24 in PM2.5, left load at 1, changed wind from 48 to 30, and changed traffic from 7 to 14; corresponding longest intervals are reported in Section 10.4 and Table 4 (pp. 16–17). Hrelax was unchanged, but we explicitly note that the hourly endpoints are multiples of the seasonal period where seasonal and ordinary persistence coincide, so this is not interpreted as baseline invariance.

> 7. Explain why ARIMA(2,0,0) was selected and whether ACF was examined.

Response: We agree that the original manuscript did not document this choice adequately. Our repository and Git-history audit found no evidence that the AR(2) order was selected from ACF/PACF, AIC/BIC, grid search, auto-ARIMA, or validation. We therefore do not make such a claim. The audit also found that the historical wind adapter requested a one-step ARIMA forecast at every evaluated horizon, so that comparison did not implement the claimed h-step protocol. We removed the ARIMA numerical robustness claims from “Models” and the Wind/Traffic result sections rather than retaining an unsupported rationale or silently changing the experiment. The requested robustness evidence is instead supplied by the prospectively specified baseline sensitivity on exact common support (Section 10.4, pp. 16–17).

> 8–9. Explain the practical utility of relaxed and strict H* and what they add beyond fixed-horizon summaries.

Response: A new “Operational interpretation and actionability” subsection (Section 3.2, p. 7) defines relaxed H* as the outer extent at which any positive baseline-relative skill is still observed and strict H*, with its interval location, as the longest continuous positive-skill decision window. We explain that fixed-horizon summaries do not identify delayed onset, gaps, fragmentation, interval location, continuity, or late recovery.

> 10. Could H* dynamically decide which horizons to forecast, and could this create feedback or overfitting?

Response: We added a substantive but bounded discussion (Section 11, p. 18). H* may inform a policy estimated on historical validation data, frozen for prospective deployment, and later updated using only realised past errors. We explicitly warn that estimating H*, selecting horizons, and evaluating on the same errors creates adaptive selection bias. A dynamic controller would require prospective, prequential, or nested validation and is not claimed as validated here.

## Reviewer 2

> 1. Explain the actionability of the findings more explicitly.

Response: We added the dedicated operational interpretation subsection described above, distinguishing outer positive reach from the longest continuous useful interval and limiting dynamic deployment claims to a future, separately validated policy.

> 2. Figures 1 and 2 are not referenced correctly.

Response: Both figures are now explicitly introduced and interpreted in the text (Fig. 1, p. 7; Fig. 2, p. 9).

> 3. In Figure 1, the curve overlaps text or annotations.

Response: We regenerated Figure 1 with protected callout boxes and separated label placement. The mathematical meaning is unchanged, and the rendered PDF (p. 7) was checked visually.

> 4. In Figure 2, text does not fit inside the boxes.

Response: We regenerated Figure 2 with larger boxes and wrapped text, eliminating overflow and clipping in the rendered PDF (p. 9).

> 5. If possible, evaluate alternative baselines beyond persistence.

Response: We performed the same pre-specified seasonal-persistence sensitivity described in our response to Reviewer 1, using exact common support and retaining results regardless of direction. The new table reports all four domains, both baselines, common-origin counts, Hrelax, Hstrict, and interval locations.

> 6. Data Availability should reduce the need to visit four or five separate sources and should clearly state whether files are cached in the code repository.

Response: The replication package now provides one entry point (`data/README.md`) and a machine-readable manifest with source identifiers, exact filenames, SHA-256 hashes, preprocessing scripts, and redistribution status. Exact PM2.5 and load inputs are tracked. Wind and traffic are deterministically retrieved, checksum-verified, and processed by one script; we do not claim they are repository-cached. The manuscript points to this entry point in “Data Availability” (p. 21).

> 7. Explain the reason for ARIMA(2,0,0).

Response: As noted above, no documented order-selection rationale exists, and the wind implementation did not satisfy the stated h-step protocol. We removed the ARIMA robustness claims and state this transparently rather than inventing an ACF/PACF justification.
