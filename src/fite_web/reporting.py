from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fite_web.monitor import MonitorSummary


class StreamReportWriter:
    def __init__(self, report_dir: Path) -> None:
        self._report_dir = report_dir

    def write(
        self,
        *,
        title: str,
        passed: bool,
        summary: Optional[MonitorSummary],
        events: list[dict[str, Any]],
        available_renditions: list[str],
        rendition_selections: int,
        auto_selected: bool,
        error: Optional[str] = None,
    ) -> tuple[Path, Path]:
        self._report_dir.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(timezone.utc)
        timestamp = created_at.strftime("%Y-%m-%dT%H-%M-%S-%fZ")
        report_path = self._report_dir / f"live-stream-summary-{timestamp}.md"
        events_path = self._report_dir / f"events-{timestamp}.json"

        events_path.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
        lines = [
            "# Live Stream Monitor Summary",
            "",
            f"- Created: {created_at.isoformat()}",
            f"- Result: {'PASS' if passed else 'FAIL'}",
            f"- Test: {title}",
        ]
        if summary is None:
            lines.extend(
                [
                    "- Metrics: unavailable; execution ended before monitoring completed.",
                ]
            )
        else:
            min_height = "n/a" if summary.min_height is None else f"{summary.min_height}p"
            lines.extend(
                [
                    f"- Monitored: {summary.monitored_seconds:.0f} seconds",
                    f"- Buffering: {summary.buffering_seconds:.0f} seconds "
                    f"({summary.buffering_ratio * 100:.2f}%), "
                    f"{summary.buffering_incidents} incidents",
                    f"- Stoppages: {summary.stoppage_incidents}",
                    f"- Resolution changes: {summary.resolution_changes}",
                    f"- Minimum resolution height: {min_height}",
                    f"- Rendition selections: {rendition_selections}",
                    f"- Available renditions: {', '.join(available_renditions)}",
                    f"- Auto selected for remaining monitoring: {auto_selected}",
                ]
            )
        if error:
            lines.append(f"- Error: {error.splitlines()[0]}")
        lines.extend(["", f"- Events: `{events_path.name}`", ""])
        report_path.write_text("\n".join(lines), encoding="utf-8")
        return report_path, events_path
