# Wind data contract for Paper 2

## Goal

Define the canonical input format for the wind domain before implementing the experiment.

## Expected raw source

- **Dataset family:** NREL Wind Toolkit
- **Target variable:** wind speed
- **Experimental frequency:** hourly

## Canonical schema

The cleaned input used by the experiment must follow:

- `timestamp`
- `value`

where:

- `timestamp` is a strictly increasing hourly datetime index
- `value` is the wind-speed target series used in the experiment

## Requirements

- no duplicated timestamps
- no missing timestamps inside the selected interval
- no future-derived preprocessing
- single univariate target series only

## Pending decision

Before creating the experiment script, we still need to fix:

1. the exact raw source file,
2. the selected location / point / station,
3. the raw-to-canonical conversion script.

## Immediate next step

Place the chosen raw wind input file inside `data/` and then implement the conversion to the canonical schema.
