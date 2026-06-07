---
layer: platform
paths:
  - "04 Notes/12-week/**/*.md"
  - "04 Notes/weekly/**/*.md"
  - "04 Notes/daily notes/**/*.md"
pillar: Time · 时间笔记
method: 12 Week Year · 十二周工作法
---

# Time Pillar Rules · 时间笔记约定

> Vision-to-execution cascade — the "Aligning" layer. Three nested horizons.

## Purpose

Connect **macro vision** ([[GOALS.md]] + Q2 OKRs) to **daily execution** through an explicit cascade. Without this, daily notes drift untethered and quarterly OKRs become memorial decoration.

**Cascade direction:**
```
12-Week (Q2 OKRs)
    ↓ informs
Weekly (this week's plan)
    ↓ executes via
Daily (today's actions)
    ↑ rolls up
Weekly review (Friday)
    ↑ rolls up
12-Week review (end of quarter)
```

Each layer links **upward** to its parent and **downward** to its children. Reverse navigation = direction integrity check.

## Folder Structure

```
04 Notes/
├── 12-week/                 Quarterly anchor docs
│   └── 2026-Q2.md           One file per 12-week cycle
├── weekly/                  Weekly cascade docs
│   └── 2026-W17.md          One file per ISO week
└── daily notes/             Daily logs (existing)
    └── 2026-04-27.md        One file per day
```

## Naming Conventions

| Layer | Format | Example |
|-------|--------|---------|
| 12-Week | `{YYYY}-Q{1-4}.md` | `2026-Q2.md` |
| Weekly | `{YYYY}-W{ISO-week}.md` | `2026-W17.md` |
| Daily | `{YYYY-MM-DD}.md` | `2026-04-27.md` |

ISO week (Monday-start) used throughout. Today (2026-04-27) is **W18 Monday**.

## Frontmatter Contracts

### 12-Week
```yaml
---
type: 12-week
cycle: 2026-Q2
start: 2026-04-01
end: 2026-06-30
goals-source: "[[GOALS.md]]"
status: active                # planning | active | review | closed
---
```

### Weekly
```yaml
---
type: weekly
week: 2026-W17
start: 2026-04-20
end: 2026-04-26
parent: "[[2026-Q2]]"
status: active                # planning | active | review | closed
# —— 双周报联动（biweekly linkage）——
biweekly-period: 2026-W17~W18                 # 本周所属双周对子
biweekly-role: week-1-of-2 (opening)          # | week-2-of-2 (closing) — closing 周的 Friday Review 触发双周报
biweekly-report: "[[商务双周报 YYYY-W##]]"     # 对子收口报告（covers 2 weeks · labeled by end ISO week）
biweekly-prev: "[[商务双周报 YYYY-W##]]"       # 上期报告 = diff baseline（其 § 下双周聚焦 = 本周期承诺）
okr-tracker: "[[Q2 OKR Tracker]]"             # 本周 OKR Progress Check 与之同 O/KR spine
---
```

### Daily
```yaml
---
type: daily
date: 2026-04-27
weekday: Monday
iso-week: W18
quarter: 2026-Q2
parent: "[[2026-W18]]"
status: active                   # active → closed (after EOD review filled)
day-mode:                        # exec | learning | hybrid | rest (set at EOD; empty = exec default)
tags:
  - daily-note
  - 2026/Q2/W18                  # nested tag — Year/Quarter/Week one shot
projects-touched: []             # ["{{PROJECT_A}}", "{{ORG_B}}-inc", "aix"] — Tracks worked
people-touched: []               # wiki refs preferred; plain strings OK if no card yet
cards-spawned: []                # ["[[Cyymmdd-...]]", ...] — synced from EOD review
actions-touched: []              # ["[[Tyymmdd-...]]", ...] — workstream files
---
```

**Field semantics:**
- `iso-week` / `quarter` — denormalized for Dataview filter speed (avoid parsing `parent` link)
- `status` — flips to `closed` after EOD review block filled. Drives "did I close out?" sanity queries
- `day-mode` — semantic kind-of-day: `exec` (busy execution), `learning` (info-intake heavy), `hybrid`, `rest`. Set at EOD
- `projects-touched` / `people-touched` / `cards-spawned` / `actions-touched` — typed link arrays. Dataview-queryable for cross-cuts ("all dailies in Q2 touching 王鹤", "all {{PROJECT_A}}-touched dailies in W19")
- `tags: 2026/Q2/W19` — nested tag enables cascade filters (`#2026/Q2`, `#2026/Q2/W19`) without separate fields

**Hybrid array convention (people / cards / actions / projects-touched):**
- Entries are either `"[[wiki-ref]]"` (preferred) or plain string (placeholder until card is created)
- Dangling wiki refs OK — Obsidian graph surfaces them as "orphan candidate" → signals "should card this entity"
- `projects-touched` uses short string slugs (`{{PROJECT_A}}`, `{{ORG_B}}-inc`, `aix`) not wiki refs, since they're Track tags not files

## File Anatomies

### 12-Week Anchor

```markdown
# 2026-Q2 — 12-Week Cycle

> Single source of truth for this quarter's commitments.

## Vision Anchor
{One paragraph: what success looks like at end of cycle. Pulled from GOALS.md.}

## Tracks & OKRs
### Track 1: 《{{PROJECT_A}}》
- O: {objective}
- KR1: {measurable}
- KR2: {measurable}

### Track 2: {{ORG_B}}
- ...

## Weekly Cascade
- [[2026-W14]] · planning
- [[2026-W15]] · active
- [[2026-W16]] · active
...

## Risks & Watch Items
- ...

## Mid-Cycle Review (W6/7)
{Filled mid-quarter}

## End-Cycle Review (W12)
{Filled at close — what shipped, what slipped, lessons → Cards}
```

### Weekly Cascade

```markdown
# 2026-W17 — Apr 20–26

> Parent: [[2026-Q2]]

## This Week's 1-3 Big Rocks
1. {Pulled from 12-Week + prev 双周报 § 下双周聚焦. The non-negotiables.}

## OKR Progress Check
> Keyed to the project OKR Tracker spine — same O/KR labels, so the biweekly buckets this 1:1.
| O / KR | This Week's Move | Status |
|--------|-----------------|--------|
| O1.KR1 ... | ... | 🟢/🟡/🔴/✅ |

## Active Tracks
- [[10 Action/12 Active/T260427-...]] — status

## Daily Cascade
- [[2026-04-20]] Mon
- [[2026-04-21]] Tue
- ...

## Friday Review
> On a biweekly **closing** week this is the report's week-2 input; on an **opening** week it's week-1 (carried into the closing week). Sync the OKR Tracker KR statuses here too.
**Shipped:** ...
**Slipped:** ...
**Cards harvested:** [[C260424-...]]
**承诺兑现核对 (vs prev 双周报 § 下双周聚焦):** ...
**Carry to next week:** ...
```

### Daily

```markdown
---
{frontmatter per Daily contract above}
---

> **Cascade:** [[GOALS.md]] → [[2026-Q2]] → [[2026-W19]] → **2026-05-09 Sat · Day 6/7**

# 2026-05-09 · Saturday

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

## 📥 昨日扫描 · 待确认 (Yesterday Sweep)
%% /morning-sweep 晨间填充 — 昨日 WeChat+Feishu 对话提取的待确认 todos。保留要做的、删掉不要的 → /morning-sweep --commit 路由到 Inbox/看板。空 = 还没跑 sweep 或昨日无可提取项 %%

---

## Meetings & Conversations Today
%% 按时间倒序，每条：HH:MM · 渠道 · 对方（[[wiki]]）· outcome %%

---

## Active Tracks

### 《{{PROJECT_A}}》— `03 Projects/{{PROJECT_A}}/`
- **Today:**

### {{ORG_B}} — `03 Projects/{{ORG_B}}/`
- **Today:**

### AIX — Track 3 ({{ORG_B}} parallel)
- **Today:**

> 本周 ⏫ 自动从 [[2026-W19]] § Big Rocks 投影 — daily 不复述

---

## Quick Capture
%% 散记，由 /inbox-process 或 /source-ingest 在日终处理 %%

---

## Ingests
%% 由 /source-ingest 自动追加 — [HH:MM] source → cards %%

## Lint
%% 由 /card-lint 自动追加 — [HH:MM] N scanned, R/Y/G findings %%

---

## End of Day Review

**Shipped:**
-

**Slipped:**
-

**Cards spawned:** _填后同步至 frontmatter `cards-spawned`_
-

**Actions touched:** _填后同步至 frontmatter `actions-touched`_
-

**People touched:** _填后同步至 frontmatter `people-touched`_
-

**Carry forward to tomorrow:**
-

**Day-mode (set at close):** `exec | learning | hybrid | rest` → 改 frontmatter
```

**Light-mode 变体（学习日 / 休息日）：** 当 `day-mode: learning` 或 `rest` 时，body 可仅保留 § Quick Capture / 自定义 § Key Learning / § End of Day。Top 3 / Active Tracks 留空不内疚。

**Cascade banner 的 Day X/7：** 周一=1/7，周日=7/7。视觉提醒在周内的位置 → 提示是否到了 weekly review（周五 5/7）。

## Cascade Rules

| Trigger | Cadence | Action |
|---------|---------|--------|
| Quarter starts | Once per cycle | Create `{YYYY}-Q{n}.md`, copy OKRs from GOALS.md, list weeks |
| Week starts (Monday) | Weekly | **Auto-create** `{YYYY}-W{nn}.md` on the first daily of a new ISO week (`/daily-note` Phase 3 — no longer just "offer"): pull Big Rocks from 12-Week, **seed OKR Progress Check from the prev 双周报 § 下双周聚焦** + the OKR Tracker spine, list days, set biweekly linkage frontmatter |
| Day starts | Daily | Create `{YYYY-MM-DD}.md` (existing flow via `/daily-note`) |
| Friday EOD | Weekly | Fill "Friday Review" in weekly file → harvest Cards → carry-forward to next week |
| **Biweekly close (every 2nd Fri · odd ISO week — W19/W21/W23/W25)** | **Biweekly** | **Run `/periodic-report --biweekly`. It reads the 2 weekly files' § Friday Review + § OKR Progress Check as pre-aggregated input (daily memos = backing detail) + diffs prev 双周报. See [[.claude/skills/periodic-report/SKILL.md]] Biweekly Phase 2.** |
| W6/7 of quarter | Mid-cycle | Fill "Mid-Cycle Review" — recalibrate KRs if needed |
| W12 of quarter | Quarter-end | Fill "End-Cycle Review" → batch-harvest Cards → archive |

## Hard Rules

- **Daily notes never freelance OKRs.** Big Rocks come from the weekly file, which comes from the 12-week file.
- **Weekly review is non-skippable.** No weekly review = direction integrity broken. Run it Friday EOD or Saturday morning.
- **Weekly OKR Progress Check shares the biweekly's spine.** The weekly's § OKR Progress Check uses the same O/KR labels as the project OKR Tracker (`03 Projects/{{PROJECT_A}}/工作进展/Q2 OKR Tracker.md`), so `/periodic-report --biweekly` buckets the 2 weekly Friday Reviews into the report 1:1 without re-deriving. **Weekly = per-week increment; biweekly = synthesis of the 2 weeklies** (+ daily backing + diff vs prev report's § 下双周聚焦). Reports land on odd ISO weeks (W19/W21/W23…), each covering the trailing 2-week pair.
- **Don't edit closed cycles.** A closed `2026-Q1.md` is historical record. Lessons from it live in Cards.
- **One source of truth for OKRs.** [[GOALS.md]] holds long-term tracks; `2026-Q{n}.md` holds the current quarter's commitments. Don't duplicate elsewhere.
