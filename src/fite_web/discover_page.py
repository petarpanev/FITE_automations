from urllib.parse import urljoin, urlparse
from playwright.sync_api import Locator, Page
from playwright.sync_api import Error as PlaywrightError
from fite_web.config import settings
from fite_web.base_page import BasePage

class DiscoverPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.url = settings.BASE_URL

        self.fite_subs_logo = page.locator(
            "#subscriptions img[alt='TrillerTV+'][src*='trillertv_plus_dark_background_Guni4gF']"
        )
        self.how_to_watch_image = page.locator(
            r"body > main > section.mb-10.py-20.px-4.xl\:px-18."
            r"flex.flex-col.lg\:flex-row.text-center.items-center."
            r"bg-mono-white.text-fite-gray-100.font-sans > "
            r"div.w-full.lg\:w-1\/2.pl-3 > a > img"
        )
        self.main = page.locator("body > main")
        self.featured_section = self.main.locator("section.featured")
        self.featured_heading = self.featured_section.get_by_role("heading")
        self.featured_links = self.featured_section.get_by_role("link")
        self.featured_images = self.featured_section.locator("img")
        self.featured_previous_control = self.featured_section.locator(".swipe-prev")
        self.featured_next_control = self.featured_section.locator(".swipe-next")

        self.featured_item_1_publisher = page.locator(r"body > main > section.mb-10.overflow-hidden.featured.px-0.relative.swiper-container.md\:mt-0.-mt-12.swiper-initialized.swiper-horizontal.swiper-android.swiper-backface-hidden > ul > li:nth-child(6) > div > div > p")
        self.featured_item_1_title = page.locator(r"body > main > section.mb-10.overflow-hidden.featured.px-0.relative.swiper-container.md\:mt-0.-mt-12.swiper-initialized.swiper-horizontal.swiper-android.swiper-backface-hidden > ul > li:nth-child(5) > div > div > h2")
        self.featured_item_1_air_time = page.locator(r"body > main > section.mb-10.overflow-hidden.featured.px-0.relative.swiper-container.md\:mt-0.-mt-12.swiper-initialized.swiper-horizontal.swiper-android.swiper-backface-hidden > ul > li.swiper-slide.w-full.swiper-slide-prev > div > div > div > time")
        self.featured_item_1_image = page.locator(r"body > main > section.mb-10.overflow-hidden.featured.px-0.relative.swiper-container.md\:mt-0.-mt-12.swiper-initialized.swiper-horizontal.swiper-android.swiper-backface-hidden > ul > li:nth-child(4) > div > a > picture")
        self.featured_swiper = page.locator(r"body > main > section.mb-10.overflow-hidden.featured.px-0.relative.swiper-container.md\:mt-0.-mt-12.swiper-initialized.swiper-horizontal.swiper-android.swiper-backface-hidden > div.swiper-paginations.text-center.absolute.bottom-0.md\:bottom-4.left-0.xl\:left-18.z-10.w-full.xl\:w-\[22\%\].swiper-pagination-clickable.fite-swiper-bullets.fite-swiper-pagination")        

        self.top_live_upcoming_section = self._section("Top Live & Upcoming")
        self.trending_section = self._section("Trending")
        self.top_replays_section = self._section("Top Replays")
        self.aew_packs_section = self._section("AEW PPV Archive Packs")
        self.pay_per_views_section = self._section("Pay Per Views")
        self.free_events_section = self._section("Free Events")
        self.recently_added_section = self._section("Recently Added")
        self.games_of_the_future_section = self._section("Games of The Future")
        self.gcw_events_section = self._section("GCW Events")
        self.bkfc_section = self._section("BKFC")
        self.glory_kickboxing_section = self._section("GLORY Kickboxing")
        self.football_section = (self.main.locator("section > header").get_by_role("heading", name="Football", exact=True).locator("xpath=../.."))
        self.my_fite_plus_section = self._section("My FITE+")
        self.aew_ppvs_section = self._section("AEW PPVs")
        #self.aew_plus_section = self._section("AEW Plus")
        self.tennis_section = self._section("Tennis")
        self.motorsports_section = self._section("Motorsports")
        
        self.subscriptions_section_title = page.locator("#subscriptions > header > h2")
        self.subscriptions_section_text = page.get_by_text("The best value in streaming sports")
        self.channels_section = self._section("Channels")
        self.profiles_section = self._section("Profiles")
        self.browse_by_interest_section_title = self._section("Browse by Interest")
        self.browse_by_interest_section_text = page.locator("#sports > header > p")
        self.news_section = page.locator("#news > header > h2 > a")
        self.big_screen_tv_section_title = self._section("Stream all the action to your big-screen TV!")
        self.big_screen_tv_section_text = page.get_by_text("Learn how to live stream to any connected smart TV, Roku, Apple TV, Chromecast, or Xbox device.")
        self.big_screen_tv_section_button = page.locator(r"body > main > section.mb-10.py-20.px-4.xl\:px-18.flex.flex-col.lg\:flex-row.text-center.items-center.bg-mono-white.text-fite-gray-100.font-sans > div.w-full.lg\:w-1\/2.pr-3 > a")
        self.discover_section = self._section("Discover {brand}")

        self.content_sections = self.main.locator("section")
        self.event_cards = self.main.locator("section:not(.featured) li, section:not(.featured) article")
        self.event_card_links = self.event_cards.get_by_role("link")
        self.content_images = self.main.locator("section img")
        self.subscription_images = self.subscriptions_section_title.locator("img")
        self.channel_cards = self.channels_section.locator("li, article")
        self.profile_cards = self.profiles_section.locator("li, article")
        self.interest_links = self.browse_by_interest_section_title.get_by_role("link")
        self.news_articles = self.news_section.locator("article, li")

        self.fite_subs_logo = self.main.locator("#subscriptions img[alt='TrillerTV+'][src*='trillertv_plus_dark_background_Guni4gF']")
        self.how_to_watch_section = self.main.locator("section").filter(has=self.page.get_by_role("heading", name="Stream all the action to your big-screen TV!", exact=True,))
        self.how_to_watch_image = self.how_to_watch_section.locator("img")
        self.featured_item_1 = self.featured_section.locator("li").first
        self.featured_item_1_publisher = self.featured_item_1.locator("p").first
        self.featured_item_1_title = self.featured_item_1.locator("h2").first
        self.featured_item_1_air_time = self.featured_item_1.locator("time").first
        self.featured_item_1_image = self.featured_item_1.locator("picture").first
        self.discover_section = self.main.locator("#discover")
        self.links = self.main.locator("a[href]")
        self.images = self.main.locator("img")
        self.buttons = self.main.locator("button")
        self.strings = self.main.locator("h1, h2, h3, h4, p, time, dt, dd, li, span, a, button")

        # All available carousels catalog which can be added to Discover page
        self.all_locators = {
            "Featured": self.featured_section,
            "Top Live & Upcoming": self.top_live_upcoming_section,
            "Top Replays": self.top_replays_section,
            "AEW PPV Archive Packs": self.aew_packs_section,
            "Pay Per Views": self.pay_per_views_section,
            "Free Events": self.free_events_section,
            "Trending": self.trending_section,
            "Recently Added": self.recently_added_section,
            "Games of The Future": self.games_of_the_future_section,
            "GCW Events": self.gcw_events_section,
            "BKFC": self.bkfc_section,
            "GLORY Kickboxing": self.glory_kickboxing_section,
            "Football": self.football_section,
            "My FITE+": self.my_fite_plus_section,
            "AEW PPVs": self.aew_ppvs_section,
            #"AEW Plus": self.aew_plus_section,
            "Tennis": self.tennis_section,
            "Motorsports": self.motorsports_section,
            "Channels": self.channels_section,
            "Profiles": self.profiles_section,
            "Subscriptions": self.subscriptions_section_title,
            "Interests": self.browse_by_interest_section_text,
            "News": self.news_section,
            "How to Watch": self.big_screen_tv_section_title,
            "Discover TrillerTV": self.discover_section,
       }
    """
    @property
    def discover_carousel_sections(self) -> dict[str, Locator]:
        configured_sections = {
            "Featured": self.featured_section,
            "Football": self.football_section,
            "Subscriptions": self.page.locator("#subscriptions"),
            "Interests": self.page.locator("#sports"),
            "News": self.page.locator("#news"),
            "How to Watch": self.big_screen_tv_section_title,
        }
        return {
            title: (
                configured_sections[title]
                if title in configured_sections
                else self._section(title)
            )
            for title in settings.discover_carousels
        }
    """
    def _section(self, heading: str) -> Locator:
        return self.main.locator("section").filter(
            has=self.page.get_by_role("heading", name=heading, exact=True)
        )
   
    def navigate(self):
        self.page.goto(self.url)

    #def check_links_reachability(self) -> list[str]:
    #    return self._check_links_reachability(self.links, self.url)
    
    def check_links_reachability(self) -> list[str]:
       # Return unique HTTP(S) links that return not-found or server-error responses.
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
        