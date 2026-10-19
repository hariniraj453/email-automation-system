"""Store and manage contact records using SQLite."""

import sqlite3
from pathlib import Path

import pandas as pd

DEFAULT_DATABASE = "data/contacts.db"


def _find_email_column(contacts: pd.DataFrame) -> str | None:
    """Find the email column in a contact DataFrame."""
    for column in contacts.columns:
        if str(column).strip().lower() in {"email", "email_id"}:
            return column
    return None


def _read_existing_contacts(database_path: str) -> pd.DataFrame:
    """Read existing contacts, returning an empty DataFrame if absent."""
    path = Path(database_path)

    if not path.is_file():
        return pd.DataFrame()

    with sqlite3.connect(path) as connection:
        table = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'contacts'
            """).fetchone()

        if table is None:
            return pd.DataFrame()

        return pd.read_sql_query("SELECT * FROM contacts", connection)


def _write_contacts(
    contacts: pd.DataFrame,
    database_path: str,
) -> None:
    """Write the supplied contacts to the contacts table."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(path) as connection:
        contacts.to_sql(
            "contacts",
            connection,
            if_exists="replace",
            index=False,
        )


def save_contacts(
    contacts: pd.DataFrame,
    database_path: str = DEFAULT_DATABASE,
) -> None:
    """Merge contacts into storage without duplicating email addresses."""
    existing = _read_existing_contacts(database_path)

    if existing.empty:
        combined = contacts.copy()
    else:
        combined = pd.concat(
            [existing, contacts],
            ignore_index=True,
            sort=False,
        )

    email_column = _find_email_column(combined)

    if email_column is not None:
        normalized_emails = (
            combined[email_column].fillna("").astype(str).str.strip().str.lower()
        )

        has_email = normalized_emails.ne("")
        without_email = combined.loc[~has_email].copy()
        with_email = combined.loc[has_email].copy()

        with_email["_email_key"] = normalized_emails.loc[has_email]
        with_email = with_email.drop_duplicates(
            subset="_email_key",
            keep="first",
        ).drop(columns="_email_key")

        combined = pd.concat(
            [with_email, without_email],
            ignore_index=True,
            sort=False,
        )

    _write_contacts(combined, database_path)


def get_contacts(
    database_path: str = DEFAULT_DATABASE,
) -> pd.DataFrame:
    """Retrieve all stored contacts."""
    return _read_existing_contacts(database_path)


def add_contact(
    contact: dict,
    database_path: str = DEFAULT_DATABASE,
) -> None:
    """Add a contact while preventing duplicate email addresses."""
    email_key = next(
        (key for key in contact if str(key).strip().lower() in {"email", "email_id"}),
        None,
    )

    if email_key is None:
        raise ValueError("Contact must contain an email or email_id field.")

    email = str(contact[email_key]).strip()

    if not email:
        raise ValueError("Email address cannot be empty.")

    if not _is_valid_email_format(email):
        raise ValueError("Please provide a valid email address.")

    existing = _read_existing_contacts(database_path)
    existing_email_column = _find_email_column(existing)

    if existing_email_column is not None:
        emails = (
            existing[existing_email_column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        if email.lower() in emails.values:
            raise ValueError("This email address already exists.")

    save_contacts(pd.DataFrame([contact]), database_path)


def _is_valid_email_format(email: str) -> bool:
    """Check basic email formatting before storing a contact."""
    if len(email) > 254 or " " in email:
        return False

    parts = email.rsplit("@", 1)

    if len(parts) != 2:
        return False

    local_part, domain = parts

    return (
        bool(local_part)
        and bool(domain)
        and "." in domain
        and not domain.startswith(".")
        and not domain.endswith(".")
    )


def delete_contact(
    email: str,
    database_path: str = DEFAULT_DATABASE,
) -> int:
    """Delete a contact by email and return the number deleted."""
    contacts = get_contacts(database_path)

    if contacts.empty:
        return 0

    email_column = _find_email_column(contacts)

    if email_column is None:
        raise ValueError("No email column was found in the contacts table.")

    matches = (
        contacts[email_column].fillna("").astype(str).str.strip().str.lower()
        == email.strip().lower()
    )

    deleted_count = int(matches.sum())

    if deleted_count:
        remaining = contacts.loc[~matches].copy()
        _write_contacts(remaining, database_path)

    return deleted_count
