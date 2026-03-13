from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DEFAULT_INPUT = Path("data/pjm_load_hourly_raw.csv")
DEFAULT_OUTPUT = Path("data/pjm_load_hourly_clean.csv")


def _resolve_column(df: pd.DataFrame, candidates: list[str], label: str) -> str:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    raise ValueError(
        f"Could not find {label} column. Expected one of: {', '.join(candidates)}"
    )


def prepare_pjm_load(input_csv: Path, output_csv: Path) -> pd.DataFrame:
    if not input_csv.exists():
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    df = pd.read_csv(input_csv)
    ts_col = _resolve_column(
        df,
        ["timestamp", "datetime", "date", "time", "utc_timestamp", "Datetime"],
        "timestamp",
    )
    load_col = _resolve_column(df, ["load", "LOAD", "mw", "MW", "demand"], "load")

    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df[ts_col], errors="coerce", utc=False),
            "load": pd.to_numeric(df[load_col], errors="coerce"),
        }
    )

    out = out.dropna(subset=["timestamp", "load"]).sort_values("timestamp")
    out = out.drop_duplicates(subset=["timestamp"], keep="last").reset_index(drop=True)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare PJM hourly load CSV into canonical timestamp/load format."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Raw PJM input CSV path")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Cleaned output CSV path (canonical timestamp,load)",
    )
    args = parser.parse_args()

    cleaned = prepare_pjm_load(args.input, args.output)
    print(f"Saved cleaned PJM load data: {args.output}")
    print(f"Rows: {len(cleaned)}")
    if not cleaned.empty:
        print(f"Time range: {cleaned['timestamp'].iloc[0]} -> {cleaned['timestamp'].iloc[-1]}")


if __name__ == "__main__":
    main()
