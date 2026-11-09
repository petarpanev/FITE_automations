from __future__ import annotations

import os
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    BASE_URL: str
    ENVIRONMENT: str = "development"
    BRAND_TERMS: str
    NEW_BRAND_TERMS: str
    DISCOVER_CAROUSELS: str = "Featured,Top Replays,AEW PPV Archive Packs,Pay Per Views,Free Events,Football,Subscriptions,Channels,Interests,News,Profiles,How to Watch,Discover FITE"
    DISCOVER_CAROUSELS_SUBSCRIBER: str = "Featured,My FITE+,Top Replays,AEW PPV Archive Packs,AEW PPVs,AEW Plus,Pay Per Views,Free Events,Football,Tennis,Motorsports,Subscriptions,Channels,Interests,News,Profiles,How to Watch"
    FITE_SUBS_CAROUSELS: str = "Featured,Join FITE+,FITE+ Top Replays,Channels,Summer Supercard Week,Recently Added,FITE+ Pro Wrestling Events,FITE+ Boxing Events,FITE+ Boxing Videos,FITE+ MMA Events,GCW: Josh Barnett's Bloodsport,FITE+ Motorsport Events,FITE+ Cricket Events,FITE+ Football Events,Football Highlights,FITE+ Skateboarding Events,Skateboarding Videos,FITE+ Cycling Events,FITE+ Athletics Events,FITE+ Water Sports Events,FITE+ Basketball Events,FITE+ American Football Events,GLORY Kickboxing on FITE+,ONE on FITE+,TNA on FITE+,NJPW on FITE+,WWE ID Wrestlers,Jon Moxley on GCW,David Mundell - BKFC’s P4P King,Mike Perry's Greatest Hits"
    FITE_SUBS_CAROUSELS_SUBSCRIBER: str = "Featured,FITE+ Top Replays,Channels,Summer Supercard Week,Recently Added,FITE+ Pro Wrestling Events,FITE+ Boxing Events,FITE+ Boxing Videos,FITE+ MMA Events,GCW: Josh Barnett's Bloodsport,FITE+ Motorsport Events,FITE+ Cricket Events,FITE+ Football Events,Football Highlights,FITE+ Skateboarding Events,Skateboarding Videos,FITE+ Cycling Events,FITE+ Athletics Events,FITE+ Water Sports Events,FITE+ Basketball Events,FITE+ American Football Events,GLORY Kickboxing on FITE+,ONE on FITE+,TNA on FITE+,NJPW on FITE+,WWE ID Wrestlers,Jon Moxley on GCW,David Mundell - BKFC’s P4P King,Mike Perry's Greatest Hits"

    TEST_USER: str
    TEST_PASSWORD: str

    NEW_TEST_NAME: str = "test user"
    NEW_TEST_EMAIL: str
    NEW_TEST_PASSWORD: str

    STRIPE_TEST_CARD: str
    STRIPE_EXP_DATE: str
    STRIPE_CVC: str
    STRIPE_NAME: str
    STRIPE_COUNTRY: str
    STRIPE_ADDRESS: str
    STRIPE_POSTAL_CODE: str
    STRIPE_CITY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def brand_terms(self) -> tuple[str, ...]:
        terms = tuple(term.strip() for term in self.BRAND_TERMS.split(",") if term.strip())
        if not terms:
            raise ValueError("BRAND_TERMS must contain at least one comma-separated term")
        return terms

    @property
    def new_brand_terms(self) -> tuple[str, ...]:
        terms = tuple(
            term.strip() for term in self.NEW_BRAND_TERMS.split(",") if term.strip()
        )
        if not terms:
            raise ValueError("NEW_BRAND_TERMS must contain at least one comma-separated term")
        return terms

    @property
    def discover_carousels(self) -> tuple[str, ...]:
        carousels = tuple(
            title.strip()
            for title in self.DISCOVER_CAROUSELS.split(",")
            if title.strip()
        )
        if not carousels:
            raise ValueError(
                "DISCOVER_CAROUSELS must contain at least one comma-separated title"
            )
        return carousels

settings = Settings()

def _number(name: str, default: str, minimum: float) -> float:
    raw_value = os.getenv(name, default)
    try:
        value = float(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} must be a number, got {raw_value!r}") from error
    if not isfinite(value):
        raise ValueError(f"{name} must be finite, got {raw_value!r}")
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}")
    return value


def _optional_bool(name: str, default: Optional[bool] = None) -> Optional[bool]:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"{name} must be true or false, got {raw_value!r}")


def _bool(name: str, default: str) -> bool:
    raw_value = os.getenv(name, default)
    normalized = raw_value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"{name} must be true or false, got {raw_value!r}")

@dataclass(frozen=True)
class MonitorSettings:
    video_url: str
    monitor_minutes: float
    min_height: int
    max_buffer_ratio: float
    buffer_alert_seconds: float
    buffer_fatal_seconds: float
    stoppage_alert_seconds: float
    warmup_seconds: float
    rendition_dwell_seconds: float
    alert_cooldown_seconds: float
    simulate_outage: bool
    headless: Optional[bool]
    smtp_user: Optional[str]
    smtp_app_password: Optional[str]
    alert_to: Optional[str]
    report_dir: Path

    @classmethod
    def from_env(cls) -> MonitorSettings:
        video_url = os.getenv(
            "VIDEO_URL",
            f"{settings.BASE_URL}/watch/atp-tennistv-classics-free-channel/2phhm/",
        ).strip()
        if not video_url:
            raise ValueError("VIDEO_URL must not be empty")

        min_height_value = _number("MIN_HEIGHT", "240", 1)
        if not min_height_value.is_integer():
            raise ValueError("MIN_HEIGHT must be a whole number")

        max_buffer_ratio = _number("MAX_BUFFER_RATIO", "0.05", 0)
        if max_buffer_ratio > 1:
            raise ValueError("MAX_BUFFER_RATIO must be <= 1")
        smtp_user = os.getenv("SMTP_USER") or None
        smtp_app_password = os.getenv("SMTP_APP_PASSWORD") or None
        if bool(smtp_user) != bool(smtp_app_password):
            raise ValueError("SMTP_USER and SMTP_APP_PASSWORD must be configured together")
        alert_to = os.getenv("ALERT_TO") or None
        if smtp_user and not alert_to:
            raise ValueError("ALERT_TO is required when SMTP is configured")
        return cls(
            video_url=video_url,
            monitor_minutes=_number("MONITOR_MINUTES", "15", 0.01),
            min_height=int(min_height_value),
            max_buffer_ratio=max_buffer_ratio,
            buffer_alert_seconds=2,
            buffer_fatal_seconds=15,
            stoppage_alert_seconds=5,
            warmup_seconds=10,
            rendition_dwell_seconds=30,
            alert_cooldown_seconds=60,
            simulate_outage=_bool("SIMULATE_OUTAGE", "false"),
            headless=_optional_bool("HEADLESS", default=False),
            smtp_user=smtp_user,
            smtp_app_password=smtp_app_password,
            alert_to=alert_to,
            report_dir=PROJECT_ROOT / "reports",
        )
