---
layer: platform
paths:
  - "10 Action/**/*.md"
pillar: Action · 任务笔记
method: Bullet/Danmaku · 弹幕笔记法
---

# Action Pillar Rules · 任务笔记约定

> Active work focus — the "Doing" layer. Days–weeks decay. One file = one workstream.

## Purpose

Capture **what's in motion right now** — not project artifacts (those live in **`03 Projects/`**), not atomic tasks (those live in per-project Kanbans per [[09 Rules/tasks.md]]). Action files are the **workstream view**: a rolling stream of context, decisions, blockers, and execution notes for one thread of work.

**Mental model:**
- **`03 Projects/{{PROJECT_A}}/`** = the project's permanent reference library
- **`03 Projects/{{PROJECT_A}}/Tasks.md`** = atomic tasks for {{PROJECT_A}} (Kanban board, urgency-laned)
- **`06 Tasks/Inbox.md`** = raw capture pool (triaged daily into project Kanbans)
- **`10 Action/12 Active/T260427-honor-second-round.md`** = **the workstream itself** — the rolling log of what's happening on this thread

## Folder Structure (Horizon-Major)

```
10 Action/
├── 11 12-Week/              Tied to current 12-week OKR. Strategic.
├── 12 Active/               In motion this week, not necessarily on OKR.
├── 13 Maybe/                Parked, not killed. Review monthly.
└── _archive/                Closed workstreams, moved here on completion.
```

**Triage logic:**
- Ladders to a Q2 OKR? → `11 12-Week/`
- Active this week, but tactical / opportunistic? → `12 Active/`
- Surfaced but no slot to act on it? → `13 Maybe/`
- Done, won, or killed? → `_archive/`

Move files between folders as horizon changes. The folder is the status.

## Naming Convention

```
T{YYMMDD}-{kebab-case-slug}.md
```

- **T** — file-type prefix (Task / Track)
- **YYMMDD** — 6-digit creation date
- **slug** — workstream identity, 2–5 words

**Examples:**
- `T260424-honor-channel-first-round.md`
- `T260427-mna-screening-criteria-v1.md`
- `T260425-helen-japan-network-mapping.md`

## Frontmatter Contract

```yaml
---
type: action
created: 2026-04-27
project: {{PROJECT_A}}                  # {{PROJECT_A}} / {{ORG_B}} / cross-border / ops
horizon: active                # 12week | active | maybe | archive
okr-link: "[[2026-Q2#KR2]]"    # required if horizon = 12week
status: open                   # open | blocked | done
owner: {{USER_NAME}}                      # {{USER_NAME}} / external counterparty
next-action: "Send brief to {{PERSON}} EOD"
---
```

## File Anatomy

```markdown
# {Workstream name}

> One-line: what this thread is about, who's the counterparty, what's the goal.

## Context
Background. Why this exists. What sparked it.

## Stream
<!-- Danmaku / rolling capture. Newest at top. Date-stamped. -->

### 2026-04-27
- Brief drafted, sent to {{PERSON}}
- Pre-eval meeting locked for 4-28 14:00

### 2026-04-26
- {{PERSON_3}} confirmed second round of interest, wants commercials by 4-30

## Decisions
<!-- Workstream-internal, tactical decisions only. Strategic / forwardable / cross-workstream / irreversible calls
     get a standalone file in 05 Decisions/ (see [[09 Rules/decisions.md]] § Boundary) — link to it here, don't copy. -->
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-25 | Skip 鸿蒙 channel first | Honor + Huawei separation reduces overlap |

## Blockers / Open Questions
- [ ] What's {{PERSON}}'s authority ceiling on rev share?

## Linked Cards
- [[C260424-honor-channel-fills-android-gap-not-harmonyos]]

## Linked Tasks
- See `06 Tasks/Inbox.md` for atomic items tagged `#{{PROJECT_A}}发行`
```

## Flow Rules

| Trigger | Action |
|---------|--------|
| New workstream surfaces | Create file in `12 Active/` (default) |
| Workstream maps to Q2 OKR | Move to `11 12-Week/`, add `okr-link:` frontmatter |
| Workstream stalls > 2 weeks with no external dep | Move to `13 Maybe/`, write a "why parked" note |
| Workstream closes (won, killed, or merged into project) | Move to `_archive/`, mark `status: done`, harvest cards |
| Atomic next-step emerges | Capture in project Kanban (or Inbox.md if cross-project) per [[09 Rules/tasks.md]]; do NOT scatter atomic todos inside Action files |

## Boundary with **`03 Projects/`**

Action files are **operational** — they die when the workstream closes. Project files are **permanent** — partnership briefs, contracts, deal memos, market reads.

Rule of thumb:
- Will I look at this in 6 months? → Project
- Is this "what's happening this week on this thread"? → Action

When a workstream closes, distill the operational log into:
1. A Card (the lesson)
2. Updated project files (the artifact)
3. Archive the Action file

## Task Binding · Action ↔ Project Kanban

Action files describe **the workstream**. Atomic todos for that workstream live in the relevant project Kanban (**`03 Projects/<project>/Tasks.md**` or `**06 Tasks/Personal.md`**) per [[09 Rules/tasks.md]]. Binding mechanism:

### 1. Declare a chain anchor in Action frontmatter

```yaml
chain-anchor: 荣耀二轮          # short CN/EN identifier, becomes [主项] in Kanban task lines
```

Pick a stable, compact label (2–6 chars CN, or kebab-case EN). Once declared, do not change — it's the join key.

### 2. Tasks use chain anchor as `[主项]`

Per [[09 Rules/tasks.md]] task line format:
```
- [ ] 荣耀二轮 | 分成议价底线 内部 alignment #{{PROJECT_A}}发行 🔼 📅 2026-04-28
- [ ] 荣耀二轮 | commercial frame draft 给{{PERSON_3}} #{{PROJECT_A}}发行 ⏫ 📅 2026-04-30
```

The `荣耀二轮` prefix = `chain-anchor` from the Action file. This is the binding contract.

### 3. Action file pulls live tasks via Dataview

In the Action file's `## Linked Tasks` section:

````markdown
## Linked Tasks (live)

```dataview
TASK
FROM "03 Projects/{{PROJECT_A}}" OR "03 Projects/{{ORG_B}}" OR "06 Tasks"
WHERE contains(text, "荣耀二轮")
```
````

This auto-renders open + completed tasks bound to this workstream across all Kanban surfaces. Always live, no manual maintenance.

### 4. When closing a workstream

Before moving file to `_archive/`:
1. Confirm all `chain-anchor` tasks in the relevant project Kanban are closed (in `✅ Done` lane) or migrated
2. Snapshot the final task list in the Action file (replace Dataview block with static `- [x]` lines for historical record)
3. Harvest Cards, then archive

---

## Auto-Creation Policy

**Never auto-spawn Action files.** When a workstream surfaces in conversation (e.g., "I need to chase 吉田 on JP governance"), Claude:

1. Recognizes the workstream pattern (counterparty + open loop + ≥2-step trajectory)
2. **Proposes** the file: "Want me to spawn `T{date}-yoshida-jp-governance.md` in `12 Active/`? It would carry: {context summary}"
3. Waits for explicit go-ahead before writing

Exceptions: NONE. Even obvious workstreams require user approval. This is the "patch don't paraphrase" principle applied to the Action pillar.

Trigger phrases that should prompt the proposal:
- "I need to chase / follow up / circle back on..."
- "Let me track {counterparty} on..."
- "We're in motion with {entity} — need to..."
- Multi-step commitment with date + counterparty + open question

---

## Hard Rules

- **One workstream per file.** Don't bundle "honor + {{ORG_F}} + helen" into one Action file. Three workstreams → three files.
- **Stream is append-newest-at-top.** Reverse-chrono. So you read latest state first.
- **Atomic todos go to the project Kanban (or **`06 Tasks/Inbox.md`** if cross-project), not buried in Action stream.** Action stream is for context; Kanban is for the doing. Bind via `chain-anchor`.
- **Don't create new files in **`03 Projects/`** from Action.** Promote artifacts when they stabilize, not while the workstream is hot.
- **Never auto-create Action files.** Propose, wait, then write (see Auto-Creation Policy above).
- **`chain-anchor` is immutable.** Once declared and used in any Kanban, do not rename — breaks the join.
