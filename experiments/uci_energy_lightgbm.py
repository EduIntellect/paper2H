#!/usr/bin/env python3
"""
Paper 2 — UCI energy LightGBM experiment (rolling-origin validation)

Input:
- results/uci_electricity_daily_aggregate.csv

Forecast setup:
- target series: value
- horizons: 1..7 days
- baseline: persistence
- model: LightGBM regressor
- features: lags 1..7
- metric: MAE
- skill(h) = 1 - MAE_model(h) / MAE_baseline(h)
- validation: rolling-origin (no static split, no leakage)

Outputs:
- results/uci_energy_lightgbm_errors.csv
- results/uci_energy_lightgbm_skill.csv
- results/uci_energy_lightgbm_hstar.txt
- figures/uci_energy_lightgbm_error_vs_horizon.png
- figures/uci_energy_lightgbm_skill_vs_horizon.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
from lightgbm import LGBMRegressor

warnings.filterwarnings("ignore", message="X does not have valid feature names")


DATA_PATH   = Path("results/uci_electricity_daily_aggregate.csv")
RESULTS_DIR = Path("results")
FIG_DIR     = Path("figures")

H_MAX        = 7
MAX_LAG      = 14
TRAIN_WINDOW = 365


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"]).sort_values("timestamp")
    y  = df["value"].values
    n  = len(y)

    horizons     = []
    baseline_mae = []
    model_mae    = []
    skill        = []

    feature_cols = [f"lag_{i}" for i in range(1, MAX_LAG + 1)]

    for h in range(1, H_MAX + 1):
        errors_model    = []
        errors_baseline = []

        for t in range(TRAIN_WINDOW, n - h):
            if t < MAX_LAG:
                continue

            train_rows = []
            for i in range(MAX_LAG, t - h + 1):
                row = [y[i - lag] for lag in range(1, MAX_LAG + 1)]
                row.append(i % 7)
                row.append(y[i + h - 1])
                train_rows.append(row)

            if len(train_rows) < 10:
                continue

            train_feature_cols = feature_cols + ["day_of_week"]
            train_df = pd.DataFrame(train_rows, columns=train_feature_cols + ["target"])
            X_train  = train_df[train_feature_cols]
            y_train  = train_df["target"].values

            x_test_row = {f"lag_{lag}": y[t - lag] for lag in range(1, MAX_LAG + 1)}
            x_test_row["day_of_week"] = t % 7
            x_test = pd.DataFrame([x_test_row], columns=train_feature_cols)

            model = LGBMRegressor(
                n_estimators=100,
                learning_rate=0.05,
                num_leaves=15,
                random_state=42,
                verbosity=-1,
            )
            model.fit(X_train, y_train)

            y_pred = float(model.predict(x_test)[0])
            y_base = float(y[t - 1])
            y_true = float(y[t + h - 1])

            errors_model.append(abs(y_true - y_pred))
            errors_baseline.append(abs(y_true - y_base))

        e_base  = float(np.mean(errors_baseline))
        e_model = float(np.mean(errors_model))
        s       = 1.0 - (e_model / e_base)

        horizons.append(h)
        baseline_mae.append(e_base)
        model_mae.append(e_model)
        skill.append(s)

        print(f"h={h}  baseline_mae={e_base:.1f}  model_mae={e_model:.1f}  skill={s:+.4f}")

    hstar = 0
    for h, s in zip(horizons, skill):
        if s > 0:
            hstar = h

    contiguous_hstar = 0
    for h, s in zip(horizons, skill):
        if s > 0:
            contiguous_hstar = h
        else:
            break

    pd.DataFrame({
        "horizon": horizons,
        "baseline_mae": baseline_mae,
        "model_mae": model_mae,
    }).to_csv(RESULTS_DIR / "uci_energy_lightgbm_errors.csv", index=False)

    pd.DataFrame({
        "horizon": horizons,
        "skill": skill,
    }).to_csv(RESULTS_DIR / "uci_energy_lightgbm_skill.csv", index=False)

    with open(RESULTS_DIR / "uci_energy_lightgbm_hstar.txt", "w", encoding="utf-8") as f:
        f.write(f"formal_hstar={hstar}\n")
        f.write(f"contiguous_hstar={contiguous_hstar}\n")

    plt.figure(figsize=(8, 5))
    plt.plot(horizons, baseline_mae, "o-", label="Persistence")
    plt.plot(horizons, model_mae,    "s--", label="LightGBM")
    plt.xlabel("Horizon (days)")
    plt.ylabel("MAE")
    plt.title("UCI energy — LightGBM error vs Horizon (rolling-origin)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "uci_energy_lightgbm_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(horizons, skill, "o-", label="Skill(h)")
    plt.axhline(0, color="black", linestyle="--", linewidth=1.0)
    plt.fill_between(horizons, 0, skill,
                     where=[s > 0 for s in skill],
                     alpha=0.15, color="steelblue")
    plt.xlabel("Horizon (days)")
    plt.ylabel("Skill(h)")
    plt.title("UCI energy — LightGBM skill vs Horizon (rolling-origin)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "uci_energy_lightgbm_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"\nH* formal      = {hstar}")
    print(f"H* contiguo    = {contiguous_hstar}")


if __name__ == "__main__":
    main()
