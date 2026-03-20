# paper2H

Paper 2 cross-domain predictability experiments.

## Purpose
This repository contains the experimental pipeline, outputs, figures, and research notes for Paper 2 on cross-domain predictability horizons in time series forecasting.

## Status
- Completed domains: PM2.5, electric load
- Current domain: wind
- Next target domain: traffic

## Repository Structure
- `data/`: raw and cleaned canonical inputs
- `experiments/`: domain experiment scripts
- `results/`: real experimental outputs only
- `figures/`: real generated figures only
- `paper/notes/`: methodological and interpretation notes

## Core Methodological Rules
- Leakage-free, time-ordered evaluation
- Explicit baselines
- Real artifacts only
- Canonical cleaned inputs

## Standard Workflow
raw data -> cleaned canonical input -> experiment -> results -> figures -> notes
