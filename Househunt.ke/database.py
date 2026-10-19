"""
Database manager for HouseHunt Kenya.
Handles SQLite connection, initialization, migrations, and query execution.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional

DB_FILE = os.environ.get("HOUSEHUNT_DB", os.path.join(os.path.dirname(__file__), "househunt.db"))
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to SQLite database with dictionary rows enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(force: bool = False) -> None:
    """Initializes the database schema if not already present or forced."""
    if force and os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = get_db_connection()
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def query_db(query: str, args: tuple = (), one: bool = False) -> Any:
    """Executes a query and returns dictionaries."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (dict(rv[0])) if rv and one else ([dict(r) for r in rv] if not one else None)


def execute_db(query: str, args: tuple = ()) -> int:
    """Executes an INSERT/UPDATE/DELETE query and returns the lastrowid or affected rowcount."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return last_id


def execute_script(script: str) -> None:
    """Executes a full SQL script."""
    conn = get_db_connection()
    conn.executescript(script)
    conn.commit()
    conn.close()

