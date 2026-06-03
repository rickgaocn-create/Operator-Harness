#!/usr/bin/env python3
"""
Inbox drift detector — hourly check; alert if 06 Tasks/Inbox.md has > N open items.

Default threshold: 20 open `- [ ]` lines (excluding section headers / done items).
Max alerts per day: 3 (avoid spam).
Mode: notification-only (DRY_RUN=1 default) — never writes to vault content.

Schedule: every hour via Windows Task Scheduler (see _setup.ps1).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT, log_event, notify_feishu, under_run_cap

ROUTINE = "inbox-drift"
THRESHOLD = 20
MAX_ALERTS_PER_DAY = 3
INBOX = VAULT / "06 Tasks" / "Inbox.md"


def count_open_items(path: Path) -> int:
    if not path.exists():
        return -1
    text = path.read_text(encoding="utf-8", errors="replace")
    # Match top-level open task lines (- [ ] at line start, optionally indented)
    return len(re.findall(r"^\s*- \[ \]", text, re.MULTILINE))


def main() -> int:
    open_count = count_open_items(INBOX)
    if open_count < 0:
        log_event(ROUTINE, "error", f"Inbox missing: {INBOX}")
        return 1

    log_event(ROUTINE, "info", f"open_count={open_count} threshold={THRESHOLD}", open_count=open_count)

    if open_count <= THRESHOLD:
        return 0

    if not under_run_cap(ROUTINE, MAX_ALERTS_PER_DAY):
        log_event(ROUTINE, "info", f"alert skipped — daily cap hit (>{MAX_ALERTS_PER_DAY} alerts today)")
        return 0

    notify_feishu(
        ROUTINE,
        f"📥 Inbox drift: 06 Tasks/Inbox.md has {open_count} open items (threshold {THRESHOLD}). Run /inbox-process.",
    )
    log_event(ROUTINE, "alert", f"Inbox at {open_count} — alert sent", open_count=open_count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
