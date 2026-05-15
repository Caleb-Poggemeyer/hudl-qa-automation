import pytest
import os
from dotenv import load_dotenv
from playwright.sync_api import Page
from pages.login_page import LoginPage

load_dotenv()


@pytest.fixture(scope="session")
def credentials():
    """Load credentials from .env file."""
    email = os.getenv("HUDL_EMAIL")
    password = os.getenv("HUDL_PASSWORD")
    assert email, "HUDL_EMAIL is not set in .env"
    assert password, "HUDL_PASSWORD is not set in .env"
    return {"email": email, "password": password}


@pytest.fixture()
def login_page(page: Page) -> LoginPage:
    """Navigate to the Hudl login page and return a LoginPage object."""
    lp = LoginPage(page)
    lp.navigate()
    return lp
