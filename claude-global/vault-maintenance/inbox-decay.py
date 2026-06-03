"""
Inbox decay sweep — weekly Sunday 21:00 CST.

Scans 06 Tasks/Inbox.md and 06 Tasks/Tasks.md (Today board) for items where:
  - checkbox is `- [ ]` (not done)
  - has `📅 YYYY-MM-DD` due date older than --threshold-days (default 14)

For each such item:
  - Append ` #stale` tag (idempotent — skips if already tagged)
  - Record in report

Output: 04 Notes/auto-reports/YYYY-MM-DD-inbox-decay.md
"""
from __future__ import annotations
import re
import sys
from datetime import date, timedelta
from pathlib import Path

VAULT = Path(r"{{VAULT_ROOT}}")
INBOX_FILES = [VAULT / "06 Tasks" / "Inbox.md", VAULT / "06 Tasks" / "Tasks.md"]
REPORT_DIR = VAULT / "04 Notes" / "auto-reports"
THRESHOLD_DAYS = 14

TASK_RE = re.compile(r"^(\s*-\s*\[ \]\s*)(.+?)(\s*📅\s*(\d{4}-\d{2}-\d{2}))(.*)$")


def process_file(path: Path, threshold: date) -> tuple[list[dict], int]:
    if not path.exists():
        return [], 0
    lines = path.read_text(encoding="utf-8").splitlines(keepends=False)
    stale_items: list[dict] = []
    modified = 0
    for i, line in enumerate(lines):
        m = TASK_RE.match(line)
        if not m:
            continue
        due = date.fromisoformat(m.group(4))
        if due >= threshold:
            continue
        if "#stale" in line:
            stale_items.append({"file": path.name, "lineno": i + 1, "due": str(due), "body": m.group(2).strip()[:100], "already_tagged": True})
            continue
        new_line = line.rstrip() + " #stale"
        lines[i] = new_line
        modified += 1
        stale_items.append({"file": path.name, "lineno": i + 1, "due": str(due), "body": m.group(2).strip()[:100], "already_tagged": False})
    if modified:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return stale_items, modified


def render_report(items: list[dict], threshold: date, today: date) -> str:
    new_tags = [i for i in items if not i["already_tagged"]]
    existing = [i for i in items if i["already_tagged"]]
    md = [
        "---",
        f"type: auto-report",
        f"report: inbox-decay",
        f"date: {today.isoformat()}",
        f"threshold-days: {THRESHOLD_DAYS}",
        f"new-stale: {len(new_tags)}",
        f"already-stale: {len(existing)}",
        "biz-eval: skip",
        "---",
        "",
        f"# Inbox Decay Report · {today.isoformat()}",
        "",
        f"Items with `📅` date before {threshold.isoformat()} (≥ {THRESHOLD_DAYS} days overdue), unchecked.",
        "",
        f"**New `#stale` tags added: {len(new_tags)}** · **Already tagged: {len(existing)}**",
        "",
    ]
    if new_tags:
        md += ["## Newly tagged #stale", ""]
        for it in new_tags:
            md.append(f"- `{it['file']}:{it['lineno']}` · 📅 {it['due']} · {it['body']}")
        md.append("")
    if existing:
        md += ["## Already tagged (consider triage or close)", ""]
        for it in existing:
            md.append(f"- `{it['file']}:{it['lineno']}` · 📅 {it['due']} · {it['body']}")
        md.append("")
    if not items:
        md.append("✅ No overdue items. Inbox is healthy.")
        md.append("")
    md += ["## Suggested action", "", "Run `/inbox-process` to triage the newly tagged items, or close them as `[x]` if no longer relevant.", ""]
    return "\n".join(md)


def main():
    today = date.today()
    threshold = today - timedelta(days=THRESHOLD_DAYS)
    all_items = []
    total_modified = 0
    for f in INBOX_FILES:
        items, modified = process_file(f, threshold)
        all_items += items
        total_modified += modified
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{today.isoformat()}-inbox-decay.md"
    report_path.write_text(render_report(all_items, threshold, today), encoding="utf-8")
    print(f"inbox-decay: tagged {total_modified} new, {len(all_items) - total_modified} already-tagged. Report: {report_path}")


if __name__ == "__main__":
    sys.exit(main())
