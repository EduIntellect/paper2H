#!/usr/bin/env python3
"""Deterministically retrieve and verify the external wind/traffic inputs."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from prepare_nrel_wind_data import prepare_wind_data
from prepare_traffic_data import prepare_traffic_data


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
WIND_RAW_SHA256 = "92194496784fbacb86ef68856488d1c270f7c339abbfa92e2f2cca6732aa3542"
WIND_CLEAN_SHA256 = "8f094e6437b50b5fd6837bfe43ad6f8a262bf5a9eec84472f2062eaac780a309"
TRAFFIC_RAW_SHA256 = "64784b76d6fb8ec9bff4b6decafb354da2bb37840468fdccee5044e511277c05"
TRAFFIC_CLEAN_SHA256 = "50fb3f411b7521cf72fc87e5660ce2809df67c9507619a6578d4d42e925d479c"
TRAFFIC_URL = "https://huggingface.co/datasets/MintBruce/SkyTraffic/resolve/main/metr-la.h5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(path: Path, expected: str) -> None:
    observed = sha256(path)
    if observed != expected:
        raise RuntimeError(f"SHA-256 mismatch for {path}: {observed} != {expected}")


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "paper2H-reproducibility/1"})
    with urllib.request.urlopen(request) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def retrieve_wind(api_key: str, email: str) -> None:
    if not email:
        raise ValueError("--email is required for the NLR wind API")
    query = urllib.parse.urlencode(
        {
            "api_key": api_key,
            "wkt": "POINT(-105.0 40.0)",
            "attributes": "windspeed_100m",
            "names": "2019",
            "interval": "60",
            "utc": "true",
            "leap_day": "false",
            "email": email,
            "affiliation": "academic research",
            "reason": "reproducible forecast evaluation",
            "mailing_list": "false",
        }
    )
    raw = DATA / "nrel_wind_toolkit_hourly_raw.csv"
    clean = DATA / "wind_hourly_clean.csv"
    download(
        "https://developer.nlr.gov/api/wind-toolkit/v2/wind/"
        f"wtk-led-conus-download.csv?{query}",
        raw,
    )
    verify(raw, WIND_RAW_SHA256)
    prepared = prepare_wind_data(raw, clean)
    if len(prepared) != 8760:
        raise RuntimeError(f"Unexpected wind row count: {len(prepared)}")
    verify(clean, WIND_CLEAN_SHA256)
    print(f"Verified wind input: {clean}")


def retrieve_traffic() -> None:
    raw = DATA / "metr-la.h5"
    clean = DATA / "traffic_hourly_clean.csv"
    download(TRAFFIC_URL, raw)
    verify(raw, TRAFFIC_RAW_SHA256)
    prepared = prepare_traffic_data(raw, clean, "773869")
    if len(prepared) != 2856:
        raise RuntimeError(f"Unexpected traffic row count: {len(prepared)}")
    verify(clean, TRAFFIC_CLEAN_SHA256)
    print(f"Verified traffic input: {clean}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", choices=["wind", "traffic", "all"])
    parser.add_argument("--api-key", default="DEMO_KEY")
    parser.add_argument("--email", default="")
    args = parser.parse_args()
    if args.domain in {"wind", "all"}:
        retrieve_wind(args.api_key, args.email)
    if args.domain in {"traffic", "all"}:
        retrieve_traffic()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
