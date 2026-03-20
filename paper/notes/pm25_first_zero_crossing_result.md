# PM2.5 Legacy First-Zero-Crossing Note

This file records a legacy diagnostic (`H*_first_zero_crossing=0`) for PM2.5 and is not the canonical Paper 2 reporting standard.

Current Paper 2 formulation:

- H*(relax): maximum evaluated horizon with Skill(h) > 0, allowing intermediate non-positive gaps.
- H*(strict): length of the longest contiguous interval [h_start, h_end] such that Skill(h) > 0.
- Report h_start and h_end explicitly.

Under the canonical formulation for `results/pm25_real_skill.csv`, PM2.5 reports H*(relax)=48 and H*(strict)=13 with [h_start, h_end]=[36,48].
