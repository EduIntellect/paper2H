# RMSE sensitivity check

## Purpose
Check whether the qualitative domain-level skill-profile classification remains stable when `Skill(h)` is recomputed with RMSE instead of MAE, keeping datasets, models, horizon grids, forecast origins, and persistence baselines fixed.

## Protocol kept fixed
- Same cleaned datasets used in the current manuscript experiments.
- Same forecasting models already used in the main experiments: PM2.5 moving average (`w=3`), load LightGBM, wind LightGBM, traffic LightGBM.
- Same horizon grids: PM2.5 `h=1..48`, Load `h=1..7`, Wind `h=1..48`, Traffic `h=1..72`.
- Same persistence baseline.
- Same evaluation logic as the current scripts; only the horizon-wise error aggregation inside `Skill(h)` was changed from MAE to RMSE.

## Domains checked
- PM2.5
- Load
- Wind
- Traffic

## RMSE-based descriptor results
| Domain | H*(relax) | H*(strict) | [h_start, h_end] | Sign changes |
|---|---:|---:|---|---:|
| PM2.5 | 48 | 18 | [31,48] | 3 |
| Load | 3 | 3 | [1,3] | 1 |
| Wind | 48 | 48 | [1,48] | 0 |
| Traffic | 72 | 63 | [10,72] | 2 |

## Comparison with MAE-based results
| Domain | MAE-based descriptors | RMSE-based descriptors | Comparison |
|---|---|---|---|
| PM2.5 | `H*(relax)=48`, `H*(strict)=13`, `[36,48]`, sign changes `=1` | `H*(relax)=48`, `H*(strict)=18`, `[31,48]`, sign changes `=3` | Late-horizon recovery remains the dominant pattern. RMSE shifts the longest positive block earlier and slightly lengthens it, but does not remove the delayed-recovery structure. |
| Load | `H*(relax)=1`, `H*(strict)=1`, `[1,1]`, sign changes `=1` | `H*(relax)=3`, `H*(strict)=3`, `[1,3]`, sign changes `=1` | This is a material change. Under RMSE the load series no longer looks like a one-day-only positive-skill case; it keeps a short contiguous positive interval through day 3. |
| Wind | `H*(relax)=48`, `H*(strict)=48`, `[1,48]`, sign changes `=0` | `H*(relax)=48`, `H*(strict)=48`, `[1,48]`, sign changes `=0` | No change. The wind profile remains fully positive and fully contiguous across the full evaluated range. |
| Traffic | `H*(relax)=72`, `H*(strict)=7`, `[46,52]`, sign changes `=19` | `H*(relax)=72`, `H*(strict)=63`, `[10,72]`, sign changes `=2` | This is a material change. Under RMSE the traffic profile is no longer strongly fragmented; it becomes a long delayed positive interval with only minor early interruptions. |

## Does the qualitative profile type change?
- PM2.5: keeps the late-recovery profile type.
- Load: changes materially from a one-day-only positive-skill case to a short contiguous positive interval through day 3.
- Wind: keeps the fully positive contiguous profile type.
- Traffic: changes materially from fragmented to largely contiguous after an initial negative segment.

## Safe wording for the appendix
Replacing MAE with RMSE does not leave all domain-level profile types unchanged. PM2.5 remains a late-recovery case and wind remains fully positive across the evaluated range, but load and traffic change materially under RMSE. In load, the positive-skill interval extends from day 1 only to days 1--3. In traffic, the MAE-based fragmented profile becomes a much longer near-contiguous positive interval under RMSE (`[10,72]`). Therefore, qualitative cross-domain conclusions are only partially stable to the choice of error metric, and this sensitivity should be stated explicitly in the appendix rather than framed as universally negligible.
