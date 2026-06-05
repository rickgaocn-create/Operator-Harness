---
type: reference
parent-skill: meeting-note
loads-when: "writing the deep-mode template body — Phase 3 (the template) and subsequent phases (Action / Wiki / Confirm / Auto-chain)"
created: 2026-05-21
---

# Deep Mode · Variant Templates + Phases 2–7

> The big template. Load after Phase 1 (Extract Header) + Phase 1.5 (Mode Detection) determine which Variant to use.

## Phase 2: Route (落档目标)

> **2026-05-15 起约定**：{{PROJECT_A}} / {{ORG_B}} 项目的会议纪要全部落档到对应项目的 `04 会议纪要/` 子目录。**废弃旧路径** **`00 Raw/会议纪要/**`（vault 根级）+ `**03 Projects/*/00 Raw/会议纪要/`**（项目内 raw）—— 这两处不再作为新纪要的写入目标。

| 条线 | 落档目标（canonical 2026-05-15 起）|
|---|---|
| **{{PROJECT_A}}** BD / 供应商 / 异业 / 渠道 / 政企 | **`03 Projects/{{PROJECT_A}}/04 会议纪要/【{{ORG_C}}商务】[对方]-[议题]会议纪要.md`** |
| **{{ORG_B}}** M&A / 标的尽调 | **`03 Projects/{{ORG_B}}/04 会议纪要/YYYY-MM-DD-[标的].md`** |
| **{{ORG_B}}** AIX 供应商 | **`03 Projects/{{ORG_B}}/04 会议纪要/YYYY-MM-DD-[供应商]-AIX.md`** |
| **跨项目 / 个人 / 其他** | **`04 Notes/Meetings/YYYY-MM-DD-[主题].md`** |

{{PROJECT_A}}文件命名：`【{{ORG_C}}商务】[对方简称]-[议题关键词]会议纪要.md` 或 `[活动名]-YYYY-MM-DD.md`（峰会 / 多发言人场景）。

**Auto-chain 影响**：**`03 Projects/{{PROJECT_A}}/04 会议纪要/**/*.md**` 与 `**03 Projects/{{ORG_B}}/04 会议纪要/**/*.md`** 均触发 [[CLAUDE.md]] § Skill Auto-Chain Rules 的 `/biz` 评估链。

---

## Phase 3: The Template

```markdown
会议时间：YYYY年M月D日
会议地点：[venue]
参会方：
● [对方公司]：[姓名1]（[职位1]）、[姓名2]（[职位2]）
● 我方：@[姓名1] @[姓名2]
会议类型：[Q&A 讨论 / 单向 vendor showcase / 我方汇报 / 混合]

## 核心结论

1.  [Situation / Status] — 我方当前状态 + 核心卡点 + 本次态度（推进 / 暂缓 / 深度评估）。
2.  [Their Offer / Key Reveal] — 对方核心方案包 OR 关键信息（视模式）。
3.  [Fit] — 对方能力 × 我方痛点的匹配度一句话判断。
4.  [Commercial Envelope] — 价格 / 条款 / 分档 / 窗口期（如适用）。
5.  [Market Context] — 行业信号 / 同品类标杆 / 窗口期判断。

---

## 1. [Section 1 — 按模式选择以下三种之一]

### Variant A — Q&A 讨论模式

`1. 我方核心问询及[对方]官方答复`

### 问题1：[问题简述]

1.  [答复要点 1 — 事实 / 机制 / 口径]
2.  [答复要点 2]
3.  [答复要点 3]

### 问题2：[问题简述]

1.  [答复要点]
2.  [答复要点]

（…每个问题一个小节；答复用编号列表，不用散文。**只列实际发生的问答**。）

---

### Variant B — 单向 vendor showcase 模式

`1. 关键信息点 / [对方]核心陈述`

按主题（不按提问顺序）组织：

#### 1.1 [主题1 — 例：视频生成模型现状]

- [关键陈述 1 — 含具体能力 / 数据 / 时间点]
- [关键陈述 2]
- [关键陈述 3]

#### 1.2 [主题2 — 例：数字人 / 语音 / 实时交互]

- [关键陈述]

#### 1.3 [主题3 — 例：企业级 agent 战略]

- [关键陈述]

#### 1.X [行业 case / 第三方实施反馈]（如有，重点列出）

- [case 1 — 含量化数据]
- [case 2]

> 关键规律：[揭示对方陈述中的底层逻辑或战略意图]

---

### Variant C — 我方汇报模式

`1. 我方核心陈述 + 关键反馈`

#### 1.1 我方汇报要点

- [汇报要点 1]
- [汇报要点 2]

#### 1.2 对方关键反馈 / 决策

- [对方姓名 / 角色] 反馈：[具体内容 + 倾向（推进 / 保留意见 / 反对）]

---

### Variant D — 多发言人 industry summit 模式

适用于 ≥ 4 位不同组织发言人、同一场会议、官方议程公开发布的场景。

`1. 官方议程速览`（一图速览表，建议直接列议程时段表）

| 时段 | 主题 | 发言人 | 录音是否覆盖 |
|---|---|---|---|
| HH:MM–HH:MM | [主题中文] | **[姓名]**（[职位 · 公司]）| ✅ / ❌ / ⚠️ 部分 |
| … | … | … | … |

`2. 发言人速览`（多对多 cross-org 场景的扫读层）

| § | 发言人 | 主题 | 与本项目相关度 | 是否 NDA |
|---|---|---|---|---|
| 2.1 | **[姓名]**（[职位 · 公司]）| [一句话主题] | 🟢 / 🟡 / 🔴 | 公开 / 部分 NDA / 完全 NDA |
| 2.X | … | … | … | … |

`2.X Session-by-session 拆解`（按议程顺序，每发言人一节）

#### 2.1 [姓名]（[职位 · 公司]）· [主题]

> **相关度：** 🟢 / 🟡 / 🔴 + 一句话定性

##### 2.1.1 [子主题 / 工作室背景 / 核心论点]
- [关键陈述 1 — 含具体数据 / 时间点 / 案例名]
- [关键陈述 2]

##### 2.1.2 [子主题 2]
- [关键陈述]

##### 2.1.X 关键学到的事 / 对方核心机制
（如适用：1-2 条 "load-bearing" 洞察）

---

（按选定 Variant 填充完后，继续 Section 2）

## 2. [对方] 核心能力及战略背景

### 1. [战略维度 1 — 例：移动端战略升级背景]
[段落叙述。解释"为什么现在"——对方的战略动机 / 行业位置 / 历史转折。]

### 2. [战略维度 2 — 例：硬件生态 / 生态合作 / 技术护城河]
[段落叙述。]

### 3. [战略维度 3 — 例：免费配套服务 / 生态红利]
[段落叙述。]

## 3. 我方痛点与[对方]优势匹配

| 我方核心痛点 | [对方]对应解决能力 | 核心收益 |
|---|---|---|
| [痛点1 — 具体、可量化] | [能力1 — 特性 / 免费项 / 版本] | [收益1 — 最好带数字 %] |
| [痛点2] | [能力2] | [收益2] |
| [痛点3] | [能力3] | [收益3] |

（MECE：痛点不重叠、覆盖本次议题全部卡点；没覆盖到的痛点 → 列为 Phase 5 的 Follow-up）

## 4. 后续行动计划

● [对方]侧：[对方承诺交付物 / 时间点 / 对接人]

● 我方侧：

  ○ [Owner] 牵头：[具体动作] — [deadline]
  ○ [参会 / 派员行动] — [时间窗口]
  ○ [内部评估 / 决策节点] — [deadline]
  ○ [后续洽谈触发条件]

● 双方：[达成条件后的联合行动]

### 附件 / 资源链接
- [外部活动链接]
- [参考文档]
- [工作微信群 / 截图 embed]
```

---

## Phase 4: Surface Action Items

For each **我方侧** action → propose append per `/task-capture` rules (routes by tag to project Kanban or **`06 Tasks/Inbox.md`** per [[09 Rules/tasks.md]]). Owner in title if not default {{USER_NAME}}; correct `#context-tag`; appropriate priority; ISO due date. **Batch ceiling: ≤ 3 new tasks per write.** Show exact lines, confirm, then write.

对方侧 action items → **stay in the minute, not in Inbox.** Their commitments aren't ours to track.

---

## Phase 5: Cross-Link to Wiki Archive

If counterparty has no entry in **`01 Wiki/`** yet:

1. Propose `(C) [对方公司].md` in the correct Wiki subfolder:
   - {{PROJECT_A}} 供应商 / 异业 → **`01 Wiki/{{PROJECT_A}}/异业合作/`**
   - {{PROJECT_A}} 渠道 → **`01 Wiki/{{PROJECT_A}}/渠道/`**
   - {{ORG_B}} 标的 → **`01 Wiki/{{ORG_B}}/[track]/`**
2. Archive should include: 公司核心档案、对接人、商务条款、支持体系、痛点匹配、AI / 技术路线、**当前决策状态**、后续 Follow-up Checklist、关联索引.
3. Always include a **`当前决策（YYYY-MM-DD）`** block — future sessions read this first to know live status without re-reading the whole transcript.

If archive exists → **update** the decision block + follow-up checklist; link the new minute into 关联索引.

---

## Phase 6: Confirm

> "会议纪要已落盘：[[path/to/note.md]]。对方档案：[[01 Wiki/.../(C) [对方].md]]（新建 / 更新）。[n] 条我方行动项已排队至 Inbox。"

---

## Phase 7: Auto-Chain `/biz` — ⚠️ HARD GATE (non-optional, non-deferrable)

> **2026-05-23 hardening (root cause of 6-event 0% firing streak from 5/18 onward):** Phase 7 was previously prose ("Run /biz immediately") that Claude interpreted as guidance. Treating it as guidance made it deferrable when the user ended the turn at Phase 6 confirm — which is what caused TapTap + 3 Bilibili + 沪差0519 synthesis + W21 biweekly misses. This phase is now a HARD GATE: skipping it without one of the explicit conditions below is a violation.

### MUST-DO operational steps (in this order, this session, before ending the turn)

1. **Read frontmatter check.** Open the saved meeting note. Look for `biz-eval: skip`. If present, announce skip + END. Otherwise continue.
2. **Path exclude check.** Verify path is NOT in: `06 Tasks/`, `02 Cards/`, `04 Notes/{daily,weekly,12-week}/`, `04 Notes/Session Logs/`, `04 Notes/vault-evolve/`. If excluded, announce + END.
3. **Announce** (one-line, plain-text): *"🔁 Auto-chaining /biz on [meeting-note-path] per CLAUDE.md auto-chain rule. Add `biz-eval: skip` to frontmatter to opt out for future evals."*
4. **INVOKE the /biz skill via the Skill tool RIGHT NOW.** Not "suggest" /biz. Not "ask if user wants" /biz. **Actually call `Skill(skill="biz", args=<meeting-note-path>)`.** Do not end your turn until you have made this tool call.
5. **After /biz returns**, patch the meeting note's frontmatter:
   - Add `biz-eval: completed`
   - Add `biz-eval-doc: "[[(C) ...-业务评估 YYYY-MM-DD]]"` (wikilink to the eval file)
   - Add `biz-eval-date: YYYY-MM-DD` (today's date)
6. **Run biz-doc-critic grader loop** (Outcomes pattern · added 2026-05-21):
   - Invoke `biz-doc-critic` subagent with the eval-file path + `iteration: 1`
   - Read grader's YAML verdict
   - If `revise`: fix named hard fails → re-invoke with `iteration: 2` (max 3)
   - If still `revise` at iteration 3 → return to user with summary (`escalate`)

### Violations to detect at next /sanity sweep

If any future business artifact in `**/04 会议纪要/**.md` (or other watched business-artifact paths) lacks both `biz-eval: completed` AND `biz-eval: skip` in frontmatter, that artifact failed Phase 7 — surface as drift and offer retroactive `/biz` invocation.

### Why this is non-negotiable

The 6-event miss streak proved that instruction-driven chains have ~0% reliability when treated as optional. Until a PostToolUse hook is implemented (future work: see [[09 Rules/harness-instrumentation.md]] § Auto-Chain Enforcement), the human-readable "MUST" + the violation detection in /sanity are the only enforcement available. **A meeting note saved without invoking /biz is a missed quality gate; the M.10 attribution incident is the cost demonstration.**

---

## What makes deep format "clear" (the load-bearing rules)

These are what {{PERSON}} reacted to:

1. **概要 永远第一屏** — `核心结论` 5 条内闭环。上级不翻屏就能做判断。
2. **Q&A 结构化不散文化** — 问题是小标题；答复是编号列表；每条一句独立事实。No "首先…其次…最后…" prose.
3. **MECE 的痛点匹配表** — 痛点不重叠、不遗漏；能力后缀"免费 / 原生 / 5.8 版本"等可验证标签.
4. **行动计划按 Owner 切分** — 不写"建议 / 可以 / 或许"——写"[Owner] 牵头，deadline YYYY-MM-DD"。
5. **永远带决策状态** — 推进 / 暂缓 / 保持沟通。"讨论了一下"不是决策。
6. **数字优先** — 30%, 150 万美金, 2%, 16 个月, 5.8 版本 — replaces "很多 / 较好 / 不错".
7. **可点开的链接** — 同事 / 公司 / 相关决策都以 `[[wiki-link]]` 形式插入.
8. **不写感想** — 会议纪要是事实载体，不是复盘感言. No "这次会议收获很多".
