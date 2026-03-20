In the PM2.5 Beijing experiment, H* reporting follows the current Paper 2 variant formulation:

- H*(relax): maximum evaluated horizon with Skill(h) > 0, allowing intermediate non-positive gaps.
- H*(strict): length of the longest contiguous interval [h_start, h_end] such that Skill(h) > 0.
- Report h_start and h_end explicitly.

Using `results/pm25_real_skill.csv`, PM2.5 yields H*(relax)=48 and H*(strict)=13 with [h_start, h_end]=[36,48]. This captures the late positive-skill recovery while preserving a contiguous operational estimate.

The evaluation pipeline is leakage-free by construction: forecasts are generated in time order without random splits, horizon-specific targets are defined as `shift(-h)`, and baseline/model errors are computed on identical valid timestamps using a shared mask. This alignment enforces fair, temporally consistent comparison across horizons.
