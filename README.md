# Hudl Login Test Automation

[![CI](https://github.com/Caleb-Poggemeyer/hudl-qa-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/Caleb-Poggemeyer/hudl-qa-automation/actions/workflows/ci.yml)

A production-ready test automation framework validating the Hudl login flow, built with Python and Playwright.

---

## Tech Stack

- **Language:** Python 3.8+
- **Framework:** Playwright
- **Test Runner:** pytest
- **Reporting:** pytest-html
- **Linting:** flake8
- **CI:** GitHub Actions

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

## Debugging Failures

When a test fails, three resources are available:

1. **HTML report** at `reports/report.html` — generated automatically after every run; includes per-test pass/fail status and captured output.
2. **Headed mode** — re-run the failing test with `--headed` to watch the browser in real time.
3. **Slow motion** — combine `--headed --slowmo 1000` (milliseconds) to step through interactions at a readable pace.

In CI, the HTML report is uploaded as a workflow artifact and can be downloaded from the Actions run summary.

---

## Project Structure

```
hudl-qa-automation/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions: lint → test on every push/PR
├── pages/
│   ├── __init__.py
│   └── login_page.py           # Page Object Model for the Hudl login page
├── tests/
│   ├── __init__.py
│   └── test_login.py           # Full login test suite
├── .env                        # Local credentials (never committed)
├── .env.example                # Credential template (safe to commit)
├── .flake8                     # Linting configuration
├── .gitignore                  # Git ignore rules
├── conftest.py                 # Shared pytest fixtures and browser setup
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

---

## Test Coverage

| Category | Test | Description |
|---|---|---|
| ✅ Success | `test_valid_login` | Valid credentials log the user in |
| ✅ Success | `test_valid_login_email_case_insensitive` | Email matching is case-insensitive |
| ❌ Failure | `test_invalid_password` | Valid email + wrong password shows a credential error |
| ❌ Failure | `test_invalid_email` | Unrecognised email shows an error |
| ❌ Failure | `test_empty_email` | Submitting with no email shows a validation error |
| ❌ Failure | `test_empty_password` | Submitting with no password shows a validation error |
| ❌ Failure | `test_invalid_email_format` | Malformed email address shows a format error |
| ❌ Failure | `test_malicious_or_extreme_input_does_not_crash` | SQL injection, XSS, and 256-char inputs are handled gracefully (parametrized) |
| 🖥️ UI | `test_login_page_title` | Browser tab title identifies the login page |
| 🖥️ UI | `test_password_field_masked_by_default` | Password field is type=password by default |
| 🖥️ UI | `test_forgot_password_link_navigates` | Forgot Password link navigates to the reset page |
| 🖥️ UI | `test_email_field_present_on_load` | Email field is visible immediately on page load |
| 🖥️ UI | `test_password_field_not_visible_before_email_step` | Password field is hidden before email is submitted |

---

## Design Decisions

- **Page Object Model (POM):** All page interactions are encapsulated in `pages/login_page.py`, keeping tests selector-free and resilient to UI changes.
- **Lazy locator resolution:** Submit-button locators are resolved via properties at call time (not at `__init__`), so they always reflect the DOM state of whichever login step is currently active.
- **Two-step login handling:** Hudl's Auth0 login flow presents email and password on separate steps. The Page Object handles both transparently.
- **Specific error assertions:** Failure tests assert not just that *an* error appeared but that its text matches expected phrasing, making failures actionable.
- **Secure credential handling:** Credentials are loaded from a `.env` file at runtime using `python-dotenv` and are never hardcoded or committed.
- **CI/CD:** GitHub Actions runs flake8 then the full test suite on every push and pull request, uploading the HTML report as an artifact.
