---
layer: platform
paths:
  - ".claude/routines/**"
  - ".claude/_state/autonomous-log.jsonl"
  - ".claude/_state/autonomous-last-run.json"
canonical_skill: ".claude/skills/autonomous-routines/SKILL.md"
created: 2026-05-21
last-major-rewrite: 2026-05-21
---

# Autonomous Routines Rules

> Guardrails for Tier-7 unattended detection routines. Five non-negotiables.

## Hard Rules

1. **DRY_RUN is the default for any routine that writes vault content.** Promotion to write mode requires explicit env-var configuration in the scheduled task. Notification-only routines (read + alert) may skip this.

2. **Every routine has a max-runs-per-day cap.** Enforced via `**.claude/routines/_common.py**::under_run_cap()`. Caps prevent runaway loops + alert spam.

3. **All events log to **`.claude/_state/autonomous-log.jsonl`**.** Append-only. Reviewable via **`/harness-health`** Section 5. No silent operation — even dry-run "would write" events log.

4. **Lossy logging — never fail the routine because logging failed.** `_common.log_event` swallows all exceptions. Same discipline as the PostToolUse usage-log hook.

5. **Routines never invoke Claude.** They're DETECTORS, not actors. If a routine notices something requiring AI reasoning, it notifies the user (via Feishu); the user invokes the appropriate skill in their next Claude Code session.

## Adding a new routine

1. Write the script at **`.claude/routines/<name>.py`**. Import shared utils from `_common.py`.
2. Define `ROUTINE = "<name>"` and `MAX_PER_DAY = N`.
3. Use `is_dry_run()` to gate any write operation.
4. Use `under_run_cap(ROUTINE, MAX_PER_DAY)` before alerting (not before logging — always log).
5. Use `log_event(ROUTINE, level, message)` for every meaningful step.
6. Use `notify_feishu(ROUTINE, message)` for user-facing alerts.
7. Register in `_setup.ps1` with appropriate trigger.
8. Document in ****`.claude/skills/autonomous-routines/SKILL.md`**** § routines table.
9. Run `_setup.ps1` to install. Verify with `Get-ScheduledTask -TaskName '{{USER_NAME}}-tier7-*'`.

## Removing a routine

1. `Unregister-ScheduledTask -TaskName {{USER_NAME}}-tier7-<name> -Confirm:$false`
2. Delete the script (preserve in git history)
3. Update SKILL.md docs

## Trust earned, not assumed

Each new routine starts in notification-only mode for ≥7 days. Promote to write mode only after:
- Reviewing log entries (every event makes sense)
- Confirming the routine fires when expected (no missed conditions)
- Confirming no false positives (no spurious alerts)
- **Confirming the task is actually registered AND firing** — `Get-ScheduledTask -TaskName {{USER_NAME}}-tier7-<name>` returns `Ready` *and* a fresh `autonomous-log.jsonl` entry appears on schedule. `_setup.ps1` registration can silently fail; never assume "I ran setup" means the task exists (incident 2026-05-26: the whole layer was dead 4.5 days, unregistered).
- **Confirming the live `notify()` path delivers** end-to-end — fire one real alert and verify receipt, not just a DRY-mode "would notify" log line. A broken send command (e.g. the phantom `+send`) stays invisible as long as everything runs in DRY (same incident).

Write-mode routines MAY still fail safely: e.g. `eod-snapshot` only edits HTML comments inside reserved anchor lines, never user-authored content.
