"""Streamlit dashboard for the Email Automation System."""

import sqlite3
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.database import (
    add_contact,
    delete_contact,
    get_contacts,
    save_contacts,
)
from modules.email_logs import get_email_logs
from modules.importer import import_file
from modules.validator import is_valid_email, validate_emails

st.set_page_config(
    page_title="Email Automation System",
    page_icon="📧",
    layout="wide",
)

st.title("📧 Email Automation System")
st.write(
    "Import contacts, validate email addresses, "
    "manage contacts, and review email logs."
)

# CSV / Excel Import
st.header("📂 CSV / Excel Import")

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
)

if uploaded_file is not None:
    try:
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
        st.dataframe(
            imported_contacts,
            use_container_width=True,
        )

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

            valid_contacts = validated_contacts.loc[
                validated_contacts["email_valid"]
            ].drop(columns=["email_valid"])

            total_rows = len(imported_contacts)
            valid_count = len(valid_contacts)
            invalid_count = total_rows - valid_count

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", total_rows)
            col2.metric("Valid Emails", valid_count)
            col3.metric("Invalid Emails", invalid_count)

            if st.button("Save Valid Contacts to Database"):
                if valid_contacts.empty:
                    st.warning("There are no valid contacts to save.")
                else:
                    try:
                        save_contacts(valid_contacts)
                        st.success(
                            "Valid contacts saved successfully. "
                            "Duplicate email addresses are removed."
                        )
                        st.rerun()
                    except (sqlite3.Error, ValueError, OSError) as error:
                        st.error(f"Could not save contacts: {error}")

    except (
        OSError,
        ValueError,
        UnicodeError,
        ImportError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as error:
        st.error(f"Could not import the file: {error}")

# Contact Management
st.divider()
st.header("👥 Contact Management")

try:
    contacts_df = get_contacts()

    if contacts_df.empty:
        st.info(
            "No contacts found. Import a CSV or Excel file " "or add a contact below."
        )
    else:
        search_term = st.text_input(
            "Search contacts by name or email",
            key="contact_search",
        )

        filtered_contacts = contacts_df.copy()

        if search_term.strip():
            searchable_columns = [
                column
                for column in filtered_contacts.columns
                if column.strip().lower()
                in {"name", "email", "email_id", "register_number"}
            ]

            if searchable_columns:
                matches = (
                    filtered_contacts[searchable_columns]
                    .astype(str)
                    .apply(
                        lambda column: column.str.contains(
                            search_term.strip(),
                            case=False,
                            na=False,
                            regex=False,
                        )
                    )
                    .any(axis=1)
                )

                filtered_contacts = filtered_contacts.loc[matches]

        st.dataframe(
            filtered_contacts,
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"Contacts displayed: {len(filtered_contacts)}")

    # Add Contact
    with st.expander("➕ Add a Contact"), st.form("add_contact_form"):
        contact_name = st.text_input("Name")
        contact_email = st.text_input("Email address")
        contact_department = st.text_input("Department")

        add_submitted = st.form_submit_button("Add Contact")

        if add_submitted:
            if not contact_name.strip():
                st.error("Name is required.")
            elif not is_valid_email(contact_email):
                st.error("Enter a valid email address.")
            else:
                try:
                    add_contact(
                        {
                            "name": contact_name.strip(),
                            "email": contact_email.strip(),
                            "department": contact_department.strip(),
                        }
                    )
                    st.success("Contact added successfully.")
                    st.rerun()
                except ValueError as error:
                    st.error(f"Could not add contact: {error}")
                except (sqlite3.Error, OSError) as error:
                    st.error(f"Database error: {error}")

    # Delete Contact
    with st.expander("🗑️ Delete a Contact"):
        email_to_delete = st.text_input(
            "Email address of the contact to delete",
            key="delete_contact_email",
        )

        if st.button("Delete Contact"):
            if not email_to_delete.strip():
                st.warning("Enter an email address first.")
            else:
                try:
                    deleted_count = delete_contact(email_to_delete.strip())

                    if deleted_count:
                        st.success("Contact deleted successfully.")
                        st.rerun()
                    else:
                        st.warning("No contact found with that email address.")
                except (ValueError, sqlite3.Error, OSError) as error:
                    st.error(f"Could not delete contact: {error}")

except (sqlite3.Error, OSError) as error:
    st.error(f"Could not load contacts: {error}")

# Email Logs
st.divider()
st.header("📨 Email Logs")

try:
    logs = get_email_logs()

    if logs:
        logs_df = pd.DataFrame(logs)

        total_logs = len(logs_df)
        sent_count = int((logs_df["status"] == "sent").sum())
        failed_count = int((logs_df["status"] == "failed").sum())

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Attempts", total_logs)
        col2.metric("Sent", sent_count)
        col3.metric("Failed", failed_count)

        st.dataframe(
            logs_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = logs_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Email Logs as CSV",
            data=csv_data,
            file_name="email_logs.csv",
            mime="text/csv",
        )
    else:
        st.info(
            "No email logs yet. Logs will appear here when "
            "email attempts are recorded."
        )

except (sqlite3.Error, OSError) as error:
    st.error(f"Could not load email logs: {error}")
