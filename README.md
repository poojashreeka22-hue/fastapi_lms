# Library Management System (LMS) with Automated Testing

A beginner-friendly Library Management System built with Python, FastAPI, SQLite, and a console CLI.

## Setup Instructions (Windows PowerShell)

```powershell
cd "$HOME\LibraryManagementSystem"
uv sync --group dev --extra standard
```

## Running the Server

```powershell
uv run uvicorn app.main:app --reload
```

## Running the CLI Client

```powershell
uv run python client/library_cli.py
```

## Running the Automated Tests

```powershell
# Run selected tests:
uv run pytest tests/test_library_cli.py -v

# Run the complete test suite:
uv run pytest
```
