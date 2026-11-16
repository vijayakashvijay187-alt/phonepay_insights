"""Business-case queries.

Each warehouse table lives in its own Postgres instance, so SQL stays inside
one database. Metrics that compare users and merchants are joined in Python.
"""

from __future__ import annotations

import pandas as pd

from phonepe.db import connect


def fetch_df(table_name: str, sql: str, params: tuple = ()) -> pd.DataFrame:
    with connect(table_name) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [desc.name for desc in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=columns)


def available_years() -> list[int]:
    frame = fetch_df(
        "aggregated_transaction",
        "SELECT DISTINCT year FROM aggregated_transaction ORDER BY year",
    )
    if frame.empty:
        return []
    return [int(year) for year in frame["year"].tolist()]


def available_states() -> list[str]:
    frame = fetch_df(
        "aggregated_transaction",
        """
        SELECT DISTINCT state
        FROM aggregated_transaction
        WHERE state <> 'india'
        ORDER BY state
        """,
    )
    return frame["state"].tolist() if not frame.empty else []


def transaction_mix(state: str, year: int) -> pd.DataFrame:
    return fetch_df(
        "aggregated_transaction",
        """
        SELECT quarter, transaction_type,
               SUM(transaction_count) AS transaction_count,
               SUM(transaction_amount) AS transaction_amount
        FROM aggregated_transaction
        WHERE state = %s AND year = %s
        GROUP BY quarter, transaction_type
        ORDER BY quarter, transaction_type
        """,
        (state, year),
    )


def state_transaction_leaders(year: int, quarter: int, limit: int = 10) -> pd.DataFrame:
    return fetch_df(
        "map_transaction",
        """
        SELECT state,
               SUM(transaction_count) AS transaction_count,
               SUM(transaction_amount) AS transaction_amount
        FROM map_transaction
        WHERE geo_level = 'state' AND year = %s AND quarter = %s
        GROUP BY state
        ORDER BY transaction_count DESC
        LIMIT %s
        """,
        (year, quarter, limit),
    )


def quarterly_state_totals() -> pd.DataFrame:
    return fetch_df(
        "aggregated_transaction",
        """
        SELECT state, year, quarter, SUM(transaction_count) AS transaction_count
        FROM aggregated_transaction
        WHERE state <> 'india'
        GROUP BY state, year, quarter
        ORDER BY state, year, quarter
        """,
    )


def add_quarter_growth(frame: pd.DataFrame, value_col: str = "transaction_count") -> pd.DataFrame:
    """Attach the previous-quarter change for each state."""
    ordered = frame.sort_values(["state", "year", "quarter"]).copy()
    ordered["prev_value"] = ordered.groupby("state")[value_col].shift(1)
    ordered["qoq_change"] = (ordered[value_col] - ordered["prev_value"]) / ordered["prev_value"]
    return ordered


def user_totals(year: int) -> pd.DataFrame:
    return fetch_df(
        "aggregated_user",
        """
        SELECT state, quarter, registered_users, app_opens
        FROM aggregated_user
        WHERE row_kind = 'total' AND year = %s AND state <> 'india'
        ORDER BY registered_users DESC
        """,
        (year,),
    )


def device_breakdown(year: int, quarter: int) -> pd.DataFrame:
    return fetch_df(
        "aggregated_user",
        """
        SELECT state, brand, device_count, device_percentage, registered_users, app_opens
        FROM aggregated_user
        WHERE row_kind = 'device' AND year = %s AND quarter = %s
        ORDER BY device_count DESC
        """,
        (year, quarter),
    )


def merchant_totals(year: int, quarter: int) -> pd.DataFrame:
    return fetch_df(
        "aggregated_merchant",
        """
        SELECT state, registered_merchants
        FROM aggregated_merchant
        WHERE year = %s AND quarter = %s AND state <> 'india'
        ORDER BY registered_merchants DESC
        """,
        (year, quarter),
    )


def merchant_penetration(year: int, quarter: int) -> pd.DataFrame:
    users = fetch_df(
        "aggregated_user",
        """
        SELECT state, registered_users
        FROM aggregated_user
        WHERE row_kind = 'total' AND year = %s AND quarter = %s AND state <> 'india'
        """,
        (year, quarter),
    )
    merchants = merchant_totals(year, quarter)
    if users.empty or merchants.empty:
        return pd.DataFrame(
            columns=["state", "registered_users", "registered_merchants", "merchants_per_user"]
        )
    merged = users.merge(merchants, on="state", how="inner")
    merged["merchants_per_user"] = merged["registered_merchants"] / merged["registered_users"].replace(0, pd.NA)
    return merged.sort_values("registered_merchants", ascending=False)


def top_entities(table_name: str, year: int, quarter: int, entity_level: str, limit: int = 10) -> pd.DataFrame:
    value_col = {
        "top_transaction": "transaction_count",
        "top_user": "registered_users",
        "top_merchant": "registered_merchants",
    }[table_name]
    return fetch_df(
        table_name,
        f"""
        SELECT entity_name, {value_col} AS metric_value
        FROM {table_name}
        WHERE scope_state = 'india'
          AND year = %s
          AND quarter = %s
          AND entity_level = %s
        ORDER BY {value_col} DESC
        LIMIT %s
        """,
        (year, quarter, entity_level, limit),
    )


def district_transactions(state: str, year: int, quarter: int) -> pd.DataFrame:
    return fetch_df(
        "map_transaction",
        """
        SELECT district, transaction_count, transaction_amount
        FROM map_transaction
        WHERE geo_level = 'district' AND state = %s AND year = %s AND quarter = %s
        ORDER BY transaction_count DESC
        """,
        (state, year, quarter),
    )
