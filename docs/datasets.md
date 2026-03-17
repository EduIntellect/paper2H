# Datasets

This project evaluates predictability horizons across multiple real-world systems using public time series datasets.

## Domains and datasets

| Domain | Dataset | Variable | Experimental frequency |
|---|---|---|---|
| Air quality | Beijing PM2.5 dataset | PM2.5 concentration | hourly |
| Energy | UCI Electricity Load Diagrams 2011–2014 | aggregate electricity load | daily |
| Wind | NREL Wind Toolkit | wind speed | hourly |
| Traffic | PeMS / METR-LA | traffic flow | 5-min |

These datasets provide complementary regimes — atmospheric chemistry, electricity demand, wind fields, and traffic systems — for testing horizon-dependent forecast skill under a common leakage-free evaluation protocol.

## Dataset decisions currently fixed

### Air quality
- **Dataset:** Beijing PM2.5 dataset
- **Variable:** PM2.5 concentration
- **Frequency:** hourly

### Energy
- **Dataset:** UCI Electricity Load Diagrams 2011–2014
- **Source:** UCI Machine Learning Repository
- **Original data:** 370 client load series at 15-minute resolution
- **Experimental series:** total aggregate load across all clients
- **Experimental frequency:** daily
- **Stable analysis window start:** 2013-03-06

### Wind
- **Dataset:** NREL Wind Toolkit
- **Variable:** wind speed
- **Frequency:** hourly
- **Status:** planned

### Traffic
- **Dataset:** PeMS / METR-LA
- **Variable:** traffic flow
- **Frequency:** 5-min
- **Status:** planned

## Rationale for the energy-domain choice

The original PJM plan was discarded for reproducibility reasons.
The project now uses **UCI Electricity Load Diagrams 2011–2014** as the public energy benchmark.

Within UCI Electricity, the selected experimental representation is the **daily aggregate series**, not an individual client series, because:

- it provides a more stable and interpretable signal,
- it is more comparable to the aggregate operational framing used in air-quality forecasting,
- and the diagnostic comparison showed better regularity and stronger medium-lag autocorrelation than a fixed individual client.

The raw UCI series contains many initially inactive clients, so the aggregate series is not constructed from the beginning of 2011.
Instead, the experimental window starts at the first stable coverage period, fixed here as **2013-03-06**.
