from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_INPUT = Path("data/nrel_wind_toolkit_hourly_raw.csv")
DEFAULT_OUTPUT = Path("data/wind_hourly_clean.csv")


def _resolve_column(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    raise ValueError(
        f"Could not find {label} column. Expected one of: {', '.join(candidates)}"
    )


def _parse_nrel_raw(input_csv: Path) -> pd.DataFrame:
    # NREL download format includes a metadata row followed by the data header row.
    df = pd.read_csv(input_csv, header=1)
    required = ["Year", "Month", "Day", "Hour", "Minute", "wind speed at 100m (m/s)"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"NREL raw format missing required columns: {', '.join(missing)}")

    ts = pd.to_datetime(
        {
            "year": pd.to_numeric(df["Year"], errors="coerce"),
            "month": pd.to_numeric(df["Month"], errors="coerce"),
            "day": pd.to_numeric(df["Day"], errors="coerce"),
            "hour": pd.to_numeric(df["Hour"], errors="coerce"),
            "minute": pd.to_numeric(df["Minute"], errors="coerce"),
        },
        errors="coerce",
        utc=False,
    )
    value = pd.to_numeric(df["wind speed at 100m (m/s)"], errors="coerce")
    return pd.DataFrame({"timestamp": ts, "value": value})


def prepare_wind_data(input_csv: Path, output_csv: Path) -> pd.DataFrame:
    if not input_csv.exists():
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    try:
        out = _parse_nrel_raw(input_csv)
    except Exception:
        # Fallback for other raw formats that already include timestamp + wind-speed column.
        df = pd.read_csv(input_csv)
        ts_col = _resolve_column(
            df,
            ["timestamp", "datetime", "date", "time", "utc_timestamp"],
            "timestamp",
        )
        wind_col = _resolve_column(
            df,
            ["wind_speed", "windspeed", "ws", "wind_speed_100m", "windspeed_100m"],
            "wind speed",
        )
        out = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(df[ts_col], errors="coerce", utc=False),
                "value": pd.to_numeric(df[wind_col], errors="coerce"),
            }
        )

    out = out.dropna(subset=["timestamp", "value"]).sort_values("timestamp")
    out = out.drop_duplicates(subset=["timestamp"], keep="last").reset_index(drop=True)

    # Enforce hourly regularity using past-only fill to remain leakage-safe.
    out = out.set_index("timestamp").asfreq("h")
    out["value"] = out["value"].ffill()
    out = out.dropna(subset=["value"]).reset_index()

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare NREL Wind Toolkit CSV into canonical timestamp/value hourly format."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Raw NREL Wind Toolkit input CSV path",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Cleaned output CSV path (canonical timestamp,value)",
    )
    args = parser.parse_args()

    cleaned = prepare_wind_data(args.input, args.output)
    print(f"Saved cleaned wind data: {args.output}")
    print(f"Rows: {len(cleaned)}")
    if not cleaned.empty:
        print(f"Time range: {cleaned['timestamp'].iloc[0]} -> {cleaned['timestamp'].iloc[-1]}")


if __name__ == "__main__":
    main()
