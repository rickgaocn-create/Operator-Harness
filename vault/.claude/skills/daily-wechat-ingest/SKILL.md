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

- {{PROJECT_A}}× TapTap対接群, {{PROJECT_A}} × 4399 対接群, bili × {{PROJECT_A}} 联运対接
- 美林 × {{PROJECT_A}} — 6月大型线下活动, {{PROJECT_A}} × 美林 — 目标广州新地标
- {{ORG_A}} × 前进街道办, 小鹏 × {{ORG_A}}, 广文旅 × {{PROJECT_A}}, 月月月月 (internal), 模之屋 × {{PROJECT_A}}
- DM: {{PERSON_1}}（{{ORG_C}}）— filtered for personal mix per `me.md` § Personal Context (text only, no media surfacing without explicit ask)
- DM: {{ORG_B}} — {{PERSON}} (Japan ops)
- DM: 珍珍 — TapTap

Add/remove chats by editing `priority_chats.json`. The script also auto-picks up new chats with > 5 messages in the window from groups whose names contain `{{PROJECT_A}}`/`3rd`/`{{ORG_A}}` (configurable threshold).

## Output shape (in daily note)

Appends a section under the templated `## Ingests` header:

```markdown
## Ingests
<!-- /source-ingest 自动 append — [HH:MM] source → cards -->

### 🤖 daily-wechat-ingest 06:00 → 12 messages from 5 chats, 3 media files

**Tasks surfaced** (sent to [[Inbox]]):
- [ ] follow up on Epic Shanghai animation event date — image from Robin 2026-05-12 09:15 #3rd-inc
- [ ] confirm 5/29 PV final assets — `{{WECHAT_ID}}` to {{PROJECT_A}} × 4399 群 2026-05-12 11:23

**Media saved** → `04 Notes/daily notes/2026-05-12-attachments/`:
- `09-15-Robin-shanghai-animation-event.jpg` — Epic Games DM (Robin)
- `11-23-zhaomu-questionnaire.xlsx` — {{PROJECT_A}} × 4399 ({{WECHAT_ID}})

**Chat highlights** (newest → oldest):
- `{{PROJECT_A}} × 4399 対接群` @ 11:29 — 招募问卷已发，4399 端确认开始处理；100 名单+手机号待回填
- `{{PROJECT_A}}× TapTap対接群` @ 09:46 — 5.28→5.29 调整同步完成

*Full digest: `.daily-ingest-queue/2026-05-12/digest.md`*
```

## Setup (one-time, already run during install)

```powershell
# Install the scheduled task (idempotent)
powershell -ExecutionPolicy Bypass -File ".claude\skills\daily-wechat-ingest\scripts\setup_schedule.ps1"

# Verify
Get-ScheduledTask -TaskName 'RG-daily-wechat-ingest' | Format-List
```

The scheduled task runs `python <ingest.py>` at 06:00 daily; logs to `.claude\.daily-ingest-queue\{date}\run.log`.

## When this skill does NOT apply

- Pulling specific messages by talker → use WeFlow API directly via `python query_in_session.py` or curl
- Ingesting non-WeChat sources (Lark, WeCom, email) → those need their own skill (lark-im / wecomcli-msg / Gmail MCP)
- Backfill > 7 days → WeFlow `/api/v1/messages` is hard-capped at 7 days history; pull deeper via WeChat client manually

## Personal Context handling

{{PERSON_1}} DM is in the priority list but messages are **never surfaced** as work-tasks or auto-OCR'd — per `me.md` § Personal Context, treat that channel as personal-mixed. Only fact-level text digest (sender, count, last timestamp); no media auto-extraction.
