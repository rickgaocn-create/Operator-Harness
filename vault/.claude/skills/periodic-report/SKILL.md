---
category: work
name: periodic-report
description: Produce periodic reports. Use --weekly for vault/project context refresh; use --biweekly for OKR-bucketed business reporting from the last 14 days. Biweekly auto-chains to /biz.
model: claude-opus-4-7
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/time.md]]"
created: 2026-05-14
created-by: claude
audit-trace: "2026-05-14 prune pass — merged /weekly-update + /biweekly-report into single skill with cadence flag"
---
# Skill: Periodic Report (`--weekly` default · `--biweekly` for PMO 双周报)

Two distinct cadences, one entry. Weekly = vault context refresh (interview-driven). Biweekly = OKR-bucketed business report (Daily-memo-mined). Pick via flag or trigger-phrase inference.

## Mode Routing

| Trigger | Mode |
|---|---|
| `/periodic-report` (no flag) OR plain "weekly update" triggers | **Weekly** |
| `/periodic-report --weekly` OR explicit weekly triggers | **Weekly** |
| `/periodic-report --biweekly` OR "双周报" / "biweekly report" / "本周双周会" / "进度报" triggers | **Biweekly** |

If genuinely ambiguous → ask plain-text 1-line: *"Weekly vault refresh or biweekly 商务条线 OKR report?"* and await reply.

---

## Weekly Mode (default)

Interview the user to refresh all context files across the vault — root CLAUDE.md, GOALS.md, each project's CLAUDE.md, and the open task surfaces. Keeps everything current so Claude starts every future session with accurate context, not stale claims.

### When to Use (weekly)

- "weekly update" / "let's do a weekly review" / "update my vault"
- Last update >7 days ago (check `Weekly Update` § Last updated date)

### How It Works (weekly)

1. Scan all context files to understand current state
2. Interview at the meta level (big picture, goals, weekly pulse)
3. Walk through each project for status updates
4. Sweep the task inbox for overdue / stale items
5. Update all files
6. Optionally create a weekly review note

#### Weekly Phase 1: Scan Current State

Read everything before asking a single question:

```bash
ls -d "03 Projects"/*/ 2>&1 || true
```

Read:
- `CLAUDE.md` — focus on **Weekly Update** (what was there last time), **My Goals & Current Progress**, **My Current Projects & Overviews**
- `GOALS.md` — if it exists, scan for sections with numbers, dates, progress that might need updating
- Each project's `CLAUDE.md` — specifically the **Current Status** section
- **`06 Tasks/Inbox.md`** (and `💼Work.md`, `🏡Personal.md` if non-empty) — skim open `- [ ]` lines. Flag **overdue** (date past today) and **stale** (no activity, no due date) for Phase 4.

**What you're building:** a mental map of what was true last time, so you can ask targeted questions about what *changed* — not make the user re-justify everything from scratch.

#### Weekly Phase 2: Meta-Level Interview

Reference what you read in Phase 1 so the user knows you're caught up.

##### Weekly Pulse

Show the user the current Weekly Update section (or note it's blank), then ask the five fields:

- What's working right now?
- What's not working?
- What are you sitting on or need to decide?
- What are you feeling pulled toward?
- Any deadlines or time-sensitive things coming up?

If a field hasn't changed, "same" is a valid answer — keep what was there.

##### Goals Check-In

Reference current state from **My Goals & Current Progress** in CLAUDE.md and anything in GOALS.md. Then:

- Any progress on your main goal since last time? (New numbers, milestones hit, setbacks)
- Has the plan changed? (New strategy, dropped something, added something)
- Anything new on the risk/runway front?

Keep this tight. If nothing changed, move on. Don't make them re-justify existing goals every week.

##### GOALS.md Specifics

If GOALS.md exists with trackable items (income, milestone dates, skill targets), surface anything that looks like it might need updating:

> "Your GOALS.md shows [X]. Still accurate, or should I update?"

If GOALS.md doesn't exist, skip — don't auto-create one here.

#### Weekly Phase 3: Project Updates

Walk through each project folder from Phase 1. For each:

1. Show the current status from that project's CLAUDE.md
2. Ask: *"What's the update on [Project Name]? Any status change or progress this week?"*
3. "No change" is a valid answer — move on.

Keep this fast. One question per project, maybe a follow-up if something big happened. This is a check-in, not a deep dive.

If a project's CLAUDE.md lacks a Current Status section, ask for status anyway and note that you'll add the section when you update the file.

#### Weekly Phase 4: Task Sweep

Surface the overdue/stale clusters from Phase 1:

> "In Inbox you have N overdue and M stale. Quick triage — reschedule, close, or keep as-is?"

Use `/inbox-process` rules — never toggle `- [ ]` → `- [x]` without explicit instruction; reschedule by editing the existing date in place; new commitments from the interview append per `/task-capture` (≤ 3 new tasks per write).

Skip this phase if all three task files have zero open items.

#### Weekly Phase 5: Update All Files

After the interview, show a summary of all proposed edits before writing.

##### Root CLAUDE.md

**Weekly Update section** — overwrite with this week's pulse:

```markdown
## Weekly Update

> **Last updated:** [today's date]

- What's working: [from interview]
- What's not working: [from interview]
- What I'm sitting on / need to decide: [from interview]
- What I'm feeling pulled toward: [from interview]
- Any deadlines or time-sensitive things: [from interview]
```

**My Goals & Current Progress** — only update if something actually changed.

**My Current Projects & Overviews** — update Status line + overview only for projects whose status changed. Leave unchanged projects alone.

##### GOALS.md

Update specific numbers/dates/milestones the user called out. Don't restructure.

##### Each project's CLAUDE.md

Update **Current Status**:

```markdown
## Current Status

> **Last updated:** [today's date]
> **Status:** [updated status]

[Any additional context from the interview]
```

**Critical:** only edit status/progress sections. Never rewrite a project's structure, process, or rules during a weekly update — those changes are out of scope here.

#### Weekly Phase 6: Weekly Review Note (Optional)

After files are updated, ask:

> "Want me to create a weekly review note? If so, where do you keep them and how do you like them structured?"

If yes: create a dated note in their folder/format. The interview answers are already the content — no extra interview needed.

If they have an existing format (template, past review notes), match the style. Read a previous one before writing.

If no: skip. Don't push.

#### Weekly: Summary of What Gets Updated

| File | Changes |
|---|---|
| Root `CLAUDE.md` § Weekly Update | All 5 pulse fields + date |
| Root `CLAUDE.md` § Goals & Progress | Only if numbers/plan/risks changed |
| Root `CLAUDE.md` § Projects & Overviews | Status line + overview for changed projects only |
| `GOALS.md` | Trackable items that changed (if file exists) |
| Each project `CLAUDE.md` § Current Status | Status + date + what happened |
| **`06 Tasks/Inbox.md`** (+ siblings) | Reschedule/close overdue; append new commitments |
| Weekly review note | Optional, user's choice and format |

---

## Biweekly Mode (`--biweekly`)

Generate a structured biweekly progress report by mining the past 14 days of Daily memos, cross-referencing the current OKR Tracker, diffing against the previous biweekly report, and surfacing gaps + suggestions before writing.

Default scope: **《{{PROJECT_A}}》商务条线**. Other tracks ({{ORG_B}}, AIX) follow the same flow with the project-scoped OKR file swapped in.

### When to Use (biweekly)

- "双周报" / "biweekly report" / "本周双周会" / "进度报"
- Friday before a 商务双周会 / PMO 双周会
- User asks to "summarize past two weeks for [project]"

### Output Location (biweekly)

**`03 Projects/<project>/09 Reports/(C) <条线>双周报 YYYY-W##.md`**

ISO week of the **end** of the reporting period. Default project: `{{PROJECT_A}}`. Default 条线: `商务`. Create `09 Reports/` if it doesn't exist.

### How It Works (biweekly)

#### Biweekly Phase 1: Scope & Window

Confirm with user (default to most recent if not specified):

> "双周报 covering [start] → [today], 商务条线, output to **`03 Projects/{{PROJECT_A}}/09 Reports/`**. Confirm?"

Compute:
- **End** = today (or user-specified)
- **Start** = end − 13 days
- **Week label** = ISO week of end date (e.g. `2026-W17`)

#### Biweekly Phase 2: Read All Inputs (parallel)

Pull these in one batch — no questions yet:

##### A. OKR Tracker (the spine)
- Default: **`03 Projects/{{PROJECT_A}}/工作进展/Q2 OKR Tracker.md`** (canonical location — verified 2026-05-27)
- Defines the O / KR structure the report buckets into. **Never invent KRs not in the tracker.**

##### B. Previous biweekly report (the diff baseline)
- Glob **`03 Projects/{{PROJECT_A}}/09 Reports/*双周报*.md`** (tolerant of the `(C)` prefix — actual files may or may not carry it)
- Pick most recent by ISO-week in filename. Read **OKR 进展** + **下双周聚焦** sections. The prev report's **§ 下双周聚焦 = this period's commitment baseline** — check each item off.
- If none exists: this is the first report. Note it; skip diff.

##### C. Past 14 days of Daily memos (the raw input)
- Path: **`04 Notes/daily notes/`** (canonical per `[[09 Rules/time.md]]`)
- Glob `YYYY-MM-DD.md` falling inside the date window
- These hold meeting minutes, partner updates, decisions
- **Legacy path check:** if **`00 Raw/Daily/**` or `**04 Notes/Daily/`** (capital D) still has files, surface as orphans for `/inbox-process` — don't silently merge

##### D. Recent project artifacts (supporting evidence)
- `ls -lat` on **`03 Projects/{{PROJECT_A}}/00 Raw/`**, `Pitches/`, `工作进展/`, `03 行程计划/`, `04 会议纪要/`, `09 Reports/`
- Anything modified inside the window is fair game to cite

##### E. Inbox (active commitments)
- **`06 Tasks/Inbox.md`** — skim open `- [ ]` lines tagged `#{{PROJECT_A}}发行` / `#{{PROJECT_A}}情报` / `#{{PROJECT_A}}ai` for context on what's in flight

##### F. The 2 weekly files in the window — **pre-aggregated input** (2026-05-27 added; the weekly↔biweekly link)
- Path: **`04 Notes/weekly/{YYYY}-W{##}.md`** × 2 — the opening + closing week of this biweekly pair (each file's `biweekly-period` / `biweekly-role` frontmatter says which; closing week = odd ISO week of the report label)
- Read each file's **§ OKR Progress Check** (already keyed to the same OKR Tracker spine as source A — buckets 1:1) + **§ Friday Review** (Shipped / Slipped / 承诺兑现核对 / Carry). These are the per-week increments {{USER_NAME}} already synthesized at each Friday — **roll them up, don't re-derive.** Source C (daily memos) becomes the *backing detail you cite*, not the raw material you mine from zero.
- If a weekly file is missing (that week wasn't scaffolded), fall back to mining source C raw for that week and note the gap in Phase 4.

#### Biweekly Phase 3: Synthesize

For each O / KR in the OKR Tracker, build:

1. **What moved this period** — concrete events from Daily memos / artifacts mapped to the KR
2. **Status tag** (pick one — match the PMO 双周报 vocabulary):
   `已完成` · `首版完成` · `部分落地` · `进展` · `进展中` · `持续推进中` · `下周启动` · `进展缓慢` · `阻塞`
3. **Completion %** at the O level (rough — 0 / 15 / 30 / 50 / 70 / 100)

**Diff against previous report:**
- KRs that were `下周启动` last time and still are this time → flag as `进展缓慢`
- KRs that hit milestones since last report → period highlights
- Last report's `下双周聚焦` items → check if they happened; missing ones surface as 风险/建议

#### Biweekly Phase 4: Surface Gaps & Suggestions (Pre-Write)

Show the user a brief pre-write summary:

```
📋 双周报草案预览 (W##):

✅ 本期亮点 (从 Daily 提炼):
  - [3-5 concrete wins]

⚠️ 待澄清 (Daily 未覆盖的 KR):
  - O# KR#: 上次状态 [X], 本期 Daily 无更新 → 标 "下周启动" 还是 "持续推进"?

🔁 上期承诺未兑现:
  - [items from last report's 下双周聚焦 that didn't happen]

💡 建议补充进双周报 (Daily 提了但你可能没意识到值得对外露出):
  - [judgment calls — items that read as routine in Daily but are signal-worthy]

确认后开始写，或先调整哪一项?
```

**Wait for user confirmation or edits.** Don't write the report file until the synthesis is signed off.

#### Biweekly Phase 5: Write the Report

File: **`03 Projects/{{PROJECT_A}}/09 Reports/(C) 商务双周报 YYYY-W##.md`**

##### Template

```markdown
---
tags: [{{PROJECT_A}}, BD, 双周报, YYYY-Q#]
project: {{PROJECT_A}}
period: YYYY-W##-W##
date_range: YYYY-MM-DD → YYYY-MM-DD
owner: 高培尧
created: YYYY-MM-DD
---

# 《{{PROJECT_A}}》商务条线 · 双周报 · YYYY-W##

> **周期：** YYYY-MM-DD → YYYY-MM-DD · **节点：** [距下个硬节点 ≈X 周]

---

## OKR 进展

### O1：[O title from tracker]（完成度 XX%）

**KR1：【[short label]】** `[status tag]`
- [evidence — concrete partner / event / artifact, ≤2 lines per bullet]

**KR2：【...】** `[status tag]`
- ...

[repeat for each KR — skip KRs not in scope this period only if explicitly agreed in Phase 4]

---

### O2 ... O3 ... O4 ...

[same structure]

> ⚠️ [any KR gaps / structural issues — e.g. "O# KR# 原始缺失，建议 OKR 周会补齐口径"]

---

## 下双周聚焦

1. [specific action with owner if not {{USER_NAME}}]
2. ...
[3–5 items max — these become next period's diff baseline]
```

##### Style rules (hard)

- **Density over prose.** One bullet = one fact. Cut adjectives.
- **Status tags in inline code** — visually scannable like the PMO example.
- **No "executive summary" / "概要" prose blocks.** OKR-bucketed format IS the summary.
- **No 风险预警 section** unless explicitly asked — risks belong inline as `⚠️` callouts under the affected KR.
- **Don't pad missing KRs with filler.** If `下周启动`, just say so.
- **Cite artifacts as wikilinks** when referenced (`[[(C) 竞品情报简报 2026-04-20.md]]`).
- **Match Daily memo language** — Daily was CN, report is CN. Don't translate partner names.
- **Length target: ≤ 80 lines** for OKR 进展 + 下双周聚焦 combined. If longer, you're padding.
- **Two-tier item format for multi-partner KRs.** When a KR has 3+ partners / sub-items at varied status, drop the single KR-level backtick tag and use per-item inline status — see `## Reference Exemplar — 2026-W19` below. Single KR-level tag still works when the KR is a single thread.

---

#### Biweekly: Reference Exemplar — 2026-W19 商务双周报

User-optimized output, ratified W19. **Match this structure** when KRs hold multiple partners/items at mixed status. Encodes patterns the earlier base template missed.

**Style anchors:**
- **O-level 重要度 band** — bracketed weight per O: `（35-40%）`. Strategic emphasis, not 完成度. Bands need not sum to 100%.
- **Two-tier status** — KR title bare; per-item status inline, no backticks: `小鹏汽车 · 双方过会 · 进入执行期`. Compose with `·` separator; right-most token is the most current state.
- **Pivot-in-place** — blocked items carry the next move on the same line: `蜜雪冰城 · 无法推进 → F&B 类目重启筛选`. Never let a dead lead end without a redirect or 理由.
- **理由 annotation** — one-line why-blocked under killed leads (e.g. `前案效果不达预期，品牌部战略重心在出海+电影`). Keeps the death documented; informs next-cycle filter.
- **结构性能力 tag** — for KRs that build long-term leverage rather than ship a deliverable: `战略价值：结构性能力（长期 leverage，非单次产出）`. Prevents these from reading as "just a side project" in board review.
- **KR summary suffix** — when a KR has a one-line aggregate, append after em-dash: `**KR3 ...全量激活** — 4 渠道转化沟通完成`.
- **One-liner KR fallback** — when a KR has nothing item-level to enumerate, render as `**KRn {label}** — {一句话状态}` (see O3 below). Don't pad with empty bullets.

**Skeleton:**

```markdown
### O{n}：[O title]（{重要度 band, e.g. 30%}）

**KR1 [label]** [— {optional summary suffix}]
1. {item} · {status1}[ · {status2}]
   - {evidence / one-line action}
2. {item} · {status} → {pivot/redirect}
   - 理由：{why-blocked}

**KR2 [label]**
1. {item} · {status}
   - 战略价值：{leverage / 结构性能力 framing}

### O{m}：[shorter O]（25%）
**KR1 [label]** — {下双周启动 / 持续跟进 / 阻塞}
**KR2 [label]** — {一句话状态}
```

**Status keyword vocabulary (per-item, no backticks):**
- **进展**：`双方过会` · `进入执行期` · `合同推进中` · `进入技术对齐` · `已激活`
- **触达**：`建联` · `已触达` · `待向上对接` · `线下对接完成`
- **阻塞**：`无法推进` · `Pass` — 必须接 ` → {重启 / 替代路径}` 或 `理由：...`
- **启动**：`下周启动` · `下双周启动` · `倒推启动`

**W19 condensed reference:**

```markdown
### O1：核心宣发节点资源交付（35-40%）

**KR1 顶级异业联动**
1. 小鹏汽车 · 双方过会 · 进入执行期
   - 试玩会 + BW 双场景锁定 / {{PROJECT_A}}出设计、对方承担制作 + ≈¥6,000 物料 (0 现金 CAC)
2. 超级安踏 · 建联 · 待向上对接
   - 触达：广州市场运营部；关键决策人需向品牌总部对接
3. 蜜雪冰城 · 无法推进 → F&B 类目重启筛选
   - 理由：前案（蛋仔派对 × 蜜雪）效果不达预期，品牌部战略重心在出海+电影

**KR2 试玩会商务合作**
1. 广州工美联名 · 合同推进中 — 「{{PROJECT_A}} × 广州工美」官方联名身份锁定
2. 政企 KOL 邀请 · 端午试玩会（6/19–21）倒推启动 · 下周启动

**KR3 交接库渠道全量激活** — 4 渠道转化沟通完成
1. TapTap · 商务+运营双线建联 · 5/14–16 上海出差对接
2. 好游快爆 · 线下对接完成
3. 4399 游戏盒 · 线下对接完成

### O2：全球商务情报 + 属地 GR 矩阵（30%）

**KR1 竞品战略摸底**
1. 商务知识库架构 · Obsidian + Claude 本地化方案投入运行
   - 全本地部署 / 零泄露验证完成 · 关联政企/渠道/异业三大资源域
   - 战略价值：结构性能力（长期 leverage，非单次产出）

**KR2 属地政企脉络** — 文旅局合作链路 · 工美联名首落地 · 下周线下汇报促进关系
**KR3 海外渠道关系激活** — Apple / Google 已激活 · 待新材料正式启动

### O3：跨部门协同效能（25%）
**KR1 中台合规 SOP** — 下双周启动
**KR2 日系美术 / 动画供应商** — 持续跟进

### O4：AI × 研发管线协同（35-40%）

**KR1 AI 切入点识别**
1. 国内外头部 AI 游戏技术公司初筛完成
2. 入选首选：超参数科技（原腾讯 AI 团队主体）
3. 海外/同业候选 Pass — 资源置换路径不通 / 不可商务化

**KR2 AI 合作方建联**
1. 超参数科技 · 已建联 · 进入技术对齐
   - 接受「深度共创案例 → 资源置换」模式
```

#### Biweekly Phase 6: Confirm + Link

After writing:
- Confirm path written
- Suggest the user link the report from the OKR Tracker's **变更日志**:
  `| YYYY-MM-DD | 双周报 W## 发布 | [[(C) 商务双周报 YYYY-W##.md]] |`
- Offer to draft tasks per `/task-capture` (≤ 3 per write) from the **下双周聚焦** items

#### Biweekly Phase 7: Auto-Chain `/biz` — ⚠️ HARD GATE (non-optional, non-deferrable)

> **2026-05-23 hardening:** This phase is now a hard gate after the W21 biweekly miss event (5/21 biweekly created at 21:15 with zero `/biz` fire). Skipping this phase without explicit skip-flag or path-exclude is a violation. See [[.claude/skills/meeting-note/references/deep-variants.md]] § Phase 7 for canonical pattern.

### MUST-DO operational steps (in this order, this session, before ending the turn)

1. **Read frontmatter check.** Look for `biz-eval: skip`. If present, announce skip + END.
2. **Announce** (one-line, plain-text): *"🔁 Auto-chaining /biz on [report-path] per CLAUDE.md auto-chain rule. Add `biz-eval: skip` to frontmatter to opt out for future evals."*
3. **INVOKE the /biz skill via the Skill tool RIGHT NOW.** Call `Skill(skill="biz", args="<report-path> --lens strategy,ops")`. Default lens override (strategy + operational read; risk/finance fire only when KR data triggers). Do NOT defer, do NOT ask, do NOT end your turn until you have made this tool call.
4. **After /biz returns**, patch the biweekly report's frontmatter: `biz-eval: completed`, `biz-eval-doc: "[[...]]"`, `biz-eval-date: YYYY-MM-DD`.
5. **Run biz-doc-critic grader loop** (Outcomes pattern):
   - Invoke `biz-doc-critic` subagent with eval-file path + `iteration: 1`
   - If `revise`: fix named hard fails → re-invoke (max 3) → escalate at iteration 3

The user sees report + business evaluation back-to-back. Eval surfaces KR-velocity insights, capacity bottlenecks, and 下双周聚焦 risk-weighting that the report itself doesn't deliver.

### Biweekly: Failure Modes & Recovery

| Symptom | Fix |
|---|---|
| Daily memos folder is empty / sparse | Tell user explicitly: "Only N Daily memos in window; report will be thin. Verbal-dump first or proceed?" |
| OKR Tracker missing | Run `/okr` first, or ask user to confirm a barebones OKR list before bucketing |
| Previous report missing | Skip diff phase, mark as "首期" in metadata |
| KRs in Daily don't map to any OKR | Park in "其他 / 待归类" callout under OKR 进展 — don't silently drop. Flag for OKR refresh. |
| User wants a different 条线 (情报 / AI / etc.) | Same flow, swap OKR scope and condition the bucketing on relevant Os |

### Biweekly: Why This Skill Exists

The first attempt at a {{PROJECT_A}} 商务双周报 went wrong by being prose-heavy, OKR-detached, and inflating speculative risks. PMO peers write OKR-bucketed, status-tagged, dense reports. This mode enforces:

1. **OKR is the spine** — never freelance categories
2. **Daily memos are source of truth** — no hallucinated progress
3. **Diff against previous** — the user wants signal on movement, not a re-list
4. **Pre-write confirmation** — surface gaps + suggestions BEFORE generating, not after
5. **PMO-grade brevity** — status tag + 1–2 lines per KR, no padding

---

## Hard Rules (both modes)

1. **NEVER toggle `- [ ]` → `- [x]`** without explicit instruction (weekly mode Inbox sweep).
2. **NEVER invent KRs not in the OKR Tracker** (biweekly mode).
3. **NEVER fabricate progress on a KR** with no Daily-memo evidence — surface as "Daily 无更新, 标 ?" in Phase 4.
4. **ALWAYS pre-write confirmation** (biweekly Phase 4) — don't write the report file until synthesis is signed off.
5. **ALWAYS update only what changed** (weekly mode) — don't restructure projects' rules / process during a status refresh.
6. **NEVER bundle biweekly + card-lint** — different tempos. Lint is graph entropy; biweekly is OKR velocity.
