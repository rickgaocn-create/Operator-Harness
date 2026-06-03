"""
Weekly metabolism report — Friday 18:00 CST.

Aggregates vault health signals:
  - Tasks Kanban lane counts across {{PROJECT_A}} + {{ORG_B}} + Personal + Inbox
  - Overdue / This-Week / Soon counts
  - Done in past 7 days
  - Cards created in past 7 days (by domain)
  - Daily-note coverage past 7 days (count + total word count)

Output: 04 Notes/auto-reports/YYYY-MM-DD-metabolism.md
"""
from __future__ import annotations
import re
from datetime import date, timedelta
from pathlib import Path

VAULT = Path(r"{{VAULT_ROOT}}")
REPORT_DIR = VAULT / "04 Notes" / "auto-reports"

KANBAN_FILES = {
    "{{PROJECT_A}}": VAULT / "03 Projects" / "{{PROJECT_A}}" / "Tasks.md",
    "{{ORG_B}}": VAULT / "03 Projects" / "{{ORG_B}}" / "Tasks.md",
    "Personal": VAULT / "06 Tasks" / "Personal.md",
    "Inbox": VAULT / "06 Tasks" / "Inbox.md",
    "Today": VAULT / "06 Tasks" / "Tasks.md",
}

LANE_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TASK_RE = re.compile(r"^\s*-\s*\[(.)\]\s*(.+)$", re.MULTILINE)
DONE_DATE_RE = re.compile(r"✅\s*(\d{4}-\d{2}-\d{2})")
CREATED_FM_RE = re.compile(r"^\s*created\s*:\s*(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def count_kanban(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    # Split by lane headings
    lanes = {}
    parts = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    for i in range(1, len(parts) - 1, 2):
        name = parts[i].strip()
        body = parts[i + 1]
        tasks = TASK_RE.findall(body)
        if not tasks:
            continue
        lanes[name] = {"total": len(tasks), "open": sum(1 for c, _ in tasks if c == " "), "done": sum(1 for c, _ in tasks if c == "x")}
    return lanes


def done_in_window(path: Path, since: date) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8")
    return sum(1 for m in DONE_DATE_RE.finditer(text) if date.fromisoformat(m.group(1)) >= since)


def cards_in_window(since: date) -> dict[str, int]:
    cards_dir = VAULT / "02 Cards"
    by_domain: dict[str, int] = {}
    if not cards_dir.exists():
        return by_domain
    for card in cards_dir.rglob("*.md"):
        rel = card.relative_to(cards_dir)
        if rel.parts[0] in ("_archive", "_inbox"):
            continue
        if card.name.startswith("(C) README") or card.name == "_index.base":
            continue
        try:
            text = card.read_text(encoding="utf-8")
        except Exception:
            continue
        m = CREATED_FM_RE.search(text[:1500])
        if not m:
            continue
        try:
            created = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if created < since:
            continue
        domain = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        by_domain[domain] = by_domain.get(domain, 0) + 1
    return by_domain


def daily_note_coverage(since: date, until: date) -> dict:
    daily_dir = VAULT / "04 Notes" / "daily notes"
    if not daily_dir.exists():
        return {"days_with_note": 0, "total_words": 0, "missing": []}
    days_in_window = []
    cur = since
    while cur <= until:
        if cur.weekday() < 5:  # weekdays
            days_in_window.append(cur)
        cur += timedelta(days=1)
    days_with_note = 0
    total_words = 0
    missing = []
    for d in days_in_window:
        f = daily_dir / f"{d.isoformat()}.md"
        if not f.exists():
            missing.append(str(d))
            continue
        days_with_note += 1
        try:
            text = f.read_text(encoding="utf-8")
            total_words += len(text.split())
        except Exception:
            pass
    return {"days_with_note": days_with_note, "total_weekday_count": len(days_in_window), "total_words": total_words, "missing": missing}


def main():
    today = date.today()
    week_ago = today - timedelta(days=7)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Kanban scan
    kanban_summary = {}
    total_overdue = 0
    total_open = 0
    total_done_window = 0
    for name, path in KANBAN_FILES.items():
        lanes = count_kanban(path)
        done = done_in_window(path, week_ago)
        kanban_summary[name] = {"lanes": lanes, "done_7d": done}
        total_done_window += done
        for lname, ldata in lanes.items():
            total_open += ldata["open"]
            if "overdue" in lname.lower() or "⚠" in lname:
                total_overdue += ldata["open"]

    # Cards
    cards_7d = cards_in_window(week_ago)
    total_cards_7d = sum(cards_7d.values())

    # Daily notes
    coverage = daily_note_coverage(week_ago, today)

    # Render
    md = [
        "---",
        "type: auto-report",
        "report: weekly-metabolism",
        f"date: {today.isoformat()}",
        f"window-start: {week_ago.isoformat()}",
        f"window-end: {today.isoformat()}",
        f"total-open: {total_open}",
        f"total-overdue: {total_overdue}",
        f"total-done-7d: {total_done_window}",
        f"total-cards-spawned-7d: {total_cards_7d}",
        "biz-eval: skip",
        "---",
        "",
        f"# Weekly Metabolism · {today.isoformat()}",
        "",
        f"Window: **{week_ago.isoformat()} → {today.isoformat()}** (7 days).",
        "",
        "## Tasks Kanban Health",
        "",
        "| Surface | Open | Overdue | Done (7d) |",
        "|---|---|---|---|",
    ]
    for name, data in kanban_summary.items():
        open_sum = sum(l["open"] for l in data["lanes"].values())
        overdue = sum(l["open"] for lname, l in data["lanes"].items() if "overdue" in lname.lower() or "⚠" in lname)
        md.append(f"| {name} | {open_sum} | {overdue} | {data['done_7d']} |")
    md += [f"| **Total** | **{total_open}** | **{total_overdue}** | **{total_done_window}** |", "", "## Lane Detail", ""]
    for name, data in kanban_summary.items():
        if not data["lanes"]:
            continue
        md.append(f"### {name}")
        for lname, ldata in data["lanes"].items():
            md.append(f"- {lname}: {ldata['open']} open / {ldata['done']} done ({ldata['total']} total)")
        md.append("")
    md += ["## Cards Spawned (past 7d)", ""]
    if total_cards_7d == 0:
        md.append("⚠️ No cards spawned this week — synthesis layer is starving. Are you only doing tasks, no learning capture?")
    else:
        md.append(f"**{total_cards_7d} cards** across:")
        for domain, n in sorted(cards_7d.items(), key=lambda x: -x[1]):
            md.append(f"- `{domain}`: {n}")
    md += ["", "## Daily Note Coverage (past 7 weekdays)", ""]
    md.append(f"- Notes created: {coverage['days_with_note']} / {coverage['total_weekday_count']}")
    md.append(f"- Total words written: {coverage['total_words']}")
    if coverage["missing"]:
        md.append(f"- Missing days: {', '.join(coverage['missing'])}")
    md += ["", "## Suggested Reads", "", "- If overdue > 5 → run `/inbox-process` to triage", "- If cards spawned == 0 → review daily notes for capture-worthy synthesis, run `/source-ingest` on raw clippings", "- If daily-note coverage < 4/5 weekdays → 你这周脑子里的 context 没卸载，必然在睡前焦虑", ""]

    report_path = REPORT_DIR / f"{today.isoformat()}-metabolism.md"
    report_path.write_text("\n".join(md), encoding="utf-8")
    print(f"metabolism: {total_open} open, {total_overdue} overdue, {total_done_window} done, {total_cards_7d} cards spawned. Report: {report_path}")


if __name__ == "__main__":
    import sys
    sys.exit(main())
