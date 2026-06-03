---
category: meta
name: rearm
description: Re-arm one quiet harness organ by id using only its manifest-declared rearm command. Use after /status identifies a stalled routine, signal, hook, or bridge.
model: claude-sonnet-4-6
allowed-tools: Bash, Read
companion-rules:
  - "[[09 Rules/autonomous-routines.md]]"
created: 2026-05-27
created-by: claude
---

# Skill: /rearm — re-arm a quiet organ from AFK

> **概要:** `/status` tells you what went quiet; `/rearm <id>` brings it back. It runs ONLY the idempotent `rearm` command declared for that organ in `harness-manifest.json` — never an arbitrary command.

## Workflow
1. **Resolve the organ.** Read `.claude/_state/harness-manifest.json`; find the organ whose `id` matches the argument (`/rearm feishu-bridge`, `/rearm vault-evolve`, …). If no match, list the valid ids and stop.
2. **Echo the command** you're about to run (the organ's `rearm` field) — one plain-text line, so the channel shows exactly what happened.
3. **Run it** via Bash. PowerShell rearm strings invoke through `powershell -ExecutionPolicy Bypass -File …` as written in the manifest.
4. **Verify** by resolving Python through `.harness/resolve_runtime.py`, then running `.claude/routines/harness_status.py --cached` and confirming the organ flipped 🟢. Report before→after **in the channel**.

## Hard rules
- **Only run the manifest's declared `rearm` string for the matched id.** No improvisation, no arbitrary shell, no chaining. If an organ's `rearm` says it's event-driven (e.g. the graders), say so and stop — there's nothing to re-arm.
- Re-arm is **idempotent by design** (re-register / restart). If it fails, report the stderr verbatim — do **not** retry in a loop or escalate to a different command.
- Bridges (`discord-bridge` / `feishu-bridge`) restart via their scheduled task. If the task itself is missing (not just the daemon down), surface that — it's a deeper break than a quiet daemon and needs the setup script, not a `/Run`.
- This skill touches scheduler/daemon state only. It never writes vault content.
