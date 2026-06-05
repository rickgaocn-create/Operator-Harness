---
type: daily
date: {{date:YYYY-MM-DD}}
weekday: {{date:dddd}}
iso-week: W{{date:WW}}
quarter: {{date:GGGG-[Q]Q}}
parent: "[[{{date:GGGG-[W]WW}}]]"
status: active
day-mode:
tags:
  - daily-note
  - {{date:GGGG/[Q]Q/[W]WW}}
projects-touched: []
people-touched: []
cards-spawned: []
actions-touched: []
created-by: "obsidian (Daily Notes core plugin button · template-only — run /daily-note for state-aware Top 3 + /daily-emit for Day Planner pre-fill)"
---

> **Cascade:** [[GOALS.md]] → [[{{date:GGGG-[Q]Q}}]] → [[{{date:GGGG-[W]WW}}]] → **{{date:YYYY-MM-DD}} {{date:ddd}} · Day {{date:E}}/7**

# {{date:YYYY-MM-DD}} · {{date:dddd}}

## Top 3 Priorities
<!-- Each line MAY carry `<!-- bound: {{operonId:: <7char>}} surface=<path> -->` to sync [x] back to a canonical surface task. /daily-note Phase 4 auto-emits bindings for Phase 3.5-matched candidates. Manual entries: no binding = no auto-sync (user owns reconciliation). -->

- [ ]
- [ ]
- [ ]

### 🥁 Daily Drum (live · Operon)
<!-- Live: today + overdue open tasks across all surfaces. If a 🔺/⏫ task here is NOT reflected in Top 3 above, reconcile before EOD. -->

```operon
filter: "Daily Drum (today + overdue · open)"
```

---

## Day Planner
<!-- Day Planner (OG) + Operon Calendar Time Grid 双读 · v3 hybrid syntax: `- [ ] HH:mm task {{operonId:: <7char>}} {{datetimeStart:: YYYY-MM-DDTHH:mm:00}}` · BREAK/END lines stay plain (no Operon block). Run /daily-emit to pre-populate from tomorrow-seed + trip context. -->

- [ ]

---

## Meetings & Conversations
<!-- 时间倒序 · HH:MM · 渠道 · 对方 ([[wiki]]) · outcome -->

---

## Active Tracks

### 《{{PROJECT_A}}》— `03 Projects/{{PROJECT_A}}/`
- **Today:**

### {{ORG_B}} — `03 Projects/{{ORG_B}}/`
- **Today:**

### AIX — Track 3 ({{ORG_B}} parallel)
- **Today:**

> 本周 Big Rocks 见 [[{{date:GGGG-[W]WW}}]] — daily 不复述

---

## Quick Capture
<!-- 散记 — /inbox-process 或 /source-ingest 在日终处理 -->

-

---

## Ingests
<!-- /source-ingest 自动 append — [HH:MM] source → cards -->

## Lint
<!-- /card-lint 自动 append — [HH:MM] N scanned, R/Y/G findings -->

---

## End of Day Review

### 📦 Shipped today (live · Operon)
<!-- Auto-computed from {{dateCompleted:: today}}. Annotate WHY below — narrative, not inventory. -->

```operon
filter: "Shipped Today"
```

**Shipped (annotations):**
-

### ⏰ Slipped (live · Operon)
<!-- Auto-computed: open tasks with {{dateDue:: < today}}. Annotate WHY + what to do. -->

```operon
filter: "Slipped (overdue · open)"
```

**Slipped (annotations):**
-

### ➡️ Carry forward — tomorrow (live · Operon)
<!-- Auto-computed: open tasks with {{dateDue:: tomorrow}}. Append manual reschedules below. -->

```operon
filter: "Carry Forward (tomorrow)"
```

**Carry forward (annotations / reschedules):**
-

### Cross-references (filled at close)

**Cards spawned:** _填后同步 frontmatter `cards-spawned`_
-

**Actions touched:** _填后同步 frontmatter `actions-touched`_
-

**People touched:** _填后同步 frontmatter `people-touched`_
-

**Day-mode (set at close):** `exec | learning | hybrid | rest` → 改 frontmatter

### Snapshot at close (frozen audit trail)
<!-- /daily-note --close freezes the Shipped/Slipped/Carry-forward embed results into HTML comments here so historical dailies stay point-in-time accurate even though the embeds are live. -->

<!-- snapshot-shipped: (filled by /daily-note --close) -->
<!-- snapshot-slipped: (filled by /daily-note --close) -->
<!-- snapshot-carry: (filled by /daily-note --close) -->
