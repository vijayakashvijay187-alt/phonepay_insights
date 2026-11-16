"""Turn PhonePe Pulse JSON files into rows for the nine warehouse tables.

The public Pulse repository currently publishes merchant files in place of the
insurance files named in the course brief, and it does not ship device-brand
or pin-code breakdowns. The parsers still accept those older shapes when the
keys or folders are present.
"""

from __future__ import annotations

import json
from pathlib import Path

from phonepe.places import canonical_place


def _load_json(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not payload.get("success", True):
        return None
    data = payload.get("data")
    if not isinstance(data, dict):
        return None
    return data


def _year_quarter_state(path: Path) -> tuple[str, int, int] | None:
    try:
        quarter = int(path.stem)
        year = int(path.parent.name)
    except ValueError:
        return None
    parent = path.parent.parent
    if parent.name == "india":
        state = "india"
    else:
        state = canonical_place(parent.name)
    if state is None:
        return None
    return state, year, quarter


def _as_int(value) -> int | None:
    if value is None:
        return None
    return int(value)


def _as_float(value) -> float | None:
    if value is None:
        return None
    return float(value)


def iter_located_files(india_dir: Path):
    if not india_dir.exists():
        return
    for path in sorted(india_dir.rglob("*.json")):
        located = _year_quarter_state(path)
        if located is None:
            continue
        data = _load_json(path)
        if data is None:
            continue
        yield path, located, data


def extract_aggregated_transaction(root: Path) -> list[tuple]:
    rows: list[tuple] = []
    india = root / "aggregated" / "transaction" / "country" / "india"
    for _path, (state, year, quarter), data in iter_located_files(india):
        for item in data.get("transactionData") or []:
            tx_type = canonical_place(item.get("name")) or "unknown"
            for instrument in item.get("paymentInstruments") or []:
                rows.append(
                    (
                        state,
                        year,
                        quarter,
                        tx_type,
                        _as_int(instrument.get("count")),
                        _as_float(instrument.get("amount")),
                    )
                )
    return rows


def extract_aggregated_user(root: Path) -> list[tuple]:
    rows: list[tuple] = []
    india = root / "aggregated" / "user" / "country" / "india"
    for _path, (state, year, quarter), data in iter_located_files(india):
        aggregated = data.get("aggregated") or {}
        registered = _as_int(
            aggregated.get("registeredCount", aggregated.get("registeredUsers"))
        )
        if registered is None:
            registered = _as_int(data.get("registeredUsers"))
        app_opens = _as_int(aggregated.get("appOpens", data.get("appOpens")))
        rows.append(
            (state, year, quarter, "total", None, registered, app_opens, None, None)
        )
        for device in data.get("usersByDevice") or []:
            brand = canonical_place(device.get("brand"))
            rows.append(
                (
                    state,
                    year,
                    quarter,
                    "device",
                    brand,
                    registered,
                    app_opens,
                    _as_int(device.get("count")),
                    _as_float(device.get("percentage")),
                )
            )
    return rows


def extract_aggregated_merchant(root: Path) -> list[tuple]:
    rows: list[tuple] = []
    india = root / "aggregated" / "merchant" / "country" / "india"
    for _path, (state, year, quarter), data in iter_located_files(india):
        aggregated = data.get("aggregated") or {}
        registered = _as_int(
            aggregated.get("registeredCount", aggregated.get("registeredUsers"))
        )
        rows.append((state, year, quarter, registered))
    return rows


def _map_rows_from_hover(data: dict, state: str, year: int, quarter: int):
    """Yield (geo_level, state, district, metric dict or count payload)."""
    hover_list = data.get("hoverDataList")
    if isinstance(hover_list, list):
        for item in hover_list:
            name = canonical_place(item.get("name"))
            metric = {}
            metrics = item.get("metric") or []
            if metrics:
                metric = metrics[0]
            if state == "india":
                yield "state", name, None, metric, None
            else:
                yield "district", state, name, metric, None
        return
    hover = data.get("hoverData")
    if isinstance(hover, dict):
        for name, payload in hover.items():
            place = canonical_place(name)
            if state == "india":
                yield "state", place, None, {}, payload
            else:
                yield "district", state, place, {}, payload


def extract_map_transaction(root: Path) -> list[tuple]:
    rows: list[tuple] = []
    india = root / "map" / "transaction" / "hover" / "country" / "india"
    for _path, (state, year, quarter), data in iter_located_files(india):
        for geo_level, geo_state, district, metric, _payload in _map_rows_from_hover(
            data, state, year, quarter
        ):
            rows.append(
                (
                    geo_level,
                    geo_state,
                    district,
                    year,
                    quarter,
                    _as_int(metric.get("count")),
                    _as_float(metric.get("amount")),
                )
            )
    return rows


def extract_map_registered(root: Path, folder: str, value_key: str) -> list[tuple]:
    rows: list[tuple] = []
    india = root / "map" / folder / "hover" / "country" / "india"
    for _path, (state, year, quarter), data in iter_located_files(india):
        for geo_level, geo_state, district, _metric, payload in _map_rows_from_hover(
            data, state, year, quarter
        ):
            payload = payload or {}
            registered = _as_int(
                payload.get("registeredCount", payload.get("registeredUsers"))
            )
            app_opens = _as_int(payload.get("appOpens"))
            if value_key == "user":
                rows.append(
                    (
                        geo_level,
                        geo_state,
                        district,
                        year,
                        quarter,
                        registered,
                        app_opens,
                    )
                )
            else:
                rows.append(
                    (geo_level, geo_state, district, year, quarter, registered)
                )
    return rows


def _top_entities(data: dict):
    for level, key in (
        ("state", "states"),
        ("district", "districts"),
        ("pincode", "pincodes"),
    ):
        for item in data.get(key) or []:
            if not isinstance(item, dict):
                continue
            metric = item.get("metric") or {}
            name = canonical_place(item.get("entityName") or item.get("name"))
            if name is None:
                continue
            count = metric.get("count", item.get("count"))
            amount = metric.get("amount")
            registered = item.get("registeredCount", item.get("registeredUsers"))
            yield level, name, count, amount, registered


def extract_top(root: Path, folder: str, kind: str) -> list[tuple]:
    rows: list[tuple] = []
    india = root / "top" / folder / "country" / "india"
    for _path, (state, year, quarter), data in iter_located_files(india):
        for level, name, count, amount, registered in _top_entities(data):
            if kind == "transaction":
                rows.append(
                    (
                        state,
                        year,
                        quarter,
                        level,
                        name,
                        _as_int(count),
                        _as_float(amount),
                    )
                )
            elif kind == "user":
                rows.append(
                    (state, year, quarter, level, name, _as_int(registered or count))
                )
            else:
                rows.append(
                    (state, year, quarter, level, name, _as_int(registered or count))
                )
    return rows


def extract_all(root: Path) -> dict[str, list[tuple]]:
    """Parse the Pulse tree into rows keyed by warehouse table name."""
    return {
        "aggregated_transaction": extract_aggregated_transaction(root),
        "aggregated_user": extract_aggregated_user(root),
        "aggregated_merchant": extract_aggregated_merchant(root),
        "map_transaction": extract_map_transaction(root),
        "map_user": extract_map_registered(root, "user", "user"),
        "map_merchant": extract_map_registered(root, "merchant", "merchant"),
        "top_transaction": extract_top(root, "transaction", "transaction"),
        "top_user": extract_top(root, "user", "user"),
        "top_merchant": extract_top(root, "merchant", "merchant"),
    }
