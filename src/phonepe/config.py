"""Database-per-table settings.

Each table runs in its own Postgres container. Ports are local defaults and
can be overridden with PHONEPE_<TABLE>_PORT.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableDB:
    name: str
    port: int
    columns: tuple[str, ...]


TABLES: tuple[TableDB, ...] = (
    TableDB(
        "aggregated_transaction",
        5601,
        (
            "state",
            "year",
            "quarter",
            "transaction_type",
            "transaction_count",
            "transaction_amount",
        ),
    ),
    TableDB(
        "aggregated_user",
        5602,
        (
            "state",
            "year",
            "quarter",
            "row_kind",
            "brand",
            "registered_users",
            "app_opens",
            "device_count",
            "device_percentage",
        ),
    ),
    TableDB(
        "aggregated_merchant",
        5603,
        ("state", "year", "quarter", "registered_merchants"),
    ),
    TableDB(
        "map_transaction",
        5604,
        (
            "geo_level",
            "state",
            "district",
            "year",
            "quarter",
            "transaction_count",
            "transaction_amount",
        ),
    ),
    TableDB(
        "map_user",
        5605,
        (
            "geo_level",
            "state",
            "district",
            "year",
            "quarter",
            "registered_users",
            "app_opens",
        ),
    ),
    TableDB(
        "map_merchant",
        5606,
        (
            "geo_level",
            "state",
            "district",
            "year",
            "quarter",
            "registered_merchants",
        ),
    ),
    TableDB(
        "top_transaction",
        5607,
        (
            "scope_state",
            "year",
            "quarter",
            "entity_level",
            "entity_name",
            "transaction_count",
            "transaction_amount",
        ),
    ),
    TableDB(
        "top_user",
        5608,
        (
            "scope_state",
            "year",
            "quarter",
            "entity_level",
            "entity_name",
            "registered_users",
        ),
    ),
    TableDB(
        "top_merchant",
        5609,
        (
            "scope_state",
            "year",
            "quarter",
            "entity_level",
            "entity_name",
            "registered_merchants",
        ),
    ),
)


def table_by_name(name: str) -> TableDB:
    for table in TABLES:
        if table.name == name:
            return table
    known = ", ".join(table.name for table in TABLES)
    raise KeyError(f"Unknown table {name}. Known tables: {known}")
