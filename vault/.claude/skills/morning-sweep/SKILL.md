---
category: work
name: morning-sweep
description: Sweep the previous day's WeChat/Feishu dialogs into a to-confirm section in today's daily note. On --commit, route kept items through /task-capture.
model: opus
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/tasks.md]]"
  - "[[09 Rules/time.md]]"
created: 2026-05-27
created-by: claude
audit-trace: "user request 2026-05-27 — daily-note confirm-from-dialogs feature; crons repaired same session (wrapper %date% bug + WeFlow restart)"
---

# Skill: Morning Sweep (昨日对话 → 待确认 todos)

Reads **yesterday's** WeChat + Feishu dialogs, extracts the to-dos that fell out of conversation, and drops them into today's daily note as a **review-and-confirm** list. Nothing enters the task system until {{USER_NAME}} confirms. This is the deliberate HITL gate the auto-ingests lack (`daily-wechat-ingest` auto-pushes to Inbox; this does not).

> **Contract reference**: [[09 Rules/tasks.md]] (task line format, routing, batch ceiling, task-naming) + [[09 Rules/time.md]] (daily-note § placement). When skill ≠ rule, rule wins.

## Relationship to the ingest skills

| Skill | Job | Auto-pushes tasks? |
|---|---|---|
| `daily-wechat-ingest` / `daily-feishu-ingest` | **Pull** primitives (cron, 6h/24h windows) + raw digests | wechat: yes (no gate) |
| **`morning-sweep`** (this) | **Consolidate yesterday + extract + CONFIRM gate** | **no — confirm required** |
| `/task-capture` | Canonical task write (routing, Operon syntax) | n/a — invoked on `--commit` |

The sweep **reuses the ingests' pull code** (via `scripts/sweep_pull.py`, which imports their `pull_chat` / `lark` primitives) — it does not re-pull independently. Keep the channel-pull logic in the ingest scripts; keep extraction + confirm here.

## Invocation modes

| Mode | Command | Behavior |
|---|---|---|
| **Default (review, since last sweep)** | `/morning-sweep` | Pull messages since `lastRunAt` (from `.claude/_state/dashboard/sweep-state.json`) → extract → **merge** into today's `## 📥 昨日扫描 · 待确认` section. Idempotent: re-runs preserve un-deleted/un-committed rows and only append genuinely new candidates. Falls back to yesterday-bounded if state is missing. |
| **Commit** | `/morning-sweep --commit` | Re-read the section, take the items {{USER_NAME}} kept (un-deleted), route them via `/task-capture` to Inbox/project surfaces. Writes `lastCommitAt` to state file. |
| **Backfill** | `/morning-sweep --since-days N` | Widen the window (e.g. after a weekend / trip). Overrides the since-last default. |
| **Explicit window** | `/morning-sweep --since YYYY-MM-DDTHH:MM` | ISO-8601 start, useful for replaying a known boundary. |
| **Pre-built cache** | Windows Task `{{USER_NAME}}-morning-sweep-pull` @ 07:00 daily | Runs `sweep_pull.py --since-last` (LLM-free) so the raw bundle is warm before {{USER_NAME}} opens the sweep. Phase 1 re-pulls fresh (authoritative), so a transient-empty 07:00 cache self-corrects. |
| **Dashboard button** | "Sweep now" in Today panel | Shells out to `claude -p "/morning-sweep --since-last"` headless; whole skill runs end-to-end. |
| **Autonomous (full)** | — | DEFERRED: the extraction half needs {{USER_NAME}}'s Max session (opus), same as `/daily-emit` / `/day-digest`. Only the *pull* is scheduled. |

## How it works

### Phase 0 — Resolve date + mode
```bash
today=$(date +%Y-%m-%d)
yesterday=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
daily_note="04 Notes/daily notes/${today}.md"
```
`--commit` → jump to Phase 5. Otherwise Phase 1.

### Phase 1 — Pull dialogs since last sweep
Run the pull script (Python 3.11; WeFlow must be running for WeChat). Default uses `--since-last`, which reads `lastRunAt` from `.claude/_state/dashboard/sweep-state.json` and pulls everything since. Falls back to `--since-days 1` automatically when the state file is missing or has no `lastRunAt`:
```bash
"{{USER_HOME}}\AppData\Local\Programs\Python\Python311\python.exe" \
  ".claude/skills/morning-sweep/scripts/sweep_pull.py" --since-last
```
For backfill or replay, pass `--since-days N` or `--since YYYY-MM-DDTHH:MM` instead. `sweep_pull.py` writes `lastRunAt` + `lastWindow` + `lastStatus` + `lastCounts` to the state file on success (preserving `lastCommitAt`).
It prints one JSON line `{bundle, status:[...]}` and writes the raw bundle to
`.claude/.daily-ingest-queue/_sweep/{today}-raw.md`. **Read the per-channel `status`** — surface it verbatim in the section header so a thin sweep is explained, not silently empty:
- WeChat `UNREACHABLE` → `sweep_pull.py` already tried to auto-start WeFlow (:5031) and failed. Tell {{USER_NAME}} to launch `WeFlow.exe` manually, then re-run. (Normal case: it self-heals silently.)
- WeChat `EMPTY in window — freshest history msg = <date>` → no new activity (or stale local history).
- Feishu `EMPTY` → known coverage gap (see § Source coverage).

### Phase 2 — Extract candidate to-dos (the judgment work)
Read the bundle. For each dialog, pull out **only {{USER_NAME}}-actionable to-dos** — things {{USER_NAME}} must *do, decide, send, confirm, or follow up*. Apply:

- **Attribution is mandatory** — every candidate carries `渠道·群/人·发件人 MM-DD HH:MM` so {{USER_NAME}} can verify against the source.
- **Dedup** — grep `06 Tasks/Inbox.md` + the project surfaces (`03 Projects/{{PROJECT_A}}/Tasks.md`, `03 Projects/{{ORG_B}}/Tasks.md`, `06 Tasks/Personal.md`) and the WeChat ingest's prior auto-pushes. If a candidate is already captured, drop it (or note "已在 Inbox").
- **Propose routing** per [[09 Rules/tasks.md]] § Context Tag Registry: `#{{PROJECT_A}}发行` / `#{{PROJECT_A}}情报` / `#{{PROJECT_A}}ai` / `#{{ORG_B}}` / `#aix` / `#nonsense`. Propose `{{status}}` + priority via the Status–Priority parity table. These are *proposals* — {{USER_NAME}} edits before commit.
- **Title hygiene** per [[09 Rules/task-naming.md]] (strip dates/assignees/scope; vague-verb fix; one action per line).
- **Personal-context exclusion** — never surface the Cathy DM ({{ORG_A}}) as a work task; per `me.md` § Personal Context it's personal-mixed (digest-only). Honor any other personal channel the same way.
- **Be conservative.** A sweep that surfaces 5 real to-dos beats one that surfaces 20 with noise. If a line is ambiguous chatter, leave it out.

### Phase 3 — Merge candidates into the 待确认 section

Insert location: **right after the 🌅 Wake-up Brief callout** (top-of-note, morning-review zone), before `## Meetings & Conversations`.

**Merge contract (replaces the old overwrite-idempotent behavior):**

1. Find `## 📥 昨日扫描 · 待确认 (Yesterday Sweep)` in today's daily note. If absent, write the section fresh with the new candidates and you're done.
2. If present, parse existing `- [ ]` and `- [x]` rows. Build a fingerprint per existing row:
   ```
   fingerprint = lower(channel) · lower(chat) · lower(sender) · MM-DD HH:MM · first-32-chars-of-todo
   ```
   from the attribution segment (`📩 {channel}·{chat}·{sender} {MM-DD HH:MM}`). Rows with corrupt/missing attribution still keep their slot — never delete or "fix" them.
3. For each newly extracted candidate, compute the same fingerprint. **Skip** any whose fingerprint matches an existing row (the user has either already triaged it, edited it, or is mid-thought on it).
4. **Append** survivors to the section, below the existing rows. Preserve the user's edits to existing rows verbatim — never rewrite their text, even if your re-extraction would phrase things differently.
5. Update the header comment marker to the new run's timestamp and merged window. Keep the prior `> ⏳ ...` / `> ✅ ...` footer intact unless this run is the first to write the section.

**Section shape:**

```markdown
## 📥 昨日扫描 · 待确认 (Yesterday Sweep)
<!-- /morning-sweep {today} {HH:MM} · window {lastRunAt}→{now} · WeChat={status} Feishu={status} -->
<!-- 确认方式: 保留要做的行(文字可改), 删掉不要的 → 跑 /morning-sweep --commit 路由到 Inbox/看板 -->

- [ ] {to-do, imperative} — 📩 WeChat·{chat}·{sender} {MM-DD HH:MM} → 建议 #{tag} · {{status}} · P{n}
- [ ] {to-do} — 📩 WeChat·{chat}·{sender} {MM-DD HH:MM} → 建议 #{tag} · {{status}} · P{n}

> ⏳ {pending count} pending · review then run `/morning-sweep --commit`. Sources: {1-line status}.
```

If a channel was unreachable/empty, add one line under the comments stating why (e.g. `> ⚠️ Feishu 无覆盖（lark morty 看不到工作群）— 见 SKILL.md § Source coverage`).

**Why merge over overwrite:** a re-run mid-day used to wipe candidates the user hadn't yet decided on. With `--since-last` runs landing multiple times per day (cron + dashboard button + manual), merge is the only sane semantics — see [[feedback-merge-not-overwrite]] if you're tempted to revert.

### Phase 4 — Confirm summary (interactive only)
Brief the user: N candidates written, the source status, and the confirm instruction. Do **not** push anything to tasks yet. Example:
> "昨日扫描完成 — {N} 条待确认写入今天 daily note（WeChat {n} 群活跃；Feishu 无覆盖）。
> 复核 § 📥 昨日扫描：要做的留着（文字随便改），不做的删掉，然后 `/morning-sweep --commit`。"

### Phase 5 — Commit (`--commit`)
1. Read today's `## 📥 昨日扫描` section. The **surviving** `- [ ]` lines ({{USER_NAME}} deleted the rejects) are the confirmed set.
2. Route each via `/task-capture` to its surface, honoring the **≤3-new-tasks-per-Write batch ceiling** ([[09 Rules/tasks.md]]). Use the proposed `#tag`/status/priority unless {{USER_NAME}} edited them.
3. Replace the trailing `> ⏳ ...` line with `> ✅ committed {M} at {HH:MM} → [[Inbox]] / surfaces ({list})`.
4. Never re-commit an already-committed section (check for the ✅ marker first).
5. Write `lastCommitAt` (ISO-8601) + `lastCommitCount` to `.claude/_state/dashboard/sweep-state.json` via a JSON merge that preserves `lastRunAt` / `lastWindow` / `lastStatus`. This lets the dashboard's "Messenger Sweep" panel show both "last swept" and "last committed" ages.

## Hard rules
1. **Never auto-push to Inbox/surfaces in default mode.** The confirm gate is the whole point — tasks move only on explicit `--commit`.
2. **Never invent a to-do not grounded in a dialog line.** Every candidate must trace to a real message (attribution proves it).
3. **Always carry attribution** (channel · chat · sender · timestamp) on every candidate.
4. **Always surface source status** in the section header — a thin/empty sweep must say *why* (WeFlow down / Feishu blind / no activity), never look like "nothing happened".
5. **Honor personal-context exclusions** (Cathy DM etc.) — digest-only, never a work task.
6. **Idempotent via merge, not overwrite** — re-running default mode preserves un-deleted rows (user edits + un-triaged candidates) and appends only fingerprint-new candidates. Never stacks duplicates; never wipes work-in-progress triage.
7. **Respect the task batch ceiling** on commit (≤3 per Write) and `/task-capture` routing — don't hand-write task lines that bypass it.
8. **Reuse the ingest pull code** — do not fork a third channel-pull implementation; extend `sweep_pull.py` / the ingest scripts instead.

## Source coverage (state as of 2026-05-27, repaired this session)
- **WeChat (WeFlow @ :5031)** — ✅ working. 13 priority chats in `daily-wechat-ingest/scripts/priority_chats.json`. **WeFlow.exe must be running** to capture/serve messages; if it's been off, recent history is stale (it captures live, limited backfill). If a sweep is empty, check WeFlow first.
- **Feishu (lark-cli profile `business-morty`)** — ✅ **PRIMARY platform going forward** (set 2026-05-27). Switched from the personal `morty` bot (saw only its own p2p) to the corporate **Business Morty** bot. Key mechanism: it reads **`--as user` (as {{USER_NAME}})**, so it auto-enumerates **every Feishu group {{USER_NAME}} is in** — coverage scales with *{{USER_NAME}}'s* membership, NOT the bot's (`--as bot` sees 0; verified 2026-05-27). **No bot-adding to groups is needed** (and avoids a visible "bot joined" in counterparty-facing chats). As {{USER_NAME}} joins/creates more Feishu work groups, the next sweep picks them up automatically — `daily-feishu-ingest` paginates chat-list (up to 2000 chats). `priority_chats.json` is now just for *pinning* must-always-poll groups. Scopes already cover full `im:message` read; refresh token rolls ~7 days (kept alive by the daily crons). (`morty` retired 2026-05-27.)
- **WeCom / 企业微信 (WXWork)** — not yet wired. Heavy usage on this machine; a future channel via the `wecomcli-*` skills (add to `--channels` + a `pull_wecom` in `sweep_pull.py`).

## Cross-skill chain
- **Upstream**: `daily-wechat-ingest` / `daily-feishu-ingest` (pull primitives, reused by `sweep_pull.py`).
- **Downstream**: `/task-capture` (commit routing) → `06 Tasks/Inbox.md` + project surfaces → `/inbox-process` triage.
- **Sibling**: `/daily-emit` seeds the empty `## 📥 昨日扫描` scaffold into the morning note; `/day-digest` reads the committed tasks as next-day signal.

---
*Morning executor. Quality bar: the 待确认 list reads like {{USER_NAME}}'s own 5-min triage of yesterday's chats — real to-dos, sourced, nothing invented, nothing auto-filed.*
