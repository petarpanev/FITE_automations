from __future__ import annotations

import re
from typing import Optional

from playwright.sync_api import Page, expect

from fite_web.models import VideoSample

_RENDITION_PATTERN = re.compile(r"^(\d{3,4})p(?:\s+\((\d+)\s+kbps\))?$", re.IGNORECASE)


class LivePlayerPage:
    def __init__(self, page: Page) -> None:
        self._page = page
        self._quality_button = page.locator(".vjs-quality-menu-button")
        self._quality_menu = self._quality_button.locator("xpath=..")

    def available_renditions(self) -> list[str]:
        self._open_quality_menu()
        labels = [
            label.strip()
            for label in self._quality_menu.locator(".vjs-menu-item-text").all_text_contents()
        ]
        self._quality_button.click()

        if "Auto" not in labels:
            raise AssertionError(f"Expected Auto quality option; found {labels!r}")

        renditions = [label for label in labels if _RENDITION_PATTERN.fullmatch(label)]
        renditions.sort(key=self._rendition_sort_key)
        if not renditions:
            raise AssertionError("Expected at least one fixed quality rendition")
        return renditions

    def select_rendition(self, rendition: str) -> None:
        self._open_quality_menu()
        self._quality_menu.get_by_text(rendition, exact=True).click()
        self._quality_button.click()
        expect(
            self._quality_menu.locator(".vjs-menu-item.vjs-selected").get_by_text(
                rendition,
                exact=True,
            )
        ).to_be_visible()
        self._quality_button.click()
        self._focus_page_at_top()

    def select_auto(self) -> None:
        self._open_quality_menu()
        self._quality_menu.get_by_text("Auto", exact=True).click()
        self._quality_button.click()
        expect(
            self._quality_menu.locator(".vjs-menu-item.vjs-selected").get_by_text(
                "Auto",
                exact=True,
            )
        ).to_be_visible()
        self._quality_button.click()
        self._focus_page_at_top()

    def return_to_live_edge(self) -> None:
        live_button = self._page.locator(".vjs-seek-to-live-control")
        at_live_edge = live_button.evaluate(
            "button => button.classList.contains('vjs-at-live-edge')"
        )
        if not at_live_edge:
            live_button.click()
            # The player exposes "currently behind live" in the button title; wait for
            # that user-facing status to change instead of relying on a version-specific class.
            self._page.wait_for_function(
                """() => {
                    const button = document.querySelector('.vjs-seek-to-live-control');
                    if (!button) return false;
                    if (button.classList.contains('vjs-at-live-edge')) return true;
                    const title = button.getAttribute('title');
                    return !!title && !title.toLowerCase().includes('behind live');
                }""",
                timeout=10_000,
            )
        
    def sample(self) -> Optional[VideoSample]:
        values = self._page.evaluate(
            """() => {
                const video = document.querySelector('video#player_html5_api');
                const player = document.querySelector('.video-js');
                if (!video) return null;
                return {
                    ct: video.currentTime,
                    rs: video.readyState,
                    paused: video.paused,
                    ended: video.ended,
                    err: video.error?.code ?? 0,
                    w: video.videoWidth,
                    h: video.videoHeight,
                    waiting: !!player?.classList.contains('vjs-waiting'),
                    ad: !!player && (
                        player.classList.contains('vjs-ad-playing')
                        || player.classList.contains('vjs-ad-loading')
                    ),
                };
            }"""
        )
        if values is None:
            return None
        return VideoSample(
            current_time=float(values["ct"]),
            ready_state=int(values["rs"]),
            paused=bool(values["paused"]),
            ended=bool(values["ended"]),
            error_code=int(values["err"]),
            width=int(values["w"]),
            height=int(values["h"]),
            waiting=bool(values["waiting"]),
            ad_playing=bool(values["ad"]),
        )

    def screenshot(self, path: str) -> None:
        self._page.screenshot(path=path)

    def _open_quality_menu(self) -> None:
        # Video.js hides its controls until the pointer returns to the player;
        # hovering first prevents the video surface from intercepting the click.
        self._page.bring_to_front()
        self._page.locator(".video-js").hover()
        self._quality_button.wait_for(state="visible")
        self._quality_button.click()

    def _focus_page_at_top(self) -> None:
        # Keep a headed run visible to the user and restore the page's top scroll position.
        self._page.bring_to_front()
        self._page.evaluate("window.scrollTo(0, 0)")

    @staticmethod
    def _rendition_sort_key(label: str) -> tuple[int, int]:
        match = _RENDITION_PATTERN.fullmatch(label)
        if match is None:
            raise ValueError(f"Unsupported rendition label: {label!r}")
        return int(match.group(1)), int(match.group(2) or 0)
