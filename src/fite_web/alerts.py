from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Optional

from fite_web.config import MonitorSettings
from fite_web.models import MonitorEvent, Severity

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, settings: MonitorSettings) -> None:
        self._settings = settings

    def send_alert(
        self,
        event: MonitorEvent,
        video_url: str,
        screenshot_path: Optional[Path] = None,
    ) -> None:
        if not self._is_configured():
            logger.warning("SMTP is not configured; alert not emailed: %s", event.message)
            return
        if event.severity == Severity.INFO:
            return

        message = EmailMessage()
        message["From"] = self._settings.smtp_user
        message["To"] = self._settings.alert_to
        message["Subject"] = (
            f"[STREAM ALERT] {event.event_type.value} ({event.severity.value}) "
            f"- Tennis TV 24/7 - {event.timestamp}"
        )
        message.set_content(
            f"{event.message}\n\nTime: {event.timestamp}\nURL: {video_url}"
        )
        if screenshot_path is not None and screenshot_path.is_file():
            message.add_attachment(
                screenshot_path.read_bytes(),
                maintype="image",
                subtype="png",
                filename=screenshot_path.name,
            )

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
                smtp.login(self._settings.smtp_user, self._settings.smtp_app_password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException):
            logger.exception("Failed to send %s alert email", event.event_type.value)

    def send_summary(self, subject: str, body: str) -> None:
        if not self._is_configured():
            return

        message = EmailMessage()
        message["From"] = self._settings.smtp_user
        message["To"] = self._settings.alert_to
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
                smtp.login(self._settings.smtp_user, self._settings.smtp_app_password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException):
            logger.exception("Failed to send stream monitor summary email")

    def _is_configured(self) -> bool:
        return bool(
            self._settings.smtp_user
            and self._settings.smtp_app_password
            and self._settings.alert_to
        )
