---
layer: platform
paths:
  - "06 Tasks/**/*.md"
  - "03 Projects/*/Tasks.md"
canonical_skill: ".claude/skills/task-capture/SKILL.md"
companion: "[[09 Rules/tasks.md]]"
created: 2026-05-21
type: rule
---

# Task Naming Rules · 标题命名约定

> Cross-cutting contract for **task title authoring** across all project Kanban surfaces. Companion to [[09 Rules/tasks.md]] (which governs line format, routing, status). This file governs **what goes in the title vs. description block**.
>
> **Principle:** Title scans on the Kanban card-face — one chain-anchor + one decidable action. Everything else (dates, assignees, scope lists, agendas, rationale) goes in the indented description block under the task line.

## Scope

Applies to atomic task lines in:
- **`03 Projects/<name>/Tasks.md`** (project Kanbans)
- **`06 Tasks/Inbox.md**`, `**06 Tasks/Personal.md**`, `**06 Tasks/Tasks.md`**

**Skip:**
- `- [x]` (Done — historical record, do not retroactively rename)
- `- [-]` (Dropped — same reason)
- Lines whose action starts with `[HH:mm]` (Day Planner contract — see [[09 Rules/tasks.md]] § Day Planner)
- Lines with no chain-anchor separator (`\|`) — bare standalone tasks. Surface as a separate cleanup later; do NOT auto-promote to canonical separator (chain-anchor adoption is a commitment, not a rename).

## Parse Model

```
- [STATE] {anchor} \| {action_phrase}{decoration} #tag {{field:: val}} ...
  {optional description lines, indent-preserved}
```

- Title segment = everything between `\| ` and the first `#tag`.
- Fields after `#tag` are **untouched** by this rule.
- Description block: only **add** lines; never remove or reorder existing content.

## Rules (apply in order, each fires independently)

### R1 · char cap
Visible title (`{anchor} \| {action_phrase}`) ≤ **30 CJK chars** (≈ 60 ASCII chars). If still over after R2–R6 apply, push residual qualifier to description.

### R2 · date-in-title
Match `\d{1,2}/\d{1,2}(-\d{1,2})?` in `action_phrase`:
- if date string has no equivalent in `{{dateDue}}` AND the date is the task's own deadline → set `{{dateDue}}`, strip from title
- if matches existing `{{dateDue}}` → just strip
- if ≥2 distinct dates in title (节点列表) → strip all, append description line `节奏：<original list>`
- if date is an **event date** (not task due) → strip from title, append description line `节奏：<date> <event>`

### R3 · assignee-name-in-title
Detect names: `{{USER_NAME}}`, `小K` / `小k`, `{{PERSON}}`, `宗寰`, `珂洁`, `煎饼`, etc.
- if person ∈ `{{assignees}}` field → strip from title
- **Exception:** keep if person is the **noun of action** (the target, not the actor): `回执曾启琦`, `跟{{PERSON_3}} follow-up`, `约 林芳羽 90min` — the counterparty's name IS what makes the task distinguishable

### R4 · parenthetical scope
Content inside `（...）` or `(...)`:
- if **list** (≥2 items separated by `+`, `/`, `·`, `、`) → strip from title, append description `scope：<original parens>`
- if **single qualifier** (`（黄岩松线）`, `（小K 主接）`, `（厦门）`, `（节点预估）`, `（批次合格判定）`) → keep
- if **rationale** (`（不涉金钱交易 → 免合同，邮件留痕）`) → strip, append description `理由：<original parens>`

### R5 · multi-action joins
Verbs joined by `+`, `→`, `、` in `action_phrase`:
- if joined deliverables have **distinct gates / owners / dates** → mark **SPLIT-CANDIDATE**, do NOT auto-rewrite. Surface to user for split decision.
- if **sequential within same gate** (one meeting produces N artifacts; one process has N stages collapsed) → keep primary action, append description `动作：(1) ... (2) ...`
- **Exception:** lineage/relationship chains using `→` (`王鹤书记→文旅局→广轻控股→广州工美 脉络梳理`) are a single noun phrase being studied — keep.

### R6 · duplicated channel
Same company/channel name appears in `action_phrase` twice OR appears in title AND in `{{contexts}}` field AND `chain-anchor` already implies it:
- drop the redundant mention
- **Example:** `沪差0519 \| B站 6/20 端午美林邀请函发 B 站核心人员` → R2 strips 6/20 + R6 drops leading "B站" → `沪差0519 \| 美林邀请函发 B 站核心人员`
- **Counter-example:** `沪差0519 \| B站 反馈预约预期数据` — only one B站 mention, chain-anchor doesn't imply B站 (could be TapTap). Keep.

### R7 · vague verb start
`action_phrase` begins with: `推进`, `跟进`, `处理`, `搞定`, `看看`, `了解一下` AND no specific noun deliverable follows:
- mark **VAGUE-SURFACE**, do NOT auto-rewrite — flag to user (true rewrite requires user judgment on what the deliverable actually is)

## Per-Line Decision Tree

1. Parse line; if SKIP condition → `action=no-change`
2. Apply rules in order: R2 → R3 → R4 → R6 → R5 → R7 → R1
3. If R5 fires SPLIT-CANDIDATE → `action=split-candidate`, queue for Phase 2 user review
4. If R7 fires VAGUE-SURFACE → `action=vague`, surface to user, do NOT rewrite
5. Else if new title differs from current → `action=trim`, emit Edit op
6. Else → `action=no-change`

## Edit Op Spec

- One `Edit` call per task line; batch as feasible (5–15 per turn).
- `old_string` = full current task line (+ existing description block if description is added).
- `new_string` = rewritten line; bump `{{datetimeModified}}` to current ISO datetime.
- If description lines generated → **prepend** to existing description block (preserve all existing content with original indent).
- **Never touch:** `{{operonId}}`, `{{status}}`, `{{priority}}`, `{{dateDue}}` (except R2 sets when previously empty), `{{contexts}}`, `{{assignees}}`, `{{estimate}}`, `{{datetimeCreated}}`, `{{dateCompleted}}`, `{{parentTask}}`, `chain-anchor`.

## Description Block Prefixes

When adding lines per rules, use these stable prefixes (machine-greppable):

| Source | Prefix |
|---|---|
| R2 date list | `节奏：` |
| R2 event date | `节奏：` |
| R4 list parens | `scope：` |
| R4 rationale parens | `理由：` |
| R5 sequential | `动作：` |

## Worked Examples

```
BEFORE: {{PROJECT_A}}BD体系 \| 起草《商务拓展决策流程图》v0.1，下周一开工，5/13 前给小k 过审
AFTER:  {{PROJECT_A}}BD体系 \| 起草《商务拓展决策流程图》v0.1
  + description prepended: "节奏：下周一开工，5/13 前给小K 过审"
Rules fired: R2 (5/13 = dateDue), R3 (小k ∈ assignees)
```

```
BEFORE: 沪差0519 \| B站 4 期 PV 节奏对齐（5/29 / 6/17-18 / 7月 / 二测期）+ 创作者激励配套
AFTER:  沪差0519 \| B站 4 期 PV 节奏对齐
  + description prepended: "节奏：5/29 / 6/17-18 / 7月 / 二测期; scope：含创作者激励配套打包"
Rules fired: R2 (4 dates), R4 (list parens), R5 (+ sequential same gate)
```

```
BEFORE: 厦差0525 \| {{USER_NAME}} × 小K 内部 1h 协同会（议程分工 + 应急流程 + 接待规格）
AFTER:  厦差0525 \| 内部 1h 协同会
  + description prepended: "scope：议程分工 + 应急流程 + 接待规格"
Rules fired: R3 ({{USER_NAME}} + 小K ∈ assignees), R4 (list parens)
```

```
BEFORE: 厦差0525 \| 跟小K confirm 同行 + 5/24 内部协同会档期
DECISION: SPLIT-CANDIDATE — distinct gates (confirm trip vs. lock meeting slot). Do not auto-rewrite. Surface for split.
Rules fired: R5 (split-candidate)
```

```
BEFORE: 沪差0519 \| TapTap 评分运营标准动作询问（黄岩松线）
AFTER:  (no change) — single qualifier parens KEPT, no other rules fire
Rules fired: none
```

## When This Rule Triggers

**On task creation** (`/task-capture` and any skill that calls it): apply rules in dry-run mode while drafting title. If the title would violate R1–R6, restructure before writing.

**On retroactive rename** (e.g., `/task-rename-sweep` ad-hoc or quarterly cleanup): apply rules across all open task surfaces. Surface SPLIT-CANDIDATE and VAGUE-SURFACE for user review.

**On `/inbox-process`**: opportunistically apply rules when promoting Inbox → project surface (free rename moment).

## Migration History

- **2026-05-21** — Rules captured after retroactive sweep across {{PROJECT_A}}/{{ORG_B}}/Personal/Inbox surfaces. Post-Operon migration revealed many tasks carried over old prose-y titles (dates / assignees / scope lists in title). Sweep performed via this rule's per-line decision tree.
