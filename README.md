# Email Automation System

## Project Overview

The Email Automation System is a Python-based project designed to import contact data, validate email address formats, store records in an SQLite database, and prepare personalized email messages.

## Features

- Import contact data from CSV files
- Import contact data from Excel files
- Normalize column names and remove surrounding whitespace
- Validate email address formats
- Store and retrieve records using SQLite
- Prepare personalized email subjects and message bodies
- Run automated unit tests

## Technology Stack

- Python
- Pandas
- SQLite
- OpenPyXL
- Pytest
- Black
- Ruff
- Git and GitHub

## Project Structure

```text
email-automation-system/
├── app.py
├── modules/
│   ├── importer.py
│   ├── validator.py
│   ├── database.py
│   └── template_engine.py
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install the required dependencies.
4. Prepare a sample CSV or Excel contact file.
5. Run the application and enter the input file path.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Run tests:

```bash
python -m pytest -v
```

Check code quality:

```bash
python -m black .
python -m ruff check .
```

## Privacy and Security

Use synthetic sample contact data for development and demonstrations. Do not upload personal contact information, passwords, API keys, or environment files.

## Project Status

Core data import, email-format validation, SQLite storage, and automated testing are part of the current project scope. Email delivery and any additional interface should be documented as complete only after implementation and testing.