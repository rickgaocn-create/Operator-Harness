---
category: ops
name: capture-routing
description: Coordinates capture intake and routing. Use when dashboard captures, pasted material, tasks, source clippings, or brain dumps need safe classification and routing.
model: claude-sonnet-4-6
allowed-tools: Read, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/operator-intents.md]]"
  - "[[09 Rules/tasks.md]]"
  - "[[09 Rules/cards.md]]"
  - "[[09 Rules/raw-immutable.md]]"
created: 2026-05-28
created-by: codex
---

# Skill: Capture Routing

Coordinate capture intake without letting the dashboard classify business content. This package turns raw inputs into the right owned workflow.

## Role

Use `capture-routing` when `/operate` routes to "Process this", or when `capture-inbox.jsonl` rows are marked ready.

## Downstream Skills

| Input shape | Use |
|---|---|
| Dashboard ready capture | `/capture-process` |
| More than 3 tasks or task chain | `/task-capture` |
| External clipping, article, source, conversation | `/source-ingest` |
| Personal monologue or reflective brain dump | `/distill` |
| Meeting-like transcript | `/meeting-note` |

## State Contract

Read:
- `.claude/_state/dashboard/capture-inbox.jsonl`
- `.claude/_state/dashboard/operate-request.jsonl`
- `04 Notes/daily notes/{today}.md`
- `00 Raw/`
- `01 Wiki/`
- `02 Cards/`
- `06 Tasks/Inbox.md`

Write only through the downstream skill that owns the target surface.

## Operating Rules

1. Preserve source text and attribution boundaries.
2. Ask before creating Action files.
3. Route task batches through `/task-capture`.
4. Do not duplicate `/capture-process`; use it for ready dashboard captures.
5. Keep confidential lanes isolated before routing to shared project surfaces.
6. If the input is ambiguous, classify visibly and ask before writing.

## Completion Gate

After changing this package or its routing contract, run:

```bash
python .claude/_eval-fixtures/runner.py capture-routing
```

Run downstream evals when their owned rules change.
