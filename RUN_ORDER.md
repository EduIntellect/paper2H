# Execution Order Guide — paper2H Re-run & Replication

This file outlines the exact order in which to execute scripts in the repository to rebuild all clean datasets, re-run all baseline-relative evaluation experiments (all models across all 6 domains), and regenerate all figures and LaTeX tables.

---

## Step 1: Install Dependencies
Ensure you have the required packages installed from the root directory:
```bash
pip install -r requirements.txt
```

---

## Step 2: Data Preprocessing (Optional)
Preprocessed/cleaned datasets are already versioned in the repository for convenience. If you wish to rebuild them from the raw files (documented in `docs/data_external.md`), run:
```bash
# 1. Aggregate daily electric load series
python3 src/aggregate_uci_electricity.py

# 2. Resample METR-LA traffic speed data
python3 src/prepare_traffic_data.py

# 3. Clean wind hourly series
python3 src/prepare_nrel_wind_data.py
```

---

## Step 3: Run Primary Model Evaluation (Ridge, LightGBM, ExtraTrees)
Evaluate the three primary model classes across all domains using the rolling-origin protocol:
```bash
# 1. Runs PM2.5, Electric Load, Wind, and Traffic domains
python3 experiments/run_all_domains.py

# 2. Runs PM10 Madrid domain
python3 experiments/run_pm10.py

# 3. Runs PM10 Barcelona domain
python3 experiments/run_pm10_bcn.py
```

---

## Step 4: Run Expansion Model Evaluation (KNN, MLP)
Add KNN and MLP estimators to the evaluation outputs for all six domains:
```bash
python3 experiments/run_new_models.py pm25
python3 experiments/run_new_models.py load
python3 experiments/run_new_models.py wind
python3 experiments/run_new_models.py traffic
python3 experiments/run_new_models.py pm10
python3 experiments/run_new_models.py pm10_bcn
```

---

## Step 5: Run Robustness/Sensitivity Checks (ARIMA)
Generate the protocol-matched ARIMA(2,0,0) validation results for wind and traffic:
```bash
# 1. Wind ARIMA evaluation
python3 experiments/wind_arima_canonical_predictability.py

# 2. Traffic ARIMA evaluation
python3 experiments/traffic_arima_canonical_predictability.py
```

---

## Step 6: Consolidate Results and Regenerate Figures
Compile all individual metrics into final output tables and regenerate figures for the manuscript:
```bash
# 1. Merges predictions, calculates DM significance, builds summaries, and plots all 6 domains
python3 src/rebuild_all_results.py

# 2. Plots style-standardized conceptual figures
python3 src/export_overleaf_figures.py
```
This final step outputs the LaTeX Table 3 equivalent values directly to the terminal, updates `results/hstar_summary.csv` and `results/unified_results_table.csv`, and writes the final `.pdf` and `.png` plots to `figures/overleaf_export/`.
