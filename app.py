"""Import, validate, and store contact records."""

from pathlib import Path

from modules.database import get_contacts, save_contacts
from modules.importer import import_file
from modules.validator import validate_emails


def main() -> None:
    """Run the contact import, validation, and storage workflow."""
    file_path = (
        input("Enter CSV or Excel file path (example: data/student.csv): ")
        .strip()
        .strip('"')
    )

    if not Path(file_path).is_file():
        print(f"File not found: {file_path}")
        return

    try:
        contacts = import_file(file_path)
        results = validate_emails(contacts)

        save_contacts(results)
        stored_contacts = get_contacts()

        print("\nImport completed successfully!")
        print(f"Total records stored: {len(stored_contacts)}")
        print(f"Valid email formats: {int(results['email_valid'].sum())}")
        print("Invalid email formats: " f"{int((~results['email_valid']).sum())}")
        print("Database: data/contacts.db")

    except (ValueError, OSError, KeyError) as error:
        print(f"Could not process the file: {error}")


if __name__ == "__main__":
    main()
