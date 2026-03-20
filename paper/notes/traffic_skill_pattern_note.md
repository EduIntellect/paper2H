# Traffic Skill Pattern Note

In the METR-LA traffic-speed experiment (sensor `773869`), the empirical `Skill(h)` curve is fragmented rather than smoothly monotonic.

Reported values remain:
- `H*(relax) = 71`
- `H*(strict) = 22`
- longest contiguous positive interval `[h_start, h_end] = [50, 71]`
- first positive interval `[4, 23]`

Interpretation:
- traffic exhibits a fragmented `Skill(h)` profile;
- useful positive skill emerges early at `[4, 23]`;
- the longest contiguous positive-skill interval appears later at `[50, 71]`.

This pattern does not require redefining `H*(strict)`, but it supports reporting the first positive interval descriptively when curves are fragmented.

The periodic dips at `h=24` and `h=48` are consistent with the competitiveness of daily-lag persistence in traffic speed, not a modeling artifact.
