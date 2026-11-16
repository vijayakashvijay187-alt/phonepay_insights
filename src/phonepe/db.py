"""Connections to the per-table PhonePe databases."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg

from phonepe.config import table_by_name

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "pulse"


def dsn(table_name: str) -> str:
    table = table_by_name(table_name)
    host = os.getenv("DB_HOST", "127.0.0.1")
    user = os.getenv("DB_USER", "app")
    password = os.getenv("DB_PASSWORD", "app")
    env_key = f"PHONEPE_{table.name.upper()}_PORT"
    port = int(os.getenv(env_key, str(table.port)))
    return (
        f"host={host} port={port} dbname={table.name} "
        f"user={user} password={password} connect_timeout=3"
    )


def connect(table_name: str) -> psycopg.Connection:
    return psycopg.connect(dsn(table_name))
