"""Store and retrieve email sending logs using SQLite."""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path("data/contacts.db")


def initialize_email_logs() -> None:
    """Create the email logs table if it does not exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                status TEXT NOT NULL,
                sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
            """
        )


def add_email_log(
    recipient: str,
    subject: str,
    status: str,
    error_message: str | None = None,
) -> None:
    """Record the result of an email sending attempt."""
    if status not in {"sent", "failed"}:
        raise ValueError("Status must be 'sent' or 'failed'.")

    initialize_email_logs()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO email_logs (
                recipient, subject, status, error_message
            )
            VALUES (?, ?, ?, ?)
            """,
            (recipient, subject, status, error_message),
        )


def get_email_logs() -> list[dict]:
    """Return email logs, newest first."""
    initialize_email_logs()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, recipient, subject, status, sent_at, error_message
            FROM email_logs
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
