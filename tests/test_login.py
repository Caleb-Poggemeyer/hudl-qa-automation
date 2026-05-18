"""
Test suite for the Hudl login page.

Test classes
------------
  TestLoginSuccess          Valid credentials and case-insensitive email.
  TestLoginFailure          Wrong credentials, empty fields, bad format, and
                            security payloads (SQL injection, XSS, oversized input).
  TestLoginNavigation       Browser back-button behaviour during the two-step flow.
  TestLoginRateLimiting     Page stability under repeated failed attempts.
  TestSSOEntryPoints        Google, Apple, and Facebook sign-in redirects.
  TestLoginPageUI           Page title, password masking, Forgot Password link,
                            and field visibility at each step.
  TestKeyboardAccessibility Tab order and Enter-key form submission.

Design notes
------------
- No test touches a raw selector. All interactions go through LoginPage
  (pages/login_page.py) — if Hudl changes the page, only that file needs updating.
- Real credentials come from the `credentials` fixture (conftest.py), which
  reads a local .env file that is never committed to version control.
- Tests that don't need real credentials use a fake address under the .invalid
  TLD, which can never reach a real mail server.
"""

import pytest
from pages.login_page import LoginPage


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestLoginSuccess:
    """Confirm that a successful login redirects the user into the Hudl app."""

    @pytest.mark.smoke
    def test_valid_login(self, login_page: LoginPage, credentials):
        """Correct email and password should land the user on the Hudl dashboard."""
        login_page.login(credentials["email"], credentials["password"])
        assert login_page.is_logged_in(), (
            "Expected to be redirected after login but URL still contains /login"
        )

    @pytest.mark.smoke
    def test_valid_login_email_case_insensitive(self, login_page: LoginPage, credentials):
        """Login should work even if the email is typed in all caps."""
        upper_email = credentials["email"].upper()
        login_page.login(upper_email, credentials["password"])
        assert login_page.is_logged_in(), (
            "Login should succeed regardless of email case"
        )


# ---------------------------------------------------------------------------
# Failure / error-message tests
# ---------------------------------------------------------------------------

class TestLoginFailure:
    """
    Confirm the login form shows a clear, specific error for every invalid input.

    Each test checks both that an error appeared and that the wording matches
    what Hudl actually shows — so a wrong error message won't sneak through.
    """

    def test_invalid_password(self, login_page: LoginPage, credentials):
        """
        A real email paired with the wrong password should show a credential error.

        Hudl uses different wording for 'wrong password on a known account' vs
        'email not found', so these two cases are tested separately.
        """
        login_page.login(credentials["email"], "WrongPassword123!")
        error = login_page.get_error_message()
        assert error, "Expected an error message but none appeared"
        assert "your email or password is incorrect" in error.lower(), (
            f"Expected credential error message, got: '{error}'"
        )

    def test_invalid_email(self, login_page: LoginPage):
        """An email address that doesn't exist in Hudl should show a credential error."""
        login_page.login("notareal@fakeemail.com", "SomePassword123!")
        error = login_page.get_error_message()
        assert error, "Expected an error message but none appeared"
        assert "incorrect username or password" in error.lower(), (
            f"Expected credential error message, got: '{error}'"
        )

    def test_empty_email(self, login_page: LoginPage):
        """Clicking Continue with no email entered should show a validation error."""
        login_page.enter_email("")
        error = login_page.get_error_message()
        assert error, "Expected a validation error for an empty email"
        assert "please enter your email address" in error.lower(), (
            f"Expected empty email error, got: '{error}'"
        )

    def test_empty_password(self, login_page: LoginPage, credentials):
        """Clicking Log In with no password entered should show a validation error."""
        login_page.enter_email(credentials["email"])
        login_page.submit_empty_password()
        error = login_page.get_error_message()
        assert error, "Expected a validation error for an empty password"
        assert "please enter your password" in error.lower(), (
            f"Expected empty password error, got: '{error}'"
        )

    def test_invalid_email_format(self, login_page: LoginPage):
        """Entering something that isn't an email address should show a format error."""
        login_page.enter_email("notanemail")
        error = login_page.get_error_message()
        assert error, "Expected a format-validation error for a malformed email"
        assert "enter a valid email" in error.lower(), (
            f"Expected email format error, got: '{error}'"
        )

    @pytest.mark.security
    @pytest.mark.parametrize("payload", [
        "' OR '1'='1",               # SQL injection attempt
        "<script>alert(1)</script>",  # Reflected XSS attempt
        "a" * 256 + "@test.com",      # Oversized input (256-char local part)
    ])
    def test_malicious_or_extreme_input_does_not_crash(
        self, login_page: LoginPage, payload
    ):
        """
        Harmful or extreme inputs should be handled gracefully.

        The page must stay on hudl.com and show a validation error — not a
        crash, blank screen, or unexpected redirect.
        """
        login_page.enter_email(payload)
        assert "hudl.com" in login_page.get_current_url(), (
            f"Page navigated away from Hudl unexpectedly with payload: {payload}"
        )
        error = login_page.get_error_message()
        assert error, "Expected a validation error for malicious or extreme input"


# ---------------------------------------------------------------------------
# Browser navigation tests
# ---------------------------------------------------------------------------

class TestLoginNavigation:
    """
    Confirm the back button works correctly during the two-step login flow.

    Going back from the password step should return the user cleanly to the
    email step, not leave them on a blank or broken page.
    """

    def test_back_button_from_password_step_returns_to_email_step(
        self, login_page: LoginPage, credentials
    ):
        """Pressing back from the password step should bring the email field back."""
        login_page.advance_to_password_step(credentials["email"])

        # Confirm step 2 is showing before we go back.
        assert login_page.is_password_field_visible(), (
            "Setup failed: password field should be visible before going back"
        )

        login_page.go_back()

        assert login_page.is_email_field_visible(), (
            "After browser back, email field should be visible again"
        )
        assert not login_page.is_password_field_visible(), (
            "After browser back, password field should not be visible"
        )


# ---------------------------------------------------------------------------
# Rate-limiting / stability tests
# ---------------------------------------------------------------------------

class TestLoginRateLimiting:
    """
    Confirm the login form stays stable under repeated failed attempts.

    IMPORTANT — these tests use a fake .invalid address so there is no risk
    of locking out the real test account. Do NOT change _PROBE_EMAIL to
    credentials["email"].

    We check for stability (error shown, still on hudl.com) rather than a
    specific lockout message, since Hudl may not show one after only a few
    attempts.
    """

    _ATTEMPT_COUNT  = 5
    _PROBE_EMAIL    = "lockout-probe@example-hudl-test.invalid"
    _PROBE_PASSWORD = "WrongPassword999!"

    @pytest.mark.security
    def test_repeated_failed_logins_handled_gracefully(self, login_page: LoginPage):
        """Five bad login attempts in a row should always show an error and stay on hudl.com."""
        for attempt in range(self._ATTEMPT_COUNT):
            # Re-open the login page before each attempt (except the first) because
            # the form may be in an error state that hides the email field.
            if attempt > 0:
                login_page.navigate()

            login_page.attempt_login_without_navigation(
                self._PROBE_EMAIL, self._PROBE_PASSWORD
            )

            error = login_page.get_error_message()
            assert error, (
                f"Attempt {attempt + 1}: expected an error message but none appeared"
            )
            assert "hudl.com" in login_page.get_current_url(), (
                f"Attempt {attempt + 1}: page left hudl.com — URL: {login_page.get_current_url()}"
            )


# ---------------------------------------------------------------------------
# SSO entry-point tests
# ---------------------------------------------------------------------------

class TestSSOEntryPoints:
    """
    Confirm each social sign-in button redirects to the right provider.

    We don't complete the full sign-in — that would need test accounts with
    Google, Apple, and Facebook. We just confirm the button sends the browser
    to the correct domain.
    """

    @pytest.mark.parametrize("provider,expected_domain", [
        ("google",   "accounts.google.com"),
        ("apple",    "appleid.apple.com"),
        ("facebook", "facebook.com"),
    ])
    def test_sso_button_redirects_to_provider(
        self, login_page: LoginPage, provider: str, expected_domain: str
    ):
        """Clicking a sign-in button should redirect to that provider's login page."""
        destination_url = login_page.click_sso_button(provider)
        assert expected_domain in destination_url, (
            f"Clicking '{provider}' SSO button should redirect to {expected_domain}, "
            f"but landed on: '{destination_url}'"
        )


# ---------------------------------------------------------------------------
# UI / element visibility tests
# ---------------------------------------------------------------------------

class TestLoginPageUI:
    """Confirm key page elements look and behave correctly."""

    def test_login_page_title(self, login_page: LoginPage):
        """The browser tab title should say 'Log In' or 'Login'."""
        title = login_page.get_page_title()
        assert "Log In" in title or "Login" in title, (
            f"Unexpected page title: '{title}'"
        )

    def test_password_field_masked_by_default(self, login_page: LoginPage, credentials):
        """The password field should hide what you type (type='password', not type='text')."""
        login_page.advance_to_password_step(credentials["email"])
        field_type = login_page.get_password_field_type()
        assert field_type == "password", (
            f"Password field should be masked (type='password'), got type='{field_type}'"
        )

    def test_forgot_password_link_navigates(self, login_page: LoginPage, credentials):
        """Clicking 'Forgot Password' should open Hudl's password reset page."""
        login_page.advance_to_password_step(credentials["email"])
        login_page.click_forgot_password()
        destination = login_page.get_current_url()
        assert "identity.hudl.com" in destination and "reset-password" in destination, (
            f"Expected Hudl password reset URL, got: '{destination}'"
        )

    def test_email_field_present_on_load(self, login_page: LoginPage):
        """The email field should be visible as soon as the page loads."""
        assert login_page.is_email_field_visible(), (
            "Email input was not visible on page load"
        )

    def test_password_field_not_visible_before_email_step(self, login_page: LoginPage):
        """The password field should be hidden until the user has entered their email."""
        assert not login_page.is_password_field_visible(), (
            "Password field should not be visible before the email step"
        )


# ---------------------------------------------------------------------------
# Keyboard / accessibility tests
# ---------------------------------------------------------------------------

class TestKeyboardAccessibility:
    """
    Confirm the login form works with a keyboard only (no mouse).

    This covers the basic accessibility requirement that all form actions are
    reachable by tabbing and pressing Enter.
    """

    def test_form_keyboard_navigation(self, login_page: LoginPage):
        """
        The email step should be completable using only Tab and Enter.

        Checks three things in order:
          1. Pressing Tab from the top of the page eventually focuses the email field.
          2. Pressing Tab from the email field eventually reaches the submit button.
          3. Pressing Enter while the email field is focused submits the form.

        A fake .invalid address is used so the real test account is never touched.
        The test passes whether the form accepts or rejects the email — either way
        it confirms Enter triggered a submission.
        """

        # 1. Tab to the email field — up to 10 presses to skip any links above it.
        focused = None
        for _ in range(10):
            login_page.press_key("Tab")
            focused = login_page.get_focused_element_tag_and_type()
            if focused["tag"] == "input" and focused["type"] == "email":
                break

        assert focused["tag"] == "input" and focused["type"] == "email", (
            f"Email input not reachable by Tab within 10 presses. "
            f"Last focused element: {focused}"
        )

        # 2. Tab to the submit button — up to 5 presses.
        for _ in range(5):
            login_page.press_key("Tab")
            focused = login_page.get_focused_element_tag_and_type()
            if focused["tag"] in ("button", "input"):
                break

        assert focused["tag"] in ("button", "input"), (
            f"Submit button not reachable by Tab from the email field. "
            f"Last focused element: {focused}"
        )

        # 3. Type an email and press Enter to submit.
        login_page.focus_email_field()
        login_page.fill_email_field("keyboard-test@example-hudl.invalid")
        login_page.press_key("Enter")

        submitted = login_page.wait_for_password_field(timeout=6000)
        if not submitted:
            # The email wasn't recognised, a validation error appeared instead.
            # Either outcome means Enter worked.
            error = login_page.get_error_message()
            submitted = bool(error)

        assert submitted, "Pressing Enter on the email field did not submit the form"
