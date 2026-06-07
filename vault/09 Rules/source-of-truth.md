---
layer: platform
type: rule
scope: source-of-truth
created: 2026-06-02
created-by: claude
companion-rules:
  - "[[09 Rules/retrieval-scheduler.md]]"
---

# Source of Truth — by data volatility

> Born from a real miss (2026-06-02): I relied on the **vault** for a *schedule* fact, but the vault lagged a reschedule that lived in **WeChat** — so I worked off stale reality and nearly put meetings on the wrong day. The fix: pick the source by how **volatile** the fact is.

## The split

- **Volatile facts — who / when / where** (meetings, schedule, RSVPs, live status, "this afternoon", "tomorrow"): check the **LIVE sources FIRST** — the **calendar** (the live truth for meetings) + **recent WeChat / Feishu** (where reschedules actually happen) — *then* the vault. The vault lags; **never treat a vault daily-note / plan as the current schedule.**
- **Stable context — companies, contacts, strategy, decisions, history:** the **vault is authoritative** (Cards / Wiki / project docs / weekly). It holds the *why / who / context*, which doesn't churn.

## Calendar = the live meeting layer

Meetings go on the **calendar** the moment they're set or moved. The vault keeps the planning + context (trip bundles, agendas, the why); the calendar holds the current **when / where**. On "what's my schedule" or "add a meeting", read the **calendar + recent WeChat**, not the daily-note.

**DEFAULT calendar = {{USER_NAME}}'s FEISHU calendar** (corrected 2026-06-02) — *especially in Feishu sessions*. Create with `lark-cli calendar +create --as user` (writes his primary Feishu calendar; China time `+08:00`). Use Google Calendar (the MCP tools) ONLY when he explicitly says Google. The Feishu calendar is the one he actually reads + the one that syncs to his G2 glasses. NB: Feishu event `app_link`s contain `&`, which breaks the Feishu *reply* plugin's send — deliver event links via a **direct `lark-cli` call** (bash preserves `&`), not the reply tool.

## The cross-check (would have caught the 2026-06-02 drift)

For any schedule / time-sensitive ask, reconcile **vault (planned) vs calendar (live) vs recent WeChat (just-arranged)** and **flag drift** rather than trusting one source. A vault plan that conflicts with a fresher WeChat message → **WeChat wins** (it's newer); surface the discrepancy instead of silently scheduling. Setting a meeting time from a stale vault plan is the failure this rule exists to prevent.

## Companion

- The **WeChat-scheduling capture feeder** (`.claude/routines/wechat_schedule_capture.py`) automates the WeChat → calendar path: it scans WeChat for scheduling messages and proposes calendar adds (human-confirmed). Pairs with [[09 Rules/retrieval-scheduler.md]] (cost-tiered vault retrieval) — this rule is about *which source*, that one about *how deep*.
