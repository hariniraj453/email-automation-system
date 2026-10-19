"""Import, validate, store, and optionally email contact records."""

from pathlib import Path

from dotenv import load_dotenv

from modules.database import get_contacts, save_contacts
from modules.email_sender import send_email
from modules.importer import import_file
from modules.template_engine import create_email
from modules.validator import validate_emails


def main() -> None:
    """Run the contact import and optional email workflow."""
    load_dotenv()

    file_path = (
        input("Enter CSV or Excel file path (example: data/students.csv): ")
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
        print(f"Invalid email formats: " f"{int((~results['email_valid']).sum())}")
        print("Database: data/contacts.db")

        choice = input(
            "\nSend emails to valid contacts? Type YES to continue: "
        ).strip()

        if choice != "YES":
            print("Email sending skipped.")
            return

        if "name" not in results.columns:
            print("Email sending stopped: a 'name' column is required.")
            return

        valid_contacts = results[results["email_valid"]]

        for _, contact in valid_contacts.iterrows():
            recipient = str(contact.get("email_id", contact.get("email", "")))
            name = str(contact["name"])

            subject, body = create_email(
                recipient_name=name,
                subject_template="Hello $name — project update",
                body_template=(
                    "Hello $name,\n\n"
                    "This is a test message from our Email Automation System.\n\n"
                    "Regards,\nProject Team"
                ),
            )

            try:
                send_email(recipient, subject, body)
                print(f"Email sent to {recipient}")
            except (ValueError, OSError, TimeoutError) as error:
                print(f"Could not send to {recipient}: {error}")

    except (ValueError, OSError, KeyError) as error:
        print(f"Could not process the file: {error}")


if __name__ == "__main__":
    main()
