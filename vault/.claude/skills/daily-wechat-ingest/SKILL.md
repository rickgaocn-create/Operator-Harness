---
category: work
name: daily-wechat-ingest
description: Pull the last 24 hours of priority WeChat activity into today's daily note and surface candidate tasks/timelines. Scheduled daily; also invocable on demand.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Skill: daily-wechat-ingest

Automated overnight WeChat ingest for priority work chats. Pulls the last 24 hours of activity (text + media), organizes downloaded files into the daily-note tree, and surfaces business-relevant signal (tasks, dates, names, decisions) into the day's daily note and task inbox.

## How it runs

| Mode | Trigger | Output |
|---|---|---|
| **Scheduled** | Windows Task Scheduler, daily 06:00 | Appends to current daily note + Inbox + media saved under **`04 Notes/daily notes/{date}-attachments/`** |
| **On-demand** | `/daily-wechat-ingest [--days N]` | Same output for the requested window; useful for backfill |

## Two-tier processing

The cron job runs whether `ANTHROPIC_API_KEY` is set or not — its output is more useful when it is.

| Step | No API key | With API key (set via `[Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', '...', 'User')`) |
|---|---|---|
| Pull messages from priority chats | ✅ | ✅ |
| Download media (images / files / voice / video) | ✅ | ✅ |
| Save organized media tree | ✅ | ✅ |
| Append message digest to daily note | ✅ | ✅ |
| **OCR + business-info extraction from images** | ❌ (filenames logged for manual review) | ✅ Claude vision extracts dates, names, action items |
| **Auto-add detected tasks to `06 Tasks/Inbox.md`** | ❌ | ❌ **OFF by default since 2026-05-27** — task intake now flows through `/morning-sweep` (confirm gate). Digest still writes. Pass `--push-inbox` to restore the old auto-push. |

## Priority chats (default scope)

Same 13 chats baselined 2026-05-12. Defined in **`scripts/priority_chats.json`** and editable in-place:

- 《{{PROJECT_A}}》× TapTap対接群, {{PROJECT_A}} × 4399 対接群, bili × {{PROJECT_A}} 联运対接
- {{ORG_G}} × {{PROJECT_A}} — 6月大型线下活动, {{PROJECT_A}} × {{ORG_G}} — 目标广州新地标
- {{ORG_E}} × 前进街道办, 小鹏 × {{ORG_E}}, 广文旅 × {{PROJECT_A}}, 月月月月 (internal), 模之屋 × {{PROJECT_A}}
- DM: Cathy（{{ORG_A}}）— filtered for personal mix per `me.md` § Personal Context (text only, no media surfacing without explicit ask)
- DM: {{ORG_B}} — 娇娇 (Japan ops)
- DM: 珍珍 — TapTap

Add/remove chats by editing `priority_chats.json`. The script also auto-picks up new chats with > 5 messages in the window from groups whose names contain `{{PROJECT_A}}`/`{{ORG_B}}`/`{{ORG_E}}` (configurable threshold).

## Output shape (in daily note)

Appends a section under the templated `## Ingests` header:

```markdown
## Ingests
<!-- /source-ingest 自动 append — [HH:MM] source → cards -->

### 🤖 daily-wechat-ingest 06:00 → 12 messages from 5 chats, 3 media files

**Tasks surfaced** (sent to [[Inbox]]):
- [ ] follow up on Epic Shanghai animation event date — image from Robin 2026-05-12 09:15 #{{ORG_B}}-inc
- [ ] confirm 5/29 PV final assets — `{{REDACTED}}` to {{PROJECT_A}} × 4399 群 2026-05-12 11:23

**Media saved** → `04 Notes/daily notes/2026-05-12-attachments/`:
- `09-15-Robin-shanghai-animation-event.jpg` — Epic Games DM (Robin)
- `11-23-zhaomu-questionnaire.xlsx` — {{PROJECT_A}} × 4399 ({{REDACTED}})

**Chat highlights** (newest → oldest):
- `{{PROJECT_A}} × 4399 対接群` @ 11:29 — 招募问卷已发，4399 端确认开始处理；100 名单+手机号待回填
- `《{{PROJECT_A}}》× TapTap対接群` @ 09:46 — 5.28→5.29 调整同步完成

*Full digest: `.daily-ingest-queue/2026-05-12/digest.md`*
```

## Setup (one-time, already run during install)

```powershell
# Install the scheduled task (idempotent)
powershell -ExecutionPolicy Bypass -File ".claude\skills\daily-wechat-ingest\scripts\setup_schedule.ps1"

# Verify
Get-ScheduledTask -TaskName '{{USER_NAME}}-daily-wechat-ingest' | Format-List
```

The scheduled task runs `python <ingest.py>` at 06:00 daily; logs to `.claude\.daily-ingest-queue\{date}\run.log`.

## WeChat backend — WeFlow or the native bridge (Windows)

Message data is pulled from a **WeFlow-shaped local HTTP API** at `WEFLOW_BASE` (default `http://127.0.0.1:5031`). Two backends serve it:

- **WeFlow.exe** (default) — the 184MB Electron app. Quirks every consumer must handle: a cold cursor returns `count=0` on the *first* `/api/v1/messages` call (use `limit=200` + retry-on-empty), media can come back with a null `mediaUrl`, and it periodically **crashes WeChat**.
- **Native bridge** (drop-in replacement, built 2026-06-05) — `Developer/operator-harness/windows/wechat/wechat_bridge.py`. Reads the SQLCipher-4 DBs directly (ctypes memory key-scan + pure-Python decrypt), serves the same 3 endpoints + Bearer auth, no Electron, never locks WeChat's live files (operates on copies). Registered as scheduled task **`{{USER_NAME}}-wechat-bridge`** (Disabled by default). Drop-in verified: this skill + `wechat_schedule_capture.py` run against it unchanged. Mechanism + caveats: that dir's `README.md`.
  - **Cutover (retire WeFlow):** ensure 微信 (`Weixin.exe`) is running → stop `WeFlow.exe` → `Enable-ScheduledTask {{USER_NAME}}-wechat-bridge` (or run `run-bridge.ps1`). `WEFLOW_BASE`/`WEFLOW_TOKEN` stay unchanged. The bridge reads the key from `Weixin.exe`'s memory, so 微信 must be open.

## When this skill does NOT apply

- Pulling specific messages by talker → use WeFlow API directly via `python query_in_session.py` or curl
- Ingesting non-WeChat sources (Lark, WeCom, email) → those need their own skill (lark-im / wecomcli-msg / Gmail MCP)
- Backfill > 7 days → WeFlow `/api/v1/messages` is hard-capped at 7 days history; pull deeper via WeChat client manually

## Personal Context handling

Cathy DM is in the priority list but messages are **never surfaced** as work-tasks or auto-OCR'd — per `me.md` § Personal Context, treat that channel as personal-mixed. Only fact-level text digest (sender, count, last timestamp); no media auto-extraction.
