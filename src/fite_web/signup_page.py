import pytest
from playwright.sync_api import Page
from fite_web.config import settings
from fite_web.base_page import BasePage

class SignUpPage(BasePage):
    def __init__(self, page: Page):
        self.page = page
        self.url = f"{settings.BASE_URL}/account/register/"
        self.name_input = page.locator("[id='id_name']")
        self.email_input = page.locator("[id='id_email']")
        self.password_input = page.locator("[id='id_password']")
        self.confirm_password_input = page.locator("[id='id_confirm_password']")
        self.signup_button = page.get_by_role("button[name='Sign Up']")

        self.select_genre_2 = page.locator("[id='id_genre_1']")
        self.submit_button = page.locator("[id='submit']") # Save preferences

    def navigate(self):
        self.page.goto(self.url)

    def signup_with_email_successfully(self):
        # Uses config directly
        self.name_input.fill(settings.NEW_TEST_NAME)
        self.email_input.fill(settings.NEW_TEST_EMAIL)
        self.password_input.fill(settings.NEW_TEST_PASSWORD)
        self.confirm_password_input.fill(settings.NEW_TEST_PASSWORD)
        self.signup_button.click()

    def select_favorites(self):
        # "Tailor TrillerTV to your interests" is expected to be visible
        self.select_genre_2.click()
        self.submit_button.click()

    def add_invalid_password(self, password):
        self.name_input.fill(settings.NEW_TEST_NAME)
        self.email_input.fill(settings.NEW_TEST_EMAIL)
        self.password_input.fill(password)
        self.confirm_password_input.fill(password)
        self.signup_button.click()        