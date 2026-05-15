from pages.login_page import LoginPage


class TestLoginSuccess:
    """Tests for successful login scenarios."""

    def test_valid_login(self, login_page: LoginPage, credentials):
        """A valid email and password should log the user in."""
        login_page.login(credentials["email"], credentials["password"])
        assert login_page.is_logged_in(), "Expected to be logged in but URL still contains /login"


class TestLoginFailure:
    """Tests for failed login scenarios."""

    def test_invalid_password(self, login_page: LoginPage, credentials):
        """A valid email with wrong password should show an error."""
        login_page.login(credentials["email"], "WrongPassword123!")
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_invalid_email(self, login_page: LoginPage):
        """An unrecognised email should show an error."""
        login_page.login("notareal@fakeemail.com", "SomePassword123!")
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_empty_email(self, login_page: LoginPage):
        """Submitting with no email should show an error."""
        login_page.enter_email("")
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_empty_password(self, login_page: LoginPage, credentials):
        """Submitting with an empty password should show an error."""
        login_page.enter_email(credentials["email"])
        login_page.password_input.wait_for(state="visible")
        login_page.login_button.click()
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_both_fields_empty(self, login_page: LoginPage):
        """Submitting with both fields empty should show an error."""
        login_page.enter_email("")
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_invalid_email_format(self, login_page: LoginPage):
        """A malformed email address should show an error."""
        login_page.enter_email("notanemail")
        assert login_page.get_error_message(), "Expected an error message but none appeared"


class TestLoginPageUI:
    """Tests for UI elements and navigation on the login page."""

    def test_forgot_password_link_navigates(self, login_page: LoginPage, credentials):
        """Clicking Forgot Password should navigate to the password reset page."""
        login_page.enter_email(credentials["email"])
        login_page.password_input.wait_for(state="visible")
        login_page.click_forgot_password()
        assert "reset" in login_page.page.url or "forgot" in login_page.page.url or \
            "password-reset" in login_page.page.url, \
            f"Expected password reset URL, got: {login_page.page.url}"

    def test_password_field_masked_by_default(self, login_page: LoginPage, credentials):
        """Password field should be type=password (masked) by default."""
        login_page.enter_email(credentials["email"])
        login_page.password_input.wait_for(state="visible")
        field_type = login_page.password_input.get_attribute("type")
        assert field_type == "password", "Password field should be masked by default"

    def test_login_page_title(self, login_page: LoginPage):
        """The login page should have the correct page title."""
        assert "Log In" in login_page.page.title(), \
            f"Unexpected page title: {login_page.page.title()}"
