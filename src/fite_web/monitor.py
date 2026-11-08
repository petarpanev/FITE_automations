from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isinf
from typing import Optional

from fite_web.config import MonitorSettings
from fite_web.models import AlertType, MonitorEvent, Severity, VideoSample


@dataclass(frozen=True)
class MonitorSummary:
    monitored_seconds: float
    buffering_seconds: float
    buffering_incidents: int
    stoppage_incidents: int
    resolution_changes: int
    min_height: Optional[int]
    buffering_ratio: float


class StreamQualityMonitor:
    def __init__(self, settings: MonitorSettings) -> None:
        self._settings = settings
        self._previous_sample: Optional[VideoSample] = None
        self._buffer_started_at: Optional[float] = None
        self._buffer_alerted = False
        self._buffer_fatal = False
        self._stoppage_started_at: Optional[float] = None
        self._stoppage_alerted = False
        self._resolution = (0, 0)
        self._resolution_candidate = (0, 0, 0)
        self._minimum_height = float("inf")
        self.monitored_seconds = 0.0
        self.buffering_seconds = 0.0
        self.buffering_incidents = 0
        self.stoppage_incidents = 0
        self.resolution_changes = 0

    def reset_sampling_baseline(self) -> None:
        self._previous_sample = None
        self._resolution = (0, 0)
        self._resolution_candidate = (0, 0, 0)

    def observe(
        self,
        sample: Optional[VideoSample],
        *,
        now: float,
        elapsed: float,
        delta_seconds: float,
    ) -> list[MonitorEvent]:
        events: list[MonitorEvent] = []

        if sample is not None and sample.ad_playing:
            self._previous_sample = None
            self._buffer_started_at = None
            self._stoppage_started_at = None
            self._resolution = (0, 0)
            self._resolution_candidate = (0, 0, 0)
            return events

        delta_seconds = max(delta_seconds, 0)
        self.monitored_seconds += delta_seconds
        buffering = (
            sample is not None
            and not sample.paused
            and not sample.ended
            and (sample.ready_state < 3 or sample.waiting)
        )

        if buffering:
            self.buffering_seconds += delta_seconds
            if self._buffer_started_at is None:
                self._buffer_started_at = now
            duration = now - self._buffer_started_at
            if duration >= self._settings.buffer_alert_seconds and not self._buffer_alerted:
                self._buffer_alerted = True
                self.buffering_incidents += 1
                events.append(
                    self._event(
                        AlertType.BUFFERING,
                        Severity.WARNING,
                        f"Buffering for {duration:.1f}s "
                        f"(readyState={sample.ready_state})",
                    )
                )
            if duration >= self._settings.buffer_fatal_seconds and not self._buffer_fatal:
                self._buffer_fatal = True
                self.stoppage_incidents += 1
                events.append(
                    self._event(
                        AlertType.STOPPAGE,
                        Severity.CRITICAL,
                        f"Stream stuck buffering for {duration:.0f}s",
                    )
                )
        elif self._buffer_started_at is not None:
            self._buffer_started_at = None
            self._buffer_alerted = False
            self._buffer_fatal = False

        stoppage_reason = self._stoppage_reason(sample, buffering)
        if stoppage_reason:
            if self._stoppage_started_at is None:
                self._stoppage_started_at = now
            duration = now - self._stoppage_started_at
            if (
                duration >= self._settings.stoppage_alert_seconds
                and not self._stoppage_alerted
            ):
                self._stoppage_alerted = True
                self.stoppage_incidents += 1
                events.append(
                    self._event(
                        AlertType.STOPPAGE,
                        Severity.CRITICAL,
                        f"Playback stopped for {duration:.1f}s: {stoppage_reason}",
                    )
                )
        elif self._stoppage_started_at is not None:
            self._stoppage_started_at = None
            self._stoppage_alerted = False

        if sample is not None and sample.width > 0:
            if elapsed < self._settings.warmup_seconds or self._resolution[1] == 0:
                self._resolution = (sample.width, sample.height)
            elif (sample.width, sample.height) != self._resolution:
                candidate_width, candidate_height, count = self._resolution_candidate
                if (candidate_width, candidate_height) == (sample.width, sample.height):
                    count += 1
                else:
                    count = 1
                self._resolution_candidate = (sample.width, sample.height, count)
                if count >= 2:
                    downgrade = sample.height < self._resolution[1]
                    direction = "DOWNGRADE" if downgrade else "upgrade"
                    severity = Severity.WARNING if downgrade else Severity.INFO
                    self.resolution_changes += 1
                    events.append(
                        self._event(
                            AlertType.RESOLUTION,
                            severity,
                            f"Resolution {direction}: "
                            f"{self._resolution[0]}x{self._resolution[1]} -> "
                            f"{sample.width}x{sample.height}",
                        )
                    )
                    self._resolution = (sample.width, sample.height)
                    self._resolution_candidate = (0, 0, 0)
            else:
                self._resolution_candidate = (0, 0, 0)

            if elapsed >= self._settings.warmup_seconds:
                self._minimum_height = min(self._minimum_height, sample.height)

        self._previous_sample = sample
        return events

    def summary(self) -> MonitorSummary:
        ratio = (
            self.buffering_seconds / self.monitored_seconds
            if self.monitored_seconds > 0
            else 0.0
        )
        min_height = None if isinf(self._minimum_height) else int(self._minimum_height)
        return MonitorSummary(
            monitored_seconds=self.monitored_seconds,
            buffering_seconds=self.buffering_seconds,
            buffering_incidents=self.buffering_incidents,
            stoppage_incidents=self.stoppage_incidents,
            resolution_changes=self.resolution_changes,
            min_height=min_height,
            buffering_ratio=ratio,
        )

    def _stoppage_reason(self, sample: Optional[VideoSample], buffering: bool) -> str:
        if sample is None:
            return "player element missing"
        if sample.error_code:
            return f"media error code {sample.error_code}"
        if sample.ended:
            return "stream ended"
        if sample.paused:
            return "playback paused"
        if (
            self._previous_sample is not None
            and not buffering
            and sample.current_time - self._previous_sample.current_time < 0.2
        ):
            return "playhead not advancing"
        return ""

    @staticmethod
    def _event(event_type: AlertType, severity: Severity, message: str) -> MonitorEvent:
        timestamp = datetime.now(timezone.utc).isoformat()
        return MonitorEvent(event_type, severity, message, timestamp)
