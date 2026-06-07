---
type: reference
parent-skill: meeting-note
loads-when: "deep mode invoked (`--deep` flag, deep-trigger phrase, or auto-detect flips to deep)"
created: 2026-05-21
---

# Deep Mode · Core Rules

> Load when SKILL.md routes to deep mode. Covers: First Principle, Role Separation (note vs eval), Voice Register C, Meeting Modes table, Mode detection.

## First Principle (governs every rule below)

**Structure emerges from substance, not the reverse.** Every artifact is a contract between content and form. When form drives content (template-fitting), the result is hallucination, filler, or mis-targeted output. When content drives form, the result is honest, lean, faithful.

Every sentence in a meeting note must do one of:

1. **Provide specific information** the reader doesn't have (a fact stated, a number quoted, an event recorded)
2. **Reduce specific risk** (source caveat, evidence boundary, transcript correction)
3. **Specify a specific action / commitment** (counterparty's promise, our follow-up handle)
4. **Cross-link** to the broader vault context (Cards 候选, eval pointer, archive, OKR)

If a sentence does none of these four, it is noise — cut it. Saturating "据官方陈述" / "vendor 主张" labels per-line is one such failure (one upfront source-criticism block conveys the same information without dilution).

---

## Role Separation: Meeting Note vs. Business Evaluation

The **meeting note** is the **factual record** of what was said. The **business evaluation** (`/biz` output) is the **analytical layer** on top.

| Belongs in meeting note | Belongs in business evaluation |
|---|---|
| Header (time / location / parties / mode) | Multi-stakeholder framing or 概要 for decision-makers |
| Source criticism (one block, not per-line tags) | Capability matching tables (痛点 × 火山能力) |
| Faithful record of what was said (vendor's own claims, third-party reports, our own observations) | Decision frameworks with Decision Gates |
| Counterparty's commitments | Strategic interpretation / 战略意图解读 |
| Our action handles (what we will follow up on) | PoC design templates |
| Cards candidates | Cost analysis / ROI |
| Pointers (to eval, archive, OKR) | Risk decomposition with mitigation |

The eval cites the meeting note as the factual source. The meeting note links to the eval as the analytical companion. **Don't duplicate.** When a meeting note tries to do both jobs (痛点匹配 tables, detailed Decision Gates), both files bloat and the role of each becomes unclear.

For one-way showcases specifically: the meeting note answers "what did the counterparty present?"; the eval answers "what should we do about it?"

---

## Voice Register C — 总体判断 / Executive Summary（项目组成员综合印象，非 AI 框架分析）

> **Hard rule（2026-04-30 加入）：** 高规格会议纪要 / 业务评估文档的 "总体判断" / "执行摘要" / "我的核心判断" 章节，**必须以参会人作为项目组成员的第一人称综合印象**呈现，而**不是** AI 框架式 / 分析师视角的客观结构化叙述。文档其余部分（事实记录、产品矩阵、时间表、风险表）保持 Register B（formal/third-person）；总体判断章节切换到 Register C。

### 为什么独立成 Register C

- 上级读总体判断是要"听项目组的人怎么看"——他们要感受参会人的判断、直觉、立场、保留意见
- 框架式叙述（"X 由 A 与 B 两条管线构成，二者节点 / 工种 / 成熟度各异"）听起来像外部分析师 / AI 总结，**削弱项目组的话语权**
- 主体（事实记录）须客观；总判断（团队 take）须有立场

### Register C 标记

| ✅ 该用的 | ❌ 该避的 |
|---------|---------|
| "我看下来…" / "我觉得…" / "我的判断是…" / "对{{PROJECT_A}}而言…" | "X 由 A 与 B 构成，二者…" — 抽象框架开头 |
| 按产品 / 板块分别讲清"对我们而言怎么用" | "整体 HOLD，除两个例外" — 解析结构语 |
| 具体保留意见明示（"这是我对 X 最大的保留"）| "应按管线独立评估" — meta-prescriptive 语 |
| 例子型直白（"火山主推方向更适合传奇类买量游戏"）| "三层 / 四层结论" 框架罗列（可作为辅助补充，但不是主角）|
| Actionable instinct（"可以借方法论，不能套打法"）| 通用决策模板话（"建议以低成本 PoC 替代…"）|

### Register C 写作模板

```
### X.Y 总体判断（项目组综合印象）

> 这一节是参会人（[姓名]）作为 [项目] 项目组成员，对 [对方/产品] 的第一手直观印象。
> 下面每一条都是直白看法，按 [产品线 / 议题板块] 分别讲清"对我们而言怎么用"，
> 不是框架式分析。细化映射 / 数据见 §X.Y 末尾，案例诊断见 §Z。

**[产品线/板块 1]** —— [项目人观察 + 对项目的具体含义 + 保留 / 推进态度]。

**[产品线/板块 2]** —— ...

[每条 2-4 句，直接、有立场、举具体细节]

> **一句话总结：** [对方角色定位 + 项目方动作分流]。
```

### 何时用 Register C

- "总体判断" / "执行摘要" / "我的核心判断" / 任何 概要 段落
- 当 audience 在问 "what's your take?" 而不是 "what's the framework?"
- 框架表 / 时间表 / 风险表仍可在该段落之后作为 supporting reference

### 何时不用（保持 Register B）

- 事实记录主体（介绍内容 / 客户案例 / 火山发布节奏 / 后续动作）
- 时间表 / 成本估算 / 风险表 / 关联文档 / 附录 — 这些是客观参考数据
- 若文档全文都用 Register C，会丢失文件作为客观记录的可信度

### Origin

{{USER_NAME}} 反馈 2026-04-30 on 火山引擎闭门会纪要 §1.2：初稿用 AI 框架口吻 ("游戏行业由研发管线与发行管线两条独立工作流构成…")；{{USER_NAME}} 反馈"这里写的更像你作为人工智能的思考，并不应该成为这个核心的判断…理应是基于项目组的人针对各产品的综合印象，比如：买量素材相关，我们这样的精品游戏，更适合传奇类的买量游戏"。重写为 Register C 项目组综合印象后接受。

---

## Meeting Modes (Phase 1.5 — non-skippable)

Before drafting any content for section 1, identify which mode this meeting is in. **Different modes use different section 1 structures.** Mode confusion is what makes meeting notes unsharable to leadership.

| Mode | Description | Section 1 structure |
|---|---|---|
| **Q&A discussion** | 我方主动问询 + 对方答复（典型：vendor negotiation, M&A diligence, partner interview, technical eval, 投后沟通） | `1. 我方核心问询及[对方]官方答复` — each question a sub-heading, answers numbered. (See Variant A in [[references/deep-variants.md]].) |
| **One-way vendor showcase** | 对方单向陈述, 我方观察记录（典型：闭门会、产品发布会、行业趋势分享、tech briefing） | `1. 关键信息点 / 对方核心陈述` — organized by **topic**, not Q&A. Each sub-section is a content domain. (See Variant B.) |
| **We present** | 我方做汇报, 对方反馈（典型：董事会汇报、partner pitch、内部 sync） | `1. 我方核心陈述 + 关键反馈` — our presentation summary + decision-makers' comments / objections / approvals. (See Variant C.) |
| **Hybrid (some Q&A in a showcase)** | 多数 vendor 单向陈述 + 局部我方问询 | Use **one-way structure as default**, then add a final sub-section `1.X 现场问答（仅限实际发生的）`. |
| **Industry summit / multi-speaker panel** | 同一会议有 ≥4 位不同组织 / 不同主题发言人 | `1. 官方议程速览` + `2. 发言人速览表` + Session-by-session 拆解. (See Variant D.) |

### Mode detection — ask if uncertain

If the source transcript / user's notes don't make the mode obvious, **ask the user explicitly** before drafting:
> "这次会议是 (a) 双方问答讨论 / (b) 对方单向 showcase / (c) 我方汇报对方听 / (d) 混合 — 主要是单向 + 局部我方问询？我会按对应结构生成。"

Never default to Q&A mode without evidence the user actually asked specific questions.

---

## ⛔ HARD RULE: Never Fabricate Q&A

**The Q&A section is for cases where there's a literal back-and-forth.** If the user did not actually ask question X and receive answer Y, **do NOT invent that exchange**. This is the failure mode that makes meeting notes unsharable — leadership reads "我方问：X" and assumes someone literally asked it; if they didn't, the report is fabrication.

**When to use Q&A structure:**
- ✅ User's source notes contain "问：... 答：..." or "我问 / 对方答" patterns
- ✅ Transcript shows back-and-forth between user and counterparty
- ✅ User explicitly tells you which questions they asked
- ✅ Mode is verified Q&A discussion

**When NOT to use Q&A structure:**
- ❌ User's notes are observation-style ("对方主推..." / "对方提到...") with no question-marker
- ❌ Vendor showcase / 闭门趋势分享 / 产品发布会
- ❌ User describes "对方介绍了..." / "对方分享了..." without describing their own questions
- ❌ When in doubt — use one-way mode and offer to add specific Q&A only if the user verifies what they actually asked

**Recovery if Q&A was fabricated and shipped:** Surface the error explicitly to the user. Replace the Q&A section with the appropriate mode's section 1. Update the biz evaluation if it referenced fabricated questions. Add a 变更日志 entry noting the correction.

---

## ⛔ HARD RULE: Party-Attribution Discipline

Canonical rule: [[09 Rules/attribution-discipline.md]]. Sibling to "Never Fabricate Q&A".

For any line of the form `**[party]**：[claim]` in this skill's outputs:

- Single-meeting notes (this skill) must follow it for any party-prefixed feedback / 评价 / 反馈 line
- Cross-meeting summaries belong in [[.claude/skills/meeting-summary/SKILL.md]] — that skill enforces the rule structurally (Phase A extract + Phase B synthesis + provenance schema + `/attribution-lint`)

**Trigger to switch to meeting-summary skill:** user asks to combine ≥2 source meeting notes → invoke `/meeting-summary` not `/meeting-note`.

**Origin incident:** [[MEMORY.md]] § 2026-05-21 (沪差汇总 TapTap 都市可玩内容捏造) — read it before producing cross-source artifacts.
