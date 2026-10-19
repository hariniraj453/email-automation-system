"""Validate email addresses in contact records."""

import re

import pandas as pd

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def is_valid_email(email: object) -> bool:
    """Return whether an email address has a valid basic format."""
    if not isinstance(email, str):
        return False

    email = email.strip()

    if not email or len(email) > 254:
        return False

    return EMAIL_PATTERN.fullmatch(email) is not None


def validate_emails(
    contacts: pd.DataFrame,
    email_column: str = "email_id",
) -> pd.DataFrame:
    """Return a copy of contacts with an email validity column."""
    if email_column not in contacts.columns:
        raise ValueError(f"Required email column '{email_column}' was not found.")

    result = contacts.copy()
    result["email_valid"] = result[email_column].apply(is_valid_email)

    return result
