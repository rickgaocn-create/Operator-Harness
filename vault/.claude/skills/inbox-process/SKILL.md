---
category: work
name: inbox-process
description: Triage 00 Raw files and 06 Tasks/Inbox.md. Use to file raw notes, route stale items, and clean the inbox before weekly review or /compress.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
# Skill: Inbox Process

Triage unprocessed files in **`00 Raw/**` and open tasks in `**06 Tasks/Inbox.md`**. File things where they belong, reschedule what's stale, close what's done. The job is curation — propose, get approval, then execute. Never bulk-move on assumed intent.

## When to Use

- "Process my inbox", "clear inbox", "file my raw notes", "triage tasks"
- **`00 Raw/`** is accumulating unsorted content
- Weekly processing session (typically Friday EOD pre-review)
- Before `/compress` — clean state makes the session log cleaner

## How It Works

1. Scan **`00 Raw/`**, propose destinations
2. Triage **`06 Tasks/Inbox.md`** for overdue / stale / untagged
3. Execute approved actions only — anything ambiguous gets flagged, not guessed

---

## Phase 1: Scan Raw Folder

```bash
ls "00 Raw/"
```

For each file, read the first ~10 lines to infer content. Map to a destination using:

| Content | Destination |
|---|---|
| {{PROJECT_A}} BD partners · press · channel · MCN · govt | **`03 Projects/{{PROJECT_A}}/`** |
| {{ORG_B}} M&A targets · AIX vendors · JP market intel | **`03 Projects/{{ORG_B}}/`** |
| External research, AI papers, industry reports | **`01 Wiki/`** |
| Working notes, raw analysis, thinking-out-loud | **`04 Notes/`** |
| Web clippings, screenshots, saved articles | `Clippings/` |
| Already-processed PDFs/images used as one-off reference | Archive outside vault, or delete |

Present the routing table to the user:

> "Found [n] files in 00 Raw/. Proposed routing — confirm or redirect before I move anything:"

Only move after explicit confirmation. When the inferred type is genuinely unclear (mixed-content notes, fragmentary captures), surface it as "uncertain — leave for manual" rather than guessing.

---

## Phase 2: Task Triage

Read **`06 Tasks/Inbox.md`**. Cluster the open tasks:

- **Overdue** — `{{dateDue:: YYYY-MM-DD}}` is before today
- **Stale** — no `{{dateDue}}`, content suggests it's outdated or superseded
- **Untagged** — missing `#context-tag`, unclear which track it belongs to

Present clusters:

> "In Inbox: [n] overdue, [n] stale, [n] untagged. Quick triage — reschedule, close, or keep?"

### Hard rules

- **Never toggle `- [ ]` → `- [x]` without explicit user instruction.** Closure is a decision.
- **Reschedule = edit the existing `{{dateDue:: YYYY-MM-DD}}` field in place + refresh `{{datetimeModified}}`.** Don't duplicate the task with a new date.
- **Add a tag = edit the existing line in place.** Same reason.
- **Triage = move to project Kanban** per [[09 Rules/tasks.md]] routing. Tagged tasks (`#{{PROJECT_A}}*` / `#{{ORG_B}}` / `#aix` / `#nonsense`) should leave `Inbox.md` and land in the appropriate Kanban file within the same triage pass. **Move preserves `{{operonId}}`** — never regenerate when relocating a task.
- **On move: update `{{status:: Project.<lane>}}`** to match the destination section + refresh `{{datetimeModified}}`.
- **Don't fabricate** `{{dateCompleted:: YYYY-MM-DD}}` stamps. Operon/Task Collector owns those on `[x]` cycle.

---

## Phase 3: Execute Approved Actions

After user confirms, execute in this order:

1. Move/rename files in **`00 Raw/`**.
2. Update tasks in **`06 Tasks/Inbox.md`**.
3. Anything uncertain → leave in place, list at the end of the report so the user can handle it manually.

Close with:

> "Done: [n] files filed, [n] tasks updated. [n] items flagged for manual review."
