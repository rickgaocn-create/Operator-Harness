---
category: work
name: daily-emit
description: Emit today's daily note from tomorrow-seed + vault state; 08:00 or on demand. Trigger on "/daily-emit", "/daily-emit --autonomous", "emit today", "起今天 note", "auto daily note", or the 08:00 Windows Task.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/tomorrow-seed.md]]"
  - "[[09 Rules/digest-job.md]]"
  - "[[09 Rules/time.md]]"
created: 2026-05-14
created-by: claude
audit-trace: "[[_prototype-2026-05-13-chew.md]] v2 baseline § Artifact B → emit consumer"
---
# Skill: Daily Emit (morning daily note 输出)

读 tomorrow-seed (yesterday EOD generated) → 写今天的 daily note. Replaces manual `/daily-note` Phase 4 ask Top 3 when seed exists.

> **Contract reference**: [[09 Rules/tomorrow-seed.md]] schema · [[09 Rules/time.md]] daily note 模板. When skill ≠ rule, rule wins.

> **Quality baseline**: [[_prototype-2026-05-13-chew.md]] v2 § Artifact B example (user-approved 2026-05-14)。

## 🚦 Invocation Mode (2026-05-14 pivot)

**Primary path (NOW)**: **On-demand manual invoke via Max account session**
- {{USER_NAME}} 早晨醒来后敲 `/daily-emit` → 当前 Claude Code session 跑完
- Read tomorrow-seed (yesterday `/day-digest` generated) → write today's daily note
- Max account, no API credit consumed

**Autonomous path (DEFERRED)**: Windows Task `RG-daily-emit` 08:00 daily
- 已建 setup_schedule.ps1 但 unregistered（同 day-digest 原因）
- Setup scripts 保留 作 future reference

**Fallback**: 如 tomorrow-seed 不存在（yesterday 没敲 /day-digest）→ skill 自动 fall back 到 `/daily-note` interactive Phase 3.5 flow，不 fail

## When to Use

- `/daily-emit` / `/daily-emit --autonomous` 显式触发
- "emit today" / "起今天 note" / "auto daily note"
- Windows Task `RG-daily-emit` 08:00 daily 自动触发（autonomous mode）

**Don't use for:**
- 没有 tomorrow-seed 的天（seed file 不存在）→ fallback `/daily-note` interactive flow
- 用户想 manual curate Top 3 → `/daily-note` interactive
- Mid-day daily note creation（系统 already 跑过 08:00 emit） → 不重复跑，用 `/daily-note` 看 / Edit

## How It Works

### Phase 0 — Resolve Date + Mode

```bash
today=$(date +%Y-%m-%d)
weekday=$(date +%A)
iso_week=$(date +%Y-W%V)
quarter="2026-Q2"  # 当前 quarter,按需 compute
daily_note="04 Notes/daily notes/${today}.md"
seed_file="04 Notes/vault-evolve/_tomorrow-seed-${today}.md"
parent_weekly="04 Notes/weekly/${iso_week}.md"
log_file="04 Notes/vault-evolve/_emit-log.md"
```

**Autonomous mode** (Windows Task): no interactive prompts
**Interactive mode** (manual): show preview before write

### Phase 1 — Check Idempotency + Seed Availability

```bash
# 1. Daily note 已存在? 
if [ -f "$daily_note" ]; then
  # 检查 frontmatter status:active 还是已 manual-edit
  # 已 manual-edit → 不覆盖，log + exit
  # 仅 scaffold (无 Top 3 填) → 可以 emit 增强（Phase 5 merge mode）
fi

# 2. Seed file 存在 + fresh?
if [ -f "$seed_file" ]; then
  # Read seed frontmatter: 检查 for-date == today
  # 不符 → log warning + fall back to /daily-note interactive flow
fi

# 3. Parent weekly 存在?
if [ ! -f "$parent_weekly" ]; then
  log warning "weekly file missing"
  # 仍 emit, 但 cascade reference 标 ❓
fi
```

### Phase 2 — Read Seed + Current Vault State

读 seed file 完整内容. Cross-reference 当下 vault state:

| Source | Why |
|---|---|
| Tomorrow-seed (primary) | Top 3 / Day Planner / Active Tracks / Drift / OKR alignment |
| Yesterday daily note § EOD § Carry forward | Final tweak — 23:00 之后 user 手填的部分 |
| Project Kanbans current state | State delta since 23:00 (rare but possible) |
| Active trip bundle if `trip-context` in seed | Trip itinerary refresh |
| 今天 morning WeChat ingest (if 06:00 ran) | Group dynamics 早晨刚 ingest |

### Phase 3 — Compose Daily Note Body

Per [[09 Rules/time.md]] § Daily 模板 + seed content:

```markdown
---
type: daily
date: {today}
weekday: {weekday}
iso-week: W{nn}
quarter: 2026-Q2
parent: "[[{iso_week}]]"
status: active
day-mode:
tags:
  - daily-note
  - 2026/Q2/W{nn}
  {如 trip-context: 加 chain-anchor tag, e.g. 沪差0518}
{如 trip: trip-context: "[[(C) 差旅...]]"}
projects-touched: []
people-touched: []
cards-spawned: []
actions-touched: []
---

> **Cascade:** [[GOALS.md]] → [[2026-Q2]] → [[{iso_week}]] → **{today} {weekday} · Day {N}/7{如 trip: · {trip-anchor} Day {x}/{y}}**
> {如 trip: ⚠️ 在 SH/XM/etc 出差中 — {summit/event name}}

# {today} · {weekday}{如 trip: · {trip-anchor} Day {x}/{y}}

## Top 3 Priorities

> {从 seed § Top 3 复制，含 OKR mapping}

- [ ] {priority emoji} **{Top 1}** — {OKR tag} {short justification}
- [ ] {Top 2}
- [ ] {Top 3}

---

## Day Planner
<!-- Day Planner (OG) + Operon Calendar Time Grid 双读 · syntax: `- [ ] HH:mm task {{datetimeStart:: YYYY-MM-DDTHH:mm:00}}` (24h, NO brackets · v3 hybrid since 2026-05-21) -->

{从 seed § Day Planner Pre-populated 复制. ⚡ 标记保留 — user 早晨能识别哪些是 AI-added}
{每一行 emit format: `- [ ] HH:mm task {{datetimeStart:: {today}THH:mm:00}}` · BREAK / END 行不加 datetimeStart}

---

> [!summary]- 🌅 Wake-up Brief — {yesterday} EOD digest summary
>
> {从 yesterday § AI-Chew § Shape of Today 摘要 1-2 行 + 关键 emerged signals + 主要 carry-forward}
>
> **5/14 战略校准**（如有）: {从 seed § Drift Signals 复制相关 1-2 条}
>
> **⏸️ Pending**（如有）: {从 seed § Pending Decisions 复制}

---

## 📥 昨日扫描 · 待确认 (Yesterday Sweep)
<!-- /morning-sweep 晨间填充 — 昨日 WeChat+Feishu 对话提取的待确认 todos。保留要做/删掉不要 → /morning-sweep --commit。emit 只铺空 scaffold；morning-sweep 负责填充 -->

---

## Meetings & Conversations
<!-- 时间倒序 · HH:MM · 渠道 · 对方 ([[wiki]]) · outcome -->

{如 trip + 知道 expected meetings: 在 ### Expected today 段 pre-fill}

---

## Active Tracks

### {{PROJECT_A}}— `03 Projects/{{PROJECT_A}}/`
- **⚠️ Overdue ({N})**: {从 seed Active Tracks 复制}
- **🔺 This Week ({N})**: {同上}
- **🔁 In-progress ({N})**: {同上}
- **Today (committed)**: 见 § Day Planner
- **Slipped from {yesterday} (carry forward)**: {如有, 从 seed 复制}

### {{ORG_B}} — `03 Projects/{{ORG_B}}/`
{同上格式}

> 本周 Big Rocks 见 [[{iso_week}]] — daily 不复述

---

## Quick Capture
<!-- 散记 — /inbox-process 或 /source-ingest 在日终处理 -->

{如 trip + 知道关键议题: pre-fill 关键 capture 段, e.g. "### EPIC 峰会 intake (待回填)" stub}

---

## Ingests
<!-- /source-ingest 自动 append — [HH:MM] source → cards -->

## Lint
<!-- /card-lint 自动 append — [HH:MM] N scanned, R/Y/G findings -->

---

## End of Day Review

**Shipped:**
-

**Slipped:**
-

**Cards spawned:** _填后同步 frontmatter `cards-spawned`_
-

**Actions touched:** _填后同步 frontmatter `actions-touched`_
{如 trip: - [[T260512-shanghai-trip-may]] · chain `{anchor}`}

**People touched:** _填后同步 frontmatter `people-touched`_
-

**Carry forward to tomorrow:**
-

**Day-mode (set at close):** `exec | learning | hybrid | rest` → 改 frontmatter
```

### Phase 4 — Write or Merge

如 daily note 不存在 → Write 全新文件
如 daily note 已存在 + 仅 scaffold (no user content) → Overwrite with emit version
如 daily note 已存在 + 含 user content → **Merge mode**:
- Top 3 / Day Planner: 如 user 已填，不动；如空白，emit fill
- Active Tracks: 永远 fresh emit fill (user 一般不手维)
- Other sections (Quick Capture / Meetings / EOD): 不动

### Phase 5 — Log Run

Append **`04 Notes/vault-evolve/_emit-log.md`**:

```
{timestamp} · {mode} · {today} daily emit · {N} sections filled · seed source: {seed_file or 'fallback /daily-note'} · {N} warnings
```

### Phase 6 — Confirm (interactive mode only)

> "Daily note for {today} written.
>
> Top 3 (from seed):
> 1. {Top 1}
> 2. {Top 2}
> 3. {Top 3}
>
> {如 trip: 注意今天是 {trip-anchor} day {x}/{y} — Day Planner = trip itinerary}
>
> 早晨 review 后, swap Top 3 任何条都可以 — manual Edit 直接改即可."

Autonomous mode 跳过 Phase 6。

## Hard Rules

1. **NEVER 覆盖 user 已 manual-edit 的 daily note** — Phase 1 检测，避免破坏 user 中途修改
2. **NEVER 改 yesterday's daily note** — emit 只动今天的
3. **NEVER 删 tomorrow-seed file** — yesterday 写的 seed 归档不删（accuracy 评估用）
4. **ALWAYS check seed `for-date` matches today** — 不符 fall back
5. **ALWAYS preserve ⚡ markers** in Day Planner — user 早晨能识别 AI-added blocks
6. **ALWAYS log run to _emit-log.md** — accuracy review 数据源
7. **ALWAYS use trip-context framing if seed has it** — trip day Day Planner = itinerary not work tasks
8. **ALWAYS emit Day Planner v3 hybrid format**：每个 task 行 `- [ ] HH:mm task {{datetimeStart:: {today}THH:mm:00}}` — Day Planner OG 读 `HH:mm task`，Operon Calendar 读 `{{datetimeStart}}`。BREAK / END 行保留纯 `- [ ] HH:mm BREAK` / `- [ ] HH:mm END`（不加 datetimeStart）。如 seed 已 emit Operon 块 → preserve 不重复

## Failure Modes

| Symptom | Behavior |
|---|---|
| Seed file 不存在 | Fall back to `/daily-note` Phase 3.5 interactive flow + log warning |
| Seed `for-date` ≠ today | Skip seed, fall back to Phase 3.5 + log warning |
| Daily note 已存在 + 已 user-edited | Don't overwrite; log "skipped — user content detected" + exit |
| Daily note 已存在 + scaffold only (无 user content) | Overwrite with emit version + log |
| Parent weekly file missing | Still emit, cascade reference 标 `[[YYYY-Www]]?` 并 warning |
| Trip bundle in seed but trip-bundle file 不存在 | Skip trip-context framing + warning |
| Multiple trip bundles 含 today | Use seed-specified one (seed disambiguates) |
| Run twice same day | Phase 1 idempotency check 防止 second run override user edits |

## Cross-skill Chain

- **Upstream**: `/day-digest` 23:00 写 tomorrow-seed → `/daily-emit` 08:00 读
- **Downstream**: `/daily-note --close` EOD Phase 7 reconciliation → `/day-digest` 23:00 chew
- **Sibling**: `/daily-note` interactive — fallback when seed missing OR user wants manual curation
- **Sibling**: `/sync-day` mid-day — sync state between daily note ↔ Kanban

---

*08:00 自动 job 的 executor. 与 `/day-digest` 形成 24h batch loop. User 早晨起床看到的 daily note = emit 产出, manual Edit override 任何部分.*
