"""
Page Object Model for the Hudl login page.

All page elements and actions live here. Tests never reference a raw selector —
if Hudl changes the page, only this file needs updating.

The login form has two steps:
  Step 1 — Enter your email and click Continue.
  Step 2 — Enter your password and click Log In.
"""

from playwright.sync_api import Page


class LoginPage:
    """Controls the Hudl login page at https://www.hudl.com/login."""

    URL = "https://www.hudl.com/login"

    # Selectors — update these if Hudl changes the page HTML.
    _EMAIL_INPUT = 'input.u-input[type="email"]'
    _PASSWORD_INPUT = 'input.u-input[type="password"]'
    _SUBMIT_BUTTON = 'button[type="submit"]'
    _FORGOT_PASSWORD = "Forgot Password"
    _ERROR_SELECTORS = '.u-alert, [class*="error"], [class*="alert"]'
    _SSO_GOOGLE = "Continue with Google"
    _SSO_APPLE = "Continue with Apple"
    _SSO_FACEBOOK = "Continue with Facebook"

    def __init__(self, page: Page):
        self.page = page

    # ------------------------------------------------------------------
    # Elements
    #
    # Each element is looked up fresh on every access. This matters for
    # the submit button, which is a different element on step 1 vs step 2.
    # ------------------------------------------------------------------

    @property
    def email_input(self):
        return self.page.locator(self._EMAIL_INPUT)

    @property
    def password_input(self):
        return self.page.locator(self._PASSWORD_INPUT)

    @property
    def _submit_button(self):
        return self.page.locator(self._SUBMIT_BUTTON)

    @property
    def forgot_password_link(self):
        return self.page.get_by_text(self._FORGOT_PASSWORD, exact=False)

    @property
    def error_message(self):
        return self.page.locator(self._ERROR_SELECTORS)

    @property
    def sso_google_button(self):
        return self.page.get_by_role("button", name=self._SSO_GOOGLE)

    @property
    def sso_apple_button(self):
        return self.page.get_by_role("button", name=self._SSO_APPLE)

    @property
    def sso_facebook_button(self):
        return self.page.get_by_role("button", name=self._SSO_FACEBOOK)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate(self):
        """Open the login page and wait for the email field to appear."""
        self.page.goto(self.URL)
        self.email_input.wait_for(state="visible")

    def go_back(self):
        """Press the browser back button and wait for the page to settle."""
        self.page.go_back()
        self.page.wait_for_load_state("domcontentloaded")

    def click_forgot_password(self):
        """Click 'Forgot Password' and wait for the reset page to load."""
        self.forgot_password_link.first.wait_for(state="visible")
        self.forgot_password_link.first.click()
        self.page.wait_for_load_state("networkidle")

    # ------------------------------------------------------------------
    # Form actions
    # ------------------------------------------------------------------

    def enter_email(self, email: str):
        """Type an email address and click Continue (step 1)."""
        self.email_input.fill(email)
        self._submit_button.click()

    def advance_to_password_step(self, email: str):
        """Submit a valid email and wait for the password field to appear."""
        self.enter_email(email)
        self.password_input.wait_for(state="visible")

    def enter_password(self, password: str):
        """Wait for the password field, fill it in, and click Log In (step 2)."""
        self.password_input.wait_for(state="visible")
        self.password_input.fill(password)
        self._submit_button.click()

    def login(self, email: str, password: str):
        """Complete the full login flow — email step followed by password step."""
        self.enter_email(email)
        self.enter_password(password)

    def submit_empty_password(self):
        """Click Log In on step 2 without entering a password."""
        self.password_input.wait_for(state="visible")
        self._submit_button.click()

    def attempt_login_without_navigation(self, email: str, password: str):
        """
        Try to log in but don't fail if the password step never appears.

        Used for repeated-attempt tests where the form might show an error
        at step 1 before ever reaching step 2.
        """
        self.email_input.wait_for(state="visible")
        self.email_input.fill(email)
        self._submit_button.click()
        try:
            self.password_input.wait_for(state="visible", timeout=6000)
            self.password_input.fill(password)
            self._submit_button.click()
        except Exception:
            # Step 2 didn't appear — an error showed at step 1 instead.
            # This is expected during rate-limit testing; carry on.
            pass

    # ------------------------------------------------------------------
    # Helpers for test assertions
    # ------------------------------------------------------------------

    def get_error_message(self) -> str:
        """Wait for an error to appear on screen and return its text."""
        self.error_message.first.wait_for(state="visible", timeout=8000)
        return self.error_message.first.inner_text()

    def get_page_title(self) -> str:
        """Return the current browser tab title."""
        return self.page.title()

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def is_email_field_visible(self) -> bool:
        """Return True if the email field is visible on screen."""
        return self.email_input.is_visible()

    def is_password_field_visible(self) -> bool:
        """Return True if the password field is visible on screen."""
        return self.password_input.is_visible()

    def get_password_field_type(self) -> str:
        """Return the input type of the password field (should always be 'password', not 'text')."""
        return self.password_input.get_attribute("type")

    def is_logged_in(self) -> bool:
        """
        Return True once the browser has fully landed on a post-login page.

        Waits for the URL to leave the login/identity pages, then confirms
        the top navigation bar is visible.

        Note: 'gloabl-navbar' is a typo in Hudl's own HTML — keep it as-is
        or the check will never find the element.
        """
        self.page.wait_for_url(
            lambda url: "login" not in url and "identity" not in url,
            timeout=15000,
        )
        self.page.locator('[data-qa-id="gloabl-navbar"]').wait_for(
            state="visible", timeout=5000
        )
        return "login" not in self.page.url

    # ------------------------------------------------------------------
    # SSO (social sign-in buttons)
    # ------------------------------------------------------------------

    def click_sso_button(self, provider: str) -> str:
        """
        Click a social sign-in button and return the URL the browser lands on.

        Args:
            provider: 'google', 'apple', or 'facebook'.

        Returns:
            The URL after the redirect has started.

        Raises:
            ValueError: If the provider name isn't recognised.
        """
        button_map = {
            "google":   self.sso_google_button,
            "apple":    self.sso_apple_button,
            "facebook": self.sso_facebook_button,
        }
        button = button_map.get(provider)
        if button is None:
            raise ValueError(
                f"Unknown SSO provider: '{provider}'. "
                f"Expected one of: {list(button_map.keys())}"
            )

        button.wait_for(state="visible")
        button.click()
        self.page.wait_for_url(
            lambda url: "hudl.com/login" not in url,
            timeout=10000,
        )
        return self.page.url

    # ------------------------------------------------------------------
    # Keyboard helpers
    # ------------------------------------------------------------------

    def focus_email_field(self):
        """Click the email field so keyboard input goes there."""
        self.email_input.click()

    def fill_email_field(self, email: str):
        """Type into the email field without clicking Continue."""
        self.email_input.fill(email)

    def wait_for_password_field(self, timeout: int = 6000) -> bool:
        """Wait for the password field to appear. Returns True if it did, False if it timed out."""
        try:
            self.password_input.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def press_key(self, key: str):
        """Press a keyboard key (e.g. 'Tab', 'Enter') on whatever element is currently focused."""
        self.page.keyboard.press(key)

    def get_focused_element_tag_and_type(self) -> dict:
        """
        Return info about the element that currently has keyboard focus.

        Returns a dict with:
          tag  — the element type, e.g. 'input' or 'button'
          type — the input type, e.g. 'email', 'password', 'submit'
          name — the element's name attribute
        """
        return self.page.evaluate("""() => {
            const el = document.activeElement;
            return {
                tag:  el ? el.tagName.toLowerCase() : null,
                type: el ? (el.getAttribute('type') || '').toLowerCase() : null,
                name: el ? (el.getAttribute('name') || '') : null,
            };
        }""")
