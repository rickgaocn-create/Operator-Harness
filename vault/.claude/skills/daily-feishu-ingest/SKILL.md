---
category: work
name: daily-feishu-ingest
description: Pull recent Feishu/Lark activity into today's daily note. Scheduled every 6 hours; use on demand to summarize incoming Feishu messages.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Skill: daily-feishu-ingest

每 6 小时自动 ingest 飞书消息（user 视角的 chats）的 skill。pull 最近 6 小时的消息，按 chat 分组，输出 digest，append 到当天 daily note。

## How it runs

| Mode | Trigger | Output |
|---|---|---|
| **Scheduled** | Windows Task Scheduler, daily 06:00 / 12:00 / 18:00 / 00:00 | Appends digest to current daily note + 保存完整 digest 到 **`.claude/.daily-ingest-queue/feishu/`** |
| **On-demand** | `/daily-feishu-ingest [--hours N]` | 同上, 但可指定回看时段（默认 6 小时） |

## Implementation

- 使用 `lark-cli --profile business-morty im +chat-list` 拉取 user 在场的所有 chats（最多 50 个）。Profile = 企业号「Business Morty」bot（2026-05-27 从个人号 `morty` 切换 — 个人 bot 只能看到自己的 p2p，企业 profile 才能看到真实工作群）。Profile 名可用 env `LARK_PROFILE` 覆盖。
- 对每个 chat，`im +chat-messages-list` 拉最近 50 条
- 按时间窗口（默认 6 小时）过滤
- 按 chat 分组，输出 digest

## Output shape (in daily note)

Appends to the templated `## Ingests` section:

```markdown
### 🤖 daily-feishu-ingest 12:00 → 23 messages from 7 chats

*Full digest: `.claude/.daily-ingest-queue/feishu/2026-05-20-1200-digest.md`*
```

完整 digest 见 `.daily-ingest-queue/feishu/` 下当时文件。

## Priority chats (将来可扩展)

当前实现是 pull all chats. 后续可加 **`scripts/priority_chats.json`** 类似 daily-wechat-ingest，过滤到 priority subset。Priority 候选（待 lock）:

- {{PERSON_1}}（PMO 双周）
- {{PERSON}}（{{USER_NAME}}）
- 何宗寰（工作室）
- 张茂威 / 罗逸 / 顾诗尧
- {{PROJECT_A}} 项目群
- 4 楼 美林 群
- {{ORG_D}} / {{ORG_B}} 相关 chats

## Setup (already run during install)

```powershell
powershell -ExecutionPolicy Bypass -File ".claude\skills\daily-feishu-ingest\scripts\setup_schedule.ps1"

Get-ScheduledTask -TaskName '{{USER_NAME}}-daily-feishu-ingest' | Format-List
```

## Cost note

每次 run pull ~50 chats × 50 msgs 数据，主要是 lark-cli HTTP roundtrip 成本（无 LLM 调用，无 token cost）。除非加 vision OCR 阶段，否则 token 0。
