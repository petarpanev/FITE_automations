from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AlertType(str, Enum):
    BUFFERING = "BUFFERING"
    STOPPAGE = "STOPPAGE"
    RESOLUTION = "RESOLUTION"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class VideoSample:
    current_time: float
    ready_state: int
    paused: bool
    ended: bool
    error_code: int
    width: int
    height: int
    waiting: bool
    ad_playing: bool


@dataclass(frozen=True)
class MonitorEvent:
    event_type: AlertType
    severity: Severity
    message: str
    timestamp: str

    def as_dict(self) -> dict[str, str]:
        return {
            "time": self.timestamp,
            "type": self.event_type.value,
            "severity": self.severity.value,
            "message": self.message,
        }
