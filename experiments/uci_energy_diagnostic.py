#!/usr/bin/env python3
"""
Preliminary diagnostic for the UCI energy domain in Paper 2.

Input:
- results/uci_electricity_daily_aggregate.csv
- data/LD2011_2014.txt

Outputs:
- figures/coverage_clientes.png
- figures/acf_comparativa.png
- figures/diagnostico_resumen_P2.png

Diagnostics:
1. Coverage stability
2. CV
3. ACF lag 1-7
4. RMSE persistence h=1..7
5. Relative persistence RMSE
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.stattools import acf


RAW_PATH = Path("data/LD2011_2014.txt")
AGG_PATH = Path("results/uci_electricity_daily_aggregate.csv")
FIG_DIR = Path("figures")

COVERAGE_THRESHOLD = 0.90
H_MAX = 7
CLIENT_ID = "MT_001"


def parse_float(value: str) -> float:
    value = value.strip().replace(",", ".")
    return float(value) if value else 0.0


def load_daily_coverage(txt_path: Path) -> pd.Series:
    with txt_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        n_clients = len(header) - 1

        stats = {}
        for row in reader:
            ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            day = ts.date()
            active = sum(1 for x in row[1:] if parse_float(x) > 0.0)
            frac = active / n_clients
            if day not in stats:
                stats[day] = [0.0, 0]
            stats[day][0] += frac
            stats[day][1] += 1

    out = {d: stats[d][0] / stats[d][1] for d in stats}
    s = pd.Series(out).sort_index()
    s.index = pd.to_datetime(s.index)
    s.name = "coverage"
    return s


def load_daily_client(txt_path: Path, client_id: str, start_date: pd.Timestamp) -> pd.Series:
    with txt_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        if client_id not in header:
            raise KeyError(f"Client {client_id} not found in raw file.")
        idx = header.index(client_id)

        daily = {}
        for row in reader:
            ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            day = pd.Timestamp(ts.date())
            if day < start_date:
                continue
            val = parse_float(row[idx])
            daily[day] = daily.get(day, 0.0) + val

    s = pd.Series(daily).sort_index()
    s.name = client_id
    return s


def rmse_persistence(series: pd.Series, h: int) -> float:
    values = series.values
    y_true = values[h:]
    y_pred = values[:-h]
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def main() -> int:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    coverage = load_daily_coverage(RAW_PATH)
    agg = pd.read_csv(AGG_PATH, parse_dates=["timestamp"]).set_index("timestamp")["value"]
    start_date = agg.index.min()
    client = load_daily_client(RAW_PATH, CLIENT_ID, start_date)

    # 1. coverage figure
    fig, ax = plt.subplots(figsize=(12, 3))
    coverage.plot(ax=ax, linewidth=0.8)
    ax.axvline(start_date, color="crimson", linestyle="--", label=f"Stable start: {start_date.date()}")
    ax.axhline(COVERAGE_THRESHOLD, color="gray", linestyle=":", label=f"Threshold {COVERAGE_THRESHOLD:.0%}")
    ax.set_title("Daily active-client coverage")
    ax.set_ylabel("Fraction active clients")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / "coverage_clientes.png", dpi=150)
    plt.close()

    # 2. CV
    cv_agg = float(agg.std() / agg.mean())
    cv_cli = float(client.std() / client.mean())

    # 3. ACF
    acf_agg = acf(agg, nlags=H_MAX, fft=True)
    acf_cli = acf(client, nlags=H_MAX, fft=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(agg, lags=14, ax=axes[0], title="ACF — Aggregate daily series")
    plot_acf(client, lags=14, ax=axes[1], title=f"ACF — {CLIENT_ID}")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "acf_comparativa.png", dpi=150)
    plt.close()

    # 4. RMSE persistence
    horizons = list(range(1, H_MAX + 1))
    rmse_agg = [rmse_persistence(agg, h) for h in horizons]
    rmse_cli = [rmse_persistence(client, h) for h in horizons]

    # 5. relative RMSE
    rmse_rel_agg = [x / float(agg.mean()) for x in rmse_agg]
    rmse_rel_cli = [x / float(client.mean()) for x in rmse_cli]

    # summary figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    (agg / agg.max()).plot(ax=axes[0, 0], label="Aggregate", linewidth=0.8)
    (client / client.max()).plot(ax=axes[0, 0], label=CLIENT_ID, linewidth=0.8)
    axes[0, 0].set_title("Normalized daily series")
    axes[0, 0].legend()

    x = np.arange(1, H_MAX + 1)
    w = 0.35
    axes[0, 1].bar(x - w/2, acf_agg[1:], width=w, label="Aggregate")
    axes[0, 1].bar(x + w/2, acf_cli[1:], width=w, label=CLIENT_ID)
    axes[0, 1].axhline(0, color="black", linewidth=0.8)
    axes[0, 1].set_title("ACF lag 1–7")
    axes[0, 1].legend()

    axes[1, 0].plot(horizons, rmse_agg, "o-", label="Aggregate")
    axes[1, 0].plot(horizons, rmse_cli, "s--", label=CLIENT_ID)
    axes[1, 0].set_title("RMSE persistence")
    axes[1, 0].set_xlabel("Horizon (days)")
    axes[1, 0].legend()

    axes[1, 1].plot(horizons, rmse_rel_agg, "o-", label="Aggregate")
    axes[1, 1].plot(horizons, rmse_rel_cli, "s--", label=CLIENT_ID)
    axes[1, 1].set_title("Relative RMSE persistence")
    axes[1, 1].set_xlabel("Horizon (days)")
    axes[1, 1].legend()

    plt.tight_layout()
    plt.savefig(FIG_DIR / "diagnostico_resumen_P2.png", dpi=150)
    plt.close()

    print(f"Stable start: {start_date.date()}")
    print(f"CV aggregate: {cv_agg:.4f}")
    print(f"CV {CLIENT_ID}: {cv_cli:.4f}")
    print(f"ACF lag-1 aggregate: {acf_agg[1]:+.4f}")
    print(f"ACF lag-1 {CLIENT_ID}: {acf_cli[1]:+.4f}")
    print(f"ACF lag-7 aggregate: {acf_agg[7]:+.4f}")
    print(f"ACF lag-7 {CLIENT_ID}: {acf_cli[7]:+.4f}")
    print(f"Relative persistence RMSE h=1 aggregate: {rmse_rel_agg[0]:.4f}")
    print(f"Relative persistence RMSE h=1 {CLIENT_ID}: {rmse_rel_cli[0]:.4f}")
    print(f"Relative persistence RMSE h=7 aggregate: {rmse_rel_agg[6]:.4f}")
    print(f"Relative persistence RMSE h=7 {CLIENT_ID}: {rmse_rel_cli[6]:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
