from playwright.sync_api import Locator, expect

from fite_web.fighter_page import FighterPage


def _expect_each_visible(locator: Locator, description: str) -> None:
    count = locator.count()
    assert count > 0, f"No {description} were found"
    for index in range(count):
        expect(
            locator.nth(index),
            f"{description.capitalize()} locator at index {index} was not visible",
        ).to_be_visible()


def test_ui_fighter_page_content_visibility(page):
    fighter_page = FighterPage(page)
    fighter_page.navigate()

    expect(fighter_page.content).to_be_visible()
    expect(fighter_page.fighter_name).to_be_visible()
    expect(fighter_page.fighter_nickname).to_be_visible()
    expect(fighter_page.follow_button).to_be_visible()
    expect(fighter_page.events_heading).to_be_visible()
    expect(fighter_page.matches_heading).to_be_visible()
    expect(fighter_page.profiles_heading).to_be_visible()
    expect(fighter_page.news_heading).to_be_visible()
    expect(fighter_page.discover_section).to_be_visible()
    expect(fighter_page.discover_heading).to_be_visible()

    _expect_each_visible(fighter_page.visible_images, "content image")
    _expect_each_visible(fighter_page.visible_buttons, "content button")
    _expect_each_visible(fighter_page.visible_strings, "content string")


def test_ui_fighter_page_links_are_reachable(page):
    fighter_page = FighterPage(page)
    fighter_page.navigate()
    expect(fighter_page.content).to_be_visible()

    unreachable_links = fighter_page.check_links_reachability()
    assert not unreachable_links, "Unreachable page links:\n" + "\n".join(
        unreachable_links
    )