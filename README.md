# paper2H

Paper 2 cross-domain operational predictability horizons.

## Canonical manuscript

The active manuscript source is Overleaf. Local TeX files in `paper/` are treated
as historical drafts unless explicitly synchronized from Overleaf.

The target submission strategy is Q1. The paper should remain a six-domain
methodological/evaluation paper, not a model-competition paper.

## Scientific scope

Central question:

Can baseline-relative operational predictability horizons describe useful
multi-horizon forecast reach across heterogeneous domains under a shared
leakage-free temporal protocol?

Domains retained for the Q1 version:

- PM2.5 air quality
- electric load
- wind speed
- traffic speed
- PM10 Madrid
- PM10 Barcelona

## Repository structure

- `data/`: local raw and cleaned canonical inputs. Large public datasets are not
  submission artifacts.
- `experiments/`: domain-specific rolling-origin experiment scripts.
- `results/`: committed result summaries and horizon-wise tables used by the paper.
- `figures/`: generated figures, including Overleaf-ready exports.
- `paper/notes/`: methodological decisions, interpretation notes, and audit trail.
- `docs/`: dataset and protocol documentation.

## Core methodological rules

- Rolling-origin temporal evaluation only.
- Preprocessing, scaling, imputation, thresholds, and feature selection must be
  train-only inside each temporal split.
- Persistence is the mandatory reference baseline.
- Skill is reported by horizon as `Skill(h) = 1 - E_model(h) / E_baseline(h)`.
- H* descriptors must report both relaxed reach and contiguous usefulness:
  `H*(relax)`, `H*(strict)`, interval location, and sign-change/fragmentation
  information when relevant.
- Cross-domain claims must separate evaluation method, empirical result, and
  conceptual interpretation.

## Q1 closeout workflow

1. Freeze the Overleaf manuscript as the source of truth.
2. Keep the six-domain scope.
3. Reconcile every Overleaf table/figure with a committed result or figure file.
4. Keep model expansion minimal; use extra models only as protocol-matched
   robustness evidence.
5. Prioritize reproducibility, baseline competitiveness, metric sensitivity, and
   limitations over new experiments.
