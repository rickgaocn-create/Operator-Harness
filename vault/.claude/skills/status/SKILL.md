---
category: meta
name: status
description: Return an on-demand harness liveness card for AFK use. Shows bridges, routines, signals, hooks, graders, today's Top 3, and quiet organs.
model: claude-sonnet-4-6
allowed-tools: Bash, Read
companion-rules:
  - "[[09 Rules/autonomous-routines.md]]"
created: 2026-05-27
created-by: claude
---

# Skill: /status — AFK Operator Snapshot

> **概要:** the pull view of harness liveness. Fire it from Discord/Feishu mid-AFK and get the current state back IN the channel — instead of waiting for the next 3h pulse or a new session. Composes with `harness-pulse` (the auto/push side): same verdict, on demand, augmented with per-organ last-fired + today's Top 3.

## Run

```bash
PY="$(python .harness/resolve_runtime.py python)"
"$PY" .claude/routines/harness_status.py           # fresh: re-runs a silent pulse first (default)
"$PY" .claude/routines/harness_status.py --cached  # faster, may be up to 3h stale
"$PY" .claude/routines/harness_status.py --json    # machine-readable
```

## Deliver
- Present the card's stdout **verbatim into the channel** — the card IS the deliverable. Do **not** collapse it to "✅ done" (per the AFK delivery-completeness rule: push the actual content, not a status word).
- If the card shows ⚠️ **Needs attention**, point at the `/rearm <id>` next step it already prints.
- Default to fresh; use `--cached` only when the caller wants speed.

## What it reads (read-only — 0 vault writes)
- `.claude/_state/harness-manifest.json` — the declarative organ list. **Add a new routine / hook / bridge there and `/status` sees it automatically.**
- `harness-pulse.json` (verdict) · `autonomous-log.jsonl` (routine last-fired) · produced artifacts (daily note / evolve report) · `usage.jsonl` (hook) · `grader-verdicts.jsonl` (graders) · live process probe (bridges).

## Notes
- Never writes vault content. Only side effect: the silent pulse refreshes its own verdict file (its job).
- Graders showing ⚪ "never fired" is expected until a bd-prospect / ma-screening producer runs — informational, not an alarm.
