---
name: capture-process
description: Route Harness Dashboard captures into tasks, card queue, daily-note edits, or action proposals. Use for /capture-process or unprocessed dashboard capture inbox entries.
---

# capture-process

The Daily board's voice/text capture is a **front door** — the dashboard only stores raw utterances. This skill is the **brain**: it reads those utterances and deduces where each one belongs, following the vault's own rules. The user dictates in natural language; you classify and route. They never hand-label.

## Inputs
- `.claude/_state/dashboard/capture-inbox.jsonl` — one JSON object per line: `{ts, text, status, source}`. Process rows with `status` of `ready` (explicitly routed via the dashboard "Route →" button) first; then `new` if the user asks for everything.
- `.claude/_state/dashboard/capture-process.request` — a touch-file written when the user taps "Route →". Its presence means "go". Delete it once you've drained the `ready` rows.
- Today's daily note `04 Notes/daily notes/YYYY-MM-DD.md` — captures are mirrored into its `## Quick Capture` for human visibility (do not duplicate-route those mirror bullets; the jsonl is the source of truth).

## What to do per utterance
Read the text and decide its intent. **Apply the relevant vault rules before writing** — read them, don't guess:
- A **task / next-action** → `09 Rules/tasks.md` (Task Capture Protocol: routing by tag, batch ceiling, Operon line schema). Write a proper Operon line to the correct surface (route by project/context per `09 Rules/tasks.md` tag registry).
- A **card-worthy insight** (a durable judgment/pattern/synthesis) → `09 Rules/cards.md`. Do NOT hand-write a finished card from a one-line capture; append a queued stub to `.claude/_state/dashboard/card-queue.jsonl` (`{ts, text, status:"pending"}`) for proper synthesis in `/vault-evolve` or a card pass. (The dashboard's "Card queue" signal reads this.)
- A **workstream / action thread** → `09 Rules/action.md` (`10 Action/`).
- A **calendar / time-block** → today's `## Day Planner` (v3 hybrid syntax).
- **Ambiguous / multi-intent** → surface a one-line proposal to the user and ask, rather than mis-routing.

Respect **MEMORY.md** hard rules and attribution discipline for anything forwardable.

## After routing each row
- Set its `status` to `routed` in `capture-inbox.jsonl` (rewrite the line in place; keep append-only history — do not delete rows). Optionally add `routed_to` (where it landed).
- When all `ready` rows are drained, delete `capture-process.request`.
- Report a terse summary: `N captures → X tasks, Y cards queued, Z note edits` (and any items you bounced back as ambiguous).

## Notes
- This is the **interactive-path** consumer the user triggers via the dashboard button (near-instant when a session is live, else next session). Keep it cheap: classification + scripted writes; heavy card synthesis stays batched in `/vault-evolve`.
- The dashboard's "today: N captured · routed · pending" status line reflects the `status` field — keeping it accurate is what closes the loop.
