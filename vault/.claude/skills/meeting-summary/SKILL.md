---
category: work
name: meeting-summary
description: Synthesize two or more source meeting notes into a forwardable BD/vendor/partner summary. Use extract-first attribution; run /attribution-lint before shipping.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/attribution-discipline.md]]"
  - "[[09 Rules/tasks.md]]"
companion-skills:
  - "[[.claude/skills/meeting-note/SKILL.md]]"
  - "[[.claude/skills/attribution-lint/SKILL.md]]"
created-by: claude
created: 2026-05-21
audit-trace: "2026-05-21 created in response to 沪差汇总 TapTap 都市可玩内容 fabrication incident; encodes extract-first workflow + §1/§2/§3 structural separation + provenance schema as Anti-fabrication defense"
---

# Skill: Meeting Summary (cross-source 汇总)

Turn 2+ source meeting notes into a structured forwardable summary. **This skill is the structural defense against the cross-source attribution fabrication failure mode** ([[MEMORY.md]] § 2026-05-21).

## When to Use

- ≥2 source meeting notes covering the same topic / counterparty class / trip / week
- Output is meant to be forwarded to {{PERSON}} / 主创 / 上级 (decision-grade)
- User says "汇总这几场" / "拼一下" / "把 N 篇拼成一篇" / "整理本周供应商对接" / "做个反馈与待办汇总"

**Do NOT use** for single meetings — those go to `/meeting-note` (with or without `--deep`).

---

## First Principle: Extract Before Synthesize

**The fabrication failure mode happens when "read 3 docs → directly generate summary table".** Synthesis pressure lands on the final output; party-attribution gets merged into the synthesis act.

This skill **forces a Phase A extract step** between reading sources and writing the summary. Every party-prefix cell in the final output must be traceable to a Phase A extracted quote. Phase A is the audit trail.

→ See [[09 Rules/attribution-discipline.md]] for the canonical rule. This skill is the workflow that operationalizes it.

---

## Workflow (4 phases)

### Phase 0: Extract Metadata

From user's request + the source files:
- **Source meeting notes**: list of files (Glob if user says "本周供应商对接" rather than naming them)
- **Date range**: from source frontmatter
- **Counterparties involved**: from each source's `counterparty:` field
- **Audience**: internal sync / {{PERSON}} / 主创 / 董事 / 跨组织
- **Output filename**: `YYYY-MM-DD-<chain-anchor>-反馈与待办汇总.md`

Save to **`03 Projects/{{PROJECT_A}}/04 会议纪要/`** (or appropriate project track per [[09 Rules/file-types.md]]).

---

### Phase A: Per-source Literal Extraction

⛔ **Non-skippable.** This is the audit trail that makes the summary verifiable.

For each source meeting note:

1. **Read the source completely** — Read tool, not Grep. Need full context to identify the right quotes.
2. **Identify each party's contribution** — for each speaker / org represented in the source, list literal quotes (or close paraphrases marked as such) by topic.
3. **Write quotes into `## §1. 各方原话档` section** organized by source meeting → by party → by topic. Use proper quote marks (「...」) and cite the source line.

Format:

```markdown
## §1. 各方原话档（按源会议 → 按方 → 按主题）

### §1.1 [源 1 — e.g. TapTap · 5/18]
源：[[2026-05-18-TapTap全口径]]

**TapTap 方：**
- **整体定位**：「翻天覆地，不是同一个游戏」（编辑级评价）— 源 §核心结论
- **玩法**：「都市玩法部分可玩内容不多，希望我方在二测包体中延长玩家停留时长」— 源 §玩法.顾虑
- **战斗**：「战斗部分手感还是有点飘，前后滑动反馈不到位」— 源 §战斗.顾虑
- **节点**：「发布的内容**我们其实不是很担心**，主要是这个节点」— 源 §三.协作意向

**我方自陈：**
- 「6 月 demo 都市探索只放 3 分钟时间」— 源 §四.我方
- 「差异点其实都在都市里面」— 源 §五.备注

### §1.2 [源 2 — e.g. B 站联运 · 5/19 14:00]
...
```

**关键规则：**
- 不在 Phase A 做任何归纳 / 锐化 / 跨方合并
- 只引该方原话或非常贴近的转述（明示「转述」）
- 我方自陈单列，**不混在对方的话里**
- 引语长度优先完整，宁长勿短

---

### Phase B: Cross-party Summary（基于 Phase A）

**只用 Phase A 中的引语作为输入。** 任何不在 Phase A 出现的"事实" → 回 Phase A 补，或归到 §2 综合判断。

#### B.1 反馈汇总表（结构）

```markdown
## §2. 跨会议反馈汇总
（每个 party-prefixed cell **必须** 在 §1 中能找到 literal anchor。否则前缀切换。）

| 主题 | 肯定 | 顾虑 | 建议 |
|---|---|---|---|
| **整体定位** | • **TapTap**：「翻天覆地」（§1.1）<br>• **B 站**：定位为战略级头部项目（§1.2） | — | — |
| **玩法** | • **B 站**：月灵都市文化结合逻辑能讲通（§1.2） | • **TapTap**：「都市玩法部分可玩内容不多，希望延长停留时长」（§1.1）<br>• **B 站**：玩法品类拥挤，{{PROJECT_A}}排末（§1.2） | • **TapTap**：二测包体加 POI / 月灵能力（§1.1 建议列）<br>• **我方判断**：B 站要求加大世界互动演示（§1.2 + 我方自陈差异点） |
| ... | ... | ... | ... |
```

#### B.2 表格写作规则

每条 cell 落笔时：
1. 找该 cell 的源 — Phase A 中哪一条引语？标出 (§1.X)
2. 若无源引语 → 改前缀为 `**我方判断**：/ **项目组观察**：` 等（[[09 Rules/attribution-discipline.md]] § 3）
3. 引语要忠实压缩，不锐化、不立场化

#### B.3 综合判断节（合成内容专属）

跨方推断 / 我方综合 → 单列在表后：

```markdown
## §3. 项目组综合判断（跨方合成）

### §3.1 都市玩法可玩内容厚度落差
**合成路径：**
- §1.1 TapTap 自陈"6 月 demo 都市只放 3 分钟"
- §1.1 我方自陈"差异点在都市里面"
- §1.2 B 站运营线"希望 8-9 月二测做大规模"

**我方判断：**
TapTap / B 站现场都未明确吐槽都市内容薄。但综合「demo 只展示 3 分钟差异点」+「运营线要做大」→ 我方判断二测包体应加厚都市可玩时长（多 POI / 月灵能力解锁）。

⚠️ 该条非任何 counterparty 直接表态，是项目组综合推断。
```

**关键规则：**
- §3 的每条必须显式列出合成路径（哪几条 §1 引语 + 我方推断逻辑）
- §3 的前缀只用 `**我方判断 / 项目组观察 / 我方推断**：`，禁用 counterparty 名

---

### Phase C: Action Items

```markdown
## §4. 待办汇总（按公司 / 按 owner 分类）
| 公司 | 优先级 | 截止 | 责任方 | 待办 |
|---|---|---|---|---|
| **TapTap** | 0 | 5/22 | 我方-商务 | 7 月发布会节点二选一对齐研发后回 TapTap |
...
```

- 仅列源会议中实际承诺 / 落地的 action items
- 我方-商务 owner 的 action items 同步 **`06 Tasks/Inbox.md`**（per [[09 Rules/tasks.md]]）
- 对方 owner action items 留在表内，不进 Inbox

---

### Phase D: Frontmatter Provenance（[[09 Rules/attribution-discipline.md]] § 4）

```yaml
---
type: meeting-summary
meeting-genre: <product-feedback | bd-pipeline | vendor-roundup | investor-debrief>
date: YYYY-MM-DD
project: <{{PROJECT_A}} | {{ORG_B}} | other>
chain-anchor: <短 anchor，例：沪差0519>
covers:
  - "[[<源 1>]]"
  - "[[<源 2>]]"
status: completed
audience: <internal | {{PERSON}} | 主创 | 上级 | 跨组织>
shareable-title: <标题>

source_anchors:
  # 每条 party-prefixed cell 一个条目
  - cell: "整体定位.肯定.TapTap"
    quote: "翻天覆地，不是同一个游戏"
    source: "[[2026-05-18-TapTap全口径]]#核心结论"
  - cell: "玩法.顾虑.TapTap"
    quote: "都市玩法部分可玩内容不多，希望我方在二测包体中延长玩家停留时长"
    source: "[[2026-05-18-TapTap全口径]]#玩法-顾虑"
  - cell: "玩法.建议.我方判断"
    synthesis_from:
      - "[[2026-05-18-TapTap全口径]]#玩法 — TapTap 自陈 demo 只放 3 分钟都市"
      - "[[2026-05-18-TapTap全口径]]#备注 — 我方自陈差异点在都市"
      - "[[2026-05-19-Bilibili联运全口径]]#8-9月规划 — B 站运营要做大"

revision-notes:
  v1-YYYY-MM-DD: 初版
created-by: claude
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
---
```

---

### Phase E: Lint Pass（强制）

写完后 **必须** 跑 `/attribution-lint <file>` 检查。skill 会：
- 扫所有 `^\*\*[^*]+\*\*：` 句式
- 验证每条在 `source_anchors` 中有匹配条目 OR 前缀是白名单（我方判断 / 项目组观察 / 我方推断 / 我方自陈）
- 不通过 → 列违规行 + 修法建议
- 通过 → 在文档加 `<!-- attribution-lint: passed YYYY-MM-DDTHH:MM -->` HTML 注释

不跑 lint 不允许声明完成。

---

### Phase F: High-Stakes 标注（[[09 Rules/attribution-discipline.md]] § 7）

若 `audience` 含 `上级 / {{PERSON}} / 主创 / 董事 / 跨组织`：

在文档开头（标题下方）加：

```markdown
> ⚠️ 该文档含 [N] 处合成判断（**`我方判断`** / **`项目组观察`** / **`我方推断`** 前缀，详见 §3）。
> 直接 counterparty 表态见 §1 原话档与 §2 表中 counterparty 前缀的 cell。
> 外发前建议人工抽查 §3 合成路径。
```

N = `source_anchors` 中 `synthesis_from` 条目数。

---

## Anti-Patterns（reject）

- ❌ 跳 Phase A，直接读 3 篇源文档 → 生成 §2 汇总表
- ❌ §2 表里出现 `**TapTap**：[某 claim]` 但 §1 原话档里找不到对应引语
- ❌ §1 引语锐化成 §2 表中的戏剧化版本（"demo 只放 3 分钟" → "玩一会儿就没东西了"）
- ❌ 跨方推断进入 §2 表 counterparty 前缀，而不是 §3 项目组综合判断
- ❌ Frontmatter 无 `source_anchors` 字段
- ❌ 不跑 `/attribution-lint` 直接声明完成
- ❌ audience 非 internal 但无 High-Stakes 标注
- ❌ Phase A 用 Grep 摘引语（会断章取义）— 必须 Read 完整源文档
