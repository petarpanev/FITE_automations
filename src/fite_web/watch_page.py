from urllib.parse import urljoin, urlparse
from playwright.sync_api import FrameLocator, Locator, Page
from playwright.sync_api import Error as PlaywrightError
from fite_web.config import settings
from fite_web.base_page import BasePage

class WatchPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.url = f"{settings.BASE_URL}/watch/badou-jack-vs-noel-mikaelian-2/2pi4l/"

        self.payment_frame: FrameLocator = page.frame_locator(
            'iframe[name="embedded-checkout"]'
        )
        self.pay_by_card = self.payment_frame.locator("#payment-form > div > div > div > div.PaymentMethodForm > div.Accordion.PaymentMethodFormAccordion > div:nth-child(1) > div > div > div > div")
        self.card_input = self.payment_frame.locator("#cardNumber")
        self.exp_date_input = self.payment_frame.locator("#cardExpiry")
        self.cvc_input = self.payment_frame.locator("#cardCvc")
        self.name_input = self.payment_frame.locator("#billingName")
        self.country_input = self.payment_frame.locator("#billingCountry")
        self.address_input = self.payment_frame.locator("#billingAddressLine1")
        self.postal_code_input = self.payment_frame.locator("#billingPostalCode")
        self.city_input = self.payment_frame.locator("#billingLocality")
        self.pay_button = self.payment_frame.get_by_test_id("hosted-payment-submit-button")
        self.ppv_purchase_success_message = page.get_by_text(
            "You purchased Badou Jack vs Noel Mikaelian 2 successfully!",
            exact=False,
        )

        self.content = page.locator("body > main")
        self.player_section = self.content.locator("#player-holder")
        self.event_details_section = self.content.locator("#event-details")
        self.fighter_stats_section = self.content.locator("section").filter(
            has_text="Votes"
        )
        self.fight_card_section = self._section("Full Fight Card")
        self.watch_more_section = self._section("Watch more")
        self.newest_from_channel_section = self._section(
            "Newest from Integrated Sports"
        )
        self.news_section = self.content.locator("#news")
        self.discover_section = self.content.locator("section#discover")
        self.more_from_channel_section = self._section("More from Integrated Sports")

        self.event_title = self.player_section.get_by_role(
            "heading", name="Badou Jack vs Noel Mikaelian 2", exact=True
        )
        self.event_date = self.player_section.locator("time")
        self.event_poster_image = self.event_details_section.locator("img")
        self.sign_up_button = self.player_section.get_by_role(
            "button", name="Sign up to Watch", exact=True
        )
        self.buy_button = self.player_section.get_by_role(
            "button", name="Buy $"
        )
        self.rating_buttons = self.player_section.get_by_role(
            "button", name="Rate"
        )

        self.event_description = self.event_details_section.locator(
            ".event-description"
        )
        self.more_details_button = self.event_details_section.get_by_role(
            "button", name="More", exact=True
        )
        self.follow_button = self.event_details_section.get_by_role(
            "button", name="Follow", exact=True
        )
        self.watch_later_buttons = self.event_details_section.get_by_role(
            "button", name="Watch Later", exact=True
        )
        self.share_buttons = self.event_details_section.get_by_role(
            "button", name="Share", exact=True
        )
        self.help_links = self.event_details_section.get_by_role(
            "link", name="Help", exact=True
        )
        self.channel_links = self.event_details_section.get_by_role(
            "link", name="Integrated Sports", exact=True
        )
        self.category_links = self.event_details_section.get_by_role(
            "link", name="Boxing", exact=True
        )
        self.fighter_images = self.fighter_stats_section.locator("img")
        self.fighter_links = self.fighter_stats_section.get_by_role("link")
        self.fight_card_heading = self.fight_card_section.get_by_role(
            "heading", name="Full Fight Card", exact=True
        )
        self.fight_card_fighter_links = self.fight_card_section.get_by_role("link")
        self.watch_more_heading = self.watch_more_section.get_by_role(
            "heading", name="Watch more", exact=True
        )
        self.recommended_event_images = self.watch_more_section.locator("img")
        self.recommended_event_links = self.watch_more_section.get_by_role("link")
        self.newest_event_heading = self.newest_from_channel_section.get_by_role(
            "heading", name="Newest from Integrated Sports", exact=True
        )
        self.news_heading = self.news_section.get_by_role(
            "heading", name="News", exact=True
        )
        self.news_links = self.news_section.get_by_role("link")
        self.discover_heading = self.discover_section.get_by_role("heading").first
        self.more_from_channel_heading = self.more_from_channel_section.get_by_role(
            "heading", name="More from Integrated Sports", exact=True
        )

        self.images = self.content.locator("img")
        self.buttons = self.content.locator("button")
        self.strings = self.content.locator(
            "h1, h2, h3, h4, p, time, dt, dd, li, span, a, button"
        )
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

    def start_ppv_purchase_flow(self):
        self.buy_button.click()     

    def ppv_purchase_with_card(self) -> None:
        self.pay_by_card.click()
        self.card_input.fill(settings.STRIPE_TEST_CARD)
        self.exp_date_input.fill(settings.STRIPE_EXP_DATE)
        self.cvc_input.fill(settings.STRIPE_CVC)

        self.name_input.fill(settings.STRIPE_NAME)
        self.country_input.select_option(label=settings.STRIPE_COUNTRY)
        self.address_input.fill(settings.STRIPE_ADDRESS)
        self.postal_code_input.fill(settings.STRIPE_POSTAL_CODE)
        self.city_input.fill(settings.STRIPE_CITY)

        self.pay_button.click()  
