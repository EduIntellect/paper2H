# Energy domain decision for Paper 2

## Final decision

The energy domain for Paper 2 is fixed to **UCI Electricity Load Diagrams 2011–2014**.

The selected experimental representation is the **daily aggregate load series**, not an individual client series.

## Why PJM was discarded

The original PJM plan was abandoned for reproducibility reasons.

Using PJM Data Miner raw data would introduce redistribution and public-reproducibility issues.
Because Paper 2 is explicitly built around public and reproducible cross-domain experiments, the energy domain must rely on a dataset that can be downloaded and reused without that friction.

## Why UCI was selected

UCI Electricity Load Diagrams 2011–2014 provides:

- a public benchmark dataset,
- a well-known forecasting use case,
- regular load time series,
- and a clean fit with the Paper 2 cross-domain design.

## Aggregate vs fixed client

A diagnostic comparison will be run between:

- the **aggregate daily series**
- a **fixed client series** (`MT_001`)

The aggregate series is the preferred candidate because it is more stable and methodologically more comparable to the operational framing used in PM2.5 / PM10 forecasting.

## Coverage correction

The raw UCI dataset cannot be aggregated directly from early 2011 because many clients are initially inactive.
Those zeros do not represent true zero consumption; they represent incomplete client activation.

Therefore, the aggregate series must only be constructed after stable coverage is reached.

## Stable analysis rule

The stable start date is defined as the first day from which coverage stays at or above **90% active clients for 7 consecutive days**.

## Preliminary diagnostic protocol

Before computing skill(h), the first diagnostic pass will use:

1. CV
2. ACF lag 1-7
3. RMSE persistence h=1..7
4. Relative persistence RMSE by horizon

No additional forecasting model is introduced in this first pass.
Skill(h) and H* will be computed only after the energy series representation is fixed.

## Moving-average screening result

- **Formal H\***: 6
- **Contiguous operational H\*** from h=1: 0
- **Interpretation**: non-contiguous positive skill region

This confirms that the aggregate energy series contains exploitable structure, but the moving-average baseline does not outperform persistence in a contiguous operational sense from short horizons.

## Final energy-domain result

After adding weekly structure features (lag-14 and day-of-week), the rolling-origin LightGBM experiment yields:

- **Formal H\***: 1
- **Contiguous H\***: 1

### Interpretation
Positive skill appears only at the 1-day horizon and disappears immediately afterwards.

This means that the UCI aggregate daily energy series is not a case of H*=0 in the strict formal sense, but rather a case of **extremely short operational predictability**, where persistence remains the dominant baseline beyond 1 day.

This makes the energy domain a useful cross-domain contrast against PM2.5, where much longer predictability horizons were observed.

