"""
Page Object Model for the Hudl Login Page.

Captures all element locators and user actions in one place.
If the page changes, update it here and all tests stay working.

Hudl uses a two-step login (email first, then password) via Auth0.
Locators for the submit buttons are resolved lazily inside each method
so they are always scoped to the correct step's DOM state.
"""

from playwright.sync_api import Page


class LoginPage:
    URL = "https://www.hudl.com/login"

    # Selector constants — single source of truth for all locators
    _EMAIL_INPUT = 'input.u-input[type="email"]'
    _PASSWORD_INPUT = 'input.u-input[type="password"]'
    _SUBMIT_BUTTON = 'button[type="submit"]'
    _FORGOT_PASSWORD = "Forgot Password"
    _ERROR_SELECTORS = '.u-alert, [class*="error"], [class*="alert"]'

    def __init__(self, page: Page):
        self.page = page

    # ------------------------------------------------------------------
    # Properties — resolved fresh each call so they always match current DOM
    # ------------------------------------------------------------------

    @property
    def email_input(self):
        return self.page.locator(self._EMAIL_INPUT)

    @property
    def password_input(self):
        return self.page.locator(self._PASSWORD_INPUT)

    @property
    def _submit_button(self):
        """The visible submit button for whatever step is currently active."""
        return self.page.locator(self._SUBMIT_BUTTON)

    @property
    def forgot_password_link(self):
        return self.page.get_by_text(self._FORGOT_PASSWORD, exact=False)

    @property
    def error_message(self):
        return self.page.locator(self._ERROR_SELECTORS)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def navigate(self):
        """Navigate to the Hudl login page and wait for the email field."""
        self.page.goto(self.URL)
        self.email_input.wait_for(state="visible")

    def enter_email(self, email: str):
        """Fill in the email field and click Continue."""
        self.email_input.fill(email)
        self._submit_button.click()

    def enter_password(self, password: str):
        """Wait for the password field to appear, fill it in, and submit."""
        self.password_input.wait_for(state="visible")
        self.password_input.fill(password)
        self._submit_button.click()

    def login(self, email: str, password: str):
        """Execute the full two-step login flow."""
        self.enter_email(email)
        self.enter_password(password)

    def get_error_message(self) -> str:
        """Wait for an error to appear and return its text."""
        self.error_message.first.wait_for(state="visible", timeout=8000)
        return self.error_message.first.inner_text()

    def is_logged_in(self) -> bool:
        """Return True if the URL has left the login/identity pages."""
        self.page.wait_for_url(
            lambda url: "login" not in url and "identity" not in url,
            timeout=15000,
        )
        return "login" not in self.page.url

    def click_forgot_password(self):
        """Click the Forgot Password link and wait for navigation to settle."""
        self.forgot_password_link.first.wait_for(state="visible")
        self.forgot_password_link.first.click()
        self.page.wait_for_load_state("networkidle")
