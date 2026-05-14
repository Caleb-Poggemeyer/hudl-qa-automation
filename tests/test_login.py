import pytest
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

    def test_empty_email(self, login_page: LoginPage, credentials):
        """Submitting with no email should show an error."""
        login_page.login("", credentials["password"])
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_empty_password(self, login_page: LoginPage, credentials):
        """Submitting with no password should show an error."""
        login_page.login(credentials["email"], "")
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_both_fields_empty(self, login_page: LoginPage):
        """Submitting with both fields empty should show an error."""
        login_page.login("", "")
        assert login_page.get_error_message(), "Expected an error message but none appeared"

    def test_invalid_email_format(self, login_page: LoginPage):
        """A malformed email address should show an error."""
        login_page.login("notanemail", "SomePassword123!")
        assert login_page.get_error_message(), "Expected an error message but none appeared"


class TestLoginPageUI:
    """Tests for UI elements and navigation on the login page."""

    def test_forgot_password_link_navigates(self, login_page: LoginPage):
        """Clicking Forgot Password should navigate away from the login page."""
        login_page.click_forgot_password()
        assert "reset" in login_page.page.url or "forgot" in login_page.page.url, \
            "Expected to land on a password reset page"

    def test_password_field_masked_by_default(self, login_page: LoginPage, credentials):
        """Password field should be type=password (masked) by default."""
        login_page.password_input.fill(credentials["password"])
        field_type = login_page.password_input.get_attribute("type")
        assert field_type == "password", "Password field should be masked by default"

    def test_login_page_title(self, login_page: LoginPage):
        """The login page should have the correct page title."""
        assert "Hudl" in login_page.page.title(), "Expected 'Hudl' in the page title"