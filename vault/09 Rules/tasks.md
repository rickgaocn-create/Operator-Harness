---
layer: mixed
paths:
  - "06 Tasks/**/*.md"
  - "03 Projects/*/Tasks.md"
plugins:
  - Operon (hasanyilmaz) — `{{key:: val}}` syntax · canonical source of truth
  - Day Planner (OG) — HH:mm time-blocks in daily note (deferred to v3 migration)
  - Task Collector (ebullient) — status cycling hotkey (kept for ergonomics)
canonical_skill: ".claude/skills/task-capture/SKILL.md"
created: 2026-05-13
last-major-rewrite: 2026-05-21
supersedes:
  - "[[_archive/ticktick.md]]"
  - "[[_archive/tasks-v1-pre-operon-2026-05-21.md]]"
operon-migration-plan: "[[(C) operon-full-migration-plan-v2-2026-05-23]]"
---

# Tasks Pillar Rules v2 · Operon-native 任务系统约定

> Cross-cutting contract for all task surfaces. Tasks live in **per-project Kanban files** (**`03 Projects/<name>/Tasks.md**`) for execution, with `**06 Tasks/Inbox.md**` as raw capture pool and `**06 Tasks/Today.md`** as a hand-curated daily "Today" board. Operon `{{key:: val}}` syntax is canonical — Markdown is source of truth.

## Why this shape (2026-05-21 rewrite)

The 2026-05-21 migration from Tasks plugin emoji syntax to Operon was driven by:
1. **Unified surface for Finder / Kanban / Calendar.** Operon's Task Finder, status-lane Kanban, and Time Grid Calendar all read the same `{{}}` syntax — no more cognitive context switch between plugins.
2. **`{{operonId}}` enables cross-file identity.** Tasks moved Inbox → Project Kanban → Daily keep the same identity; Action chain joins are stronger.
3. **Status as canonical field (not lane).** Status lives in the task body as `{{status:: Project.<lane>}}` — moving a task = updating the field, not editing positional ordering. Kanban view renders status visually but isn't the source of truth.

Older history: 2026-05-13 migration from TickTickSync → Tasks plugin emoji, see [[_archive/tasks-v1-pre-operon-2026-05-21.md]] for the emoji-era contract.

## File Routing

> **All 5 surfaces below are equal-status canonical task stores.** Per-project **`03 Projects/<name>/Tasks.md**` files are NOT subordinate to `**06 Tasks/**` — they're peers. `**06 Tasks/**` holds **cross-project pool surfaces** (Inbox · Today · Personal) that don't belong to a single project; `**03 Projects/<name>/Tasks.md`** holds **project-scoped surfaces**. Operon indexes all of them uniformly via `{{operonId}}`; folder structure is for human cognition only.

| File | Purpose | Source of truth for |
|---|---|---|
| **`03 Projects/{{PROJECT_A}}/Tasks.md`** | {{PROJECT_A}} project surface | `#{{PROJECT_A}}发行` / `#{{PROJECT_A}}情报` / `#{{PROJECT_A}}ai` atomic tasks |
| **`03 Projects/{{ORG_B}}/Tasks.md`** | {{ORG_B}} project surface | `#{{ORG_B}}` / `#aix` atomic tasks |
| **`06 Tasks/Personal.md`** | Personal surface | `#nonsense` + life-admin tasks |
| **`06 Tasks/Today.md`** | 🌅 Today board | Hand-curated daily, pulled from project surfaces (renamed from `Tasks.md` 2026-05-21 to disambiguate from per-project **`<Project>/Tasks.md`**) |
| **`06 Tasks/Inbox.md`** | Raw capture pool | Unsorted intake (`/daily-wechat-ingest`, mid-conversation drops). Triaged daily into project surfaces. |

**Section headers** in each surface remain as visual organization but are NOT the source of truth — Operon reads `{{status}}` field. Headers still help humans skim. Convention:

| Section header (visual) | Operon `{{status}}` field |
|---|---|
| `## ⚠️ Overdue` | `Project.Overdue` |
| `## 🔺 This Week` | `Project.ThisWeek` |
| `## ⏫ Soon` | `Project.Soon` |
| `## 🔼 Later` | `Project.Later` |
| `## 🔽 Backlog` | `Project.Backlog` |
| `## ✅ Done` | `Project.Done` |

(Section emoji are decorative only after Operon migration — Operon's Kanban view reads `{{status}}`.)

## Task Line Format

```
- [ ] [chain-anchor] | [step] #context-tag {{operonId:: <7char>}} {{status:: Project.ThisWeek}} {{priority:: 2}} {{dateDue:: 2026-05-30}} {{datetimeCreated:: 2026-05-21T16:00:00}} {{datetimeModified:: 2026-05-21T16:00:00}}
```

| Element | Rule |
|---|---|
| `- [ ]` | Always unchecked on creation. Operon (or Task Collector) cycles state. |
| `[chain-anchor] \| [step]` | For chain members. Standalone tasks use bare imperative. Timed work prefix `[HH:MM]` for Day Planner pickup. |
| `#context-tag` | Optional inside a project surface (visual only); required in `Inbox.md` to enable routing. |
| `{{operonId:: <7char>}}` | 7-char alphanumeric · auto-generated · cross-file identity · **immutable** |
| `{{status:: Project.<lane>}}` | One of: Backlog / Later / Soon / ThisWeek / Overdue / Done / Dropped |
| `{{priority:: <label>}}` | `0` extreme · `1` urgent · `2` high · `3` medium-default · `4` low · `5` very low · `/` dormant. **Status-priority parity recommended** (see table below). |

### Status–Priority parity (default heuristic for new tasks)

When capturing a new task and the user doesn't override, derive priority from the status to keep the spread balanced:

| Status | Default priority | Reasoning |
|---|---|---|
| `Project.Overdue` | `0` | already late · extreme |
| `Project.ThisWeek` | `1` | this-week commitment · urgent |
| `Project.Soon` | `2` | within 30 days · high |
| `Project.Later` | `3` | within 90 days · medium |
| `Project.Backlog` in project files | `4` | deliberately deferred · low |
| `Project.Backlog` in **`06 Tasks/Inbox.md`** | `5` | raw untriaged capture · very low |
| `Project.Dropped` | `/` | dormant · parked |
| `Project.Done` | preserve pre-completion priority | historical signal |

User can override (e.g. a Soon-status task that's actually urgent → priority `1`). The parity is the DEFAULT, not a hard rule. Original Tasks-plugin emoji mapping (🔺→`1`, ⏫→`2`, 🔼→`3`, 🔽→`4`) remains for reading historical lines.
| `{{dateDue:: YYYY-MM-DD}}` | ISO date. Operon Calendar Time Grid pins to this. |
| `{{dateScheduled:: ...}}` | Optional. When work begins. |
| `{{dateStarted:: ...}}` | Optional. When work was started. |
| `{{datetimeCreated:: YYYY-MM-DDTHH:MM:SS}}` | Auto-stamped by Operon on creation. |
| `{{datetimeModified:: YYYY-MM-DDTHH:MM:SS}}` | Auto-stamped on each edit. |
| `{{dateCompleted:: YYYY-MM-DD}}` | Set on status → Done. |
| `{{contexts:: a; b; c}}` | LIST — chain-anchor membership + functional area. **Separator: `; ` (semicolon-space)** per Operon parser. NOT comma. |
| `{{assignees:: {{USER_NAME}}; 小K}}` | LIST — same separator. Default `{{USER_NAME}}`. |
| `{{estimate:: 60}}` | NUMBER — task time estimate in minutes. Default 30. |
| `{{parentTask:: <operonId>}}` | TEXT — reference to parent task by operonId (skip if no actual hierarchy). |

### Operon parser gotchas (2026-05-21 discovered)

1. **List fields use `; ` separator, not `,`.** Source: `main.js` L17 — `"list" && n ? n.split("; ").map(a => a.trim())`. A comma-separated value is stored as a single text string, breaking Kanban/Finder filters that expect list semantics.
2. **Inline hashtags are ASCII-only.** Operon's tag regex is `/#([a-zA-Z0-9_\-/]+)/g` (main.js L11). Chinese tags like `#{{PROJECT_A}}发行` `#{{PROJECT_A}}情报` `#{{PROJECT_A}}ai` do NOT match → never indexed. Only ASCII tags (`#{{ORG_B}}`, `#aix`, `#nonsense`) work as filterable.
3. **Workaround for CN-tag concepts**: mirror them into `{{contexts:: {{PROJECT_A}}发行; 厦差0525; @trip-XM; ...}}` where they ARE filterable. Inline `#{{PROJECT_A}}发行` in body is decorative-only post-Operon.
4. **Tags field via inline `{{tags:: ...}}`** untested — Operon may support explicit YAML-frontmatter-style tags, but the safe path is contexts mirroring.

### Priority emoji legacy mapping (for reading historical context only)

| Pre-Operon emoji | Operon `{{priority}}` |
|---|---|
| 🔺 | `1` |
| ⏫ | `2` |
| 🔼 | `3` |
| 🔽 | `4` |

(Don't write emoji priorities in new tasks. They're not parsed by Operon. Priority labels per **`.operon/priorities.json`**: `0/1/2/3/4/5` + `/` for dormant. For default priority assignment on new tasks, see Status–Priority parity table above.)

### Description block (anchor task only)

Indent additional context under the task line. Operon renders the indent block as the inline card body:

```
- [ ] 广州工美 PO | 打样完成 + 工艺确认 #{{PROJECT_A}}发行 {{operonId:: a3k7z9p}} {{status:: Project.Soon}} {{priority:: 2}} {{dateDue:: 2026-05-08}} {{datetimeCreated:: 2026-05-21T16:00:00}} {{datetimeModified:: 2026-05-21T16:00:00}}
  合作已敲定，规模小、不升管理层层级，聚焦执行。
  关联：[[广州工美（广轻控股集团）]]
```

## Context Tag Registry

| Tag | Track | Routes to |
|---|---|---|
| `#{{PROJECT_A}}发行` | {{PROJECT_A}} BD, partnerships, delivery | **`03 Projects/{{PROJECT_A}}/Tasks.md`** |
| `#{{PROJECT_A}}情报` | Competitive intel, GR, channel scans | **`03 Projects/{{PROJECT_A}}/Tasks.md`** |
| `#{{PROJECT_A}}ai` | AI vendors / PoC inside {{PROJECT_A}} | **`03 Projects/{{PROJECT_A}}/Tasks.md`** |
| `#{{ORG_B}}` | {{ORG_B}} M&A track | **`03 Projects/{{ORG_B}}/Tasks.md`** |
| `#aix` | {{ORG_B}} AIX vendor / solution | **`03 Projects/{{ORG_B}}/Tasks.md`** |
| `#nonsense` | Low-stakes admin / comms replies | **`06 Tasks/Personal.md`** |

**New tag → propose explicitly on first use; confirm before reusing.**

## Chain Anchors (Action ↔ Task Binding)

Action files in **`10 Action/`** declare `chain-anchor:` in frontmatter (e.g. `蜜雪联动`, `沪差0514`). Atomic tasks in project surfaces use it as `[主项]`:

```
- [ ] 蜜雪联动 | 内部三方对齐 GO/NO-GO #{{PROJECT_A}}发行 {{operonId:: ...}} {{status:: Project.Soon}} {{priority:: 2}} {{dateDue:: 2026-04-30}} ...
```

Action file's `## Linked Tasks` Dataview block auto-renders bound tasks across all surfaces. **`chain-anchor` is immutable.**

**`{{operonId}}` is also immutable** — once written, never change. It's how Operon tracks identity across file moves. If you need to retire a task, set `{{status:: Project.Dropped}}` rather than delete.

## Day Planner Integration (v3 hybrid · since 2026-05-21 PM)

Daily note (**`04 Notes/daily notes/{date}.md`**) carries a dedicated `## Day Planner` section. Two plugins consume it simultaneously:
- **Day Planner (OG)** reads `HH:mm task` time-blocks for the status-bar "next item" indicator + sidebar timeline.
- **Operon Calendar Time Grid** reads `{{datetimeStart}}` for the day-grid render.

**v3 hybrid syntax (additive, non-breaking):**

```markdown
## Day Planner
<!-- Day Planner (OG) + Operon Calendar Time Grid 双读 · syntax: - [ ] HH:mm task {{datetimeStart:: YYYY-MM-DDTHH:mm:00}} (v3 hybrid since 2026-05-21) -->

- [ ] 09:30 改 xlsx 3 处占位 + 发申请邮件 {{datetimeStart:: 2026-05-22T09:30:00}}
- [ ] 11:30 BREAK
- [ ] 14:00 B站「跨次元营销沙龙」 {{datetimeStart:: 2026-05-22T14:00:00}}
- [ ] 16:00 BREAK
- [ ] 18:00 END
```

Rationale (v3 Phase A · 2026-05-21):
- Day Planner OG regex `^- \[(.)\] (\d{2}:\d{2}) (.+)$` still matches — the trailing `{{datetimeStart}}` is just part of "task body" from OG's perspective.
- Operon Calendar Time Grid reads `{{datetimeStart}}` and renders the time-block.
- Both plugins live; no UI disablement yet. Phase B (post-trip 5/27+): observe whether OG remains useful or Operon Calendar fully replaces it. Phase C: drop one plugin if redundant.

**Allowed Operon fields on Day Planner lines:**
- `{{datetimeStart:: YYYY-MM-DDTHH:mm:00}}` — REQUIRED on task lines (not BREAK / END).
- `{{datetimeEnd:: YYYY-MM-DDTHH:mm:00}}` — OPTIONAL. Add only when duration is known and meaningful (e.g. 60-min meeting block); skip otherwise.

**Banned Operon fields on Day Planner lines** (those belong on the canonical project surface task line, not the transient time-block view):
- `{{operonId}}`, `{{status}}`, `{{priority}}`, `{{dateDue}}`, `{{contexts}}`, `{{assignees}}`, `{{estimate}}`, `{{parentTask}}`, `{{datetimeCreated}}`, `{{datetimeModified}}`, `{{dateCompleted}}`.

Day Planner task lines DO carry `{{operonId}}` (v3 Phase A 2026-05-21 PM correction — without operonId, Operon's indexer ignores the line entirely, breaking Calendar Time Grid rendering). The operonId on a Day Planner line is a **fresh, separate task identity** from the canonical project-surface task (NOT a duplicate of it) — Day Planner remains the **time-block transient view**, project surface remains the **canonical task**, and `/sync-day` reconciles `[x]` toggles across via fuzzy text match + chain-anchor + wikilink. Future enhancement (Phase 4 of 2026-05-21 daily-note overhaul): make Day Planner lines reference the canonical surface task's operonId directly so the two share identity.

| Requirement | Rule |
|---|---|
| Time format on task line | `HH:mm` 24-hour, **no brackets** + matching `{{datetimeStart:: <today>THH:mm:00}}` |
| `HH:mm` ↔ `{{datetimeStart}}` parity | Always equal. When moving an item to a new time, BOTH must update (skill writes do this atomically). |
| Position | Top-level checkbox only; indented children are sub-tasks |
| `BREAK` keyword | `- [ ] HH:mm BREAK` — plain, no Operon block (not a task) |
| `END` keyword | `- [ ] HH:mm END` — plain, no Operon block (day terminator) |

### Day Planner contract (revised 2026-05-13 · v2 unchanged)

Day Planner is **input-curated, output-reconciled.** Two write paths in, one reconciliation pass out.

**Input paths:**
1. **Morning curation** — manual copy from **`06 Tasks/Today.md`** 🌅 Today board into daily note `## Day Planner` with `HH:mm` prefixes.
2. **Mid-day scheduling** — `/task-capture --schedule HH:mm <task> #tag` OR a task whose text begins with `[HH:mm]` auto-inserts a `- [ ] HH:mm <task>` line into today's Day Planner.

**Output path:**
- **EOD reconciliation** — `/daily-note --close` reads each Day Planner checkbox and walks user through shipped/slipped/partial. On shipped → updates the matching project surface task's `{{status}}` to `Project.Done` + sets `{{dateCompleted}}`. On slipped → leaves source task as-is and logs to daily note's "Slipped" line.

**Closure semantics:**
- `completePastItems: false` is canonical. The plugin **must not** auto-toggle by time-elapse.
- Bare Inbox captures (no time prefix, no schedule flag) do NOT auto-insert into Day Planner.

## Task Collector (TC) Hotkeys

Configured in plugin settings (defaults shown):
- `Ctrl+;` → cycle `[ ]` → `[/]` → `[x]` → `[-]`
- `Ctrl+Shift+;` → collect completed `[x]` into `## ✅ Done` section

**Important under Operon**: TC cycles the checkbox state, but the `{{status}}` field is NOT auto-updated by TC. To fully transition a task to Done in Operon, you should also set `{{status:: Project.Done}}` and `{{dateCompleted:: YYYY-MM-DD}}` — Operon UI does this automatically when you change status via its right-click menu. If you only use TC's Ctrl+;, the checkbox flips but Operon's status stays "out of sync" with the checkbox.

**Recommendation for v2**: prefer Operon's right-click `Set Status` over TC for canonical status changes. Use TC for quick `[x]` ticks where status update can wait.

## Hard Rules (v2)

- **Don't fabricate** `{{operonId}}` values manually. Operon generates them; skills must use a 7-char alphanumeric generator if writing new tasks via Edit tool.
- **Don't toggle** `- [ ]` → `- [x]` without explicit user request. Closures are decisions.
- **Don't bulk-rewrite** an entire surface file. Edit task by task (preserves `{{datetimeModified}}` accuracy).
- **One task = one decidable unit.** Multi-step → chain by `[anchor] | [step]`.
- **Inbox.md is for raw capture only.** Anything with a `#context-tag` should be moved to its project surface within 24h.
- **Never write emoji syntax in new tasks.** Operon doesn't parse emoji — they become dead text. Use `{{}}` form only.
- **Batch ceiling: ≤3 new tasks per single Write.** Preserves capture quality.
- **`{{operonId}}` is immutable.** Once a task has one, never change it.
- **`{{datetimeModified}}` should update on EVERY edit** to a task line. Skills writing edits should refresh this field.

## Cadence

| Trigger | Action |
|---|---|
| Morning (~09:00) | Glance Operon Kanban `Overdue` + `ThisWeek` lanes; hand-curate **`06 Tasks/Today.md`** 🌅 Today board |
| Throughout day | New tasks → `Operon: New Inline Task` (lands in Inbox.md) OR direct to project surface via skill |
| End of day | TC "Move completed to bottom" on each surface touched today |
| Friday EOD | `/inbox-process` — triage Inbox.md raw items into project surfaces; reschedule overdue |
| Weekly | `/sanity` — health audit |

## Operon Filter Embeds (2026-05-21 PM addition)

Operon supports inline filter views via a code-block fence — the daily note (and any other markdown file) can render live task queries that re-evaluate on every render against the current Operon index. The embed syntax:

```
` ` `operon
filter: "<saved filterSet name>"
` ` `
```

or by ID:

```
` ` `operon
filterId: "<filterSet id>"
` ` `
```

FilterSets are stored as JSON files in **`.operon/filters/<id>.json**` and indexed by `**.operon/filters/index.json`**. Each filter has a `rootGroup` with nested condition/group children. Conditions take the shape `{id, field, fieldType, operator, value?}` where `fieldType` matches the field's type from **`.operon/key-mappings.json`** (text / date / datetime / number / list / checkbox).

Field operators by type (discovered 2026-05-21):
- **checkbox**: `isOpen`, `isDone`, `isCancelled`
- **date**: `dateIs`, `before`, `after`, `isToday`, `notToday`, `beforeToday`, `afterToday`, `exactlyDaysAgo`, `exactlyDaysAway`, `underDaysAgo`, `underDaysAway`, `overDaysAgo`, `overDaysAway`

Production filterSets (provisioned 2026-05-21 PM for daily-note overhaul):

| Filter | File | Used by |
|---|---|---|
| `Daily Drum (today + overdue · open)` | **`.operon/filters/fs_daily_drum.json`** | Daily note § Top 3 Priorities embed |
| `Shipped Today` | **`.operon/filters/fs_shipped_today.json`** | Daily note § EOD Review embed |
| `Slipped (overdue · open)` | **`.operon/filters/fs_slipped.json`** | Daily note § EOD Review embed |
| `Carry Forward (tomorrow)` | **`.operon/filters/fs_carry_forward.json`** | Daily note § EOD Review embed |

**Trade-off**: live embeds reflect current state on every render (good for working-day truth), but historical dailies don't preserve a point-in-time snapshot. `/daily-note --close` Phase 7 freezes the embed result into HTML-comment snapshot lines so closed dailies retain audit-trail value.

**Pre-flight before authoring new filter JSON**: read **`.operon/key-mappings.json**` for canonical field names + types, and use one of the operator strings above. Validate by adding the filter and embedding it in `**04 Notes/_sandbox/operon-embed-test.md`** first.

## Companion rules

- [[09 Rules/task-naming.md]] — title authoring (R1–R7: char cap, date/assignee/scope stripping, multi-action split, dup channel, vague verb). Applied at draft time by `/task-capture` and at retroactive sweep time.

## Skill Hand-offs

| Skill | Role | Hand-off |
|---|---|---|
| `/task-capture` | Canonical workflow — decomposition, chain naming, routing, Operon syntax | Reference for ALL task writes |
| `/inbox-process` | Triage Inbox.md → project surfaces; reschedule overdue | Honors closure / reschedule rules |
| `/meeting-note` · `/meeting-note-deep` | Surface {{USER_NAME}}-owned action items as tasks | Delegate to `/task-capture` |
| `/new-project` | Seed initial project surface | Includes Operon-aware Tasks.md scaffold |
| `/okr` | Surface check-in commitments as tasks | Delegate to `/task-capture` |
| `/source-ingest` | Atomic todos discovered during ingest | Delegate to `/task-capture` |
| `/morning-sweep` | Sweep yesterday's WeChat+Feishu dialogs → 待确认 list in daily note; **confirm gate** (no auto-push) | On `--commit`, delegates kept items to `/task-capture` (≤3/Write) |
| `/weekly-update` | Task sweep | Delegate to `/inbox-process` |
| `/card-lint` | Surface task-worthy follow-ups | Delegate to `/task-capture` |
| `/sanity` | Audit (read-only) | Surface findings, don't auto-edit |

## Migration History

- **Pre-2026-05-13** — TickTickSync v1.1.17 era. Plugin disabled, syntax stripped. See [[_archive/ticktick.md]].
- **2026-05-13** — Tasks plugin emoji syntax era. Project Kanban shape (Tasks plugin + Kanban plugin). Contract preserved at [[_archive/tasks-v1-pre-operon-2026-05-21.md]].
- **2026-05-21 (PM)** — Operon `{{key:: val}}` migration. 124 tasks converted across 5 surfaces. Tasks plugin disabled, Kanban plugin disabled (frontmatter removed). Plan: [[(C) operon-full-migration-plan-v2-2026-05-23]].
- **2026-05-21 (EOD, pre-BJ trip)** — v3 Phase A · Day Planner hybrid format landed: Day Planner lines now emit `- [ ] HH:mm task {{datetimeStart:: YYYY-MM-DDTHH:mm:00}}`, allowing Day Planner OG + Operon Calendar Time Grid to both consume the same line. `/daily-emit` `/sync-day` `/replan` skills updated. Day Planner OG still ENABLED — no plugin disable in Phase A (Phase B/C deferred post-trip per trial-log review). Existing pre-2026-05-21 daily notes (incl. today's 2026-05-21.md) NOT retrofitted — only new emits use hybrid format.

## Operon Reference

- Plugin: **`.obsidian/plugins/operon/`** v1.0.2
- Configs: **`.operon/*.json`** (pipelines, priorities, key-mappings, task-creation-profile, etc.)
- Status pipeline single `Project` (configured 2026-05-21) with 7 statuses
- Priorities: S/A/B/C/D/E/F · only A/B/C/D used in practice · default = C
- Inline task target: **`06 Tasks/Inbox.md`** (no heading required — appends to file end)
- Calendar Time Grid: reads `{{dateDue}}` + `{{datetimeStart}}` + `{{datetimeEnd}}`
- Task Finder: reads everything with `{{operonId}}`
