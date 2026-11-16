"""Replace-load each extracted table into its own database."""

from __future__ import annotations

from phonepe.config import table_by_name
from phonepe.db import connect


def replace_table(table_name: str, rows: list[tuple]) -> int:
    table = table_by_name(table_name)
    column_list = ", ".join(table.columns)
    with connect(table_name) as conn:
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY")
            if rows:
                copy_sql = f"COPY {table_name} ({column_list}) FROM STDIN"
                with cur.copy(copy_sql) as copy:
                    for row in rows:
                        copy.write_row(row)
        conn.commit()
    return len(rows)
