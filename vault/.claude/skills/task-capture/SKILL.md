---
category: work
name: task-capture
description: Capture and decompose tasks into the correct project Kanban or 06 Tasks/Inbox.md per 09 Rules/tasks.md. Use for follow-ups, batch task capture, and strategic next steps.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
# Skill: Task Capture & Decomposition

Write tasks to the right surface per the contract in [[09 Rules/tasks.md]], with decomposition that makes progress trackable rather than monolithic. The goal isn't "more tasks" — it's making each row a checkpoint where reality reveals itself.

> **Contract reference:**
> - [[09 Rules/tasks.md]] — canonical task line format, file routing, hard rules, batch ceiling
> - [[09 Rules/task-naming.md]] — title authoring rules (R1–R7: char cap, date/assignee/scope stripping, multi-action split, dup channel, vague verb). Apply at draft time before writing.
>
> This skill operationalizes those contracts through decomposition heuristics and a routing workflow. When a rule file and this skill disagree, the rule file wins.

## When to Use

- User says "add this as a task", "track this", "create follow-ups", "拆解 / 分解任务"
- End of a strategic session → "Next Tactical Steps" get captured as routed tasks
- A captured commitment has a multi-step rhythm (节奏) spanning weeks/owners — decompose it
- Project Kanban review reveals opaque umbrella tasks — refactor them
- **Mid-day scheduling** — user invokes `/task-capture --schedule HH:mm <task> #tag` OR a task text begins with `[HH:mm]`. In addition to the normal Kanban write, the task is inserted into today's `## Day Planner` block (see Mid-day Scheduling section below).

For triage, close, or reschedule of *existing* tasks → use `/inbox-process` instead. For bulk writes without pause discipline → don't (see batch ceiling in [[09 Rules/tasks.md]]).

---

## Principles

1. **One task = one decidable unit.** Multiple owners, dates, or gating conditions = chain, not task.
2. **Decompose by node, not by activity.** Each sub-task = checkpoint where reality reveals itself (deliverable, confirmation, gate). Not "work on X" verbs.
3. **Title scans, description carries weight.** Title for Kanban card-face. Indented description carries the why + links.
4. **Route by tag.** Tag determines file. No tag = raw capture in Inbox; tagged = direct to project Kanban.

---

## Routing Decision (route by `#context-tag`)

| Tag | Target file | `{{status}}` heuristic from `{{dateDue}}` |
|---|---|---|
| `#{{PROJECT_A}}发行` / `#{{PROJECT_A}}情报` / `#{{PROJECT_A}}ai` | **`03 Projects/{{PROJECT_A}}/Tasks.md`** | dateDue ≤ today+7 → `Project.ThisWeek` · ≤ today+30 → `Project.Soon` · ≤ today+90 → `Project.Later` · else `Project.Backlog` · dateDue < today → `Project.Overdue` |
| `#{{ORG_B}}` / `#aix` | **`03 Projects/{{ORG_B}}/Tasks.md`** | Same logic |
| `#nonsense` | **`06 Tasks/Personal.md`** | Same logic |
| (no tag / cross-project / not sure) | **`06 Tasks/Inbox.md`** | Append to bottom · `{{status:: Project.Backlog}}` — raw capture, triaged later by `/inbox-process` |

Section header (e.g. `## 🔺 This Week`) inside the target file is visual organization — but the canonical status lives in `{{status:: Project.ThisWeek}}` on the task line. When writing a new task, place it under the matching section AND set the matching `{{status}}` field.

**Never** route a tagged task to `Inbox.md` "to be safe." Tagged tasks belong in their project Kanban; that's the whole point of typed surfaces. If the user wants the task visible TODAY across projects, they pull it into **`06 Tasks/Today.md`** 🌅 Today board manually (don't write there from this skill — that's a user-owned curation surface).

---

## Decomposition Heuristic

For any captured commitment, ask:

1. **Sequence?** Does step N unblock N+1?
2. **Different owners?** Different counterparties or functions?
3. **Different due dates?** "Done by 5/20" hides milestones on 5/5, 5/12, 5/20?
4. **Different risk profile?** Routine steps vs. gates (e.g., 打样 → 量产 → 质检 → 出库)?

Yes to any → decompose. Yes to none → keep as one.

### Naming: `[chain-anchor] | [step]`

- `chain-anchor` = chain identity, stable across all members (`广州工美 PO`, `5月路演`, `交接库激活`). Should match the bound Action file's `chain-anchor:` frontmatter if one exists.
- `step` = one checkpoint — deliverable, confirmation, or gate. Not a verb phrase.
- Pipe `|` separator scans well in Kanban card-face; chain members visually cluster.
- **Title-shape rules ([[09 Rules/task-naming.md]]):** title ≤ 30 CJK chars; no dates (→ `{{dateDue}}`); no assignee names already in `{{assignees}}`; list parentheticals → description `scope:` line; multi-action joins → split or push secondary to description `动作:` line; no leading vague verbs (`推进` / `跟进` / `处理`). Apply R1–R7 at draft time.

**Good:** `广州工美 PO | 打样完成 + 工艺确认` · `5月路演 | 档期敲定（上海 + 厦门双站）`

**Bad:** `推进工美合作` (no checkpoint, no end state). When a single line lists `→ → →` arrows, that line IS a decomposition request — break it apart.

### Worked example: 5月路演

Captured umbrella:

> 5 月路演行程落地：上海（Taptap 等）+ 厦门（4399 等）· 节奏：素材 ETA 确认 → 档期定 → 建联对齐 → 行程 / 酒店 / 机票预订

Decomposed → all under `chain-anchor: 5月路演`, all routed to **`03 Projects/{{PROJECT_A}}/Tasks.md`**:

```
- [ ] 5月路演 | 与{{PERSON}}确认试玩会素材生产 ETA（决定档期基准） #{{PROJECT_A}}发行 {{operonId:: <gen>}} {{status:: Project.ThisWeek}} {{priority:: 2}} {{dateDue:: 2026-04-28}} {{datetimeCreated:: <now>}} {{datetimeModified:: <now>}}
  路演因素材未就绪从 4 月推迟到 5 月。必须拿到{{PERSON}}书面/微信确认的素材交付时间表，据此倒排 5 月中下旬路演档期。
  关联：[[路演排期]]
- [ ] 5月路演 | 档期敲定（上海 + 厦门双站） #{{PROJECT_A}}发行 {{operonId:: <gen>}} {{status:: Project.ThisWeek}} {{priority:: 3}} {{dateDue:: 2026-04-30}} {{datetimeCreated:: <now>}} {{datetimeModified:: <now>}}
- [ ] 5月路演 | 渠道建联对齐（Taptap / 4399 / 抖音游戏 / B站等） #{{PROJECT_A}}发行 {{operonId:: <gen>}} {{status:: Project.Soon}} {{priority:: 3}} {{dateDue:: 2026-05-05}} {{datetimeCreated:: <now>}} {{datetimeModified:: <now>}}
- [ ] 5月路演 | 行程 / 酒店 / 机票预订 #{{PROJECT_A}}发行 {{operonId:: <gen>}} {{status:: Project.Soon}} {{priority:: 3}} {{dateDue:: 2026-05-08}} {{datetimeCreated:: <now>}} {{datetimeModified:: <now>}}
```

Note: ETA confirmation is `{{priority:: 2}}` (high) because downstream can't start without it. Dates cascade 4/28 → 4/30 → 5/5 → 5/8. Only the entry task carries description; the rest are self-explanatory once the chain is visible.

`<gen>` = 7-char alphanumeric (lowercase + digits) · `<now>` = current ISO datetime `YYYY-MM-DDTHH:MM:SS`. Skills MUST generate fresh values per task — never reuse.

For all line-format details (priority semantics, context tag registry, description block conventions), see [[09 Rules/tasks.md]] § Task Line Format.

---

## Write Workflow

1. **Decide routing** — for each task, pick the target file per the routing table above. Confirm with user if a tag is new (not in the registry).
2. **Read the target file** to see existing lane structure and existing chain members.
3. **Propose decomposition + lane assignment** before writing. Confirm with user when adding > 3 new tasks (batch ceiling).
4. **Set `{{status}}`** based on `{{dateDue}}` + tag's lane heuristic above. **Set `{{priority}}` via status-priority parity** (see [[09 Rules/tasks.md]] § Status–Priority parity): Overdue→`0`, ThisWeek→`1`, Soon→`2`, Later→`3`, Backlog→`4` (project) or `5` (Inbox), Dropped→`/`. User can override per task. **Generate fresh `{{operonId}}`** (7-char alphanumeric, no collisions with existing IDs in the target file). **Stamp `{{datetimeCreated}}` and `{{datetimeModified}}`** with current ISO datetime.
5. **Write with Edit (preferred) or Write.** Edit inserts into the correct lane preserving Kanban structure. Avoid Write on an existing Kanban file — it's the whole-file replace path.
6. **No post-write wait.** No external sync; the file is the source of truth. Markdown saved = task captured.

---

## Mid-day Scheduling (Day Planner Insertion)

Per **`09 Rules/tasks.md`** § Day Planner contract (revised 2026-05-13), a task can opt into today's time block at capture time via:

- **Flag form:** `/task-capture --schedule HH:mm <task text> #tag`
- **Prefix form:** task text begins with `[HH:mm]`, e.g. `[16:30] call kazuki #{{PROJECT_A}}发行`

When either trigger fires, **after** the normal Kanban write completes, also insert into today's Day Planner.

### Insertion algorithm

1. **Compute target file:** **`04 Notes/daily notes/{today YYYY-MM-DD}.md`**. If it doesn't exist, surface to user: *"Today's daily note doesn't exist yet — run `/daily-note` first, then re-capture."* Don't auto-create from this skill.
2. **Locate `## Day Planner` section** in today's note. If missing, surface and stop — don't insert into a daily note that's been deliberately authored without the section.
3. **Build the line:** `- [ ] HH:mm <task text without [HH:mm] prefix, without trailing #tags>` — tags belong on the Kanban line, not in the Day Planner block (keeps the timeline readable).
4. **Sort-insert by time** between existing items. Walk the section's `- [ ] HH:mm` lines:
   - Find the first existing line whose time is strictly greater than the new line's time → insert immediately before it.
   - If no such line (new time is later than all existing) → insert before the `END` keyword line if one exists, otherwise append to the section.
   - **Preserve** `BREAK` and `END` keyword lines verbatim — don't reorder them, don't delete them.
5. **Duplicate handling:** if an existing line shares the same `HH:mm`, surface to user: *"16:30 already has `Call with tencent Kazuki` scheduled. (a) move existing to a different slot · (b) replace existing · (c) pick a different time for the new item."* Don't silently overwrite.

### Guard rails

- **Today only.** If user passes `--schedule HH:mm` with a date that isn't today's local date, write to Kanban only and warn: *"Day Planner insertion is today-only — captured to Kanban without time block."* The plan's design rationale is to keep mid-day capture from leaking schedules onto unrelated days.
- **Combined batch ceiling.** The ≤3 new tasks rule from **`09 Rules/tasks.md`** line 152 counts Kanban + Day Planner inserts as a single combined budget. A `--schedule` task = 1 Kanban write + 1 Day Planner insert, both inside the same batch.
- **No tag → still allowed.** A scheduled task without a tag routes to **`06 Tasks/Inbox.md`** for the canonical write AND still inserts into today's Day Planner. The "user explicitly opted into a time block" signal overrides the curation gate.
- **Day Planner state preserved.** Newly inserted lines are always `- [ ]` unchecked — never pre-check based on past time, because Day Planner OG's `completePastItems` is now `false` and Day Planner state is user-authored truth.

### Confirm pattern

After both writes complete:

> Captured: `call kazuki #{{PROJECT_A}}发行 dateDue 2026-05-13` →
> - **`03 Projects/{{PROJECT_A}}/Tasks.md`** § 🔺 This Week (`{{status:: Project.ThisWeek}}` · 1 new task)
> - **`04 Notes/daily notes/2026-05-13.md`** § Day Planner, inserted at 16:30 between 16:00 BREAK and 19:00 item.

---

## Batch Ceiling: ≤3 new tasks per single Write

This is a **capture-quality gate**, not a sync-safety constraint. The discipline is: if you're about to write more than 3 tasks in one swing, the chain isn't decomposed enough OR there's a category-error (one of these isn't really a task, it's a workstream — propose an Action file instead).

For end-of-session batches > 3:
- **(a)** Decompose deeper — extract the latent chains and write each chain's anchor task first; cascade members can be queued in a follow-up Write
- **(b)** Propose an Action file for any "task" that's actually a multi-week workstream (counterparty + ≥2-step trajectory)
- **(c)** Split the writes into multiple turns with user confirm between batches

---

## Confirm Pattern

After writing, close with:

> Written to **`03 Projects/{{PROJECT_A}}/Tasks.md`** (`{{status:: Project.ThisWeek}}` · 🔺 This Week section): [n] tasks in chain `[anchor]`. Bound to [[T260427-...]] via chain-anchor + `{{operonId}}`. Total open in {{PROJECT_A}} surface: ~N.
