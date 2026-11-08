from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from fite_web.player_page import LivePlayerPage


class PlaybackFlow:
    def __init__(self, page: Page, player: LivePlayerPage) -> None:
        self._page = page
        self._player = player

    def start_live_stream(self, url: str) -> None:
        self._page.goto(url, wait_until="domcontentloaded")
        self._accept_consent_if_present()
        self._page.get_by_role("button", name="Watch Live").first.click()
        self._page.wait_for_function(
            """() => {
                const video = document.querySelector('video#player_html5_api');
                const player = document.querySelector('.video-js');
                return !!video
                    && !player?.classList.contains('vjs-ad-playing')
                    && !player?.classList.contains('vjs-ad-loading')
                    && video.readyState >= 3
                    && !video.paused
                    && video.currentTime > 0;
            }""",
            timeout=120_000,
        )

    def _accept_consent_if_present(self) -> None:
        accept_all = self._page.locator('[data-cky-tag="accept-button"]')
        try:
            accept_all.wait_for(state="visible", timeout=5_000)
        except PlaywrightTimeoutError:
            return
        accept_all.click()
        accept_all.wait_for(state="hidden", timeout=5_000)
