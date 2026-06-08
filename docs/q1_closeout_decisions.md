# Q1 Closeout Decisions

Date: 2026-06-01

## Decisions

- Manuscript source of truth: Overleaf.
- Local `paper/paper2_draft.tex`: historical draft unless synchronized from Overleaf.
- Paper scope: six domains.
- Target level: Q1.
- Primary contribution: operational evaluation descriptors for baseline-relative
  predictability horizons, not a new forecasting model.

## Domains

- PM2.5 air quality
- electric load
- wind speed
- traffic speed
- PM10 Madrid
- PM10 Barcelona

## Must stay in the final paper

- Leakage-free rolling-origin evaluation.
- Train-only preprocessing.
- Persistence baseline.
- Horizon-wise skill curves.
- `H*(relax)` and `H*(strict)` with interval locations.
- DM/BH evidence where available.
- Metric sensitivity, especially MAE versus RMSE.
- Discussion of baseline competitiveness.

## Do not add

- New model families unless needed for a narrow robustness check.
- Probabilistic forecasting.
- Variance-retention diagnostics from the PM10 variance paper.
- Claims that H* is a universal system constant independent of baseline, metric,
  model, data frequency, and protocol.

## Cleanup policy

- Keep Overleaf-ready figures in `figures/overleaf_export/`.
- Keep reproducible numeric summaries in `results/`.
- Keep large public raw datasets local or externally documented; they are not
  submission artifacts.
- Every manuscript claim should map to one committed result table, figure, or
  methodological note.
