---
category: quality
name: forwardable-quality
description: Coordinates quality gates for sendable artifacts. Use when work must become partner-ready, leadership-ready, CN-ready, or otherwise forwardable.
model: claude-sonnet-4-6
allowed-tools: Read, Glob, Grep, Bash, Task
companion-rules:
  - "[[09 Rules/operator-intents.md]]"
  - "[[09 Rules/attribution-discipline.md]]"
  - "[[09 Rules/sensitivity-guard.md]]"
  - "[[09 Rules/auto-chain-style.md]]"
created: 2026-05-28
created-by: codex
---

# Skill: Forwardable Quality

Coordinate the quality chain for anything {{USER_NAME}} may forward, send upward, or share with a counterparty. This package protects judgment, attribution, language, confidentiality, and reader fit.

## Role

Use `forwardable-quality` when `/operate` routes to "Make this forwardable" or when a major artifact is being finalized.

## Downstream Skills

| Gate | Use |
|---|---|
| Major artifact candidate generation | `/best-of-n` |
| Business-grade critique | `/biz` |
| Source and quote discipline | `/attribution-lint` |
| CN-audience residue cleanup | `/localize-cn` |
| Project-internal pragmatic style | `/pragmatic` |
| Creative/human register | `/humanize` |
| Interactive report surface | `/interactive-report` |

## State Contract

Read:
- draft artifact
- `09 Rules/operator-intents.md`
- `09 Rules/attribution-discipline.md`
- `09 Rules/sensitivity-guard.md`
- `09 Rules/auto-chain-style.md`
- `.claude/_state/underlays/source-graph.json`
- `.claude/_state/underlays/taste-engine.json`

Write only to the artifact or review surface explicitly requested by {{USER_NAME}}.

## Operating Rules

1. Major forwardable artifacts use `/best-of-n` unless {{USER_NAME}} explicitly skips it.
2. Counterparty claims need source anchors or must be labeled as judgment.
3. CN-audience work artifacts must pass residue checks.
4. Do not mix confidential lanes into audience-facing artifacts.
5. Make reader fit explicit: partner, leadership, PMO, board, or personal.
6. Never let system diagnostics leak into business artifacts.

## Completion Gate

After changing this package or the forwardable quality chain, run:

```bash
python .claude/_eval-fixtures/runner.py forwardable-quality
```

Run downstream evals for changed quality-gate skills.
