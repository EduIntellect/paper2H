#!/usr/bin/env python3
"""
Paper 2 — UCI energy predictability experiment

Input:
- results/uci_electricity_daily_aggregate.csv

Forecast setup:
- target series: value
- horizons: 1..7 days
- baseline: persistence
- model: moving average, window=3
- metric: MAE
- skill(h) = 1 - MAE_model(h) / MAE_baseline(h)

Outputs:
- results/uci_energy_errors.csv
- results/uci_energy_skill.csv
- results/uci_energy_hstar.txt
- figures/uci_energy_error_vs_horizon.png
- figures/uci_energy_skill_vs_horizon.png
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("results/uci_electricity_daily_aggregate.csv")
RESULTS_DIR = Path("results")
FIG_DIR = Path("figures")

H_MAX = 7
WINDOW = 3


def mae(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.mean(np.abs(y_true - y_pred)))


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
    y = df["value"].values

    horizons = []
    baseline_mae = []
    model_mae = []
    skill = []

    for h in range(1, H_MAX + 1):
        y_true = []
        y_base = []
        y_model = []

        for t in range(WINDOW, len(y) - h + 1):
            train = y[t - WINDOW:t]
            target = y[t + h - 1]

            pred_base = y[t - 1]
            pred_model = float(np.mean(train))

            y_true.append(target)
            y_base.append(pred_base)
            y_model.append(pred_model)

        e_base = mae(y_true, y_base)
        e_model = mae(y_true, y_model)
        s = 1.0 - (e_model / e_base)

        horizons.append(h)
        baseline_mae.append(e_base)
        model_mae.append(e_model)
        skill.append(s)

    hstar = 0
    for h, s in zip(horizons, skill):
        if s > 0:
            hstar = h

    errors_df = pd.DataFrame({
        "horizon": horizons,
        "baseline_mae": baseline_mae,
        "model_mae": model_mae,
    })
    skill_df = pd.DataFrame({
        "horizon": horizons,
        "skill": skill,
    })

    errors_df.to_csv(RESULTS_DIR / "uci_energy_errors.csv", index=False)
    skill_df.to_csv(RESULTS_DIR / "uci_energy_skill.csv", index=False)

    with open(RESULTS_DIR / "uci_energy_hstar.txt", "w", encoding="utf-8") as f:
        f.write(str(hstar) + "\n")

    plt.figure(figsize=(8, 5))
    plt.plot(horizons, baseline_mae, "o-", label="Persistence")
    plt.plot(horizons, model_mae, "s--", label=f"Moving average (w={WINDOW})")
    plt.xlabel("Horizon (days)")
    plt.ylabel("MAE")
    plt.title("UCI energy — Error vs Horizon")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "uci_energy_error_vs_horizon.png", dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(horizons, skill, "o-", label="Skill(h)")
    plt.axhline(0, color="black", linestyle="--", linewidth=1.0)
    plt.xlabel("Horizon (days)")
    plt.ylabel("Skill")
    plt.title("UCI energy — Skill vs Horizon")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "uci_energy_skill_vs_horizon.png", dpi=150)
    plt.close()

    print(f"H* = {hstar}")
    print("Horizons:", horizons)
    print("Baseline MAE:", baseline_mae)
    print("Model MAE:", model_mae)
    print("Skill:", skill)


if __name__ == "__main__":
    main()
