# Hudl Login Test Automation

[![CI](https://github.com/Caleb-Poggemeyer/hudl-qa-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/Caleb-Poggemeyer/hudl-qa-automation/actions/workflows/ci.yml)

A production-ready test automation framework validating the Hudl login flow, built with Python and Playwright.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Language |
| Playwright | Browser automation |
| pytest | Test runner |
| pytest-html | HTML test reports |
| flake8 | Linting |
| GitHub Actions | CI/CD |

---

## Prerequisites

Ensure the following are installed before getting started:

- [Python 3.11](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/) (required internally by Playwright)
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

**macOS / Linux:**
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

Copy the provided template and fill in your Hudl test credentials:

```bash
cp .env.example .env
```

Open `.env` and set both values:

```
HUDL_EMAIL=your_test_email@example.com
HUDL_PASSWORD=your_test_password
```

> ⚠️ **Never commit `.env`.** It is listed in `.gitignore`. The CI pipeline reads credentials from GitHub repository secrets — the `.env` file is for local runs only.

---

## Running the Tests

### Full suite

```bash
pytest
```

### By test class

```bash
pytest tests/test_login.py::TestLoginSuccess -v
pytest tests/test_login.py::TestLoginFailure -v
pytest tests/test_login.py::TestLoginNavigation -v
pytest tests/test_login.py::TestLoginRateLimiting -v
pytest tests/test_login.py::TestSSOEntryPoints -v
pytest tests/test_login.py::TestLoginPageUI -v
pytest tests/test_login.py::TestKeyboardAccessibility -v
```

### By marker

```bash
pytest -m smoke       # Happy-path tests only
pytest -m security    # Security and stability tests only
```

### Single test

```bash
pytest tests/test_login.py::TestLoginSuccess::test_valid_login -v
```

### Headed mode (watch the browser)

```bash
pytest --headed
```

### Slow motion (useful for debugging)

```bash
pytest --headed --slowmo 1000
```

---

## Reports

After any run, an HTML report is generated at:

```
reports/report.html
```

Open it in any browser. The report includes per-test pass/fail status, captured output, and timing. In CI it is uploaded as a workflow artifact and can be downloaded from the Actions run summary — even when the run fails.

---

## Linting

This project uses flake8 to enforce code style. To run the linter:

```bash
flake8 .
```

A clean run produces no output. The CI pipeline runs flake8 before tests; a lint failure blocks the test job.

---

## Debugging Failures

Three resources are available when a test fails:

1. **HTML report** (`reports/report.html`) — generated after every run; includes captured output and error details for each test.
2. **Headed mode** — re-run the failing test with `--headed` to watch the browser in real time.
3. **Slow motion** — combine `--headed --slowmo 1000` (milliseconds per action) to step through interactions at a readable pace.

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
│   └── test_login.py           # Full login test suite (21 tests)
├── .env                        # Local credentials (never committed)
├── .env.example                # Credential template (safe to commit)
├── .flake8                     # Linting configuration
├── .gitignore                  # Git ignore rules
├── conftest.py                 # Shared pytest fixtures
├── pytest.ini                  # Pytest configuration and marker definitions
├── requirements.txt            # Pinned project dependencies
└── README.md                   # This file
```

---

## Test Coverage

21 tests across 7 classes.

### TestLoginSuccess
| Test | Description |
|---|---|
| `test_valid_login` ⭐ | Valid credentials redirect the user to the Hudl app |
| `test_valid_login_email_case_insensitive` ⭐ | Email matching is case-insensitive |

*⭐ marked `smoke`*

### TestLoginFailure
| Test | Description |
|---|---|
| `test_invalid_password` | Valid email + wrong password shows a credential error |
| `test_invalid_email` | Unrecognised email shows a credential error |
| `test_empty_email` | Submitting with no email shows a validation error |
| `test_empty_password` | Submitting with no password shows a validation error |
| `test_invalid_email_format` | Malformed email address shows a format error |
| `test_malicious_or_extreme_input_does_not_crash` 🔒 ×3 | SQL injection, XSS, and 256-char inputs are handled gracefully (parametrized) |

*🔒 marked `security`*

### TestLoginNavigation
| Test | Description |
|---|---|
| `test_back_button_from_password_step_returns_to_email_step` | Browser back restores the email step cleanly |

### TestLoginRateLimiting
| Test | Description |
|---|---|
| `test_repeated_failed_logins_handled_gracefully` 🔒 | 5 consecutive failures all produce an error and stay on hudl.com |

*🔒 marked `security`*

### TestSSOEntryPoints
| Test | Description |
|---|---|
| `test_sso_button_redirects_to_provider[google]` | Continue with Google redirects to accounts.google.com |
| `test_sso_button_redirects_to_provider[apple]` | Continue with Apple redirects to appleid.apple.com |
| `test_sso_button_redirects_to_provider[facebook]` | Continue with Facebook redirects to facebook.com |

### TestLoginPageUI
| Test | Description |
|---|---|
| `test_login_page_title` | Browser tab title identifies the login page |
| `test_password_field_masked_by_default` | Password field has type='password' |
| `test_forgot_password_link_navigates` | Forgot Password navigates to the reset page |
| `test_email_field_present_on_load` | Email field is visible on page load |
| `test_password_field_not_visible_before_email_step` | Password field is hidden before step 1 is completed |

### TestKeyboardAccessibility
| Test | Description |
|---|---|
| `test_form_keyboard_navigation` | Tab reaches email field → Tab reaches submit button → Enter submits the form |

---

## Design Decisions

**Page Object Model (POM)**
All element locators and page interactions live in `pages/login_page.py`. Tests contain no raw selectors and never touch Playwright directly — every action and assertion goes through a named method on `LoginPage`. If Hudl changes the page, only the POM needs updating; every test that uses it automatically benefits.

**POM as the only interface**
Tests interact exclusively through `LoginPage` methods such as `login()`, `get_error_message()`, `is_logged_in()`, and `get_current_url()`. Locator properties (`email_input`, `password_input`, etc.) are internal building blocks used only inside the POM — tests never call them directly.

**Fresh element lookups**
Every locator is resolved fresh on each access rather than being stored once at startup. This is essential for the submit button, which points to a different element on each login step — storing it once would capture the wrong one.

**Two-step Auth0 flow**
Hudl's login page delegates to Auth0, which presents email and password on separate steps. The POM models both steps and exposes helpers (`advance_to_password_step`, `enter_password`, `submit_empty_password`) so tests can start from whichever step they need.

**Specific error assertions**
Failure tests assert the exact error text rather than just checking that *some* error appeared. This means a regression that shows the wrong error message will fail the test, not pass it silently.

**Credential safety in stability tests**
The rate-limiting test uses a throwaway address under the `.invalid` TLD. This domain can never resolve, so there is no risk of accidentally authenticating or locking out the shared test account.

**Secure credential handling**
Credentials are loaded from a `.env` file at runtime using `python-dotenv`. They are never hardcoded, never committed, and injected into CI via GitHub repository secrets.

**CI/CD**
GitHub Actions runs flake8 then the full test suite on every push and pull request. The HTML report is uploaded as an artifact so failures are always inspectable — even when the run itself fails.
