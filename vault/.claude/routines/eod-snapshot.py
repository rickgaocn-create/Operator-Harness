#!/usr/bin/env python3
"""
EOD auto-snapshot — daily 23:30; freeze Operon embed query results into snapshot HTML
comments at the bottom of today's daily note.

This makes historical dailies point-in-time accurate even though the embed code-blocks
re-render live. Without this freeze, opening a 3-week-old daily would show TODAY's
embed results (wrong) instead of what was actually completed that day.

Mode: notification-only by default (DRY_RUN=1). To actually write snapshots, run with
DRY_RUN=0 explicitly. Recommended: 7-day dry-run period before promoting to write mode.

Schedule: daily 23:30 via Windows Task Scheduler.
Max snapshots per day: 1 (idempotent — same-day re-run overwrites with current state).
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT, is_dry_run, log_event, notify_feishu

ROUTINE = "eod-snapshot"
TODAY_ISO = date.today().isoformat()
DAILY_NOTE = VAULT / "04 Notes" / "daily notes" / f"{TODAY_ISO}.md"
OPERON_INDEX = VAULT / ".operon" / "index.json"


def query_operon_for_snapshot() -> dict[str, list[str]]:
    """Read Operon index, compute the 3 filter buckets used in EOD embeds.

    Returns: {filter_name: [task_descriptions]}
    """
    if not OPERON_INDEX.exists():
        return {}
    try:
        data = json.loads(OPERON_INDEX.read_text(encoding="utf-8"))
    except Exception as e:
        log_event(ROUTINE, "error", f"Operon index unreadable: {e}")
        return {}
    tasks = data.get("tasks", {})
    shipped: list[str] = []
    slipped: list[str] = []
    carry: list[str] = []
    tomorrow_iso = date.fromtimestamp(
        datetime.now().timestamp() + 86400
    ).isoformat()
    for tid, t in tasks.items() if isinstance(tasks, dict) else []:
        fv = t.get("fieldValues", {}) if isinstance(t, dict) else {}
        desc = (t.get("description") or "")[:120]
        if fv.get("dateCompleted") == TODAY_ISO:
            shipped.append(f"{tid}: {desc}")
        due = fv.get("dateDue", "")
        checkbox = t.get("checkbox", "")
        is_open = checkbox not in ("done", "cancelled")
        if is_open and due and due < TODAY_ISO:
            slipped.append(f"{tid}: {desc} (due {due})")
        if is_open and due == tomorrow_iso:
            carry.append(f"{tid}: {desc}")
    return {
        "shipped": shipped[:50],
        "slipped": slipped[:50],
        "carry": carry[:50],
    }


def freeze_snapshot(daily_path: Path, buckets: dict[str, list[str]]) -> bool:
    """Replace the 3 snapshot-comment lines at bottom of daily note with fresh data."""
    if not daily_path.exists():
        log_event(ROUTINE, "info", f"daily note missing — skip ({daily_path.name})")
        return False
    text = daily_path.read_text(encoding="utf-8", errors="replace")

    snapshots = {
        "shipped": f"<!-- snapshot-shipped: ts={datetime.now().isoformat(timespec='seconds')} count={len(buckets.get('shipped', []))} -->\n"
                   + "\n".join(f"<!--   - {x} -->" for x in buckets.get("shipped", [])),
        "slipped": f"<!-- snapshot-slipped: ts={datetime.now().isoformat(timespec='seconds')} count={len(buckets.get('slipped', []))} -->\n"
                   + "\n".join(f"<!--   - {x} -->" for x in buckets.get("slipped", [])),
        "carry":   f"<!-- snapshot-carry: ts={datetime.now().isoformat(timespec='seconds')} count={len(buckets.get('carry', []))} -->\n"
                   + "\n".join(f"<!--   - {x} -->" for x in buckets.get("carry", [])),
    }

    out = text
    for kind in ("shipped", "slipped", "carry"):
        pattern = rf"<!-- snapshot-{kind}:.*?-->(\n<!--   - .*? -->)*"
        replacement = snapshots[kind]
        out, n = re.subn(pattern, replacement, out, flags=re.DOTALL)
        if n == 0:
            log_event(ROUTINE, "info", f"no {kind} snapshot anchor in daily — skipping that bucket")

    if is_dry_run():
        diff_size = len(out) - len(text)
        log_event(ROUTINE, "info", f"[DRY] would write {diff_size:+d} bytes to {daily_path.name}")
        return True

    daily_path.write_text(out, encoding="utf-8")
    log_event(
        ROUTINE, "info",
        f"snapshot written: shipped={len(buckets.get('shipped', []))} slipped={len(buckets.get('slipped', []))} carry={len(buckets.get('carry', []))}",
    )
    return True


def main() -> int:
    buckets = query_operon_for_snapshot()
    if not buckets:
        log_event(ROUTINE, "error", "operon index unavailable — abort")
        return 1

    ok = freeze_snapshot(DAILY_NOTE, buckets)
    if ok and not is_dry_run():
        notify_feishu(
            ROUTINE,
            f"📸 EOD snapshot saved: shipped={len(buckets.get('shipped', []))}, "
            f"slipped={len(buckets.get('slipped', []))}, carry={len(buckets.get('carry', []))}",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
