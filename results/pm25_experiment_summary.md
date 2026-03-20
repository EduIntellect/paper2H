# PM2.5 Real Experiment Summary

- **Skill source:** `results/pm25_real_skill.csv`
- **Horizon range:** `h=1..48`

## Definición operativa

- H*(relax): maximum evaluated horizon with Skill(h) > 0, allowing intermediate non-positive gaps.
- H*(strict): length of the longest contiguous interval [h_start, h_end] such that Skill(h) > 0.
- Report h_start and h_end explicitly.

## H* Variants

- **H*(relax):** `48` (maximum horizon with `Skill(h) > 0`)
- **H*(strict):** `13` (length of the longest contiguous positive-skill interval)
- **H*(time):** `13 h`
- **Longest positive interval:** `[h_start, h_end] = [36, 48]`

The time-based H* field refers to the contiguous positive-skill interval represented by H*(strict), not to H*(relax).

## Interpretation

PM2.5 shows a late positive-skill recovery after a long negative region. This yields a high `H*(relax)` because skill is positive again at long horizons, while `H*(strict)` isolates the contiguous useful segment and avoids interpreting the entire horizon range as operationally predictable.
