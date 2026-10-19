"""REST API for the Email Automation System."""

import json
import tempfile
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

from modules.database import get_contacts, save_contacts
from modules.importer import import_file
from modules.validator import validate_emails

app = FastAPI(
    title="Email Automation System API",
    description="Import, validate, and retrieve contact records.",
    version="1.0.0",
)


def find_email_column(columns: list[str]) -> str:
    """Find a supported email column in the imported data."""
    for column in ("email_id", "email"):
        if column in columns:
            return column

    raise ValueError("The file must contain an email_id or email column.")


@app.get("/")
def home() -> dict[str, str]:
    """Return API information."""
    return {"message": "Email Automation System API is running."}


@app.get("/health")
def health() -> dict[str, str]:
    """Check API availability."""
    return {"status": "healthy"}


@app.post("/contacts/import")
async def import_contacts(file: UploadFile = File(...)) -> dict:
    """Import contacts, validate email formats, and save records."""
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(
            status_code=400,
            detail="Upload a CSV or Excel file.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="The file is empty.")

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_path = Path(temporary_file.name)

        contacts = import_file(str(temporary_path))
        email_column = find_email_column(list(contacts.columns))
        results = validate_emails(contacts, email_column=email_column)

        save_contacts(results)

        return {
            "message": "Contacts imported and saved successfully.",
            "total_records": len(results),
            "valid_emails": int(results["email_valid"].sum()),
            "invalid_emails": int((~results["email_valid"]).sum()),
        }

    except (ValueError, OSError, KeyError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

        await file.close()


@app.get("/contacts")
def list_contacts() -> dict:
    """Return all saved contact records."""
    try:
        contacts = get_contacts()
        records = json.loads(contacts.to_json(orient="records"))

        return {
            "total_records": len(records),
            "contacts": records,
        }

    except (FileNotFoundError, ValueError, OSError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
