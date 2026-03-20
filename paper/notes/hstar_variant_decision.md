# H* Variant Decision for Paper 2

Current Paper 2 formulation:

- H*(relax): maximum evaluated horizon with Skill(h) > 0, allowing intermediate non-positive gaps.
- H*(strict): length of the longest contiguous interval [h_start, h_end] such that Skill(h) > 0.
- Report h_start and h_end explicitly.

## Rationale

- PM2.5 may show late positive recovery after a long negative interval, so H*(relax) captures recoveries while H*(strict) captures only contiguous useful predictability.
- Wind may show negative skill at the shortest horizons and then a long contiguous positive interval, which would be badly represented by a strict-from-h=1 definition.
- Therefore, Paper 2 reports H*(relax), H*(strict), and explicit h_start/h_end across domains.
