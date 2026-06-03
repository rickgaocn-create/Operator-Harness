#!/usr/bin/env python3
"""
Pre-trip auto-prep — daily 18:00 check; alert if any trip bundle has trip-date within next 24h.

Scans 03 Projects/<project>/03 行程计划/(C) 差旅*.md frontmatter for `trip-date:` field.
If trip starts tomorrow → alert with link to bundle + checklist reminder.

Mode: notification-only.
Max alerts per day: 2.
"""
from __future__ import annotations

import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT, log_event, notify_feishu, under_run_cap

ROUTINE = "pre-trip"
MAX_ALERTS_PER_DAY = 2

PROJECTS_ROOT = VAULT / "03 Projects"


def extract_trip_dates(frontmatter: str) -> list[str]:
    """Pull all YYYY-MM-DD dates from the trip-date field (may be list or string)."""
    m = re.search(r"^trip-date:\s*(.*)$", frontmatter, re.MULTILINE)
    if not m:
        return []
    value = m.group(1)
    # Catch ISO dates anywhere in the value (handles "2026-05-22" or "[2026-05-22, 2026-05-23]")
    return re.findall(r"\d{4}-\d{2}-\d{2}", value)


def find_trip_bundles() -> list[Path]:
    bundles: list[Path] = []
    if not PROJECTS_ROOT.exists():
        return bundles
    for trip_dir in PROJECTS_ROOT.glob("*/03 行程计划"):
        for f in trip_dir.glob("(C) 差旅*.md"):
            bundles.append(f)
        for f in trip_dir.glob("差旅*.md"):
            bundles.append(f)
    return bundles


def main() -> int:
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    matched: list[tuple[Path, list[str]]] = []

    for bundle in find_trip_bundles():
        try:
            text = bundle.read_text(encoding="utf-8", errors="replace")
            if not text.startswith("---"):
                continue
            fm_end = text.find("---", 3)
            if fm_end < 0:
                continue
            frontmatter = text[3:fm_end]
            dates = extract_trip_dates(frontmatter)
            if tomorrow in dates:
                matched.append((bundle, dates))
        except Exception as e:
            log_event(ROUTINE, "error", f"failed reading {bundle.name}: {e}")

    log_event(
        ROUTINE, "info",
        f"checked {len(find_trip_bundles())} bundles, {len(matched)} match tomorrow",
        tomorrow=tomorrow,
    )

    if not matched:
        return 0

    if not under_run_cap(ROUTINE, MAX_ALERTS_PER_DAY):
        log_event(ROUTINE, "info", f"alert skipped — daily cap")
        return 0

    for bundle, dates in matched:
        rel = bundle.relative_to(VAULT).as_posix()
        msg = (
            f"✈️ Trip tomorrow ({tomorrow}): {bundle.stem}\n"
            f"Bundle: {rel}\n"
            f"Pre-flight checklist reminder: § 3 飞前节点 + § 4 会前确认稿"
        )
        notify_feishu(ROUTINE, msg)
        log_event(ROUTINE, "alert", f"trip alert: {bundle.stem}", bundle=rel)

    return 0


if __name__ == "__main__":
    sys.exit(main())
