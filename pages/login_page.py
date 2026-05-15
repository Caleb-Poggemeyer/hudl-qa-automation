from playwright.sync_api import Page


class LoginPage:
    URL = "https://www.hudl.com/login"

    def __init__(self, page: Page):
        self.page = page

        # Step 1 - Email
        self.email_input = page.locator('input.u-input[type="email"]')
        self.continue_button = page.locator('button[type="submit"]')

        # Step 2 - Password
        self.password_input = page.locator('input.u-input[type="password"]')
        self.login_button = page.locator('button[type="submit"]')

        # Other elements
        self.forgot_password_link = page.get_by_text("Forgot Password", exact=False)
        self.error_message = page.locator('.u-alert, [class*="error"], [class*="alert"]')

    def navigate(self):
        """Navigate to the Hudl login page and wait for it to load."""
        self.page.goto(self.URL)
        self.email_input.wait_for(state="visible")

    def enter_email(self, email: str):
        """Fill in email and click Continue."""
        self.email_input.fill(email)
        self.continue_button.click()

    def enter_password(self, password: str):
        """Wait for password field, fill it in and submit."""
        self.password_input.wait_for(state="visible")
        self.password_input.fill(password)
        self.login_button.click()

    def login(self, email: str, password: str):
        """Full two-step login flow."""
        self.enter_email(email)
        self.enter_password(password)

    def get_error_message(self) -> str:
        """Return the visible error message text."""
        self.error_message.first.wait_for(state="visible", timeout=8000)
        return self.error_message.first.inner_text()

    def is_logged_in(self) -> bool:
        """Check if login succeeded by verifying URL no longer contains login."""
        self.page.wait_for_url(
            lambda url: "login" not in url and "identity" not in url,
            timeout=15000
        )
        return "login" not in self.page.url

    def click_forgot_password(self):
        """Click the Forgot Password link."""
        self.forgot_password_link.first.wait_for(state="visible")
        self.forgot_password_link.first.click()
        self.page.wait_for_load_state("networkidle")
