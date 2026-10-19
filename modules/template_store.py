
"""Save and manage email templates in SQLite."""

import sqlite3
from pathlib import Path

import pandas as pd

DATABASE_PATH = Path("data/contacts.db")


def initialize_templates() -> None:
    """Create the email templates table if it does not exist."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                body TEXT NOT NULL
            )
            """
        )


def save_template(name: str, subject: str, body: str) -> None:
    """Save a new email template."""
    initialize_templates()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO email_templates (name, subject, body)
            VALUES (?, ?, ?)
            """,
            (name.strip(), subject.strip(), body.strip()),
        )


def get_templates() -> pd.DataFrame:
    """Return all saved email templates."""
    initialize_templates()

    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(
            "SELECT id, name, subject, body "
            "FROM email_templates ORDER BY id DESC",
            connection,
        )


def delete_template(template_id: int) -> None:
    """Delete an email template by its ID."""
    initialize_templates()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "DELETE FROM email_templates WHERE id = ?",
            (template_id,),
        )
