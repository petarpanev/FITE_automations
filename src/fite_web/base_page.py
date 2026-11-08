import sys
from urllib.parse import urljoin, urlparse
from playwright.sync_api import Error as PlaywrightError
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

#not needed from playwright.sync_api import Error as PlaywrightError, Page, Locator
from playwright.sync_api import Page, Locator
from fite_web.config import settings


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.url = settings.BASE_URL
        # HEADER elements locators:
        self.header = page.locator("body > header")
        self.header_links = self.header.locator("a[href]")
        self.header_logo_link = page.locator("header a[href='/']")
        self.header_logo = self.header_logo_link.locator("svg")
        self.header_navigation = self.header.locator("nav")
        self.header_discover_link = page.get_by_role("link", name="Discover")
        self.header_schedule_link = page.locator("body > header > div.page-header.flex.flex-row.flex-wrap.xl\:flex-nowrap.justify-between.items-center.pt-1\.5.md\:pt-3.pb-2.lg\:pt-2.lg\:pb-3.relative.px-4.xl\:px-18 > nav > ul > li:nth-child(2) > a")
        self.header_fite_subs_link = page.locator("body > header > div.page-header.flex.flex-row.flex-wrap.xl\:flex-nowrap.justify-between.items-center.pt-1\.5.md\:pt-3.pb-2.lg\:pt-2.lg\:pb-3.relative.px-4.xl\:px-18 > nav > ul > li:nth-child(3) > a")
        # self.header_willow_subs_link = page.get_by_role("link", name="Willow")
        self.header_news_link = page.locator("body > header > div.page-header.flex.flex-row.flex-wrap.xl\:flex-nowrap.justify-between.items-center.pt-1\.5.md\:pt-3.pb-2.lg\:pt-2.lg\:pb-3.relative.px-4.xl\:px-18 > nav > ul > li:nth-child(6) > a")
        self.header_tv_link = page.locator("body > header > div.page-header.flex.flex-row.flex-wrap.xl\:flex-nowrap.justify-between.items-center.pt-1\.5.md\:pt-3.pb-2.lg\:pt-2.lg\:pb-3.relative.px-4.xl\:px-18 > nav > ul > li:nth-child(7) > span")
        self.header_tv_option_1 = page.locator("#home_t78_g0 > li:nth-child(1) > a")
        self.header_tv_option_2 = page.locator("#home_t78_g0 > li:nth-child(2) > a")
        self.header_deals_link = page.locator("body > header > div.page-header.flex.flex-row.flex-wrap.xl\:flex-nowrap.justify-between.items-center.pt-1\.5.md\:pt-3.pb-2.lg\:pt-2.lg\:pb-3.relative.px-4.xl\:px-18 > ul > li:nth-child(1) > a > img.normal")
        self.header_categories_link = page.locator("body > header > div.page-header.flex.flex-row.flex-wrap.xl\:flex-nowrap.justify-between.items-center.pt-1\.5.md\:pt-3.pb-2.lg\:pt-2.lg\:pb-3.relative.px-4.xl\:px-18 > ul > li:nth-child(2) > span > img.normal")
        self.header_category_option_1 = page.locator("#home_t64_g0 > li:nth-child(1) > a")
        self.header_category_option_2 = page.locator("#home_t64_g0 > li:nth-child(2) > a")
        self.header_category_option_3 = page.locator("#home_t64_g0 > li:nth-child(3) > a")
        self.header_category_option_4 = page.locator("#home_t64_g0 > li:nth-child(4) > a")
        self.header_search_button = self.header.get_by_role("button", name="Search", exact=True)
        
        self.header_search_panel = page.locator("#js-nav-search")
        self.header_search_input = self.header_search_panel.get_by_placeholder("Events, fighters, channels and more...", exact=True)
        self.header_search_cancel_button = page.locator("#js-nav-search > div > form > input")
        #header_search_panel.get_by_role("button", name="Cancel", exact=True)
        self.header_search_results = self.header_search_panel.locator("ul")
        self.header_search_result_items = self.header_search_results.locator("li")
        self.header_search_result_links = self.header_search_result_items.get_by_role("link")

        self.header_account_button = page.locator("#js-nav-account > svg > use")

        # FOOTER elements locators:
        self.footer = page.locator("body > footer")
        self.footer_links = self.footer.locator("a[href]")
        self.footer_how_to_watch_link = self.footer.get_by_role("link", name="How to Watch", exact=True)
        self.footer_schedule_link = self.footer.get_by_role("link", name="Schedule", exact=True)
        self.footer_promotions_link = self.footer.get_by_role("link", name="Promotions", exact=True)
        self.footer_about_link = page.locator("html > body > footer > div:nth-of-type(1) > div > div > ul:nth-of-type(2) > li:nth-of-type(1) > a")
        self.footer_news_link = page.locator("html > body > footer > div.max-w-4xl.mx-auto.mb-6.md\:mb-10 > div > div > ul:nth-child(2) > li:nth-child(2) > a")
        self.footer_help_center_link = self.footer.get_by_role("link", name="Help Center", exact=True)
        self.footer_social_links = self.footer.locator(
            "a[href*='facebook.com'], "
            "a[href*='x.com'], "
            "a[href*='instagram.com'], "
            "a[href*='youtube.com'], "
            "a[href*='linkedin.com']"
        )
        self.footer_app_store_links = self.footer.locator(
            "a[href*='play.google.com'], " 
            "a[href*='apps.apple.com'], " 
            "a[href*='amazon.com'], " 
            "a[href*='appgallery'], " 
            "a[href*='roku.com']"
        )
        self.footer_terms_of_service_link = self.footer.get_by_role("link", name="Terms of Service", exact=True)
        self.footer_privacy_policy_link = self.footer.get_by_role("link", name="Privacy Policy", exact=True)
        self.footer_consent_preferences_link = self.footer.get_by_text("Consent Preferences", exact=True)
        self.footer_copyright = self.footer.locator("p")

    def _check_links_reachability(
        self,
        links: Locator,
        page_url: str,
    ) -> list[str]:
        hrefs = links.evaluate_all(
            "(links) => links.map((link) => link.getAttribute('href'))"
        )
        targets = []
        failures = []
        allow_development_404 = settings.ENVIRONMENT.strip().lower() in {
            "dev",
            "development",
        }
        for href in dict.fromkeys(href for href in hrefs if href):
            target_url = urljoin(page_url, href)
            if urlparse(target_url).scheme not in {"http", "https"}:
                continue

            targets.append(target_url)

        def check_target(target_url: str) -> tuple[str, int | None, str | None]:
            try:
                request = Request(
                    target_url,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urlopen(request, timeout=5) as response:
                    return target_url, response.status, None
            except HTTPError as error:
                return target_url, error.code, None
            except (URLError, OSError) as error:
                return target_url, None, str(error)

        failures = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            results = executor.map(check_target, targets)
            for target_url, status, error in results:
                if error is not None:
                    failures.append(f"{target_url} could not be reached: {error}")
                elif status == 404 and allow_development_404:
                    continue
                elif status in {404, 410} or (
                    status is not None and status >= 500
                ):
                    failures.append(f"{target_url} returned HTTP {status}")
        return failures

    def cookie_consent_accept(self):
        self.page.get_by_role("button", name="Accept All").click()


    def navigate_to_discover(self):
        self.header_logo_link.click()

    """    
    def check_links_reachability(self,hrefs) -> list[str]:
        # Return unique HTTP(S) links that return not-found or server-error responses.
    #    hrefs = self.links.evaluate_all(
    #        "(links) => links.map((link) => link.getAttribute('href'))"
    #    )
        failures = []
        for href in dict.fromkeys(href for href in hrefs if href):
            target_url = urljoin(self.url, href)
            print(f"\n Opening: {target_url}")
            if urlparse(target_url).scheme not in {"http", "https"}:
                continue
            try:
                response = self.page.request.get(target_url, timeout=10_000)
            except PlaywrightError as error:
                failures.append(f"{target_url} could not be reached: {error}")
                continue
            if response.status in {404, 410} or response.status >= 500:
                failures.append(f"{target_url} returned HTTP {response.status}")
        return failures    
    """

    def run_app():
        """Главна функция, която стартира логиката на приложението."""
        print(f"--- Стартиране на приложението в режим: {settings.ENVIRONMENT} ---")

        # Използваме конфигурираните променливи от .env през config.py
        # print(f"Свързване с база данни: {settings.DATABASE_URL}")
        print(f"Целеви уеб адрес (Base URL): {settings.BASE_URL}")

        # Симулация на проверка на API ключ
        if not settings.API_KEY or settings.API_KEY == "your_api_key_here":
            print("Грешка: Невалиден или липсващ API ключ!", file=sys.stderr)
            return False

        print("Приложението стартира успешно и очаква заявки...")
        return True

    # Този блок гарантира, че кодът ще се изпълни САМО ако файлът се пусне директно,
    # а не ако се импортира в тестовете ви.
    if __name__ == "__main__":
        success = run_app()
        sys.exit(0 if success else 1)
