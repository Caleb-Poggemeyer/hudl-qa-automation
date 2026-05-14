from playwright.sync_api import Page, expect


class LoginPage:
    URL = "https://www.hudl.com/login"

    def __init__(self, page: Page):
        self.page = page

        # Locators
        self.email_input = page.get_by_label("Email")
        self.password_input = page.get_by_label("Password")
        self.login_button = page.get_by_role("button", name="Log In")
        self.error_message = page.locator("[data-qa='error-display']")
        self.forgot_password_link = page.get_by_role("link", name="Forgot Password")
        self.password_toggle = page.locator("[data-qa='password-visibility-toggle']")

    def navigate(self):
        """Go to the login page."""
        self.page.goto(self.URL)

    def login(self, email: str, password: str):
        """Fill in credentials and submit the login form."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error_message(self) -> str:
        """Return the visible error message text."""
        return self.error_message.inner_text()

    def is_logged_in(self) -> bool:
        """Check if login was successful by verifying URL change."""
        return "/login" not in self.page.url

    def toggle_password_visibility(self):
        """Click the show/hide password toggle."""
        self.password_toggle.click()

    def click_forgot_password(self):
        """Click the forgot password link."""
        self.forgot_password_link.click()