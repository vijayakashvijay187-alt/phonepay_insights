import json
from pathlib import Path

from phonepe.analysis import add_quarter_growth
from phonepe.extract import extract_all
from phonepe.places import canonical_place
import pandas as pd


def test_canonical_place_folds_slugs_and_ampersands():
    assert canonical_place("andaman-&-nicobar-islands") == "andaman and nicobar islands"
    assert canonical_place("Andaman & Nicobar Islands") == "andaman and nicobar islands"
    assert canonical_place("  Karnataka ") == "karnataka"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_extract_reads_current_and_legacy_shapes(tmp_path: Path):
    root = tmp_path
    _write(
        root / "aggregated/transaction/country/india/state/karnataka/2024/1.json",
        {
            "success": True,
            "data": {
                "transactionData": [
                    {"name": "P2P", "paymentInstruments": [{"type": "TOTAL", "count": 10, "amount": 50.5}]}
                ]
            },
        },
    )
    _write(
        root / "aggregated/user/country/india/2024/1.json",
        {
            "success": True,
            "data": {
                "aggregated": {"registeredUsers": 100, "appOpens": 40},
                "usersByDevice": [{"brand": "Xiaomi", "count": 20, "percentage": 20.0}],
            },
        },
    )
    _write(
        root / "aggregated/merchant/country/india/state/karnataka/2024/1.json",
        {"success": True, "data": {"aggregated": {"registeredCount": 7}}},
    )
    _write(
        root / "map/transaction/hover/country/india/2024/1.json",
        {
            "success": True,
            "data": {"hoverDataList": [{"name": "karnataka", "metric": [{"count": 10, "amount": 50.5}]}]},
        },
    )
    _write(
        root / "map/user/hover/country/india/state/karnataka/2024/1.json",
        {"success": True, "data": {"hoverData": {"bengaluru urban district": {"registeredCount": 5, "appOpens": 2}}}},
    )
    _write(
        root / "map/merchant/hover/country/india/2024/1.json",
        {"success": True, "data": {"hoverData": {"karnataka": {"registeredCount": 7}}}},
    )
    _write(
        root / "top/transaction/country/india/2024/1.json",
        {
            "success": True,
            "data": {
                "states": [{"entityName": "karnataka", "metric": {"count": 10, "amount": 50.5}}],
                "pincodes": [{"entityName": "560001", "metric": {"count": 3, "amount": 9}}],
            },
        },
    )
    _write(
        root / "top/user/country/india/state/karnataka/2024/1.json",
        {"success": True, "data": {"districts": [{"name": "bengaluru urban district", "registeredUsers": 5}]}},
    )
    _write(
        root / "top/merchant/country/india/2024/1.json",
        {"success": True, "data": {"states": [{"name": "karnataka", "registeredCount": 7}]}},
    )

    tables = extract_all(root)
    assert tables["aggregated_transaction"] == [("karnataka", 2024, 1, "p2p", 10, 50.5)]
    assert ("india", 2024, 1, "total", None, 100, 40, None, None) in tables["aggregated_user"]
    assert ("india", 2024, 1, "device", "xiaomi", 100, 40, 20, 20.0) in tables["aggregated_user"]
    assert tables["aggregated_merchant"] == [("karnataka", 2024, 1, 7)]
    assert tables["map_transaction"][0][0] == "state"
    assert tables["map_user"][0] == ("district", "karnataka", "bengaluru urban district", 2024, 1, 5, 2)
    assert tables["map_merchant"][0][1] == "karnataka"
    levels = {row[3] for row in tables["top_transaction"]}
    assert levels == {"state", "pincode"}
    assert tables["top_user"][0][0] == "karnataka"
    assert tables["top_merchant"][0][5] == 7


def test_quarter_growth_is_relative_to_the_previous_state_row():
    frame = pd.DataFrame(
        [
            {"state": "goa", "year": 2024, "quarter": 1, "transaction_count": 100},
            {"state": "goa", "year": 2024, "quarter": 2, "transaction_count": 150},
        ]
    )
    grown = add_quarter_growth(frame)
    assert pd.isna(grown.iloc[0]["qoq_change"])
    assert grown.iloc[1]["qoq_change"] == 0.5


def test_failed_payloads_are_skipped(tmp_path: Path):
    path = tmp_path / "aggregated/transaction/country/india/2020/1.json"
    path.parent.mkdir(parents=True)
    path.write_text("{not json", encoding="utf-8")
    assert extract_all(tmp_path)["aggregated_transaction"] == []
