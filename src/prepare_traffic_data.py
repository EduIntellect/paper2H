from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_INPUT = Path("data/metr-la.h5")
DEFAULT_OUTPUT = Path("data/traffic_hourly_clean.csv")
DEFAULT_SENSOR = "773869"

def prepare_traffic_data(input_h5: Path, output_csv: Path, sensor_column: str) -> pd.DataFrame:
    if not input_h5.exists():
        raise FileNotFoundError(f"Input file not found: {input_h5}")

    df = pd.read_hdf(input_h5, key="df")
    sensor_col = str(sensor_column)
    if sensor_col not in df.columns:
        raise ValueError(f"Sensor column not found in METR-LA raw data: {sensor_col}")

    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df.index, errors="coerce", utc=False),
            "value": pd.to_numeric(df[sensor_col], errors="coerce"),
        }
    )

    # Domain-specific contract for Paper 2 traffic domain:
    # 5-min METR-LA speed -> hourly mean -> regular hourly series.
    out = out.dropna(subset=["timestamp"]).sort_values("timestamp")
    out = out.drop_duplicates(subset=["timestamp"], keep="last")
    out = out.set_index("timestamp").resample("h").mean()
    out = out.asfreq("h")
    out["value"] = out["value"].ffill()
    out = out.dropna(subset=["value"]).sort_index().reset_index()

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare METR-LA HDF into canonical hourly timestamp/value format "
            "using one univariate speed sensor."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Raw METR-LA HDF path (expects key='df')",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Cleaned output CSV path (canonical timestamp,value, hourly)",
    )
    parser.add_argument(
        "--sensor",
        type=str,
        default=DEFAULT_SENSOR,
        help="METR-LA sensor column to extract as canonical univariate series",
    )
    args = parser.parse_args()

    cleaned = prepare_traffic_data(args.input, args.output, args.sensor)
    print(f"Saved cleaned traffic data: {args.output}")
    print(f"Sensor: {args.sensor}")
    print(f"Rows: {len(cleaned)}")
    if not cleaned.empty:
        print(f"Time range: {cleaned['timestamp'].iloc[0]} -> {cleaned['timestamp'].iloc[-1]}")


if __name__ == "__main__":
    main()
