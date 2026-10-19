from pathlib import Path

import streamlit as st

from modules.database import save_contacts
from modules.importer import import_file
from modules.validator import validate_emails
st.header("📂 CSV / Excel Import")

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
)

if uploaded_file is not None:
    try:
        import tempfile

        suffix = Path(uploaded_file.name).suffix.lower()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = Path(temp_file.name)

        try:
            imported_contacts = import_file(str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)

        st.subheader("Import Preview")
        st.dataframe(imported_contacts, use_container_width=True)

        email_column = next(
            (
                column
                for column in imported_contacts.columns
                if column.strip().lower() in {"email", "email_id"}
            ),
            None,
        )

        if email_column is None:
            st.error(
                "An email column is required. "
                "Use a column named 'email' or 'email_id'."
            )
        else:
            validated_contacts = validate_emails(
                imported_contacts,
                email_column=email_column,
            )

            st.subheader("Email Validation")
            st.dataframe(
                validated_contacts,
                use_container_width=True,
            )

            valid_contacts = validated_contacts[
                validated_contacts["email_valid"]
            ].drop(columns=["email_valid"])

            st.write(f"Total rows: {len(imported_contacts)}")
            st.write(f"Valid email rows: {len(valid_contacts)}")
            st.write(
                f"Invalid email rows: "
                f"{len(imported_contacts) - len(valid_contacts)}"
            )

            if st.button("Save Valid Contacts to Database"):
                if valid_contacts.empty:
                    st.warning("There are no valid contacts to save.")
                else:
                    try:
                        save_contacts(valid_contacts)
                        st.success(
                            "Valid contacts saved successfully! "
                            "Existing contacts are preserved and "
                            "duplicate emails are removed."
                        )
                        st.rerun()
                    except Exception as error:
                        st.error(f"Could not save contacts: {error}")

    except Exception as error:
        st.error(f"Could not import the file: {error}")
