
"""Streamlit dashboard for the Email Automation System."""

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.database import save_contacts
from modules.email_logs import get_email_logs
from modules.importer import import_file
from modules.validator import validate_emails


st.set_page_config(
    page_title="Email Automation System",
    page_icon="📧",
    layout="wide",
)

st.title("📧 Email Automation System")
st.write("Import contacts, validate email addresses, and review email logs.")

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
                            "Valid contacts saved to the database. "
                            "Existing contacts are preserved and "
                            "duplicate email addresses are removed."
                        )
                        st.rerun()
                    except Exception as error:
                        st.error(
                            f"Could not save contacts: {error}"
                        )

    except Exception as error:
        st.error(f"Could not import the file: {error}")


st.divider()

# Email Logs
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

except Exception as error:
    st.error(f"Could not load email logs: {error}")
