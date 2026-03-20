Building on the preliminary H* framing introduced in Paper 1, Paper 2 adopts a two-variant operational definition to handle heterogeneous, non-monotonic empirical skill curves across domains.

Current Paper 2 formulation:

- H*(relax): maximum evaluated horizon with Skill(h) > 0, allowing intermediate non-positive gaps.
- H*(strict): length of the longest contiguous interval [h_start, h_end] such that Skill(h) > 0.
- Report h_start and h_end explicitly.

This preserves the original interpretation of H* as an operational predictability horizon while separating late-horizon recoveries from contiguous operational usefulness.
