"""Idempotent daily-note creator for scheduled invocation.

Creates 04 Notes/daily notes/{YYYY-MM-DD}.md from the daily-note skill's canonical
template if missing. Safe to run multiple times per day — never overwrites.

Intended use: Windows Task Scheduler weekday 09:00 trigger (RG-daily-note-create).
"""

from __future__ import annotations

import datetime as dt
import io
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VAULT = Path(r"{{VAULT_ROOT}}")
DAILY_DIR = VAULT / "04 Notes" / "daily notes"
WEEKLY_DIR = VAULT / "04 Notes" / "weekly"

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def quarter_of(month: int) -> int:
    return (month - 1) // 3 + 1


def iso_week(today: dt.date) -> tuple[int, int]:
    iso_year, iso_w, _ = today.isocalendar()
    return iso_year, iso_w


def build_template(today: dt.date) -> str:
    weekday_idx = today.weekday()  # Mon=0..Sun=6
    weekday_name = WEEKDAYS[weekday_idx]
    iso_year, week_n = iso_week(today)
    quarter = quarter_of(today.month)
    day_of_week = weekday_idx + 1  # ISO day 1-7

    parent = f"{iso_year}-W{week_n:02d}"
    quarter_tag = f"{today.year}/Q{quarter}/W{week_n:02d}"
    quarter_link = f"{today.year}-Q{quarter}"

    return f"""---
type: daily
date: {today.isoformat()}
weekday: {weekday_name}
iso-week: W{week_n:02d}
quarter: {today.year}-Q{quarter}
parent: "[[{parent}]]"
status: active
day-mode:
tags:
  - daily-note
  - {quarter_tag}
projects-touched: []
people-touched: []
cards-spawned: []
actions-touched: []
---

> **Cascade:** [[GOALS.md]] → [[{quarter_link}]] → [[{parent}]] → **{today.isoformat()} {weekday_name} · Day {day_of_week}/7**

# {today.isoformat()} · {weekday_name}

## Top 3 Priorities

- [ ]
- [ ]
- [ ]

---

## Day Planner
%% Day Planner (OG) reads this section · syntax: `- [ ] HH:mm task` (24h, NO brackets) · `BREAK` and `END` are keywords %%

- [ ] 09:00 Review 今日 daily note + Top 3
- [ ] 11:30 BREAK
- [ ] 14:00
- [ ] 16:00 BREAK
- [ ] 18:00 END

---

## Meetings & Conversations
%% 时间倒序 · HH:MM · 渠道 · 对方 ([[wiki]]) · outcome %%

---

## Active Tracks

### {{PROJECT_A}}— `03 Projects/{{PROJECT_A}}/`
- **Today:**

### {{ORG_B}} — `03 Projects/{{ORG_B}}/`
- **Today:**

### AIX — Track 3 ({{ORG_B}} parallel)
- **Today:**

> 本周 Big Rocks 见 [[{parent}]] — daily 不复述

---

## Quick Capture
%% 散记 — /inbox-process 或 /source-ingest 在日终处理 %%

-

---

## Ingests
%% /source-ingest 自动 append — [HH:MM] source → cards %%

## Lint
%% /card-lint 自动 append — [HH:MM] N scanned, R/Y/G findings %%

---

## End of Day Review

**Shipped:**
-

**Slipped:**
-

**Cards spawned:** _填后同步 frontmatter `cards-spawned`_
-

**Actions touched:** _填后同步 frontmatter `actions-touched`_
-

**People touched:** _填后同步 frontmatter `people-touched`_
-

**Carry forward to tomorrow:**
-

**Day-mode (set at close):** `exec | learning | hybrid | rest` → 改 frontmatter
"""


def main() -> int:
    today = dt.date.today()
    target = DAILY_DIR / f"{today.isoformat()}.md"

    DAILY_DIR.mkdir(parents=True, exist_ok=True)

    if target.exists():
        print(f"[skip] {target.name} already exists ({target.stat().st_size} bytes)")
        return 0

    parent_path = WEEKLY_DIR / f"{iso_week(today)[0]}-W{iso_week(today)[1]:02d}.md"
    if not parent_path.exists():
        print(f"[warn] parent weekly missing: {parent_path.name} — daily will reference dead link")

    target.write_text(build_template(today), encoding="utf-8")
    print(f"[ok] created {target.name} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
