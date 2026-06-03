---
category: meta
name: operate
description: Operator-intent wrapper for {{USER_NAME}}'s harness. Use when the user asks what matters today, process this, make this forwardable, think with me, or check the machine.
model: claude-sonnet-4-6
allowed-tools: Read, Glob, Grep, Bash, Task
companion-rules:
  - "[[09 Rules/operator-intents.md]]"
  - "[[09 Rules/underlays.md]]"
created: 2026-05-27
created-by: codex
---

# Skill: Operate

Use this as the thin operator-facing layer above the existing skill system. The goal is to let {{USER_NAME}} speak in natural work intents while keeping today's built skills intact underneath.

Direct slash skills still work. `/operate` is a wrapper, not a replacement.

## Cockpit Model

`/operate` is the conversational cockpit. Harness Dashboard is the visual cockpit. The daily note is the machine ledger/backing store that both read and write through existing skills. Do not send {{USER_NAME}} to the daily note unless he is editing, creating, or closing the ledger.

## Core Rule

Classify the request into exactly one of the five operator intents in [[09 Rules/operator-intents.md]], then follow that contract. When an intent is ambiguous, surface the top two plausible intents and ask before writing or dispatching a high-risk workflow.

Do not hide important routing decisions. The wrapper should make the harness quieter for {{USER_NAME}}, not more opaque.

## Intents

| Intent | Use when {{USER_NAME}} says | Primary downstream skills |
|---|---|---|
| What matters today? | "what should I do", "today", "priorities", "top 3" | `/day-ops` |
| Process this | "process this", "turn this into notes/tasks/cards", pasted transcript/clipping/brain dump | `/capture-routing` |
| Make this forwardable | "sendable", "forwardable", "proposal", "report", "to leadership", "to partner" | `/forwardable-quality` |
| Think with me | "options", "pre-mortem", "sanity check this plan", "what are the moves" | `strategist`, `vault-researcher`, `/biz` when artifact-shaped |
| Check the machine | "harness health", "what is broken", "status", "drift", "eval" | `/machine-health` |

## Package Routing

`/operate` routes normal work into four packaged organs before touching thin implementation skills:

| Package | Owns |
|---|---|
| `/day-ops` | Daily operating loop: priorities, sync, replan, inbox triage, and EOD status. |
| `/capture-routing` | Raw intake: dashboard captures, pasted material, tasks, sources, and brain dumps. |
| `/forwardable-quality` | Sendable artifact gates: best-of-N, business critique, attribution, language, confidentiality, and reader fit. |
| `/machine-health` | Diagnostics: profile visibility, middleware, evals, liveness, status, and rearm triage. |

Direct slash skills remain expert escape hatches and implementation details. Use them when a package delegates to an owned workflow or when {{USER_NAME}} explicitly names the skill.

## Workflow

1. Read [[09 Rules/operator-intents.md]] before acting.
2. Read [[09 Rules/underlays.md]] when the request maps to "Make this forwardable", "Think with me", or "Check the machine".
3. Parse the user request into intent, object, audience, risk, and write-permission posture.
4. Pull only the context needed for that intent. For daily-priority questions, treat Dashboard Today/Actionable state, live tasks, and the daily note as one cockpit state.
5. Use underlays as grounding aids when available; do not treat them as authority above live vault files or hard rules.
6. Use existing skills as implementation details; do not rewrite their procedures inline unless the user needs an explanation.
7. Apply the intent's hard gates before producing a final answer or writing any artifact.
8. If the workflow suggests a skill is now mostly procedural scaffolding, note it as a future Distill candidate; do not prune in the same run.

## Underlay Use

Generated underlays live at `.claude/_state/underlays/` and are governed by [[09 Rules/underlays.md]]. They support the wrapper; they do not replace authored Cards, Actions, Wiki, Tasks, or skills.

| Intent | Underlay behavior |
|---|---|
| Make this forwardable | Read `source-graph.json` first for entity and claim grounding, especially counterparty claims, source anchors, workstreams, decisions, and task bindings. Then run the existing best-of-N, biz, attribution, confidentiality, audience, language, and style gates. |
| Think with me | Read `taste-engine.json` first for value nodes, framework nodes, and correction-derived rules. Use it to shape options, tradeoffs, pre-mortems, and recommendations; do not infer taste from Cards. |
| Check the machine | Read `underlay-report.md` and report freshness, counts, fixture checks, and skipped correction lines alongside normal status/map/eval health. |

If underlays are stale or missing, fall back to current vault reads and say so. Stale means missing, older than the newest scoped source file, or older than 24 hours for active harness work.

## Write Discipline

- Default to read-only for "What matters today?", "Think with me", and "Check the machine".
- Prefer dashboard state and `operate-request.jsonl` as the human-facing surface; daily-note internals may be verbose machine logs.
- For "Process this", ask before creating Action files or writing more than 3 tasks.
- For "Make this forwardable", never finalize without the relevant audience, attribution, confidentiality, and language gates.
- Respect confidential lane rules from [[me.md]], [[MEMORY.md]], and project-scoped CLAUDE.md files.
- For Dashboard captures, prefer `/capture-process` as the consumer rather than duplicating capture routing in this wrapper.

## Future-Model Ratchet

When a stronger model is available, `/operate` can run a shadow comparison:

1. Current skill-driven flow.
2. Contract-only flow using [[09 Rules/operator-intents.md]].
3. Compare with existing graders and hard gates.

Only propose shrinking an underlying skill after repeated contract-only passes. Never prune because a better model is expected to handle it in theory.
