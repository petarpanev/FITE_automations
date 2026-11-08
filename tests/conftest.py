from __future__ import annotations

from typing import Any

import json
import os
from pathlib import Path
import pytest
from playwright.sync_api import Page
from playwright.sync_api import Browser
from fite_web.config import MonitorSettings
from fite_web.alerts import AlertService
from fite_web.config import settings
from fite_web.login_page import LoginPage
from fite_web.discover_page import DiscoverPage
from fite_web.base_page import BasePage
from fite_web.brand_validation import BrandTextValidationStrategy
from fite_web.brand_validation import ImageSimilarityValidationStrategy

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_COOKIES_PATH = PROJECT_ROOT / "FITE_automations/.auth/cookies.json"
PLAYWRIGHT_STATE_PATH = PROJECT_ROOT / "FITE_automations/.auth/state.json"

@pytest.fixture(scope="session")
def app_settings():
    from fite_web.config import Settings
    return Settings

@pytest.fixture(scope="session")
def base_url():
    return settings.BASE_URL

@pytest.fixture(scope="function")
def browser_context(browser):
    context = browser.new_context()

    yield context

    try:
        context.clear_cookies()
        context.clear_permissions()
    except Exception as e:
        print(f"Clear context error: {e}")
    finally:
        context.close()

@pytest.fixture(scope="function")        
def page(browser_context):
    page = browser_context.new_page()

    yield page

    page.close()

@pytest.fixture(scope="session")
def monitor_settings() -> MonitorSettings:
    return MonitorSettings.from_env()


@pytest.fixture
def alert_service(monitor_settings: MonitorSettings) -> AlertService:
    return AlertService(monitor_settings)


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: dict[str, Any],
    monitor_settings: MonitorSettings,
) -> dict[str, Any]:
    options = dict(browser_type_launch_args)
    if monitor_settings.headless is not None:
        options["headless"] = monitor_settings.headless
    options["args"] = list(options.get("args", [])) + ["--mute-audio"]
    return options


@pytest.fixture
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}} 


@pytest.fixture(scope="session")
def saved_auth_state(browser: Browser):
    context = browser.new_context()
    page = context.new_page()
    
    # 1. Initialize your Page Object with the clean page instance
    login_page = LoginPage(page)
    discover_page = DiscoverPage(page)
    
    # 2. Call your existing POM functions
    login_page.navigate()
    discover_page.cookie_consent_accept()
    login_page.login_with_email_successfully()

    # page.pause()

    # 3. Capture the state and close this temporary session context
    storage = context.storage_state()
    context.close()
    return storage

@pytest.fixture(scope="function")
def auth_page(browser: Browser, saved_auth_state):
    # Generates a fresh, authenticated page for individual tests
    context = browser.new_context(storage_state=saved_auth_state) # ".auth/ims-gw-dev-cf.trillertv.com_cookies.json")
    page = context.new_page()
    yield page
    context.close()

# Споделени стратегии за валидация
@pytest.fixture(scope="session")
def text_strategy():
    return BrandTextValidationStrategy()

@pytest.fixture(scope="session")
def image_strategy():
    return ImageSimilarityValidationStrategy(baseline_dir=f"resources/baselines/brand_FITE")

# Фикстури за страниците (автоматично получават Playwright 'page')
@pytest.fixture
def discover_page(page: Page):
    return DiscoverPage(page)

@pytest.fixture
def login_page(page: Page):
    return LoginPage(page)

@pytest.fixture(scope="session")
def external_session():
    """Loads manually exported cookies and formats them for Playwright."""
    
    if not os.path.exists(RAW_COOKIES_PATH):
        pytest.fail(f"Please export your cookies to {RAW_COOKIES_PATH} first!")
        
    with open(RAW_COOKIES_PATH, "r") as f:
        raw_cookies = json.load(f)
        
    # --- SANITIZATION STEP ---
    # Loop through each cookie and fix the sameSite formatting
    for cookie in raw_cookies:
        if "sameSite" in cookie and cookie["sameSite"]:
            # Convert string to lowercase to catch "lax", "strict", etc.
            val = str(cookie["sameSite"]).lower()

            if val == "lax":
                cookie["sameSite"] = "Lax"
            elif val == "strict":
                cookie["sameSite"] = "Strict"
            elif val == "none":
                cookie["sameSite"] = "None"
            else:
                # If it's something invalid (like "unspecified" or "no_restriction"),
                # Playwright behaves best if you default it to "Lax" or "None"
                cookie["sameSite"] = "Lax" 
        else:
            # If sameSite is missing or null, default it to "Lax"
            cookie["sameSite"] = "Lax"
    # --------------------------

    # Format it into the structure Playwright expects
    playwright_state = {
        "cookies": raw_cookies,
        "origins": [] 
    }
    
    os.makedirs(os.path.dirname(PLAYWRIGHT_STATE_PATH), exist_ok=True)
    with open(PLAYWRIGHT_STATE_PATH, "w") as f:
        json.dump(playwright_state, f)
        
    yield PLAYWRIGHT_STATE_PATH