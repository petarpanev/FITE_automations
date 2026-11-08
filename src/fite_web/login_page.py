from playwright.sync_api import Page
from fite_web.config import settings
from fite_web.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page):
        self.page = page
        self.url = f"{settings.BASE_URL}/account/login"
        self.username_input = page.locator("[id='id_email']")
        self.password_input = page.locator("[id='id_password']")
        self.login_button = page.get_by_role("button[name='Log In']")
        self.logo = page.locator("#general-wrapper > div > a > svg")

    def navigate(self):
        self.page.goto(self.url)

    def login_with_email_successfully(self):
        # Uses config directly
        self.username_input.fill(settings.TEST_USER)
        self.password_input.fill(settings.TEST_PASSWORD)
        self.login_button.click() 