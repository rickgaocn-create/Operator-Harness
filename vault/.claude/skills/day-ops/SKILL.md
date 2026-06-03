---
category: ops
name: day-ops
description: Coordinates the daily operating loop. Use for day state, priority sync, replanning, inbox triage, and end-of-day digest when /operate routes into daily execution.
model: claude-sonnet-4-6
allowed-tools: Read, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/operator-intents.md]]"
  - "[[09 Rules/time.md]]"
  - "[[09 Rules/tasks.md]]"
created: 2026-05-28
created-by: codex
---

# Skill: Day Ops

Coordinate the daily operating loop as a package over the existing thin skills. This is an organ, not a replacement for the daily ledger.

## Role

Use `day-ops` when `/operate` routes to "What matters today?", day planning, mid-day replan, inbox triage, sync, or end-of-day review.

The human surface is Harness Dashboard plus `/operate`. The daily note remains the parser-stable ledger.

## Downstream Skills

| Need | Use |
|---|---|
| Create/open/update the ledger | `/daily-note` |
| Sync task and day state | `/sync-day` |
| Re-rank priorities | `/replan` |
| Triage inbox items | `/inbox-process` |
| Produce EOD digest | `/day-digest` |
| Write more than 3 tasks | `/task-capture` |

## State Contract

Read:
- `04 Notes/daily notes/{today}.md`
- `04 Notes/weekly/{iso_week}.md`
- `06 Tasks/Today.md`
- `06 Tasks/Inbox.md`
- `03 Projects/{{PROJECT_A}}/Tasks.md`
- `03 Projects/{{ORG_B}}/Tasks.md`
- `.claude/_state/dashboard/capture-inbox.jsonl`

Write only through the downstream skill that owns the target surface.

## Operating Rules

1. Treat Dashboard Today/Needs Attention and the daily note as one cockpit state.
2. Prefer read-first answers unless {{USER_NAME}} explicitly asks to change the day.
3. Never fabricate priorities when live state is missing.
4. If task, OKR, and daily surfaces disagree, state which source is newer.
5. Route task batches through `/task-capture`; do not inline large task writes.
6. Keep daily-note prose machine-readable rather than pleasant.

## Completion Gate

After changing this package or its downstream contracts, run:

```bash
python .claude/_eval-fixtures/runner.py day-ops
```

If any downstream daily-driver skill changes, also run that skill's own eval.
