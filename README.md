# Hudl Login Test Automation

A production-ready test automation framework validating the Hudl login flow, built with Python and Playwright.

---

## Tech Stack

- **Language:** Python 3.8+
- **Framework:** Playwright
- **Test Runner:** pytest
- **Reporting:** pytest-html
- **Linting:** flake8

---

## Prerequisites

Ensure the following are installed before getting started:

- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/) (required by Playwright internally)
- [Git](https://git-scm.com/)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Caleb-Poggemeyer/hudl-qa-automation.git
cd hudl-qa-automation
```

### 2. Create and activate a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install chromium
```

### 5. Configure credentials

Create a `.env` file in the project root based on the provided template:

```bash
cp .env.example .env
```

Then open `.env` and fill in your Hudl test credentials:

```
HUDL_EMAIL=your_test_email@example.com
HUDL_PASSWORD=your_test_password
```

> ⚠️ Never commit the `.env` file. It is listed in `.gitignore` and must be kept local.

---

## Running the Tests

### Run the full test suite

```bash
pytest -v
```

### Run a specific test class

```bash
pytest tests/test_login.py::TestLoginSuccess -v
pytest tests/test_login.py::TestLoginFailure -v
pytest tests/test_login.py::TestLoginPageUI -v
```

### Run a single test

```bash
pytest tests/test_login.py::TestLoginSuccess::test_valid_login -v
```

### Run in headed mode (watch the browser)

```bash
pytest -v --headed
```

### Run in slow motion (useful for debugging)

```bash
pytest -v --headed --slowmo 1000
```

### View the HTML report

After running the tests, open the generated report in your browser:

```
reports/report.html
```

---

## Linting

This project uses flake8 to enforce code quality. To run the linter:

```bash
flake8 .
```

A clean run produces no output.

---

## Project Structure

```
hudl-qa-automation/
├── pages/
│   ├── __init__.py
│   └── login_page.py       # Page Object Model for the Hudl login page
├── tests/
│   ├── __init__.py
│   └── test_login.py       # Full login test suite
├── .env                    # Local credentials (never committed)
├── .env.example            # Credential template (safe to commit)
├── .flake8                 # Linting configuration
├── .gitignore              # Git ignore rules
├── conftest.py             # Shared pytest fixtures and browser setup
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Project dependencies
└── README.md               # This file
```

---

## Test Coverage

| Category | Test | Description |
|----------|------|-------------|
| ✅ Success | `test_valid_login` | Valid credentials log the user in |
| ❌ Failure | `test_invalid_password` | Valid email with wrong password shows error |
| ❌ Failure | `test_invalid_email` | Unrecognised email shows error |
| ❌ Failure | `test_empty_email` | Empty email submission shows error |
| ❌ Failure | `test_empty_password` | Empty password submission shows error |
| ❌ Failure | `test_both_fields_empty` | Both fields empty shows error |
| ❌ Failure | `test_invalid_email_format` | Malformed email shows error |
| 🖥️ UI | `test_forgot_password_link_navigates` | Forgot Password link navigates correctly |
| 🖥️ UI | `test_password_field_masked_by_default` | Password field is masked by default |
| 🖥️ UI | `test_login_page_title` | Page title is correct |

---

## Design Decisions

- **Page Object Model (POM):** All page interactions are encapsulated in `pages/login_page.py`, keeping tests clean and maintainable.
- **Two-step login handling:** Hudl's login flow uses a two-step form (email first, then password). The Page Object handles both steps transparently.
- **Secure credential handling:** Credentials are loaded from a `.env` file at runtime using `python-dotenv` and are never hardcoded or committed.
- **HTML reporting:** Test results are automatically saved to `reports/report.html` after every run.
