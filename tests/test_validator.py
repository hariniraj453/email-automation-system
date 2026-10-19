"""Tests for email validation."""

import pandas as pd

from modules.validator import is_valid_email, validate_emails


def test_valid_email():
    """Accept a correctly formatted email."""
    assert is_valid_email("student@example.com") is True


def test_invalid_email():
    """Reject an incorrectly formatted email."""
    assert is_valid_email("invalid-email") is False


def test_empty_email():
    """Reject an empty email."""
    assert is_valid_email("") is False


def test_validate_emails_column():
    """Add an email_valid column to the contact data."""
    contacts = pd.DataFrame({"email_id": ["student@example.com", "invalid-email"]})

    result = validate_emails(contacts)

    assert result["email_valid"].tolist() == [True, False]
