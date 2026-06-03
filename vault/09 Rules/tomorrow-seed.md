---
layer: platform
paths:
  - "04 Notes/vault-evolve/_tomorrow-seed-*.md"
applies-to: 23:00 day-digest job 输出的 tomorrow-seed 文件 schema (08:00 daily-emit job 读取)
companion-rules:
  - "[[09 Rules/digest-job.md]]"
  - "[[09 Rules/time.md]]"
created: 2026-05-14
created-by: claude
audit-trace: "[[_prototype-2026-05-13-chew.md]] v2 baseline § Artifact B"
---

# Tomorrow Seed · Schema Contract

> 23:00 job 写 → 08:00 job 读 的中间文件 schema。是 batch loop 的 join point。

## 命名 + 位置

```
04 Notes/vault-evolve/_tomorrow-seed-{YYYY-MM-DD}.md
```

- `{YYYY-MM-DD}` = **明天**的日期（不是 generated date）
- 文件路径下划线前缀 = 由 system 管理（`_log.md` / `_decisions.md` / `_tomorrow-seed-*.md` / etc.）
- 文件被 08:00 emit job consume 后，**不删除**（归档作为 emit accuracy 评估的 truth-source）

## Frontmatter Contract

```yaml
---
type: tomorrow-seed
for-date: YYYY-MM-DD              # ISO，明天的日期
generated-at: YYYY-MM-DD HH:MM     # 23:00 job 的执行时间戳
generated-by: claude (day-digester) # 实际生成者 — 当前为 /day-digest skill body
source-digest: "[[04 Notes/daily notes/{today}.md]] § AI-Chew"  # source 引用
trip-context: "[[(C) 差旅...]]" 或 null  # 如明天是 trip day
q-okr-bucket: "O1 dominant" 或 "O2/O3 mix" 或 "O1+O2"  # 明天 OKR 倾向
quality-status: "auto" 或 "manual-curated"
---
```

## Body Schema (required sections)

```markdown
# Tomorrow Seed · {weekday MM/DD} · {context tag (出差日 / 周末 / 普通工作日 / etc.)}

> 顶部 1-line context. e.g. "⚠️ 出差日 — Day Planner = 行程 + 关键 work block 镶嵌（不是 work tasks list）"

## 🎯 Suggested Top 3 (ranked by Q2 OKR leverage)

3 个 items，每个含:
- Priority emoji（⏫ / 🔴 / 🟠 / 🟡）
- Headline（1 line）
- 2-4 行说明（为何 leverage 高 / 业务后果）
- **明确标 Q2 OKR mapping**: `O{n}.KR{m}` 或 `multi-OKR (e.g. O1.KR1 + O2.KR1)`
- **失败模式 (optional)**: "如不做会发生什么"

## 📅 Day Planner Pre-populated (high-confidence time blocks)

- [ ] HH:MM 行程 / 主要 task
- [ ] HH:MM ...
- ⚡ 标记**新增的 AI-proposed work block**（不是 user 历史时段，是基于 carry-forward / seed 推断的）

**Day Planner OG syntax**: `- [ ] HH:mm task`（24h，无方括号）。详 [[09 Rules/tasks.md]] § Day Planner Contract。

## 📊 Active Tracks Auto-populate

按 project：

### {{PROJECT_A}}— `03 Projects/{{PROJECT_A}}/`
- **⚠️ Overdue (N)**: count + 列前 3
- **🔺 This Week (N)**: count + 列前 3 by chain-anchor
- **🔁 In-progress (N)**: 所有 `[/]` items across Kanban (any project)
- **Today (committed)**: 见 § Day Planner
- **Slipped from 5/{N-1} (carry forward)**: 列出昨天 EOD § Carry forward + Slipped

### {{ORG_B}} — `03 Projects/{{ORG_B}}/`
（同上格式）

## 🚨 Drift Signals (carry from chew)

- 持续 slip pattern 警示（"连续 N 天 outreach 静默"）
- Silent slipped item（未在 Slipped 写但 Active Tracks 提到的）
- Day-mode self-rating drift（昨天自评 vs 真实形状不符）

3-5 条 max。每条 ≤2 行。

## 🪨 This Week's Big Rocks Reference

引用 `04 Notes/weekly/2026-W{nn}.md` § This Week's Big Rocks 段。如该段为空 → 标"weekly file 未填，建议早 review 时补"。

## 🎯 Q2 OKR Alignment Tomorrow

表格形式：

| OKR | Tomorrow contribution | Status |
|---|---|---|
| O1.KR1 | {具体动作 or "无"} | 强 day / 弱 day / 跳过 |
| O1.KR2 | ... | ... |
| O1.KR3 | ... | ... |
| O2.KR1 | ... | ... |
| O2.KR2 | ... | ... |
| O3 | ... | ... |

Source: [[04 Notes/12-week/2026-Q2.md]] 当前 KR list。

## 🧠 Recent Cards / Insights to Reference Today

最近 7 天 spawned 的 Cards / instincts 中 tomorrow 该 reference 的（cluster signal / relevant pattern / new mental model）。3-5 个 max。

## 🤖 Pending Decisions / Open Threads

未 close 的 grill threads / 等回复的 outreach / 已发但未确认的 commits。简短 list。
```

## Hard Rules

- **`for-date`** 必填 — emit job 用这个 disambiguate 哪个 seed 是今天该读的
- **Top 3 各自 mapping OKR** — 不允许 generic Top 3，必须显式 OKR-tagged
- **Day Planner pre-populated 时段必须用 Day Planner OG syntax**（`- [ ] HH:mm task`，24h，无 brackets）
- **NEVER 写 generic Day Planner items** like `- [ ] 09:00 工作`，必须具体
- **AI-added work blocks** 必须 ⚡ 标记，让 user 知道哪些是 AI 推断的
- **不删旧 tomorrow-seed**（归档作 accuracy 评估）

## Lifecycle

| Stage | Trigger | Action |
|---|---|---|
| **Create** | 23:00 day-digest job | Write `_tomorrow-seed-{tomorrow}.md` |
| **Consume** | 08:00 daily-emit job (next morning) | Read seed → write **`04 Notes/daily notes/{today}.md`** |
| **Archive** | After consumption | Don't delete — stays in **`04 Notes/vault-evolve/_tomorrow-seed-{date}.md`** for accuracy review |
| **Audit** | Periodic (weekly?) | Compare seed prediction vs actual EOD truth → log to `_emit-accuracy.md` |

## 与 daily-note Phase 3.5 关系

- Daily-note Phase 3.5 (State-aware Bootstrap) 现 grep 6 sources 后 ask user Top 3
- 08:00 emit job = Phase 3.5 + tomorrow-seed read **自动完成**，不 ask user
- 用户起床看到的 daily note = emit-mode 输出，可以 manual edit override 任何部分
- Manual `/daily-note` invocation 仍走 Phase 3.5 interactive flow（catch-up / 周末 / 特殊情况）

## Failure Modes

| Symptom | Behavior |
|---|---|
| Seed 文件不存在 (08:00 时) | Fall back to `/daily-note` Phase 3.5 interactive flow + log warning |
| Seed `for-date` 与今天不符 | Skip seed read, fall back to Phase 3.5 |
| Seed schema 不完整（missing required section） | Use partial data + log warning + fall back fill |
| Multiple seed files for same date | 用 latest by mtime + log warning |

---

*Schema baseline: [[_prototype-2026-05-13-chew.md]] v2 § Artifact B. 后续修订 patch 此规则。*
