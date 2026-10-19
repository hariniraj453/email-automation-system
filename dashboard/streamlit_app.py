"""Streamlit dashboard for the Email Automation System."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from modules.database import (
    add_contact,
    delete_contact,
    get_contacts,
    save_contacts,
)
from modules.importer import import_file
from modules.validator import validate_emails
from modules.template_engine import create_email
from modules.template_store import (
    delete_template,
    get_templates,
    save_template,
)

st.set_page_config(
    page_title="Email Automation System",
    page_icon="📧",
    layout="wide",
)

st.title("📧 Email Automation System")
st.caption(
    "Import contacts, manage recipients, and create personalized "
    "email templates."
)

# --------------------------------------------------
# 1. Dashboard Overview
# --------------------------------------------------

st.header("📊 Dashboard Overview")

try:
    stored_contacts = get_contacts()
    total_contacts = len(stored_contacts)
except (FileNotFoundError, ValueError, OSError):
    stored_contacts = pd.DataFrame()
    total_contacts = 0

try:
    saved_templates = get_templates()
    total_templates = len(saved_templates)
except (ValueError, OSError):
    saved_templates = pd.DataFrame()
    total_templates = 0

col1, col2 = st.columns(2)
col1.metric("Total Recipients", total_contacts)
col2.metric("Saved Templates", total_templates)

st.divider()

# --------------------------------------------------
# 2. Import CSV or Excel
# --------------------------------------------------

st.header("📁 Import Contacts")

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx", "xls"],
)

if uploaded_file is not None:
    temporary_path = (
        PROJECT_ROOT / f"_dashboard_upload{Path(uploaded_file.name).suffix}"
    )

    try:
        temporary_path.write_bytes(uploaded_file.getvalue())
        contacts = import_file(str(temporary_path))

        email_column = next(
            (
                column
                for column in contacts.columns
                if column.strip().lower() in {"email", "email_id"}
            ),
            None,
        )

        if email_column is None:
            st.error(
                "No email column found. Use a column named "
                "'email' or 'email_id'."
            )
        else:
            results = validate_emails(
                contacts,
                email_column=email_column,
            )

            st.subheader("Import Preview")
            st.dataframe(results, use_container_width=True)

            valid_count = int(results["email_valid"].sum())
            invalid_count = len(results) - valid_count

            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("Uploaded Records", len(results))
            metric2.metric("Valid Email Formats", valid_count)
            metric3.metric("Invalid Email Formats", invalid_count)

            if st.button("Save Imported Contacts"):
                # Existing save_contacts replaces the contacts table.
                # Avoid importing until you have backed up existing data.
                st.warning(
                    "Your current save_contacts function replaces the "
                    "contacts table. Back up existing contacts before "
                    "saving an import."
                )

    except (ValueError, OSError, KeyError) as error:
        st.error(f"Could not process the file: {error}")

    finally:
        temporary_path.unlink(missing_ok=True)

st.divider()

# --------------------------------------------------
# 3. Manage Recipients
# --------------------------------------------------

st.header("👥 Manage Recipients")

try:
    recipients = get_contacts()
except (FileNotFoundError, ValueError, OSError):
    recipients = pd.DataFrame()

with st.form("add_recipient_form"):
    st.subheader("Add a Recipient")

    recipient_name = st.text_input("Recipient Name")
    recipient_email = st.text_input("Email Address")
    recipient_department = st.text_input(
        "Department (optional)"
    )

    add_clicked = st.form_submit_button("Add Recipient")

    if add_clicked:
        if not recipient_name.strip() or not recipient_email.strip():
            st.error("Enter both a name and an email address.")
        else:
            email_column = (
                "email_id"
                if "email_id" in recipients.columns
                else "email"
            )

            contact = {
                "name": recipient_name.strip(),
                email_column: recipient_email.strip(),
            }

            if "department" in recipients.columns or recipients.empty:
                contact["department"] = recipient_department.strip()

            try:
                add_contact(contact)
                st.success("Recipient added successfully!")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
            except (OSError, RuntimeError) as error:
                st.error(f"Could not add recipient: {error}")

st.subheader("Stored Recipients")

try:
    recipients = get_contacts()

    if recipients.empty:
        st.info("No recipients have been stored yet.")
    else:
        st.dataframe(
            recipients,
            use_container_width=True,
            hide_index=True,
        )

        email_column = next(
            (
                column
                for column in recipients.columns
                if column.strip().lower() in {"email", "email_id"}
            ),
            None,
        )

        if email_column:
            emails = (
                recipients[email_column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            if emails:
                selected_email = st.selectbox(
                    "Select a recipient to delete",
                    emails,
                )

                if st.button("Delete Selected Recipient"):
                    try:
                        deleted = delete_contact(selected_email)

                        if deleted:
                            st.success("Recipient deleted.")
                            st.rerun()
                        else:
                            st.warning("Recipient was not found.")
                    except (ValueError, OSError) as error:
                        st.error(f"Could not delete recipient: {error}")

except (FileNotFoundError, ValueError, OSError) as error:
    st.info(f"No stored recipients available: {error}")

st.divider()

# --------------------------------------------------
# 4. Create and Preview Email Templates
# --------------------------------------------------

st.header("✉️ Email Template Management")

with st.form("create_template_form"):
    st.subheader("Create a Template")

    template_name = st.text_input(
        "Template Name",
        key="template_name",
    )

    subject_text = st.text_input(
        "Email Subject",
        value="Welcome, $name!",
        key="template_subject",
    )

    body_text = st.text_area(
        "Email Body",
        value=(
            "Hello $name,\n\n"
            "Welcome to our email automation system.\n\n"
            "Best regards,\n"
            "The Team"
        ),
        height=180,
        key="template_body",
    )

    save_clicked = st.form_submit_button("Save Template")

    if save_clicked:
        if not template_name.strip():
            st.error("Enter a template name.")
        elif not subject_text.strip() or not body_text.strip():
            st.error("Subject and body cannot be empty.")
        else:
            try:
                save_template(
                    template_name,
                    subject_text,
                    body_text,
                )
                st.success("Template saved successfully!")
                st.rerun()
            except Exception as error:
                if "UNIQUE constraint failed" in str(error):
                    st.error("That template name already exists.")
                else:
                    st.error(f"Could not save template: {error}")

st.subheader("Preview an Email")

preview_name = st.text_input(
    "Recipient Name for Preview",
    value="Harini",
    key="preview_name",
)

preview_subject = st.text_input(
    "Preview Subject",
    value="Welcome, $name!",
    key="preview_subject",
)

preview_body = st.text_area(
    "Preview Body",
    value="Hello $name,\n\nWelcome to our project!",
    key="preview_body",
)

try:
    rendered_subject, rendered_body = create_email(
        preview_name,
        preview_subject,
        preview_body,
    )

    st.markdown("**Rendered Subject**")
    st.write(rendered_subject)

    st.markdown("**Rendered Message**")
    st.text(rendered_body)

except (ValueError, TypeError) as error:
    st.error(f"Could not preview the template: {error}")

st.subheader("Saved Templates")

try:
    templates = get_templates()

    if templates.empty:
        st.info("No saved templates yet.")
    else:
        st.dataframe(
            templates,
            use_container_width=True,
            hide_index=True,
        )

        template_options = {
            f"{row['name']} (ID: {row['id']})": int(row["id"])
            for _, row in templates.iterrows()
        }

        selected_template = st.selectbox(
            "Select a template to delete",
            list(template_options.keys()),
        )

        if st.button("Delete Selected Template"):
            delete_template(template_options[selected_template])
            st.success("Template deleted.")
            st.rerun()

except (ValueError, OSError) as error:
    st.error(f"Could not load saved templates: {error}")
