"""Wait for the table databases, apply schema, and reload Pulse data."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from phonepe.config import TABLES  # noqa: E402
from phonepe.db import DATA_DIR, connect  # noqa: E402
from phonepe.extract import extract_all  # noqa: E402
from phonepe.load import replace_table  # noqa: E402
from phonepe.sql_util import split_sql  # noqa: E402


def wait_for_databases(timeout: int = 120) -> None:
    pending = {table.name for table in TABLES}
    deadline = time.time() + timeout
    while pending and time.time() < deadline:
        for name in list(pending):
            try:
                with connect(name) as conn:
                    conn.execute("SELECT 1")
                pending.remove(name)
                print(f"ready  {name}")
            except Exception:
                pass
        if pending:
            time.sleep(1)
    if pending:
        missing = ", ".join(sorted(pending))
        raise SystemExit(f"Timed out waiting for: {missing}")


def migrate() -> None:
    sql_dir = ROOT / "sql"
    for table in TABLES:
        script = (sql_dir / f"{table.name}.sql").read_text(encoding="utf-8")
        with connect(table.name) as conn:
            with conn.cursor() as cur:
                for statement in split_sql(script):
                    cur.execute(statement)
            conn.commit()
        print(f"migrated  {table.name}")


def sync() -> None:
    if not (DATA_DIR / "aggregated").exists():
        raise SystemExit(
            f"Pulse data not found at {DATA_DIR}. Run scripts/download_data.sh first."
        )
    print(f"extracting {DATA_DIR}")
    tables = extract_all(DATA_DIR)
    for name, rows in tables.items():
        loaded = replace_table(name, rows)
        print(f"loaded  {name}: {loaded} rows")


def main() -> None:
    wait_for_databases()
    migrate()
    sync()


if __name__ == "__main__":
    main()
