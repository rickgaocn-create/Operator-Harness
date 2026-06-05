---
category: meta
name: autonomous-routines
description: Docs + management for the 4 Tier-7 autonomous routines (inbox-drift, pre-trip, eod-snapshot, harness-pulse). Trigger on /autonomous-routines, "show me my routines", "what's running automatically", or auditing autonomous activity.
model: claude-sonnet-4-6
allowed-tools: Bash, Read
last-major-rewrite: 2026-05-21
companion-rules: "[[09 Rules/autonomous-routines.md]]"
---

# Skill: Autonomous Routines

4 narrow, fail-safe routines that run unattended via Windows Task Scheduler. Each detects a specific condition and notifies (or freezes state). NONE invoke Claude — they're cheap detectors, not actors.

## The 4 routines

| Routine | Schedule | Script | What it does | Default mode |
|---|---|---|---|---|
| `inbox-drift` | hourly | **`.claude/routines/inbox-drift.py`** | Counts open `- [ ]` in ****`06 Tasks/Inbox.md`****. Alerts Feishu if > 20. | notification-only |
| `pre-trip` | daily 18:00 | **`.claude/routines/pre-trip.py`** | Scans **`03 Projects/*/03 行程计划/(C) 差旅*.md`** for `trip-date: tomorrow`. Alerts Feishu with bundle path + checklist reminder. | notification-only |
| `eod-snapshot` | daily 23:30 | **`.claude/routines/eod-snapshot.py`** | Queries Operon index for today's Shipped/Slipped/Carry-forward. Freezes results into HTML-comment lines at bottom of today's daily note (Phase 2 of daily-note overhaul reserved the anchor lines). | **DRY_RUN default** — write mode after 7-day validation |
| `harness-pulse` | every 3h | **`.claude/routines/harness-pulse.py`** | Consolidated liveness reflex. Checks channel daemons (Discord/Feishu), Tier-7 scheduler health (is the hourly routine still firing?), today's `/vault-evolve` report, `_pending` backlog, stuck `raw` corrections, 24h tool error rate. Writes one verdict to **`.claude/_state/harness-pulse.json`** (`green｜yellow｜red`). **Edge-triggered**: pushes via `notify()` only when severity worsens vs the previous pulse (+ a recovery note back to green); steady state is silent. `PULSE_SILENT=1` = compute+log without pushing. | notification-only |

> `harness-pulse` is the meta-detector — its scheduler check is how a silent death of the *other three* routines surfaces (it catches "no hourly routine in >150 min"). Conversely, if `harness-pulse` itself stops, today's `/vault-evolve` will note its verdict file going stale.

## Setup

```powershell
# As Administrator
powershell -ExecutionPolicy Bypass -File "D:\Administrator\Documents\{{USER_NAME}}\.claude\routines\_setup.ps1"
```

Idempotent: unregisters existing entries, re-registers. Run after editing routine schedules.

## Common contract

All 3 routines share **`.claude/routines/_common.py`** for:
- `is_dry_run()` — reads `DRY_RUN` env, defaults to `1` (notification-only mode is the safe default)
- `under_run_cap(routine, max_per_day)` — daily cap enforcement; logs skip when exceeded
- `log_event(routine, level, msg, **extras)` — append to **`.claude/_state/autonomous-log.jsonl`**
- `notify_feishu(routine, msg)` — best-effort Feishu via lark-cli (per [[MEMORY.md]] · [[agent-morty-feishu-bridge]]). DRY_RUN-gated; used by the original 3 routines. Delegates to `_send_feishu`.
- `notify(routine, msg)` — real-delivery alert path for detector routines (used by `harness-pulse`). Sends a Feishu DM via `lark-cli --profile morty im +messages-send` to the allowlisted operator (resolved from `channels/feishu/access.json` `allowFrom`, or `HARNESS_PULSE_FEISHU_USER`). Skips the DRY_RUN gate (Hard Rule 1). Stays in the **single Feishu lane** — does NOT cross to Discord (Discord keeps its own healthcheck). If the send fails, drops a `CRITICAL-*.signal` into `_pending/` so the next SessionStart leads with it.

> ⚠️ Both senders go through `_send_feishu`, which calls `lark-cli ... im +messages-send`. The earlier `+send` invocation was **not a real command** and silently failed every live send — fixed 2026-05-26. The original 3 routines never hit it (they only ran in DRY mode), so it went unnoticed until `harness-pulse` exercised the real path.

## Audit log

```bash
# Last 50 events across all routines
tail -n 50 .claude/_state/autonomous-log.jsonl | jq .

# Per-routine event counts last 24h
grep "$(date -u -d 'yesterday' +%Y-%m-%dT)" .claude/_state/autonomous-log.jsonl \
  | jq -r '.routine' | sort | uniq -c
```

## Promotion path (dry-run → write mode)

`eod-snapshot` ships in DRY_RUN mode by default. To promote:

1. Let it run 7 days. Inspect **`.claude/_state/autonomous-log.jsonl`** for `[DRY] would write` entries. Verify the proposed snapshots look right (byte diff +/- sensible).
2. Open Windows Task Scheduler → `{{USER_NAME}}-tier7-eod-snapshot` → Actions → Edit → add environment variable `DRY_RUN=0` to the python invocation.
3. Watch for 3 days. Snapshot HTML comments should appear at the bottom of each daily note. If they look wrong, revert by removing the env var.

`inbox-drift` and `pre-trip` are notification-only by design and don't need promotion — they never write to vault content.

## Failure modes

| Symptom | Diagnosis |
|---|---|
| No events in `autonomous-log.jsonl` | Task not registered. Re-run `_setup.ps1`. |
| Events present but no Feishu notifications | `lark-cli` not on PATH OR not authenticated. See `[[lark-cli-setup]]` memory entry. |
| `[DRY] would write` always (eod-snapshot never writes) | `DRY_RUN` env var still set to default. Edit the Windows Task action to add `DRY_RUN=0`. |
| Inbox alerts spam | `MAX_ALERTS_PER_DAY` in `inbox-drift.py` is 3. Edit if more/less needed. |
| Trip alert missed | `pre-trip.py` only checks tomorrow's `trip-date`. Multi-day trips need each day to match. |

## Hard guardrails (per [[09 Rules/autonomous-routines.md]])

1. **DRY_RUN default** for any routine that writes vault content. Write mode requires explicit env var.
2. **Max-runs-per-day caps** prevent runaway alerts.
3. **Lossy logging** — `_common.log_event` swallows all exceptions; routines never fail because logging failed.
4. **Read-only checks** for inbox-drift and pre-trip. Only eod-snapshot writes (and only in non-DRY mode).
5. **Audit trail required** — every event logs to **`.claude/_state/autonomous-log.jsonl`**. Reviewable via `/harness-health` Section 5.
