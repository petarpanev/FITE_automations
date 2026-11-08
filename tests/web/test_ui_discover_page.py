import re
from datetime import datetime
from pathlib import Path
#from unittest.mock import MagicMock
import pytest_check as check

from fite_web.discover_page import DiscoverPage
from fite_web.base_page import BasePage
from fite_web.brand_validation import (
    BrandVisualAsset,
    ImageSimilarityValidationStrategy,
)
from playwright.sync_api import Browser, Locator, expect
from fite_web.config import PROJECT_ROOT, settings


def test_ui_discover_page_header_visibility(page):
    discover_page = DiscoverPage(page)
    base_page = BasePage(page)
    discover_page.navigate()
    expect(page).to_have_url(re.compile(r".*ims-gw-dev-cf.trillertv.com"), timeout=15000)
    base_page.cookie_consent_accept()

    # HEADER: Strings and images visibility verification:
    visible_header_locators: tuple[Locator, ...] = (
        # base_page.header,
        # base_page.header_logo_link,
        base_page.header_logo,
        base_page.header_navigation,
        base_page.header_discover_link,
        base_page.header_schedule_link,
        base_page.header_fite_subs_link,
        # base_page.header_willow_subs_link,
        base_page.header_news_link,
        base_page.header_tv_link,
        base_page.header_account_button,
        base_page.header_search_button,
        base_page.header_categories_link,
        base_page.header_deals_link,
    )
    for locator in visible_header_locators:
        expect(locator, f"UI Component Missing: '{locator}' was not visible on the header").to_be_visible()

#    for title, section in discover_page.discover_carousel_sections.items():
#        expect(
#            section,
#            f"Discover section '{title}' was not visible at {discover_page.url}",
#        ).to_be_visible()

    attached_header_locators: tuple[Locator, ...] = (
        base_page.header_tv_option_1,
        base_page.header_tv_option_2,
        base_page.header_category_option_1,
        base_page.header_category_option_2,
        base_page.header_category_option_3,
        base_page.header_category_option_4,
        base_page.header_search_input,
        base_page.header_search_cancel_button,
        base_page.header_search_results,
        #base_page.header_search_result_items,
        #base_page.header_search_result_links,
    )
    for locator in attached_header_locators:
        expect(locator, f"UI Component Missing: '{locator}' was not attached on the header").to_be_attached()


def test_ui_discover_page_anonymous_required_carousels_verification(page):
    discover_page = DiscoverPage(page)
    discover_page.navigate()
    required_carousels = settings.DISCOVER_CAROUSELS.strip()
    
    # 2. Fallback: If DISCOVER_CAROUSELS variable in .env is missing or with no value, all locators catalog will be taken from POM (discover_page.py)
    if not required_carousels:
        print("\nℹ️ The .env configuration is empty. Automatic fallback: ALL elements in the POM are checked.")
        required_keys = list(discover_page.all_locators.keys())
    else:
        # DISCOVER_CAROUSELS value is parsed
        required_keys = [key.strip() for key in required_carousels.split(",") if key.strip()]

    # Transform rewuired carousels/keys in set for quick comparison
    expected_set = set(required_keys)
    
    missing_elements = []
    # print(f"\n--- Start an inspection for components: {required_keys} ---\n")
    
    # 3. Inspection and verification of components
    for name in required_keys:
        if name not in discover_page.all_locators:
            check.is_true(
                False, 
                msg=f"⚠️ Configuration error: The element '{name}' is listed in .env, but it's missing from the POM catolog!"
            )
            continue
            
        locator = discover_page.all_locators[name]
        
        # Wait for the element to appear for up to 2000 ms (2 seconds)
        try:
            locator.wait_for(state="visible", timeout=2000)
            is_visible = True
        except Exception:
            # If a TimeoutError is thrown, it means the element did not appear
            is_visible = False
        
        check.is_true(is_visible, msg=f"❌ The required element '{name}' is NOT visible!")
        
        if not is_visible:
            missing_elements.append(f"{name} ({locator})")


        # print(f"\n--- Search for items that ARE VISIBLE but ARE NOT in the .env list ---")

    # 2. Iterate through ALL defined locators in the POM
    for name, locator in discover_page.all_locators.items():
        
        # Check whether the element is currently visible on the screen
        try:
            # Use a short timeout so as not to slow down the test if the element is simply missing
            locator.wait_for(state="visible", timeout=1500)
            is_visible = True
        except Exception:
            is_visible = False
            
        # 3. If the element is visible but is not in the required DISCOVER CAROUSELS variable list in .env file
        if is_visible and (name not in expected_set):
            
            # We log a warning or fail the test (depending on your requirements)
            # Here, we use a soft assertion to display a message
            check.is_true(
                False, 
                msg=f"⚠️ An item found that is not on the list: '{name}' is visible, but it is not present in REQUIRED_HOME_ELEMENTS!"
            )
            print(f" 👀 Unidentified element discovered: {name}")

    # Console report
    if missing_elements:
        print(f"\n⚠️ Мissing required carousels: ({len(missing_elements)}):")
        for item in missing_elements:
            print(f" - {item}")
    # else:
        # print("\n✅ All verified items are visible on the page!")      

"""
def test_ui_discover_page_subscriber_required_carousels_verification(browser: Browser, external_session: Path):
    context = browser.new_context(storage_state=external_session)
    page = context.new_page()
    discover_page = DiscoverPage(page)

    discover_page.navigate()
    required_carousels = settings.DISCOVER_CAROUSELS_SUBSCRIBER.strip()
    
    # 2. Fallback: If DISCOVER_CAROUSELS variable in .env is missing or with no value, all locators catalog will be taken from POM (discover_page.py)
    if not required_carousels:
        print("\nℹ️ The .env configuration is empty. Automatic fallback: ALL elements in the POM are checked.")
        required_keys = list(discover_page.all_locators.keys())
    else:
        # DISCOVER_CAROUSELS value is parsed
        required_keys = [key.strip() for key in required_carousels.split(",") if key.strip()]

    # Transform rewuired carousels/keys in set for quick comparison
    expected_set = set(required_keys)
    
    missing_elements = []
    # print(f"\n--- Start an inspection for components: {required_keys} ---\n")
    
    # 3. Inspection and verification of components
    for name in required_keys:
        if name not in discover_page.all_locators:
            check.is_true(
                False, 
                msg=f"⚠️ Configuration error: The element '{name}' is listed in .env, but it's missing from the POM catolog!"
            )
            continue
            
        locator = discover_page.all_locators[name]
        
        # Wait for the element to appear for up to 2000 ms (2 seconds)
        try:
            locator.wait_for(state="visible", timeout=2000)
            is_visible = True
        except Exception:
            # If a TimeoutError is thrown, it means the element did not appear
            is_visible = False
        
        check.is_true(is_visible, msg=f"❌ The required element '{name}' is NOT visible!")
        
        if not is_visible:
            missing_elements.append(f"{name} ({locator})")


        # print(f"\n--- Search for items that ARE VISIBLE but ARE NOT in the .env list ---")

    # 2. Iterate through ALL defined locators in the POM
    for name, locator in discover_page.all_locators.items():
        
        # Check whether the element is currently visible on the screen
        try:
            # Use a short timeout so as not to slow down the test if the element is simply missing
            locator.wait_for(state="visible", timeout=1500)
            is_visible = True
        except Exception:
            is_visible = False
            
        # 3. If the element is visible but is not in the required DISCOVER CAROUSELS variable list in .env file
        if is_visible and (name not in expected_set):
            
            # We log a warning or fail the test (depending on your requirements)
            # Here, we use a soft assertion to display a message
            check.is_true(
                False, 
                msg=f"⚠️ An item found that is not on the list: '{name}' is visible, but it is not present in REQUIRED_HOME_ELEMENTS!"
            )
            print(f" 👀 Unidentified element discovered: {name}")

    # Console report
    if missing_elements:
        print(f"\n⚠️ Мissing required carousels: ({len(missing_elements)}):")
        for item in missing_elements:
            print(f" - {item}")
    # else:
        # print("\n✅ All verified items are visible on the page!")   
"""


"""    
def test_ui_discover_page_carousel_sections_follow_settings(monkeypatch):
    page = MagicMock()
    discover_page = DiscoverPage(page)

    monkeypatch.setattr(
        settings,
        "DISCOVER_CAROUSELS",
        "Top Live & Upcoming,New Carousel",
    )
    sections = discover_page.discover_carousel_sections
    assert tuple(sections) == (
        "Top Live & Upcoming",
        "New Carousel",
    )
    page.get_by_role.assert_any_call("heading", name="New Carousel", exact=True)

    monkeypatch.setattr(settings, "DISCOVER_CAROUSELS", "Featured")
    assert tuple(discover_page.discover_carousel_sections) == ("Featured",)
   

def test_ui_discover_page_required_carousels_are_configured():
    required_titles = {"Featured", "How to Watch"}
    configured_titles = set(settings.discover_carousels)
    missing_titles = sorted(required_titles - configured_titles)

    assert not missing_titles, (
        "DISCOVER_CAROUSELS is missing required title(s): "
        + ", ".join(missing_titles)
    )


def test_ui_discover_page_carousels_visibility(page):
    discover_page = DiscoverPage(page)
    discover_page.navigate()
    discover_page.cookie_consent_accept()

    configured_titles = set(settings.discover_carousels)
    carousel_headings = discover_page.main.locator("section:not(.featured):has(ul) > header").get_by_role("heading")
    #("section:not(.featured):has(ul) > header").get_by_role("heading")
    visible_titles = {
        " ".join(carousel_headings.nth(index).inner_text().split())
        for index in range(carousel_headings.count())
        if carousel_headings.nth(index).is_visible()
    }
    brand = settings.new_brand_terms[0]
    heading_aliases = {
        "Browse by Interest": "Interests",
        f"Subscriptions on {brand}": "Subscriptions",
        f"{brand} News": "News",
    }
    unconfigured_titles = sorted(
        title
        for title in visible_titles
        if heading_aliases.get(title, title) not in configured_titles
    )
    assert not unconfigured_titles, (
        "Visible Discover content carousel(s) missing from DISCOVER_CAROUSELS: "
        + ", ".join(unconfigured_titles)
    )

    for title, section in discover_page.discover_carousel_sections.items():
        expect(
            section,
            f"Discover section '{title}' was not visible at {discover_page.url}",
        ).to_be_visible()
"""

def test_ui_discover_page_footer_visibility(page):
    discover_page = DiscoverPage(page)
    base_page = BasePage(page)
    discover_page.navigate()
    base_page.cookie_consent_accept()

    # FOOTER: Strings and images visibility verification:
    visible_footer_locators: tuple[Locator, ...] = (
        base_page.footer_how_to_watch_link,
        base_page.footer_schedule_link,
        base_page.footer_promotions_link,
        base_page.footer_about_link,
        base_page.footer_news_link,
        base_page.footer_help_center_link,
        base_page.footer_terms_of_service_link,
        base_page.footer_privacy_policy_link,
        #base_page.footer_consent_preferences_link,
        base_page.footer_copyright,
    )
    for locator in visible_footer_locators:
        expect(locator, f"UI Component Missing: '{locator}' was not visible on the footer").to_be_visible()

    social_links = base_page.footer_social_links
    expect(social_links).to_have_count(5)
    for index in range(social_links.count()):
        expect(social_links.nth(index)).to_be_visible()

    store_links = base_page.footer_app_store_links
    expect(store_links).to_have_count(5)
    for index in range(store_links.count()):
        expect(store_links.nth(index)).to_be_attached()   


def test_ui_discover_page_brand_strings_verification(page):
    discover_page = DiscoverPage(page)
    base_page = BasePage(page)
    discover_page.navigate()
    base_page.cookie_consent_accept()
    #not needed brand_terms = settings.NEW_BRAND_TERMS
    #not needed clean_text = brand_terms.strip("settings.NEW_BRAND_TERMS")
    brand = settings.new_brand_terms[0]

    # Brand related strings verification:
    expect(base_page.header_fite_subs_link).to_have_text(f"{brand}+")
    expect(discover_page.subscriptions_section_title).to_have_text(f"Subscriptions on {brand}")
    expect(discover_page.browse_by_interest_section_text).to_have_text(f"Tailor {brand} to your interests!")
    expect(discover_page.news_section).to_have_text(f"{brand} News")
    expect(base_page.footer_about_link).to_have_text(f"About {brand}")
    expect(base_page.footer_news_link).to_have_text(f"{brand} News")
    expect(base_page.footer_copyright).to_have_text(f"Copyright © 2016-{datetime.now().year}, Flipps Media Inc.")


def test_ui_discover_page_brand_images_verification(page):
    discover_page = DiscoverPage(page)
    base_page = BasePage(page)
    discover_page.navigate()
    base_page.cookie_consent_accept()

    # Brand related images verification:
    image_strategy = ImageSimilarityValidationStrategy(minimum_similarity=90.0)
    image_assets = (
        BrandVisualAsset(
            name="Header logo",
            selector=base_page.header_logo,
            baseline_path=(PROJECT_ROOT / "resources" / "baselines" / "brand_FITE" / "logo.svg"),
        ),
        BrandVisualAsset(
            name="FITE+ subscription logo",
            selector=discover_page.fite_subs_logo,
            baseline_path=(PROJECT_ROOT / "resources" / "baselines" / "brand_FITE" / "fiteplus_logo_subs.svg"),
        ),
        BrandVisualAsset(
            name="How to Watch image",
            selector=discover_page.how_to_watch_image,
            baseline_path=(PROJECT_ROOT / "resources" / "baselines" / "brand_FITE" / "how-to-watch-fite.jpg"),
        ),
    )

    for asset in image_assets:
        result = image_strategy.compare(page, asset)
        assert result.status == "passed", f"{result.name}: {result.detail}"

"""
def test_ui_discover_page_link_locators_exclude_header_and_footer(page):
    discover_page = DiscoverPage(page)
    base_page = BasePage(page)
    discover_page.navigate()

    expect(discover_page.links).not_to_have_count(0)
    expect(base_page.header_links).not_to_have_count(0)
    expect(base_page.footer_links).not_to_have_count(0)
"""
"""
def test_ui_discover_page_links_are_reachable(page):
    discover_page = DiscoverPage(page)
    discover_page.navigate()
    expect(discover_page.main).to_be_visible()

    unreachable_links = discover_page.check_links_reachability()
    assert not unreachable_links, "Unreachable page links:\n" + "\n".join(
        unreachable_links
    )
"""