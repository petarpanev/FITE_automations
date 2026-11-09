from playwright.sync_api import Locator, expect

from fite_web.watch_page import WatchPage


def _expect_each_visible(locator: Locator, description: str) -> None:
    count = locator.count()
    assert count > 0, f"No {description} were found"
    for index in range(count):
        expect(
            locator.nth(index),
            f"{description.capitalize()} locator at index {index} was not visible",
        ).to_be_visible()


def test_ui_watch_page_content_visibility(page):
    watch_page = WatchPage(page)
    watch_page.navigate()
    watch_page.cookie_consent_accept()

    expect(watch_page.content).to_be_visible()
    expect(watch_page.event_title).to_be_visible()
    expect(watch_page.event_date).to_have_text("Dec 14, 2025")
    expect(watch_page.sign_up_button).to_be_visible()
    expect(watch_page.buy_button).to_be_visible()
    expect(watch_page.event_poster_image).to_have_count(1)
    expect(watch_page.event_description).to_be_visible()
    expect(watch_page.more_details_button).to_be_visible()
    expect(watch_page.follow_button).to_be_visible()
    expect(watch_page.fighter_stats_section).to_be_visible()
    expect(watch_page.fighter_images).to_have_count(12)
    expect(watch_page.fight_card_heading).to_be_visible()
    expect(watch_page.watch_more_heading).to_be_visible()
    expect(watch_page.newest_event_heading).to_be_visible()
    expect(watch_page.news_heading).to_be_visible()
    expect(watch_page.discover_heading).to_be_visible()
    expect(watch_page.more_from_channel_heading).to_be_visible()

    _expect_each_visible(
        watch_page.visible_images,
        "content image",
    )
    _expect_each_visible(
        watch_page.visible_buttons,
        "content button",
    )
    _expect_each_visible(watch_page.visible_strings, "content string")


def test_ui_watch_page_links_are_reachable(page):
    watch_page = WatchPage(page)
    watch_page.navigate()
    expect(watch_page.content).to_be_visible()

    unreachable_links = watch_page.check_links_reachability()
    assert not unreachable_links, "Unreachable page links:\n" + "\n".join(
        unreachable_links
    )