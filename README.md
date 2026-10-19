# Email Automation System

A Python-based project for importing contact data, validating email addresses, managing records with SQLite, and supporting email automation workflows through a Streamlit dashboard.

## Project Overview

The Email Automation System simplifies contact data processing by combining CSV and Excel imports, email validation, database storage, and personalized email template preparation. The project is designed with reusable Python modules, automated tests, and a user-friendly dashboard.

## Features

- **CSV Import:** Import contact records from CSV files.
- **Excel Import:** Read contact data from Excel files.
- **Data Cleaning:** Normalize column names and remove surrounding whitespace.
- **Email Validation:** Validate email address formats.
- **SQLite Database:** Store, retrieve, and manage contact records.
- **Contact Management:** Add, view, and delete contacts through the dashboard.
- **Email Templates:** Prepare personalized email subjects and message bodies.
- **Streamlit Dashboard:** Access supported application features through a visual interface.
- **Email Logs:** View recorded email statuses and failures, where logging is implemented.
- **Automated Testing:** Use Pytest to test application components.
- **Code Quality:** Use Black and Ruff to maintain consistent Python code.

*Note: Email sending and other features should be considered complete only after they have been implemented and tested successfully.*

## Technology Stack

- Python
- Pandas
- SQLite
- OpenPyXL
- Streamlit
- Pytest
- Black
- Ruff
- Git and GitHub
- SMTP, if configured for email delivery

## Project Structure

```text
email-automation-system/
├── dashboard/
│   └── streamlit_app.py
├── modules/
│   ├── importer.py
│   ├── validator.py
│   ├── database.py
│   ├── template_engine.py
│   ├── email_sender.py
│   └── ...
├── tests/
├── data/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The structure above is illustrative. Your actual repository may contain additional modules and files.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/hariniraj453/email-automation-system.git
cd email-automation-system
```

### 2. Create a Virtual Environment

For Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Prepare Contact Data

Prepare a CSV or Excel file with suitable contact columns, such as:

- Name
- Email
- Department

Use synthetic sample data when testing or demonstrating the application.

### 5. Configure Email Settings

If SMTP email sending is implemented, copy `.env.example` to `.env` and provide your own authorized SMTP configuration.

Example:

```dotenv
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USERNAME=your_email_address
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email_address
```

Never upload your actual `.env` file, credentials, or app passwords to GitHub.

## Running the Application

### Run the Streamlit Dashboard

From the project root, run:

```bash
python -m streamlit run dashboard/streamlit_app.py
```

Open the local URL displayed in the terminal.

### Run the Command-Line Application

If `app.py` is configured as a working command-line entry point, run:

```bash
python app.py
```

## Testing

Run the automated tests:

```bash
python -m pytest -v
```

Check code formatting:

```bash
python -m black --check .
```

Check code quality:

```bash
python -m ruff check .
```

## Dashboard Screenshots

Add screenshots of your working dashboard to a `screenshots/` directory and display them here.

Example:

```markdown
![Email Automation Dashboard](screenshots/dashboard.png)
```

Additional screenshots can demonstrate data import, contact management, and email logs. Ensure screenshots do not expose personal contact information or credentials.

## Privacy and Security

- Use synthetic contact data for development and demonstrations.
- Store credentials in environment variables.
- Keep `.env`, private datasets, database files, and virtual environments out of Git.
- Never commit passwords, app passwords, API keys, or personal contact information.
- Use authorized SMTP accounts when testing email delivery.

## Project Status

The project covers contact data import, email-format validation, SQLite storage, reusable modules, and automated testing.

The Streamlit dashboard provides a visual interface for the features implemented in the repository. Email delivery and any additional functionality should be reported as complete only after successful implementation and testing.

## Future Improvements

- Automated testing with GitHub Actions.
- Improved email template customization.
- Scheduled email workflows.
- Enhanced reporting and dashboard analytics.
- More comprehensive validation and error-handling tests.

## Author

**Harini R.**

- GitHub: https://github.com/hariniraj453
- LinkedIn: https://linkedin.com/in/harini-r-492ba0328

## License

A license can be added if you intend to specify how others may use, modify, and distribute this project.