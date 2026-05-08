import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "finance.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                period TEXT NOT NULL UNIQUE,           -- e.g. '2026-04'
                source_filename TEXT,
                uploaded_at TEXT NOT NULL DEFAULT (datetime('now')),
                statement_total REAL,
                detected_period_start TEXT,
                detected_period_end TEXT
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement_id INTEGER NOT NULL,
                txn_date TEXT NOT NULL,                -- ISO date
                merchant TEXT NOT NULL,
                description TEXT,
                amount REAL NOT NULL,                  -- positive = charge, negative = credit
                category TEXT NOT NULL,
                FOREIGN KEY (statement_id) REFERENCES statements(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_txn_statement ON transactions(statement_id);
            CREATE INDEX IF NOT EXISTS idx_txn_category ON transactions(category);

            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_limit REAL NOT NULL
            );
            """
        )


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
