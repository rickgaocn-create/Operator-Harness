---
layer: platform
paths:
  - "04 Notes/vault-evolve/_tomorrow-seed-*.md"
applies-to: 23:00 day-digest job 的 output contract（today daily note § AI-Chew 段 + tomorrow-seed.md）
companion-rules:
  - "[[09 Rules/time.md]]"
  - "[[09 Rules/tomorrow-seed.md]]"
  - "[[09 Rules/instincts.md]]"
created: 2026-05-14
created-by: claude (codify 23:00 咀嚼 job 的 output contract)
audit-trace: "[[_prototype-2026-05-13-chew.md]] v2 baseline approved → automation build"
---

# Day Digest Job · Output Contract

> 23:00 自动 job 的 contract — 输出去哪、什么 schema、写什么不写什么。`/day-digest` skill 是 executor，本规则是 contract。

## 触发

- **Autonomous**: Windows Task `{{USER_NAME}}-day-digest` 每日 23:00（含周末）
- **Manual**: 用户敲 `/day-digest` 或 "咀嚼今天 / 反刍今天 / 看看今天" — interactive 模式

## 双 deliverable

### Deliverable A · 今天 daily note 追加 4 段 🤖 section

写到 **`04 Notes/daily notes/{today}.md`**，**在用户手填的 `## End of Day Review` 之前** 插入。如 daily note 不存在或不可读，停 → log error。

```markdown
## 🤖 Shape of Today (AI 咀嚼)

[1-2 段。今天本质形状定性。含 Q2 OKR alignment 一句话挂钩。]

## 🤖 What Resisted (AI 嚼出的卡点)

[Slipped items × business consequence 表。或 1 段 root-cause 分析。]

## 🤖 What Emerged (AI 嚼出的非预期 work signal)

[3-5 个 work-actionable 信号。每个含 业务含义 + next action。]

## 🤖 Insight Candidates (待 promote)

[按 promote value 排序的候选 — 新 Cards / 新 instincts / 新 SOPs。每个标 propose path。]
```

### Deliverable B · `_tomorrow-seed-{tomorrow}.md`

写到 **`04 Notes/vault-evolve/_tomorrow-seed-{tomorrow date YYYY-MM-DD}.md`**。完整 schema 详 [[09 Rules/tomorrow-seed.md]]。

## Hard Content Rules（v1.0 quality bar）

按 [[_prototype-2026-05-13-chew.md]] v2 baseline 校准：

### ✅ DO

- **Work substance focus**: BD activities / 渠道 / 异业 / M&A / OKR / 节点。这是核心。
- **Business consequence framing** for Slipped: 每个 Slipped 标"if 继续 slip 会怎样"
- **Q2 OKR alignment**: Shape of Today 段必含 O1/O2/O3 各 KR 的 progress 评价
- **Next-day actionable**: Emerged / Insight 段每条 ≤2 行 next action（具体到"早晨发哪条微信"）
- **Pattern detection across days**: 对比 yesterday / 同周 / 类型相似 day（如 trip day vs build day vs office day）
- **Tomorrow-seed Top 3 标 OKR + leverage**: 每个 Top 3 item 显式 mapping `O{n}.KR{m}`
- **Auto-spawn full Cards from high-confidence Insight Candidates** (2026-05-14 update per {{USER_NAME}} approval):
  - Confidence ≥ 0.85 → auto-write **full Card** (Evidence + Mechanism + Application + Related) to **`02 Cards/{domain}/C{date}-{slug}.md`**
  - Frontmatter MUST include `auto-generated: true`, `generated-by: /day-digest`, `confidence: 0.X`, `archive-deadline: {today + 14 days}`
  - 0.7 ≤ confidence < 0.85 → auto-spawn **instinct** (**`02 Cards/instincts/I{date}-{slug}.md`**) per [[09 Rules/instincts.md]]
  - confidence < 0.7 → still list in Insight Candidates section, no auto-create
- **Chain /latent-connection-finder** after each auto-Card spawn (cascade depth 1 — single hop only; per Hard Rule below)
- **Weekend light mode**: 如 today 是 Sat or Sun + daily note 内容稀薄 (< 200 字 in non-Day-Planner sections), skip Shape/Resisted/Emerged/Insight 4 段，仅生成 minimal tomorrow-seed (Carry forward + Pending decisions only)

### ❌ DON'T

- **No AI/vault meta-pattern as Emerged/Insight subject**：不写"image injection pattern" / "user push-back triggers rule extraction" / "vault grep before X" 这类元层 instincts — 那些归 [[09 Rules/instincts.md]] capture 流程，不进 chew output
- **No system-level proposals to user**：不在 chew output 里 propose 改 vault rules / 加 skill / 改 hook — 那归 `/vault-evolve` daily report
- **No generic LLM platitudes**："今天很充实 / 你完成了很多 / 继续加油" — 全砍
- **No tutorial-style explanation**：不解释 vault concepts / OKR framework / chain-anchor 含义给 {{USER_NAME}} 看 — 他懂
- **No filler emoji / headings without content**：每个 section 必有 substance，不要 4 段都 ≤ 1 行
- **No cascade > depth 3** (2026-05-14): /day-digest spawns Card → triggers /latent-connection-finder (depth 1) → spawns Card update (depth 2) → STOP. No further chain. Each spawned skill must check `CASCADE_DEPTH` env / param.
- **No auto-Card spawn 没标 `auto-generated: true`**: 必须 frontmatter 显式标，{{USER_NAME}} 可 grep + bulk audit

## Length Targets

| Section | Target |
|---|---|
| Shape of Today | 2-4 段，~120-200 字 |
| What Resisted | 5-10 行（表 or bullets），~150-250 字 |
| What Emerged | 3-5 个 signals，每个 60-100 字 |
| Insight Candidates | 3-5 candidates，每个含 trigger/action/confidence/propose-path |
| Tomorrow-seed | 完整 schema 详 [[09 Rules/tomorrow-seed.md]] |

总长目标：4 段 chew = 600-900 字。Tomorrow-seed 独立 ~400-600 字。

## Data Sources（Job 必读）

| Source | Why |
|---|---|
| Today daily note (entire file) | 主信号源 |
| Yesterday daily note § EOD § Carry forward | 持续性 context |
| Past 7 days daily notes (light scan) | Pattern detection |
| Project Kanbans (**`03 Projects/*/Tasks.md`**) | Slipped task identification + state delta |
| Personal Kanban (**`06 Tasks/Personal.md`**) | 同上 |
| Inbox.md | New ad-hoc capture not yet triaged |
| Active Action files (**`10 Action/12 Active/*.md`**) | Workstream context |
| Q2 OKR file (**`04 Notes/12-week/2026-Q2.md`**) | OKR alignment |
| This week file (**`04 Notes/weekly/2026-W{nn}.md`**) | Big Rocks reference |
| Today modified Cards (**`02 Cards/**/C{YYMMDD}-*.md`**) | Cards spawned 今天 |
| Today modified instincts (**`02 Cards/instincts/I{YYMMDD}-*.md`**) | Instincts captured 今天 |
| Today modified wikis (**`01 Wiki/**/*.md`**) | People/entities touched 今天 |
| Active trip bundle (**`03 Projects/*/03 行程计划/*.md`** containing `trip-date` 含 today) | Trip context |
| `_decisions.md` recent entries | Vault-evolve learning loop |
| Today's WeChat ingest digest (if exists) | Group chat signals |

## Idempotency

- 同一天多次跑 `/day-digest` → 后续跑 **覆盖** 4 段 🤖 section（保持最新），**不重复** append
- Tomorrow-seed 同样 — 覆盖式写
- 用户已手填 `## End of Day Review` 不动 — 那是 truth-source

## Job Status Tracking

每次跑后 append 一行到 **`04 Notes/vault-evolve/_digest-log.md`**:

```
2026-05-14 23:01 · autonomous · 5/14 daily chew written · tomorrow-seed for 5/15 written · 0 errors
2026-05-15 23:00 · manual · 5/15 daily chew written · tomorrow-seed for 5/16 written · 1 warning: weekly file 2026-W20 not found
```

## Failure Modes

| Symptom | Behavior |
|---|---|
| Today daily note 不存在 | Log error, skip A, still attempt B (build seed from sparse data) |
| Today daily note `## End of Day Review` 不存在 | Insert 4 段 🤖 section + empty EOD scaffold + log warning |
| 7 天内某 daily 缺失 | Pattern detection 用可用数据 + log warning |
| Q2 OKR file 不存在 | Shape of Today 跳过 OKR alignment 段 + log warning |
| Tomorrow-seed 已存在 | 覆盖（默认 idempotent） |
| 用户 5/14 出差中且 daily note 是 trip-context | Chew 必须 reflect trip context，not generic office day |
| **Daily note exists but is bare template / sparse** (Top 3 + Day Planner + Meetings 全 empty) | **⚠️ DO NOT 推断 "quiet day."** Empty daily ≠ no activity — {{USER_NAME}} may be AFK. Scan 6 alternative sources before concluding: (1) Trip bundles with `trip-date: today`, esp. `execution-status: executed-pending-notes` · (2) `00 Raw/Wechat/{today}.md` · (3) `03 Projects/*/04 会议纪要/{today}*.md` mtime · (4) Project Kanban / Operon `Today.md` task `dateCompleted: today` · (5) `git log --since={today} --until={tomorrow}` in vault · (6) `09 Rules/*.md`, `.claude/skills/*/SKILL.md`, `02 Cards/**/*.md` modified today (direct-codification day per M.16). If evidence found 1-6 → write chew from that evidence + prepend `⚠️ Daily note was sparse — chew reconstructed from {sources}. Reconcile if mis-inferred.` If NO evidence found across 6 sources → that's the only valid "quiet day" inference; flag explicitly: `⚠️ No activity signal across 6 sources — inferred quiet day.` Rule origin: [[02 Cards/_inbox/C260523-empty-daily-note-not-equal-quiet-day]] (2026-05-22 京差0522 incident). |

---

*Output quality contract baseline: [[_prototype-2026-05-13-chew.md]] v2. Future iterations 提升 quality bar 时 patch 此规则 §"Hard Content Rules"。*
