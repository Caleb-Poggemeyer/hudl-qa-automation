"""
Test suite for the Hudl login flow.

Covers:
  - Successful login
  - Failure scenarios (bad credentials, empty fields, malformed input)
  - UI/navigation checks (page title, password masking, forgot password)

All page interactions go through LoginPage (POM) — tests contain no selectors.
Credentials are injected via the `credentials` fixture in conftest.py.
"""

import pytest
from pages.login_page import LoginPage


class TestLoginSuccess:
    """Happy-path login scenarios."""

    @pytest.mark.smoke
    def test_valid_login(self, login_page: LoginPage, credentials):
        """Valid credentials should redirect the user away from the login page."""
        login_page.login(credentials["email"], credentials["password"])
        assert login_page.is_logged_in(), (
            "Expected to be redirected after login but URL still contains /login"
        )

    @pytest.mark.smoke
    def test_valid_login_email_case_insensitive(self, login_page: LoginPage, credentials):
        """Email matching should be case-insensitive."""
        upper_email = credentials["email"].upper()
        login_page.login(upper_email, credentials["password"])
        assert login_page.is_logged_in(), (
            "Login should succeed regardless of email case"
        )


class TestLoginFailure:
    """Scenarios that should produce a visible error message."""

    def test_invalid_password(self, login_page: LoginPage, credentials):
        """A valid email with the wrong password should show a credential error."""
        login_page.login(credentials["email"], "WrongPassword123!")
        error = login_page.get_error_message()
        assert error, "Expected an error message but none appeared"
        assert "your email or password is incorrect" in error.lower(), (
            f"Expected credential error message, got: '{error}'"
        )

    def test_invalid_email(self, login_page: LoginPage):
        """An unrecognised email address should show a credential error."""
        login_page.login("notareal@fakeemail.com", "SomePassword123!")
        error = login_page.get_error_message()
        assert error, "Expected an error message but none appeared"
        assert "incorrect username or password" in error.lower(), (
            f"Expected credential error message, got: '{error}'"
        )

    def test_empty_email(self, login_page: LoginPage):
        """Submitting the email step with no value should show a validation error."""
        login_page.enter_email("")
        error = login_page.get_error_message()
        assert error, "Expected a validation error for an empty email"
        assert "please enter your email address" in error.lower(), (
            f"Expected empty email error, got: '{error}'"
        )

    def test_empty_password(self, login_page: LoginPage, credentials):
        """Advancing past email and submitting an empty password should show an error."""
        login_page.enter_email(credentials["email"])
        login_page.submit_empty_password()
        error = login_page.get_error_message()
        assert error, "Expected a validation error for an empty password"
        assert "please enter your password" in error.lower(), (
            f"Expected empty password error, got: '{error}'"
        )

    def test_invalid_email_format(self, login_page: LoginPage):
        """A string that is not a valid email address should show a format error."""
        login_page.enter_email("notanemail")
        error = login_page.get_error_message()
        assert error, "Expected a format-validation error for a malformed email"
        assert "enter a valid email" in error.lower(), (
            f"Expected email format error, got: '{error}'"
        )

    @pytest.mark.security
    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",
        "<script>alert(1)</script>",
        "a" * 256 + "@test.com",
    ])
    def test_malicious_or_extreme_input_does_not_crash(self, login_page: LoginPage, payload):
        """Injection attempts and extreme-length inputs should be handled gracefully."""
        login_page.enter_email(payload)
        assert "hudl.com" in login_page.page.url, (
            f"Page navigated away from Hudl unexpectedly with payload: {payload}"
        )
        error = login_page.get_error_message()
        assert error, "Expected a validation error for malicious or extreme input"


class TestLoginPageUI:
    """UI element checks and navigation tests."""

    def test_login_page_title(self, login_page: LoginPage):
        """The browser tab title should identify this as a login page."""
        title = login_page.page.title()
        assert "Log In" in title or "Login" in title, (
            f"Unexpected page title: '{title}'"
        )

    def test_password_field_masked_by_default(self, login_page: LoginPage, credentials):
        """The password input should have type='password' so the value is hidden."""
        login_page.advance_to_password_step(credentials["email"])
        field_type = login_page.password_input.get_attribute("type")
        assert field_type == "password", (
            f"Password field should be masked (type='password'), got type='{field_type}'"
        )

    def test_forgot_password_link_navigates(self, login_page: LoginPage, credentials):
        """Clicking Forgot Password should navigate to the password-reset page."""
        login_page.advance_to_password_step(credentials["email"])
        login_page.click_forgot_password()
        destination = login_page.page.url
        assert "identity.hudl.com" in destination and "reset-password" in destination, (
            f"Expected Hudl password reset URL, got: '{destination}'"
        )

    def test_email_field_present_on_load(self, login_page: LoginPage):
        """The email input field should be immediately visible when the page loads."""
        assert login_page.email_input.is_visible(), (
            "Email input was not visible on page load"
        )

    def test_password_field_not_visible_before_email_step(self, login_page: LoginPage):
        """The password field should be hidden until after the email step is completed."""
        assert not login_page.password_input.is_visible(), (
            "Password field should not be visible before the email step"
        )
