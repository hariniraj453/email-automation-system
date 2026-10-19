"""Tests for contact data import."""

import pandas as pd
import pytest

from modules.importer import import_csv


def test_import_csv(tmp_path):
    """Import records from a temporary CSV file."""
    csv_file = tmp_path / "contacts.csv"
    pd.DataFrame(
        {
            "NAME :": ["Test Student"],
            "EMAIL ID:": ["student@example.com"],
        }
    ).to_csv(csv_file, index=False)

    result = import_csv(str(csv_file))

    assert result.columns.tolist() == ["name", "email_id"]
    assert result.loc[0, "name"] == "Test Student"


def test_missing_csv_file():
    """Raise an error when the CSV file does not exist."""
    with pytest.raises(FileNotFoundError):
        import_csv("missing_file.csv")
