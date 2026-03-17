#!/usr/bin/env python3
"""
Aggregate UCI Electricity Load Diagrams 2011-2014 into a daily aggregate series.

Input:
- data/LD2011_2014.txt

Output:
- results/uci_electricity_daily_aggregate.csv

Rules:
- detect active-client coverage (> 0)
- find first stable start date with >= 90% active clients for 7 consecutive days
- aggregate all client series
- resample to daily totals
- export canonical CSV: timestamp,value
"""

from __future__ import annotations

import csv
from collections import deque
from datetime import datetime, date
from pathlib import Path


DATA_PATH = Path("data/LD2011_2014.txt")
OUTPUT_PATH = Path("results/uci_electricity_daily_aggregate.csv")

COVERAGE_THRESHOLD = 0.90
STABLE_DAYS = 7


def parse_float(value: str) -> float:
    value = value.strip().replace(",", ".")
    return float(value) if value else 0.0


def detect_stable_start(txt_path: Path) -> date:
    with txt_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        n_clients = len(header) - 1

        day_stats = {}

        for row in reader:
            ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            day = ts.date()

            active = sum(1 for x in row[1:] if parse_float(x) > 0.0)
            frac = active / n_clients

            if day not in day_stats:
                day_stats[day] = [0.0, 0]
            day_stats[day][0] += frac
            day_stats[day][1] += 1

    days = sorted(day_stats.keys())
    coverage = [(d, day_stats[d][0] / day_stats[d][1]) for d in days]

    window = deque(maxlen=STABLE_DAYS)
    for d, cov in coverage:
        window.append((d, cov >= COVERAGE_THRESHOLD))
        if len(window) == STABLE_DAYS and all(flag for _, flag in window):
            return window[0][0]

    raise RuntimeError("No stable start found with >= 90% active clients for 7 consecutive days.")


def aggregate_daily(txt_path: Path, stable_start: date, output_path: Path) -> None:
    daily = {}

    with txt_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # header

        for row in reader:
            ts = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            day = ts.date()
            if day < stable_start:
                continue

            total = sum(parse_float(x) for x in row[1:])
            daily[day] = daily.get(day, 0.0) + total

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for day in sorted(daily.keys()):
            writer.writerow([day.isoformat(), f"{daily[day]:.6f}"])


def main() -> int:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing input file: {DATA_PATH}")

    stable_start = detect_stable_start(DATA_PATH)
    aggregate_daily(DATA_PATH, stable_start, OUTPUT_PATH)

    print(f"Stable start: {stable_start.isoformat()}")
    print(f"Output written to: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
