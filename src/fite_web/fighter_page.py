from urllib.parse import urljoin, urlparse

from playwright.sync_api import Error as PlaywrightError, Locator, Page

from fite_web.config import settings
from fite_web.base_page import BasePage


class FighterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{settings.BASE_URL}/fighter/kubrat-pulev-the-cobra/4012/"

        self.content = page.locator("body > main")
        self.profile_section = self.content.locator("section.fighter-profile")
        self.events_section = self._section("Kubrat Pulev Events")
        self.matches_section = self._section("Matches")
        self.profiles_section = self._section("Profiles")
        self.news_section = self.content.locator("section#news")
        self.discover_section = self.content.locator("section#discover")

        self.fighter_name = self.profile_section.get_by_role("heading", name="Kubrat Pulev", exact=True)
        self.fighter_nickname = self.profile_section.get_by_role("heading", name='"The Cobra"', exact=True)
        self.follow_button = self.profile_section.get_by_role("button", name="Follow", exact=True)
        self.profile_images = self.profile_section.locator("img")
        self.social_links = self.profile_section.get_by_role("link")
        self.profile_stat_labels = self.profile_section.locator("dt")
        self.profile_stat_values = self.profile_section.locator("dd")

        self.events_heading = self.events_section.get_by_role("heading", name="Kubrat Pulev Events", exact=True)
        self.event_cards = self.events_section.locator("li")
        self.event_images = self.events_section.locator("img")
        self.event_links = self.events_section.get_by_role("link")

        self.matches_heading = self.matches_section.get_by_role("heading", name="Matches", exact=True)
        self.match_cards = self.matches_section.locator("li")
        self.match_images = self.matches_section.locator("img")
        self.match_links = self.matches_section.get_by_role("link")

        self.profiles_heading = self.profiles_section.get_by_role("heading", name="Profiles", exact=True)
        self.related_profile_cards = self.profiles_section.locator("li")
        self.related_profile_images = self.profiles_section.locator("img")
        self.related_profile_links = self.profiles_section.get_by_role("link")

        self.news_heading = self.news_section.get_by_role("heading").first
        self.news_links = self.news_section.get_by_role("link")
        self.discover_heading = self.discover_section.get_by_role("heading").first
        self.discover_links = self.discover_section.get_by_role("link")

        self.images = self.content.locator("img")
        self.buttons = self.content.locator("button")
        self.strings = self.content.locator("h1, h2, h3, h4, p, time, dt, dd, li, span, a, button")
        self.visible_images = self.content.locator("img:visible")
        self.visible_buttons = self.content.locator("button:visible")
        self.visible_strings = self.content.locator(
            "h1:visible, h2:visible, h3:visible, h4:visible, p:visible, "
            "time:visible, dt:visible, dd:visible, li:visible, span:visible, "
            "a:visible, button:visible"
        )
        self.links = self.content.locator("a[href]")

    def navigate(self) -> None:
        self.page.goto(self.url)

    def check_links_reachability(self) -> list[str]:
        """Return unique HTTP(S) links that return not-found or server-error responses."""
        hrefs = self.links.evaluate_all(
            "(links) => links.map((link) => link.getAttribute('href'))"
        )
        failures = []
        for href in dict.fromkeys(href for href in hrefs if href):
            target_url = urljoin(self.url, href)
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

    def _section(self, heading: str) -> Locator:
        return self.content.locator("section").filter(
            has=self.page.get_by_role("heading", name=heading, exact=True)
        )
