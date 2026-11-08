#import logging
from urllib.parse import urljoin, urlparse
from playwright.sync_api import FrameLocator, Locator, Page
from playwright.sync_api import Error as PlaywrightError
from fite_web.config import settings
from fite_web.base_page import BasePage

# logger = logging.getLogger(__name__)

class FITESubsPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.url = f"{settings.BASE_URL}/join/trillertv-subscription/"

        self.payment_frame: FrameLocator = page.frame_locator('iframe[name="embedded-checkout"]')
        self.card_input = self.payment_frame.locator("#cardNumber")
        self.exp_date_input = self.payment_frame.locator("#cardExpiry")
        self.cvc_input = self.payment_frame.locator("#cardCvc")
        self.name_input = self.payment_frame.locator("#billingName")
        self.country_input = self.payment_frame.locator("#billingCountry")
        self.address_input = self.payment_frame.locator("#billingAddressLine1")
        self.postal_code_input = self.payment_frame.locator("#billingPostalCode")
        self.city_input = self.payment_frame.locator("#billingLocality")
        self.pay_button = self.payment_frame.get_by_test_id("hosted-payment-submit-button")
        self.subscription_success_message = page.get_by_text(
            "You subscribed for FITE+ Monthly successfully!",
            exact=False,
        )
        # self.monthly_pass_button = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(2) > button")

        # self.monthly_pass_button = page.get_by_role("button[name='Start 7-Day Free Trial']")  #for fresh user
        # self.monthly_pass_button = page.get_by_role("button[name='Join FITE+']")  #for returned user with canceled subscription

        self.main = page.locator("body > main")
        self.subscription_featured_section = self.main.locator("section.featured")
        self.subscription_featured_cards = (self.subscription_featured_section.locator("li")) 
        self.subscription_featured_images = (self.subscription_featured_cards.locator("img"))
        self.subscription_featured_links = (self.subscription_featured_cards.get_by_role("link"))
        self.subscription_featured_titles = (self.subscription_featured_cards.locator(".title"))
        self.subscription_featured_times = (self.subscription_featured_cards.locator("time"))
        # self.subscription_featured_access_labels = (self.subscription_featured_cards.locator(".card-price"))

        self.subscription_details_section = self.main.locator("section.subs-details")
        self.subscription_details_heading = self.subscription_details_section.locator("p").first
        self.subscription_details_benefits = self.subscription_details_section.locator("ul.subscription-tags")
        self.subscription_details_plan1_card = (self.subscription_details_section.locator(".sub-package").filter(has=self.page.get_by_text("Monthly Pass", exact=True)))
        self.subscription_details_plan2_card = (self.subscription_details_section.locator(".sub-package").filter(has=self.page.get_by_text("Annual Pass", exact=True)))
        self.subscription_details_plan1_title = (self.subscription_details_plan1_card.locator("p.card-title"))
        self.subscription_details_plan2_title = (self.subscription_details_plan2_card.locator("p.card-title"))
        self.subscription_details_plan1_logo = (self.subscription_details_plan1_card.locator("img.subscription-logo"))
        self.subscription_details_plan2_logo = (self.subscription_details_plan2_card.locator("img.subscription-logo"))
        self.subscription_details_plan1_price = (self.subscription_details_plan1_card.locator("p.text-5xl"))
        self.subscription_details_plan2_price = (self.subscription_details_plan2_card.locator("p.text-5xl"))
        self.subscription_details_plan1_button = (self.subscription_details_plan1_card.get_by_role("button"))
        self.subscription_details_plan2_button = (self.subscription_details_plan2_card.get_by_role("button"))
        self.subscription_details_plan1_cancel = (self.subscription_details_plan1_card.locator("p.card-price"))
        self.subscription_details_plan2_cancel = (self.subscription_details_plan2_card.locator("p.card-price"))
        self.monthly_pass_button = self.subscription_details_plan1_button
        self.annual_pass_button = self.subscription_details_plan2_button

        #self.subscription_details_section = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div")
        #self.subscription_details_heading = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div.order-last.md\:order-first.basis-auto.md\:basis-1\/2.xl\:basis-2\/12.shrink > p")
        #self.subscription_details_benefits = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div.order-last.md\:order-first.basis-auto.md\:basis-1\/2.xl\:basis-2\/12.shrink")
        """
        self.subscription_details_plan1_logo = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(2) > div > img")
        self.subscription_details_plan1_title = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(2) > p.font-sans.font-bold.card-title")
        self.subscription_details_plan1_card = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(2)")
        self.subscription_details_plan1_price = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(2) > p.text-5xl.font-bold.py-2")
        self.subscription_details_plan1_button = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(2) > button")
        self.subscription_details_plan1_cancel = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(2) > p.card-price.pt-2")
        self.subscription_details_plan2_logo = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(3) > div > img")
        self.subscription_details_plan2_title = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(3) > p.font-sans.font-bold.card-title")
        self.subscription_details_plan2_card = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(3)")
        self.subscription_details_plan2_price = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(3) > p.text-5xl.font-bold.py-2")
        self.subscription_details_plan2_button = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(3) > button")
        self.subscription_details_plan2_cancel = page.locator("body > main > section.mb-10.carousel-gradient.subs-details > div > div > div:nth-child(3) > p.card-price.pt-2")
        """

        #self.subscription_top_replays = page.locator("body > main > section:nth-child(4) > header > h2 > a")
        #self.subscription_top_replays_more = page.locator("body > main > section:nth-child(4) > header > a")
        #self.subscription_channels_section = page.locator("body > main > section:nth-child(5) > header > h2")
        """
        self.subscription_wrestling_events = page.locator("html > body > main > section:nth-child(8) > header > h2 > a")
        self.subscription_wrestling_videos = page.locator("html > body > main > section:nth-child(9) > header > h2 > a")
        self.subscription_boxing_events = page.locator("html > body > main > section:nth-child(10) > header > h2 > a")
        self.subscription_boxing_videos = page.locator("html > body > main > section:nth-child(11) > header > h2 > a")
        self.subscription_mma_events = page.locator("html > body > main > section:nth-child(12) > header > h2 > a")
        self.subscription_mma_videos = page.locator("html > body > main > section:nth-child(13) > header > h2 > a")
        self.subscription_motorsports_events = page.locator("html > body > main > section:nth-child(15) > header > h2 > a")
        self.subscription_cricket_events = page.locator("html > body > main > section:nth-child(16) > header > h2 > a")
        self.subscription_football_events = page.locator("html > body > main > section:nth-child(17) > header > h2 > a")
        self.subscription_skateboarding_events = page.locator("html > body > main > section:nth-child(19) > header > h2 > a")
        self.subscription_cycling_events = page.locator("html > body > main > section:nth-child(21) > header > h2 > a")
        self.subscription_athletics_events = page.locator("html > body > main > section:nth-child(22) > header > h2 > a")
        self.subscription_water_sports_events = page.locator("html > body > main > section:nth-child(23) > header > h2 > a")
        self.subscription_basketball_events = page.locator("html > body > main > section:nth-child(24) > header > h2 > a")
        self.subscription_american_football_events = page.locator("html > body > main > section:nth-child(25) > header > h2 > a")
        self.subscription_glory_events = page.locator("html > body > main > section:nth-child(26) > header > h2 > a")
        self.subscription_one_events = page.locator("html > body > main > section:nth-child(27) > header > h2 > a")
        self.subscription_njpw_events = page.locator("html > body > main > section:nth-child(29) > header > h2 > a")

        
        self.subscription_details_section = self.main.locator("section.subs-details")
        self.subscription_details_heading = (self.subscription_details_section.get_by_text("Join TrillerTV+",exact=True,))
        self.subscription_benefits = (self.subscription_details_section.locator("ul.subscription-tags li"))
        self.subscription_packages = self.subscription_details_section.locator(".sub-package")
        self.monthly_pass = self.subscription_packages.filter(has=page.get_by_text("Monthly Pass", exact=True))
        self.annual_pass = self.subscription_packages.filter(has=page.get_by_text("Annual Pass", exact=True))
        self.subscription_logos = self.subscription_packages.locator("img.subscription-logo")
        self.subscription_prices = self.subscription_packages.locator("p.text-5xl")
        self.subscription_trial_buttons = self.subscription_packages.get_by_role("button",name="Start 7-Day Free Trial",exact=True,)
        self.subscription_cancel_terms = self.subscription_packages.locator("p.card-price")
        """
        #self.subscription_info_section = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300")

        self.subscription_info_section = self.main.locator("section.subs-info")
        self.subscription_info_exclusive_icon = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(1) > img")
        self.subscription_info_exclusive_title = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(1) > h3")
        self.subscription_info_exclusive_text = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(1) > p")

        self.subscription_info_organizations_icon = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(2) > img")
        self.subscription_info_organizations_title = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(2) > h3")
        self.subscription_info_organizations_text = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(2) > p")

        self.subscription_info_wrestling_icon = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(3) > img")
        self.subscription_info_wrestling_title = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(3) > h3")
        self.subscription_info_wrestling_text = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(3) > p")

        self.subscription_info_content_icon = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(4) > img")
        self.subscription_info_content_title = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(4) > h3")
        self.subscription_info_content_text = page.locator("body > main > section.mb-10.py-10.subs-info.bg-mono-ns-300 > div > div:nth-child(4) > p")

        self.main = page.locator("body > main")
        self.content_sections = self.main.locator("section")
        self.links = self.main.locator("a[href]")

        self.images = self.main.locator("img")
        self.buttons = self.main.locator("button")
        self.strings = self.main.locator("h1, h2, h3, h4, p, time, dt, dd, li, span, a, button")

        self.subscription_top_replays_section = self._collection_section("Top Replays")
        self.subscription_top_replays = self._collection_heading("Top Replays")
        self.subscription_top_replays_more = (self.subscription_top_replays_section.locator("header > a"))
        self.subscription_channels_section = self._section("Channels").get_by_role("heading", name="Channels", exact=True)
        self.summer_supercard_week_section = self._collection_heading("Summer Supercard Week")
        self.free_events_section = self._collection_heading("Free Events")
        self.trending_section = self._collection_heading("Trending")
        self.recently_added_section = self._collection_heading("Recently Added")
        self.football_section = self._collection_heading("Football")
        self.football_highlights = self._collection_heading("Football Highlights")
        self.barnetts_bloodsport = self._collection_heading("GCW: Josh Barnett's Bloodsport")
        self.subscription_boxing_events = self._collection_heading("Basketball Events")
        self.skateboarding_videos = self._collection_heading("Skateboarding Videos")
        self.subscription_glory_kickboxing = self._collection_heading("GLORY Kickboxing")
        self.subscription_one = self._collection_heading("ONE")
        self.subscription_tna = self._collection_heading("TNA")
        self.subscription_njpw = self._collection_heading("NJPW")
        self.wwe_id_wrestlers = self._collection_heading("WWE ID Wrestlers")
        self.jon_moxley_gcw = self._collection_heading("Jon Moxley on GCW")
        self.david_mundell_bkfc = self._collection_heading("David Mundell - BKFC’s P4P King")
        self.mike_perrys_hits = self._collection_heading("Mike Perry's Greatest Hits")
        self.games_of_the_future = self._collection_heading("Games of The Future")
        self.gcw_events = self._collection_heading("GCW Events")
        self.bkfc = self._collection_heading("BKFC")
        self.tennis_section = self._collection_heading("Tennis")
        self.subscription_profiles_section = self._collection_heading("Profiles")        
        self.subscription_wrestling_events = self._collection_heading("Pro Wrestling Events")
        self.subscription_wrestling_videos = self._collection_heading("Pro Wrestling Videos")
        self.subscription_boxing_events = self._collection_heading("Boxing Events")
        self.subscription_boxing_videos = self._collection_heading("Boxing Videos")
        self.subscription_mma_events = self._collection_heading("MMA Events")
        self.subscription_mma_videos = self._collection_heading("MMA Videos")
        self.subscription_motorsports_events = self._collection_heading("Motorsports Events")
        self.subscription_cricket_events = self._collection_heading("Cricket Events")
        self.subscription_football_events = self._collection_heading("Football Events").filter(has_not_text="American")
        self.subscription_skateboarding_events = self._collection_heading("Skateboarding Events")
        self.subscription_cycling_events = self._collection_heading("Cycling Events")
        self.subscription_athletics_events = self._collection_heading("Athletics Events")
        self.subscription_water_sports_events = self._collection_heading("Water Sports Events")
        self.subscription_basketball_events = self._collection_heading("Basketball Events")
        self.subscription_american_football_events = self._collection_heading("American Football Events")
        self.subscription_glory_events = self._collection_heading("GLORY Kickboxing")
        self.subscription_one_events = self._collection_heading("ONE on")
        self.subscription_njpw_events = self._collection_heading("NJPW on")

        # All available carousels catalog which can be added to Discover page
        self.all_locators = {
            "Featured": self.subscription_featured_section,
            "Subscripton Details": self.subscription_details_section,
            "FITE+ Top Replays": self.subscription_top_replays_section,            
            "Summer Supercard Week": self.summer_supercard_week_section,
            "Free Events": self.free_events_section,
            "Trending": self.trending_section,
            "Recently Added": self.recently_added_section,
            "FITE+ Pro Wrestling Events": self.subscription_wrestling_events,
            "FITE+ Boxing Events": self.subscription_boxing_events,
            "FITE+ Boxing Videos": self.subscription_boxing_videos,
            "FITE+ MMA Events": self.subscription_mma_events,
            "GCW: Josh Barnett's Bloodsport": self.barnetts_bloodsport,
            "FITE+ Motorsports Events": self.subscription_motorsports_events,
            "FITE+ Cricket Events": self.subscription_cricket_events,
            "FITE+ Football Events": self.subscription_football_events,
            "Football Highlights": self.football_highlights,
            "FITE+ Skateboarding Events": self.subscription_skateboarding_events,
            "Skateboarding Videos": self.skateboarding_videos,
            "FITE+ Cycling Events": self.subscription_cycling_events,
            "FITE+ Athletics Events": self.subscription_athletics_events,
            "FITE+ Water Sports Events": self.subscription_water_sports_events,
            "FITE+ Basketball Events": self.subscription_basketball_events,
            "FITE+ American Football Events": self.subscription_american_football_events,
            "GLORY Kickboxing on FITE+": self.subscription_glory_kickboxing,
            "ONE on FITE+": self.subscription_one,
            "TNA on FITE+": self.subscription_tna,
            "NJPW on FITE+": self.subscription_njpw,
            "WWE ID Wrestlers": self.wwe_id_wrestlers,
            "Jon Moxley on GCW": self.jon_moxley_gcw,
            "David Mundell - BKFC’s P4P King": self.david_mundell_bkfc,
            "Mike Perry's Greatest Hits": self.mike_perrys_hits,
            "Games of The Future": self.games_of_the_future,
            "GCW Events": self.gcw_events,
            "BKFC": self.bkfc,
            "Tennis": self.tennis_section,
            "Channels": self.subscription_channels_section,
            "Profiles": self.subscription_profiles_section,
            "Subscription Benefits": self.subscription_info_section,
       }


    def navigate(self):
        self.page.goto(self.url) 

#    def check_links_reachability(self) -> list[str]:
#        return self._check_links_reachability(self.links, self.url)

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

    def start_subscribe_monthly_flow(self):
        self.monthly_pass_button.click()     

    def fite_monthly_subscription_with_card(self) -> None:
        self.card_input.fill(settings.STRIPE_TEST_CARD)
        self.exp_date_input.fill(settings.STRIPE_EXP_DATE)
        self.cvc_input.fill(settings.STRIPE_CVC)

        self.name_input.fill(settings.STRIPE_NAME)
        self.country_input.select_option(label=settings.STRIPE_COUNTRY)
        self.address_input.fill(settings.STRIPE_ADDRESS)
        self.postal_code_input.fill(settings.STRIPE_POSTAL_CODE)
        self.city_input.fill(settings.STRIPE_CITY)

        self.pay_button.click()  
        
    def _section(self, heading: str) -> Locator:
        return self.main.locator("section").filter(
            has=self.page.get_by_role("heading", name=heading, exact=True)
            )    

    def _collection_section(self, heading_fragment: str) -> Locator:
        return self._collection_heading(heading_fragment).locator(
            "xpath=ancestor::section[1]"
        )

    def _collection_heading(self, heading_fragment: str) -> Locator:
        return self.main.locator("h2 a").filter(has_text=heading_fragment)
          