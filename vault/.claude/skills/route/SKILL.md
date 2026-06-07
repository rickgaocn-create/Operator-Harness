---
category: meta
name: route
description: Pick the right downstream skill for an ambiguous natural-language workflow request. Use /route when multiple skills could apply or the user asks which skill to run.
model: claude-sonnet-4-6
allowed-tools: Read, Grep
last-major-rewrite: 2026-05-21
companion-rules: "[[09 Rules/skill-routing.md]]"
---

# Skill: Intent Router

When the user's intent could plausibly match 2+ skills, run THIS first to pick the right one and surface reasoning. Reduces "wrong skill fired" cases — the failure mode where Claude Code's heuristic trigger-matching picks the wrong skill from description-substring overlap.

## When to use

- User typed `/route <intent>` explicitly
- User said something workflow-ish but didn't slash-command: "summarize today", "let's wrap up", "what should I do next"
- 2+ skill descriptions plausibly match — disambiguate before firing
- User asks "which skill does X" — explanation use

**Don't use** when:
- A slash command was explicitly typed — respect it
- The user is in mid-conversation and clearly continuing a thread (no fresh intent)
- It's a one-shot question, not a workflow

## How it works

Three-step routing:

### Step 1 — Parse intent

Extract from the user message:
- **Verbs**: write / read / summarize / plan / review / capture / fix / triage / ...
- **Objects**: today / yesterday / meeting / task / project / report / decision / ...
- **Modifiers**: now / tomorrow / EOD / morning / per-project / cross-project / quick / deep

### Step 2 — Match against skill catalog

Score each skill in ****`.claude/skills/<name>/SKILL.md`**** against the parsed intent. Top candidates by:
- **Description-keyword overlap** (current Claude Code default behavior — establishes baseline)
- **Trigger-phrase exact match** (description's "Trigger on" clause matches verbs/phrases in intent)
- **Read-path overlap** (intent mentions a file/folder the skill reads)
- **Companion-rule match** (intent matches phrasing in a referenced 09 Rules file)
- **Recent-use boost** (skills used in the same session this turn get a small bump — likely continuation)

### Step 3 — Surface decision (don't auto-execute)

```
Routing "summarize today":

Top candidates:
1. /day-digest         ★★★★★  — "EOD 反刍 job ... 23:00 daily"
2. /compress           ★★☆☆☆  — "session compression"
3. /daily-note --close ★★★☆☆  — "EOD reconciliation phase"

→ Recommend /day-digest (matches "today" + EOD + summarize verb).
  Run it? (y / pick #N / "explain why" / type a different command)
```

User picks; router DOES NOT fire the skill directly. The user invokes the chosen one (or types something else).

## Why router-as-recommendation, not router-as-dispatcher

Two reasons:

1. **Trust by transparency.** If router silently dispatches, the user can't learn the skill catalog or correct a wrong pick before damage. Surfacing the decision teaches the user the system AND gives them veto.

2. **Avoid feedback loops.** Router-dispatched skill failures don't have a clear blame line — was it router's fault or skill's? Surfacing keeps causality clean.

## Learning from misses

When the user picks a NON-top candidate or types a different command:

- Log to **`.claude/_state/routing-misses.jsonl`** (`{ts, intent, top_recommendation, user_choice, reason?}`)
- If a pattern emerges (≥3 misses for same intent type) → propose an instinct card capturing the routing heuristic to add
- `/vault-evolve` promotion path: routing-miss instinct cards → **`09 Rules/skill-routing.md`** § Heuristics

This is the same shape as 2026-05-14 trip-grep instinct → **`09 Rules/digest-job.md`**.

## What router is NOT

- **Not a fuzzy auto-completer.** Doesn't guess what you meant if intent is incoherent — asks back.
- **Not a skill catalog.** That's **`/harness-health`** Section 2.
- **Not a permission gate.** Doesn't decide whether a skill SHOULD fire — just which.
- **Not for code tasks.** Code-side skills (`/code-review`, `/run`, etc.) are domain-specific and don't go through router.

## Companion rule

**`09 Rules/skill-routing.md`** — heuristics for tie-breaks, recent-use boost weights, miss-promotion thresholds.

## Failure modes

| Symptom | Fix |
|---|---|
| Router picks consistently wrong | Inspect **`.claude/_state/routing-misses.jsonl`**. Pattern? Add heuristic to **`09 Rules/skill-routing.md`**. |
| Router can't decide (all candidates tied) | Surface all top-3 + ask user to pick — that's fine, not a failure |
| User wants to skip routing | Just type the slash command directly. Router only fires when invoked or intent is ambiguous. |
