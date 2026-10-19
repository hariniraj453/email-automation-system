"""Store and manage contact records using SQLite."""

import sqlite3
from pathlib import Path

import pandas as pd

DEFAULT_DATABASE = "data/contacts.db"


def save_contacts(
    contacts: pd.DataFrame,
    database_path: str = DEFAULT_DATABASE,
) -> None:
    """Save imported contacts to the SQLite database."""
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
    database_path: str = DEFAULT_DATABASE,
) -> pd.DataFrame:
    """Retrieve all stored contacts."""
    path = Path(database_path)

    if not path.is_file():
        raise FileNotFoundError(f"Database not found: {path}")

    with sqlite3.connect(path) as connection:
        return pd.read_sql_query(
            "SELECT * FROM contacts",
            connection,
        )


def add_contact(
    contact: dict,
    database_path: str = DEFAULT_DATABASE,
) -> None:
    """Add a contact and prevent duplicate email addresses."""
    email_key = next(
        (
            key
            for key in contact
            if key.strip().lower() in {"email", "email_id"}
        ),
        None,
    )

    if email_key is None:
        raise ValueError("Contact must contain an email or email_id field.")

    email = str(contact[email_key]).strip().lower()

    if not email:
        raise ValueError("Email address cannot be empty.")

    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.is_file():
        try:
            existing = get_contacts(database_path)
        except (sqlite3.Error, ValueError):
            existing = pd.DataFrame()
    else:
        existing = pd.DataFrame()

    if not existing.empty:
        existing_email_key = next(
            (
                column
                for column in existing.columns
                if column.strip().lower() in {"email", "email_id"}
            ),
            None,
        )

        if existing_email_key:
            emails = (
                existing[existing_email_key]
                .astype(str)
                .str.strip()
                .str.lower()
            )
            if email in emails.values:
                raise ValueError("This email address already exists.")

    new_contact = pd.DataFrame([contact])
    combined = pd.concat(
        [existing, new_contact],
        ignore_index=True,
    )
    save_contacts(combined, database_path)


def delete_contact(
    email: str,
    database_path: str = DEFAULT_DATABASE,
) -> int:
    """Delete a contact by email and return the number deleted."""
    contacts = get_contacts(database_path)
    email_key = next(
        (
            column
            for column in contacts.columns
            if column.strip().lower() in {"email", "email_id"}
        ),
        None,
    )

    if email_key is None:
        raise ValueError("No email column was found in the contacts table.")

    matches = (
        contacts[email_key]
        .astype(str)
        .str.strip()
        .str.lower()
        == email.strip().lower()
    )
    deleted_count = int(matches.sum())

    if deleted_count:
        save_contacts(contacts.loc[~matches].copy(), database_path)

    return deleted_count
