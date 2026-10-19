"""Import and prepare contact data from CSV and Excel files."""

from pathlib import Path

import pandas as pd


def _prepare_contacts(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and remove surrounding whitespace."""
    data = data.copy()

    data.columns = [
        str(column).strip().lower().replace(":", "").strip().replace(" ", "_")
        for column in data.columns
    ]

    for column in data.select_dtypes(include=["object"]).columns:
        data[column] = data[column].str.strip()

    return data


def import_csv(file_path: str) -> pd.DataFrame:
    """Import contact records from a CSV file."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    return _prepare_contacts(pd.read_csv(path))


def import_excel(file_path: str) -> pd.DataFrame:
    """Import contact records from an Excel file."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Excel file not found: {path}")

    return _prepare_contacts(pd.read_excel(path))


def import_file(file_path: str) -> pd.DataFrame:
    """Import a CSV or Excel file based on its extension."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".csv":
        return import_csv(file_path)

    if extension in (".xlsx", ".xls"):
        return import_excel(file_path)

    raise ValueError("Unsupported file type. Please use CSV or Excel.")
