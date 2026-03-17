# Wind domain plan for Paper 2

## Goal

Add the wind domain as the next cross-domain predictability experiment in Paper 2.

## Dataset target

- **Dataset:** NREL Wind Toolkit
- **Variable:** wind speed
- **Experimental frequency:** hourly
- **Status:** planned

## Rationale

The wind domain is intended to provide a third contrastive forecasting setting after PM2.5 and energy.

It is suitable for Paper 2 because:

- it is physically different from air quality and electricity demand,
- it introduces a meteorological forecasting regime,
- and it helps test whether operational predictability horizons remain short, long, or highly domain-dependent under the same evaluation protocol.

## Planned protocol

The wind experiment must follow the same core rules already fixed in Paper 2:

- leakage-free temporal validation,
- rolling-origin evaluation,
- explicit persistence baseline,
- horizon-dependent skill computation,
- final estimation of formal and contiguous H*.

## Pending practical decision

Before implementing the experiment, the raw wind dataset and exact target series must be fixed.

The next concrete task is:

1. choose the exact NREL Wind Toolkit source file or subset,
2. define the canonical schema,
3. place the raw input in `data/`,
4. create the first wind experiment script.

## Immediate next step

Find or prepare the raw wind input file that will be used as the canonical starting point for the wind domain.
