# PM2.5 Closure Status (Paper 2, Phase 1)

The PM2.5 domain is considered closed for Paper 2 Phase 1. The PM2.5 experimental package includes reproducible experiment code, generated outputs, comparison figures, and associated interpretive/methodological notes. Evaluation is implemented with a leakage-free, time-ordered protocol.

H* reporting in this domain follows the current Paper 2 formulation:
- H*(relax): maximum evaluated horizon with Skill(h) > 0, allowing intermediate non-positive gaps.
- H*(strict): length of the longest contiguous interval [h_start, h_end] such that Skill(h) > 0.
- Report h_start and h_end explicitly.

For PM2.5 (`results/pm25_real_skill.csv`), the reported values are H*(relax)=48, H*(strict)=13, with [h_start, h_end]=[36,48]. The primary domain-level finding remains that strong temporal persistence makes the baseline highly competitive at short and medium horizons, while positive skill appears only in a late contiguous segment.
