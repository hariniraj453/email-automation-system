"""Store and retrieve contact records using SQLite."""

import sqlite3
from pathlib import Path

import pandas as pd


def save_contacts(
    contacts: pd.DataFrame,
    database_path: str = "data/contacts.db",
) -> None:
    """Save contact records to a SQLite database."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as connection:
        contacts.to_sql(
            "contacts",
            connection,
            if_exists="replace",
            index=False,
        )


def get_contacts(
    database_path: str = "data/contacts.db",
) -> pd.DataFrame:
    """Retrieve contact records from the SQLite database."""
    path = Path(database_path)

    if not path.is_file():
        raise FileNotFoundError(f"Database not found: {path}")

    with sqlite3.connect(path) as connection:
        return pd.read_sql_query(
            "SELECT * FROM contacts",
            connection,
        )
