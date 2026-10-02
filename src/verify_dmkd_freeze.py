"""Verify the frozen DMKD result package without fitting any model.

The checks are read-only: hashes, dimensions, key uniqueness, cross-table
linkage, and exact canonical linkage for the repaired Traffic A1 artifact.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_ARTIFACTS = {
    "data/pm25_series.csv": ("09e4164af5159c21ca9bd1b09399173c8e7ab67c1445903a126722e4d576abdf", 41757, 1),
    "results/uci_electricity_daily_aggregate.csv": ("7a5675255e1de1cedc1d026004cad13052382843aed9c00d429f186c0f5216d3", 667, 2),
    "data/wind_hourly_clean.csv": ("8f094e6437b50b5fd6837bfe43ad6f8a262bf5a9eec84472f2062eaac780a309", 8760, 2),
    "data/traffic_hourly_clean.csv": ("50fb3f411b7521cf72fc87e5660ce2809df67c9507619a6578d4d42e925d479c", 2856, 2),
    "data/pm10_elx_daily.csv": ("3d8fff43108c5cbc0480ed9f21173e21e89613cef4c99da5636a3ecd90d6bea0", 2922, 2),
    "data/pm10_bcn_daily.csv": ("d6ccc9c61b1e8fdec68daa6839645ad8cd01016f1f4cd0f65dc04798fc74bfb3", 2827, 2),
    "results/pm25_predictions_all.csv": ("ddeea697561d181241e36475aae58c05c81616d6f62c2984bc01f0af4ed055f6", 87600, 10),
    "results/load_predictions_all.csv": ("98b3cbd4f2b416b24c341e5117863f6a01ee23092a9a5ecf1e3caf1b47451625", 9730, 10),
    "results/wind_predictions_all.csv": ("dad533f3d7da121b02eb945f757d683add66c1acb47b59db87eb49f55bc0f319", 84290, 10),
    "results/traffic_predictions_all.csv": ("7820e5a8ee98cbdcb6f881982bf04fea8547681de2b2eba2e8fc3b8b6c3e685d", 37335, 10),
    "results/pm10_predictions_all.csv": ("20481ab50fff854b8c5eb4924de888110c095e982bea75773d17116565874e75", 88655, 10),
    "results/pm10_bcn_predictions_all.csv": ("c0b1bf8da9dfa59462f6b422e0856e1cf8aa7989a6813dc6cfccc22865bcbc17", 85330, 10),
    "results/pm25_skill_all.csv": ("439f21d475882ddb30488c6e9447374cabd393d927419046dc1842db8eb29fd8", 240, 7),
    "results/load_skill_all.csv": ("2527401d4ec1a612d86c61f89961529a6f540606857bb130931d5276246f443c", 35, 7),
    "results/wind_skill_all.csv": ("740f3f39d364274d6f50d17a2da41a709afe91b4bbca41814d6972c1a7f777cd", 240, 7),
    "results/traffic_skill_all.csv": ("3ad87393c7bbda1c534092817c70a67c2d6011af16706730b7868ad162b057f2", 360, 7),
    "results/pm10_skill_all.csv": ("46e646208708ba31ee254c52a46eb8998852a928d9aab3ca07b1fa2a3a6be738", 35, 7),
    "results/pm10_bcn_skill_all.csv": ("3f011a1a9167862e0d5dcdfcd34b40f41a86acf824afa1999c13e9a86628c7b9", 35, 7),
    "results/dm_tests_all.csv": ("ac1a91a7d14dcf49fdd2e11bb25bbb6b4b191f1a557acef0f66b9294831283e8", 1065, 8),
    "results/hstar_all_domains.csv": ("ed56873d51ded1bab7c6ab467143e7e3a99b4abe227ead150b6d703af39b109f", 32, 7),
    "results/hstar_summary.csv": ("3d0aa069ec0fb82cbfc19ba6b460f645a45d18dba4b696dbc976e9953a40fdcd", 32, 9),
    "results/unified_results_table.csv": ("eac03818b5f61651b6e1d4af7969ee4bcac385951b4dbb2ea3a62263b11ee056", 1065, 17),
}

DOMAIN_HORIZONS = {"pm25": 48, "load": 7, "wind": 48, "traffic": 72,
                   "pm10": 7, "pm10_bcn": 7}
PRIMARY_MODELS = {"ridge", "lightgbm", "extratrees", "knn", "mlp"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_artifacts() -> None:
    for relative, (expected_hash, rows, columns) in EXPECTED_ARTIFACTS.items():
        path = ROOT / relative
        require(path.is_file(), f"Missing frozen artifact: {relative}")
        require(digest(path) == expected_hash, f"Hash mismatch: {relative}")
        frame = pd.read_csv(path)
        require(frame.shape == (rows, columns),
                f"Unexpected shape for {relative}: {frame.shape}")


def verify_domain_tables() -> None:
    for domain, max_horizon in DOMAIN_HORIZONS.items():
        predictions = pd.read_csv(ROOT / f"results/{domain}_predictions_all.csv")
        skill = pd.read_csv(ROOT / f"results/{domain}_skill_all.csv")
        require(set(predictions["model"]) == PRIMARY_MODELS,
                f"Unexpected prediction models for {domain}")
        require(set(skill["model"]) == PRIMARY_MODELS,
                f"Unexpected skill models for {domain}")
        require(set(predictions["horizon"]) == set(range(1, max_horizon + 1)),
                f"Incomplete horizons for {domain}")
        require(not predictions.duplicated(["model", "horizon", "origin_idx"]).any(),
                f"Duplicate prediction key for {domain}")
        require(not skill.duplicated(["model", "horizon"]).any(),
                f"Duplicate skill key for {domain}")
        counts = (predictions.groupby(["model", "horizon"]).size()
                  .rename("expected_n").reset_index())
        linked = skill.merge(counts, on=["model", "horizon"], how="outer",
                             validate="one_to_one")
        require(not linked["expected_n"].isna().any(), f"Skill key without predictions: {domain}")
        require(np.array_equal(linked["n_origins"].to_numpy(), linked["expected_n"].to_numpy()),
                f"Origin-count mismatch between predictions and skill: {domain}")


def verify_traffic_linkage() -> None:
    canonical = pd.read_csv(ROOT / "data/traffic_hourly_clean.csv", parse_dates=["timestamp"])
    predictions = pd.read_csv(ROOT / "results/traffic_predictions_all.csv")
    target_idx = (predictions["origin_idx"].astype(int) +
                  predictions["horizon"].astype(int)).to_numpy()
    origin_idx = predictions["origin_idx"].astype(int).to_numpy()
    require(np.array_equal(predictions["y_true"].to_numpy(),
                           canonical["value"].to_numpy()[target_idx]),
            "Traffic y_true is not exactly canonical")
    require(np.array_equal(predictions["y_pred_baseline"].to_numpy(),
                           canonical["value"].to_numpy()[origin_idx]),
            "Traffic baseline is not exactly canonical")
    require(np.array_equal(pd.to_datetime(predictions["origin_timestamp"], format="mixed").to_numpy(),
                           canonical["timestamp"].to_numpy()[origin_idx]),
            "Traffic origin timestamps are not canonical")


def verify_aggregate_tables() -> None:
    dm = pd.read_csv(ROOT / "results/dm_tests_all.csv")
    unified = pd.read_csv(ROOT / "results/unified_results_table.csv")
    hstar = pd.read_csv(ROOT / "results/hstar_all_domains.csv")
    summary = pd.read_csv(ROOT / "results/hstar_summary.csv")
    key = ["domain", "model", "horizon"]
    hkey = ["domain", "model"]
    require(not dm.duplicated(key).any(), "Duplicate DM key")
    require(not unified.duplicated(key).any(), "Duplicate unified-table key")
    require(set(map(tuple, dm[key].to_numpy())) == set(map(tuple, unified[key].to_numpy())),
            "DM and unified-table keys differ")
    require(not hstar.duplicated(hkey).any(), "Duplicate H* key")
    require(not summary.duplicated(hkey).any(), "Duplicate H* summary key")
    require(set(map(tuple, hstar[hkey].to_numpy())) == set(map(tuple, summary[hkey].to_numpy())),
            "H* and H* summary keys differ")


def main() -> None:
    verify_artifacts()
    verify_domain_tables()
    verify_traffic_linkage()
    verify_aggregate_tables()
    print("DMKD freeze verification: PASS")
    print(f"Verified {len(EXPECTED_ARTIFACTS)} frozen artifacts across 6 domains.")
    print("Traffic canonical mismatches: 0; no fitting or training executed.")


if __name__ == "__main__":
    main()
