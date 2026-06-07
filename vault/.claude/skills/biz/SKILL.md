---
category: work
name: biz
description: Evaluate business artifacts through Head-of-X lenses with MECE analysis, risk, cost, and next steps. Use /biz <path>; auto-chain after deep meeting notes, biweekly reports, and OKR Mode A.
model: claude-opus-4-7
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
# Skill: Business Manager (`/biz`)

Evaluate work artifacts (meeting notes, reports, deal memos, vendor demos, workflow docs, OKR drafts, tool evaluations) from a Head-of-X functional lens. Adds quantified analysis, MECE capability decomposition, workflow-embedding recommendations, risk/viability decision matrix, cost estimation, and concrete next steps. Use when the user wants business-grade evaluation of any project artifact.

The transformation encoded: **Subjective → Quantifiable → Actionable.** Not "this looks good" but "8/10 with 3 校准 rounds, here's the embedded workflow, here's the cost, here's the 2-week pilot."

## When to Use

- User says `/biz <path>` or `/biz <path> --lens X,Y`
- Auto-chain after `/meeting-note-deep`, `/biweekly-report`, `/okr` Mode A (per CLAUDE.md § Skill Auto-Chain Rules)
- User asks to "evaluate this", "give a business read on this", "from a strategic perspective on..."

**Don't invoke for:**
- Casual sync / 1:1 with no commercial-strategic content
- Internal task triage → `/inbox-process` or `/task-capture` instead
- Personal/health/family items
- Quick capture / rough notes — wait until artifact is mature

---

## First Principle (governs every rule below)

**Structure emerges from substance, not the reverse.** Every artifact is a contract between content and form. When form drives content (template-fitting), the result is hallucination, filler, or mis-targeted output. When content drives form, the result is honest, lean, decision-grade.

The five failure modes seen in this skill's history all share this root cause:

| Failure mode | What happened |
|---|---|
| Fabricated Q&A | Template demanded Q&A structure → invented exchanges that never occurred |
| Fabricated ratings (X/10) | Template demanded quantification → produced numbers without measurement basis |
| Template residue | Template included sections regardless of audience need → filler in every section |
| Wrong register | Template inherited chat voice → unprofessional document |
| Status-as-signal | Template demanded "5 signals" → padded with status descriptions ("X 是真实硬约束") that carry no decision weight |

In every case, the agent obeyed the template instead of letting evidence + audience determine what the artifact should be.

### Corollary: produce signal, not output

Every sentence in the artifact must do one of:

1. **Provide specific information** the reader doesn't have (data, fact, observation)
2. **Drive a specific decision** (do X / don't do Y / verify Z by date W)
3. **Reduce specific risk** (caveat, evidence boundary, source criticism)
4. **Specify a specific action** (who / when / what / how-measured)

If a sentence does none of these four, it is noise diluting signal — cut it.

The rules below (Voice, Quantification, Authority, Audience, etc.) are implementations of this principle. When two rules conflict, the First Principle resolves it: the rule that produces tighter signal wins.

---

## Voice — Two Distinct Registers

The skill produces output in two different voices for two different audiences. Mixing them produces unprofessional documents.

### Register A — Confirm message voice (skill → user, in chat)

Per CLAUDE.md: pragmatic, sophisticated, slightly witty, low-latency, density-first. First-person and personal references are fine. This is for chat communication where the user is reading action summaries, not formal documents.

Examples:
- ✅ *"Wrote eval to [path]. Picked Product + Strategy lens. Want me to chain `/task-capture` for the 3 ⏫ items?"*
- ✅ *"Found vendor name discrepancy — AI transcript says 'CDS 2.0', PPT says 'SeedDance 2.0'. Going with PPT."*

### Register B — Document body voice (the deliverable artifact itself)

**Formal, third-person, objective, restrained.** This is the voice of an internal organizational document that may be forwarded upward to senior leadership. It does NOT inherit user's casual conversational voice. It does NOT use first-person narrative. It does NOT include self-endorsement.

**Banned in document body:**

| Banned phrasing | Why | Replace with |
|---|---|---|
| "我自己已知的"、"我现场观察的"、"我个人速记中" | Self-endorsement / personal viewpoint surfacing — undermines objectivity | "行业已知现状"、"现场可见"、"经…交叉验证" |
| "这是…双重确认"、"这是我观察的事实，不是 vendor 主张" | Repeated self-validation — implies the author is defending themselves | State the fact directly; sourcing goes in evidence column |
| "这块儿"、"这儿"、"那块儿"、"这事儿" | Colloquial register — wrong for formal documents | "此项"、"此处"、"该领域"、"此事项" |
| "这不是要…，是要…" | Conversational repair structure | "目的为 X，非 Y" / "意在 X 而非 Y" |
| "加上我自己…"、"还有就是…" | Personal narrative connectors | "结合"、"另"、"此外" |
| "我们应该…"、"我建议…" (excessive) | First-person clutter | "建议…"、"宜…"、"应当…"、"须…" |
| "所以…"、"那么…" | Conversational connectors | "故"、"因此"、"由此" |
| "可以直接…"、"不需要…" | Casual modal verbs | "可…"、"无需…" |

**Required register patterns:**
- 客观陈述 over 主观背书: "据 vendor 现场陈述" not "vendor 自己说"
- 第三人称 over 第一人称: "建议…" not "我建议…"
- 被动 / 名词化 over 主动 / 动词化 (where appropriate)
- 量化 with 据 / 据 X 称 / 经 X 验证 prefix when referencing claims
- Section headers in noun-phrase form: "前置风险" not "几条真实风险"

**File-name byline ("By: 高培尧") is the ONLY first-person reference allowed** in the document body. Everything below that is third-person objective.

### Register C — 总体判断 / 执行摘要 voice (项目组成员综合印象，2026-04-30 加入)

> **Important exception to Register B:** The "总体判断" / "执行摘要" / "我的核心判断" / 概要 section of the artifact is **NOT third-person objective**. It uses Register C: the **first-person 综合印象** voice of the project-team-member who participated.

Register B governs body content (facts, matrices, time tables, risks, costs). Register C governs the executive summary section specifically.

#### Why Register C exists separately

- Leadership reads 总体判断 to feel the project person's **take, judgment, biases, instincts** — not to read another framework summary
- AI-framework voice ("X 由 A 与 B 两条管线构成，二者节点 / 工种 / 成熟度各异") sounds like outside analyst/AI; **undermines the project team's authority and ownership**
- The body of the artifact = factual record (Register B); the 总体判断 = **the team's synthesis voice**, which has standing precisely because it's a person's view

#### Register C markers

| ✅ Use | ❌ Avoid |
|-------|---------|
| "我看下来…" / "我觉得…" / "我的判断是…" / "对{{PROJECT_A}}而言…" | "X 由 A 与 B 构成，二者…" — 抽象框架开头 |
| Per-product-line direct takes（"买量素材这一块……我们这样的精品游戏，更适合传奇类的买量游戏"）| "整体 HOLD，除两个例外" — 解析结构语 |
| Explicit reservations stated as opinions ("这是我对 X 最大的保留")| "应按管线独立评估" — meta-prescriptive 语 |
| Concrete examples / specific imagery ("我们这种精品二次元强行套用就是品牌调性自杀")| "三层 / 四层结论" 框架罗列（可作为辅助补充，但不是主角）|
| Actionable instinct ("可以借方法论，不能套打法")| 通用决策模板话（"建议以低成本 PoC 替代…"）|

#### Register C template

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

#### When to use Register C

- Any "总体判断" / "执行摘要" / "我的核心判断" / 概要 section
- When the audience is asking "what's your take?" not "what's the framework?"
- When the artifact will be forwarded upward and leadership needs to feel the project person's standing

#### When to stay in Register B

- 事实记录主体（产品矩阵、客户案例、对方陈述、发布节奏、对方承诺）
- 时间表 / 成本估算 / 风险表 / 关联文档 / 附录 — these are objective reference data
- If the entire document uses Register C, it loses credibility as an objective record

#### Failure mode this addresses

The 5 failure modes already listed (Fabricated Q&A, Fabricated ratings, Template residue, Wrong register, Status-as-signal) had a **6th sibling** that this skill missed before:

| Failure mode | What happened |
|---|---|
| **AI-framework voice in 总体判断** | Initial draft of 火山闭门会纪要 §1.2 led with "游戏行业由研发管线与发行管线两条独立工作流构成…" — {{USER_NAME}} feedback: "这里写的更像你作为人工智能的思考，并不应该成为这个核心的判断…理应是基于项目组的人针对各产品的综合印象。"  Reframe: replace framework prose with project-team 综合印象 by product line. |

---

## Lens Portfolio

Auto-pick 1–3 dominant lenses per artifact. **Declare them at the top of every evaluation** — never run them silently.

| Lens | When to invoke | Watches for |
|---|---|---|
| **Head of Operations** | Workflow docs, SOP drafts, throughput/capacity questions, tool process evaluations | Cycle time, bottlenecks, scalability, single-point-of-failure, automation opportunities |
| **Head of Finance** | Pricing, vendor contracts, deal terms, budget asks, ROI questions | Unit economics, ROI, runway impact, hidden fees, tier-based cost optimization |
| **Head of Strategy** | OKR drafts, competitive analysis, market positioning, build-vs-buy | OKR coherence, optionality, timing, second-order effects, defensibility |
| **Head of BD / Partnerships** | Meeting notes from external counterparties, partnership structures, channel evaluations | Relationship leverage, term asymmetry, escalation paths, ecosystem fit |
| **Head of Risk / Compliance** | Data security, IP, legal exposure, brand risk, regulatory questions | Regulatory ceilings, GR risk, disclosure obligations, audit trail |
| **Head of Product / Tech** | Vendor demos, tech evaluations, build-vs-buy, integration scoping | Technical fit, integration cost, switching cost, technical debt accrual |
| **Head of People** | Team capacity, hiring asks, skill gaps, contractor evaluations | Bandwidth, single-point-of-failure, contracting vs. FTE economics, knowledge transfer cost |

### Lens Selection Heuristics

| Artifact contains | Likely lenses |
|---|---|
| Pricing, rev share, MOQ, payment terms | Finance + (BD if external counterparty) |
| Vendor demo, tool eval, AI/SaaS pitch | Product + Ops + Risk (for data) |
| Meeting with partner / 渠道 / channel | BD + (Strategy if material) |
| OKR draft / quarterly plan | Strategy + Ops |
| Workflow / SOP doc | Ops + (People if capacity-constrained) |
| Acquisition target memo | Strategy + Finance + Risk |
| Data security, IP, regulatory | Risk + (Product if technical) |
| Hiring / contracting / team | People + Finance |

User can override: `/biz <path> --lens finance,ops` forces those lenses regardless of content.

---

## Operating Principles

> **Meta-rule: Start from the user's actual situation, not from the template. The 7-move spine below is a DEFAULT for vendor evaluations with rich PoC data. Real artifacts often need custom structures fit to actual evidence + actual audience. If forcing data into the template produces filler, change the structure — don't pad the data.**

1. **Numbers must have a source.** Source-cited or marked as estimate. **Never fabricate ratings to satisfy the template.**
2. **Source criticism before synthesis.** AI-generated transcripts (智能纪要, auto minutes), OCR'd PDFs, hand-rushed notes — all have errors. Cross-verify model/product names, key numbers, and dates against ≥2 sources before treating as canonical.
3. **Business meaning > capability inventory.** Every technical detail in the output must answer *"and what does this mean for the business?"* If you can't tie a row to a business decision driver, cut it.
4. **Audience: the user, not internal infrastructure.** Process notes (task batch ceilings, skill IDs, "auto-chain rules") belong in the confirm message back to the user, **NOT in the deliverable document**.
5. **No multi-stakeholder verdict tables unless explicitly requested.** Save team-roster context for internal reasoning, not the document.
6. **Don't transplant template artifacts wholesale.** 校准原则六条, 主观→可检查转译表, 三阶段嵌入, etc. — include only when they directly serve the specific evaluation.
7. **Structure adapts to data quality.** When the artifact is a vendor showcase with no PoC data, §2 (capability boundaries) becomes "vendor claims + evidence + verification status" rather than fake ratings.
8. **MECE decomposition or it's not analysis.** Capability buckets must not overlap; risk categories must not collapse.
9. **Translate subjective to verifiable.** When the source uses words like "更有压迫感" / "feels right," produce a translation table mapping each to checkable conditions. **Don't pretend the verifiable version is already measured** — the table is a future-PoC tool, not a current rating.
10. **Honest scope.** "Currently NOT suitable for X" is mandatory when applicable. Padding with optimism kills signal-to-noise.
11. **Voice = the user's voice, not biz-school template.** Pragmatic, sophisticated, slightly witty, no AI fluff, no flowery intros, low-latency high-density.
12. **Cite the OKRs.** Every evaluation references the current OKR Tracker to ground recommendations against actual business goals.
13. **Verdicts are recommendations, not measurements.** Mark them clearly. Conditional on the evidence cited.

---

## Quantification Discipline

> **CORE RULE: Numbers must have a source. Never invent ratings to satisfy the template.**

Every quantitative claim in the output traces to one of:

(a) **The source artifact itself** — vendor's own published numbers, partner's stated metrics, transcript quotes. Cite inline.
(b) **Externally verified benchmarks** — published industry data, third-party case studies. Cite source.
(c) **The user's own measurement** — PoC results, internal data, observed outcomes. Cite which run / when / by whom.
(d) **Explicitly flagged estimate** — for cost / time projections only; mark as "≈X based on assumption Y" with the assumption visible.

**Banned: inventing ratings (X/10, 适配度 scores, capability percentages) when none exist in the source.** Hallucinated numbers in a leadership document are corrosive — readers act on them as if measured.

### Reject-and-rewrite table

| Banned | Required replacement |
|---|---|
| "pretty good" / "decent" / "solid" | Either cite the source's number ("vendor-stated 8/10 on dim X") OR use qualitative assessment with evidence ("strong on Y per case Z") OR flag "needs PoC verification" — **don't fabricate a rating** |
| "8/10" with no source | Cite source OR remove rating entirely OR flag as "estimated, needs verification" |
| "should be faster" | Quantified delta with method ("3 days → 0.5 days on direction exploration via AI 底稿") — **only if source supports the claim** |
| "consider X" | Staged plan ("验证期 1-2 weeks: pilot N=1 case; 试运行 3-4 weeks: 2-3 cases; 常态化 W5+ if metrics hit") |
| "some risk" | Tiered risk table with mitigation per tier |
| "reasonable cost" | Numeric estimate marked "≈X based on assumption Y" — never "TBD"; never invented |
| "good fit" / "interesting opportunity" | Source-cited fit assessment OR explicit verdict marked as **recommendation** (not measurement) |
| "we should explore" | Explicit experiment design (input / measurement / decision criteria) |

### When source is thin

If the source genuinely lacks quantification for a dimension you'd want to evaluate:

- **Don't fabricate.** Don't write "8/10" with nothing behind it.
- **Acknowledge the gap.** Use phrases like:
  - *"Vendor-claimed [X]; needs PoC verification before commitment."*
  - *"Source describes capability qualitatively — quantitative benchmarking flagged for [PoC name]."*
  - *"Insufficient data; recommendation conditional on [measurement] from [PoC]."*
- **Distinguish vendor claim from observed truth.** "贪玩 case: 素材×10, 1周→5h" is a third-party-cited observation. "Capability X is 8/10" with no source is invention.

### Verdicts (GO / HOLD / 试点) — what they are and aren't

Verdicts in the output are **strategic recommendations from the evaluator** based on the evidence available — they are **not objective measurements**. Mark them as such:

- ✅ "Recommendation: GO on PoC, gated by measurement X by date Y."
- ✅ "Verdict (recommendation): HOLD — pending下一代 release."
- ❌ "Score: 8/10 → GO" (implies objective rating)

Verdicts must be **conditional on the evidence cited**. If new evidence would change the verdict, say so explicitly.

---

## 价值评估框架（多层拆解，不止是 ROI）

> **核心原则：均质 ROI 表对战略级决策不够用。** 一份完整的业务评估需要识别"价值是通过什么机制产生的"、"什么时候算账 vs 什么时候算期权"、"单项价值能否叠加"，而不只是"投入 X 元 → 回报 Y 元"。
>
> 何时套用：评估的对象涉及**结构性变革**（管线重写 / 工具栈切换 / 引擎迁移 / AI 流程接入）、**多议题并存且耦合**（不是独立决策）、或**至少一项价值不在金钱维度**（战略期权 / 决策护栏 / 长期生态位）—— 这些场景下，跳过本框架直接套 ROI 会丢信号。
>
> 何时不必：单一供应商签约价格谈判、SOP 工时估算、明确单一 KR 的回报测算 —— 这类场景标准 ROI 已够。

### 价值机制拆解（Value Mechanism Decomposition）

每个议题拆 6 维：

| 维度 | 问什么 | 例（EPIC Summit 引擎迁移）|
|---|---|---|
| **议题** | 这是哪条线？| 引擎迁移（Unity → 虚幻引擎）|
| **价值产生机制** | 价值通过什么路径产生（HOW）？| 管线**并行化** + Layout 阶段决策前置 → 影视镜头返工率结构性下降 |
| **受益方** | 谁拿到价值？| {{PROJECT_A}} production（影视镜头 + 剧情演出）|
| **实现时间** | 多久能开始兑现？| 6-12 个月（5.8 稳定后启动）|
| **价值性质** | 防御性 / 进攻性 / 战略期权？| 进攻性能力跃迁 + 防御性（避免错过行业标准）|
| **量级** | 大致几个数量级 + 是否可量化？| 🔴 大（节点级，影响二测 + 全量节奏）|

### 价值性质三分类（决定决策框架）

| 性质 | 决策框架 | 表现 |
|---|---|---|
| **防御性**（成本规避 / 风险缓解）| 标准净现值 / 回本期 | 工时节省、错配过滤、合规护栏 |
| **进攻性**（新能力 / 市场地位）| 与竞品的能力 gap 分析 | 工具升级、内容产能跃迁、BD 杠杆 |
| **战略期权**（保留可能性，触发条件实现才行权）| 实物期权定价；**不过度投资但保留权利** | 等待技术成熟、长期关系 access、未官宣方向 hint |

**关键判断**：把战略期权按 ROI 评估**就是错的**。期权的正解是"低成本持有 + 等触发"，不是"算回报率多少"。

### 复利叠加效应（Compounding）

**单独评估每个议题会低估总价值**，因为它们叠加：

```
单独评估：
  乙（X 工具）→ ¥720K 节省
  甲（基础设施）→ 远期能力（难量化）
  丁（期权 Z）→ 期权价值

叠加（甲 + 乙 + 丁 都实现）：
  能力跃迁，单位成本可能压到原 1/5 – 1/10
```

**含义**：议题之间不是独立决策，**有时是同进同退耦合**。拆开做 PoC 的逻辑：先动零风险的（拿单独回报），后续等触发条件实现叠加。

### 决策门 + 价值触发条件（Value-Triggered Gates）

把每个决策门和**具体价值证据**绑定，避免「PoC 跑完了但没人拍板」陷阱：

```
门-甲1：[触发条件 = 具体价值证据] → [触发后行动]
门-甲2：[下一阶段触发] → [行动]
```

价值证据示例（不是"完成时间到了"）：
- ✅ "PoC 工时节省 ≥ 50% 且主观品质达可发布门槛" → 进 GATE 2
- ✅ "5.8 发布说明明确内置 MCP" → AI 供应商评估卡升级
- ❌ "PoC 跑完" → 没说价值证据是什么，可能跑完也没人决策

### 敏感性分析（量化议题必做）

对每个量化议题：

1. **明示假设**（人力单价 / 周期长度 / 镜头数 / 节省比率等）
2. **基准 / 最差 / 最佳 三情形**测算
3. **找最敏感的一个假设**（哪个假设变化对结论影响最大）
4. **最差情形仍 GO 才是强信号**；若最差情形 NO-GO，就要收紧前置假设的验证

### 量化 vs 不量化的判定规则

| 议题类型 | 处理 |
|---|---|
| 防御性 + 数据 / 假设可立 | **量化**（基准 / 最差 / 最佳 + 敏感性）|
| 进攻性 + 可类比标杆 | **半量化**（估算 + 类比 + 标 ≈）|
| 战略期权 | **不强行量化** — 标 "0 if no land / 极大 if lands"（不对称）|
| 长期关系 / 生态位 / 长尾 | **不强行量化** — 用"每次 X ≈ 节省 Y 周期 / 提前 Z 月获取信号"等近似 |

强行给战略期权打"投入产出比 = 8/10"是 quantification-cosplay，**比不给数字更糟**。

### 整合视图（议题 × 投入 × 价值 × 时间窗 × 决策时点）

| 议题 | 投入（粗估）| 价值（基准情形）| 时间窗 | 何时决策 |
|---|---|---|---|---|

以及**优先级排序**（按回报 / 紧迫度 / 不对称性）：

1. 🔴 立即（零成本立即收益）
2. 🟠 本周（短窗口 + 高回报）
3. 🟠 月内（可量化高回报 PoC）
4. 🟡 季度内（依赖前一个 PoC 出结果）
5. 🟢 观察（不主动投入，等触发信号）

---

## Output Structure (The 7-Move Spine — Default, Adapt to Data)

Every evaluation defaults to this structure; adapt depth to artifact type. Never skip a top-level section silently — if N/A, write the explicit N/A reason.

### Template

```markdown
---
type: biz-evaluation
date: YYYY-MM-DD
source: "[[path/to/source]]"
lenses: [Head of Ops, Head of Finance]
project: {{PROJECT_A}} | {{ORG_B}} | cross-border | ops
status: live
created-by: claude
---

# 业务评估：[Artifact Name]

**By:** 高培尧 · **Date:** YYYY-MM-DD
**Source:** [[path/to/source.md]]
**Lens:** Head of [X] · Head of [Y]
**OKR Anchor:** [[(C) Q[n] OKR Tracker]] § O[#]

> ⚠️ **证据边界**：[describe evidence quality — PoC vs vendor showcase vs cross-source verified]

---

## 结论

[Single paragraph 概要 — concrete capability claims, recommendation, key conditional. Function-named "结论", not "一句话".]

---

## [Domain-relevant sections — adapt structure to actual content]

[For vendor showcase without PoC: vendor claims + evidence + verification status, NOT fake ratings.
For PoC results: measured outcomes vs baseline.
For OKR draft: coherence + KR ambition calibration + alignment.
Custom structure beats template-fitting.]

---

## 推进项 / 暂搁项

| 推进 | 暂搁（HOLD） |
|---|---|

---

## 前置风险

[Decomposed by dimension. Each risk: what triggers it, mitigation strategy.]

---

## 时间表

[Calendar with Decision Gates per action.]

---

## 价值与成本评估

> 若议题涉及结构性变革 / 多议题耦合 / 至少一项战略期权 → 必须套用 **价值评估框架**（见 § 价值评估框架）：
>
> - 价值机制拆解（6 维：议题 / HOW / 受益方 / 时间 / 性质 / 量级）
> - 防御性 vs 进攻性 vs 战略期权 三分类
> - 复利叠加效应（议题间耦合）
> - 量化测算（仅对可量化议题，含敏感性 + 基准 / 最差 / 最佳情形）
> - 决策门 + 价值触发条件
> - 整合视图（议题 × 投入 × 价值 × 时间窗 × 决策时点）+ 优先级排序
>
> 若是简单单一供应商签约 / 工时估算 → 维持原 "成本估算" 单层格式即可，本节简化为 quantified 投入 + ≈X 假设。

---

## 本周行动项

[2-3 numbered: actor — action — deadline — measurement.]
```

### Adapting the spine to artifact type

| Artifact type | Heaviest sections | Lightest |
|---|---|---|
| Tool / vendor evaluation (rich data) | Capability, Operational, Risk | Next steps |
| Meeting note → board memo | 概要 (结论), Risk, Next steps | Operational |
| OKR draft | 概要, Coherence, Next experiments | Operational, Risk |
| Workflow / SOP doc | Operational, Embed, Cost | Risk |
| Deal memo / acquisition target | 概要, Risk, Cost | Operational |
| Biweekly report | 概要, Next focus | Capability, Operational |

---

## Phase 0: Loop Guard & Skip Check

Before doing anything:

1. **Loop guard** — If artifact path matches `**/(C) * - 业务评估.md`, **refuse**: *"This is a biz evaluation file. Running /biz on an eval would create a loop."*
2. **Skip flag** — Read the artifact's frontmatter. If `biz-eval: skip` is set, announce skip and exit cleanly.
3. **Path validation** — Refuse **`06 Tasks/`** and **`03 Projects/*/Tasks.md`** (task surfaces, not business artifacts). If artifact is a card / daily note / action stream, surface: *"This is a [pillar] file, not a business artifact. Did you mean a meeting note / report / memo?"*

## Phase 1: Read & Identify

When invoked with `/biz <artifact-path>`:

1. Read the source artifact in full
2. Identify artifact type
3. Auto-pick 1–3 lenses (or honor `--lens` override)
4. Read business context:
   - Root `CLAUDE.md` for active OKRs and project status
   - `GOALS.md` if it exists
   - Project's `CLAUDE.md` if artifact is project-scoped
   - Current quarter's `(C) Q[n] OKR Tracker.md`

## Phase 2: Decompose & Quantify

For each section, build content per the source's actual evidence — never to fill template structure:

1. **概要 (结论)** — extract or infer recommendation. If insufficient evidence, mark explicitly.
2. **Capability boundaries** — MECE decomposition. For vendor showcases without PoC: "vendor claim + evidence + verification status" — NOT fake ratings.
3. **Operational** — extract templates, calibration rules, translation tables. Include only if THIS evaluation needs them.
4. **Scenarios + Not-suitable** — both required when applicable.
5. **Risk** — tier or dimension decomposition. Tier comparison table when service/tier comparison applies.
6. **Cost** — numeric. "≈X based on assumption Y" if rough; never "TBD".
7. **Next steps** — actor-action-deadline-measurement format.

## Phase 3: Cross-Reference OKRs & Existing Workstreams

```bash
ls "10 Action/11 12-Week/" 2>/dev/null
ls "10 Action/12 Active/" 2>/dev/null
```

For each next-step recommendation:
- Does it map to an existing Action file (`chain-anchor:`)? Reference it.
- Does it advance a current OKR KR? Cite `[[(C) Q[n] OKR Tracker]] § O# KR#`.
- Is it a NEW workstream? Flag for user — propose Action file via `[[09 Rules/action.md]]` Auto-Creation Policy.

## Phase 4: Write the Evaluation

**Path resolution（2026-05-15 起 per-project canonical）：**
- Source in **`03 Projects/{{PROJECT_A}}/04 会议纪要/**` → eval at `**03 Projects/{{PROJECT_A}}/Pitches/(C) [name] · 业务评估 YYYY-MM-DD.md`**
- Source in **`03 Projects/{{ORG_B}}/04 会议纪要/**` → eval at `**03 Projects/{{ORG_B}}/09 Reports/(C) [name] · 业务评估 YYYY-MM-DD.md`**
- Source in **`04 Notes/Meetings/**` → eval at `**04 Notes/Meetings/(C) [name] - 业务评估.md`**
- Source in **`00 Raw/Clippings/**` → eval at `**04 Notes/biz-evaluations/YYYY-MM-DD-[name] - 业务评估.md`**
- Source in **`03 Projects/<project>/...**`（非 04 会议纪要）→ eval at `**03 Projects/<project>/(C) [name] - 业务评估.md`**

**废弃路径**：旧 **`00 Raw/会议纪要/**` 与 `**03 Projects/<project>/00 Raw/会议纪要/`** 自 2026-05-15 起不再作为 source 写入目标 —— 历史文件已迁入对应项目的 `04 会议纪要/`。

### Register self-check (mandatory before save)

After drafting the body, scan for register violations per Voice § Register B above:
1. First-person pronouns beyond byline → rewrite to third-person
2. Colloquialisms (这块儿、这儿、这事儿) → formal equivalents
3. Self-endorsement phrases (双重确认、我现场观察、我自己已知的) → objective statement with sourcing in evidence
4. Conversational connectors (所以、那么) → formal connectors (故、因此、由此)
5. Section headers in verb / personal phrasing (我接下来要做的) → noun-phrase (本周行动项)
6. **Abstract templating placeholders that should be concrete entity names** ("vendor" when the vendor is named 火山; "partner" when the partner is named 小鹏)
7. **Form-named section headers** ("一句话"→"结论"; "几条信号"→ noun-phrase; "我接下来要做的"→"本周行动项")
8. **Signals that are merely status descriptions** ("X 是硬约束"、"Y 真实存在") — these don't drive decisions; either rewrite to surface a decision implication, or delete

This pass does NOT change structural content — only register.

## Phase 5: Confirm + Optional Hand-offs

Close with:

> **业务评估完成:** [[(C) name - 业务评估.md]]
> **Lens:** [declared lenses]
> **OKR anchor:** [[(C) Q[n] OKR Tracker]] § O[#]
> **核心结论:** [first 概要 point as one-liner]
>
> **Next-step recommendations:** [n] items.
>
> Want me to:
> (a) Surface these to **`06 Tasks/Inbox.md`** via `/task-capture`? (≤3 per write)
> (b) Spawn an Action file for [workstream-worthy item]?
> (c) Update [[(C) Q[n] OKR Tracker]] § [KR#] 下一步 with [recommendation]?

Wait for user direction. Never auto-execute hand-offs.

---

## ⛔ NDA Downstream Handling

当上游 source 文件（meeting note）的 frontmatter 含 `nda-sections: [§X.Y, §Z.W]` 时，本 eval **必须**：

1. **不引用 NDA 段的可识别细节** — 路线图具体版本号 / 内部代号 / 未官宣方向，统一抽象为"基于供应商路线图 hint，**结论摘要不含可识别细节**"
2. **在 § 前置风险 中单列一条** — "NDA 边界：本评估含基于 [meeting note §X.Y] 的 NDA 路线图 hint。**转发上级前需 redact** 或与 [对方对接人] 确认释放边界"
3. **在 § 本周行动项 中包含一条 NDA 边界确认** — "跟 [对方对接人] 确认 NDA 内容对内决策层 cc 边界，YYYY-MM-DD 前"
4. **生成 v1 对外稿（如 Action Items 涉及）需走单独 redact 流程** — 不让 eval 主文件直接成为对外稿

---

## ⛔ 中英混用偏好

继承 [[.claude/skills/meeting-note-deep/SKILL.md]] § "中英混用偏好" 同一约定：

**默认中文化的（特别是表格列名 + 框架标签）**：

| 应避免 | 应使用 |
|---|---|
| Value Mechanism / Beneficiary / Magnitude | 价值机制 / 受益方 / 量级 |
| Defensive / Offensive / Option Value | 防御性 / 进攻性 / 战略期权 |
| Compounding Effects / Stack | 复利叠加 / 同进同退耦合 |
| Base / Worst / Best case | 基准 / 最差 / 最佳情形 |
| Sensitivity 分析 / GO/NO-GO 闸 | 敏感性分析 / 推进-否决 闸 / 决策门 |
| Mitigation / Next Action / Vendor | 缓解措施 / 下一步行动 / 供应商 |

**保留英文的（专有 / 行业通用 / 缩写）**：产品 / 引擎名（UE / MetaHuman / MCP / Lumen 等）· 工种 / 流程（PoC / cinematic / agent / diffusion）· 缩写（概要 / MECE / SCORARO / ROI / NPV / OKR）· 公司名（Epic / Sony / AGBO 等）。

判断规则：**"中文读者 1 秒内能理解的英文 → 保留，否则翻译"**。

---

## Hard Rules

- **Name entities concretely.** If the vendor is 火山引擎, write "火山", not "vendor". Abstract placeholders signal template-fitting, not synthesis.
- **Section names describe function, not form.** "结论" not "一句话"; "前置风险" not "几条真实风险"; "本周行动项" not "我接下来要做的". Headers earn space by naming what the section accomplishes.
- **Every "signal" must carry decision weight.** Status descriptions ("X 是真实硬约束") are not signals — they're default assumptions. Cut signals that boil down to "this thing exists" or "this thing is real" — keep only signals that yield "do X / don't do Y / verify Z."
- **Never invent ratings.** Source-cited numbers only. Hallucinated numbers in leadership artifacts are corrosive.
- **Never invent percentage estimates ("30-60% 节省" etc.) without source.**
- **Never include process plumbing in the document.** Task batch ceilings, skill IDs, "auto-chain rules" — these belong in the confirm message, not the deliverable.
- **Never include team-roster dispatch tables unless explicitly asked.**
- **Cut every row that doesn't have a business hook.** "战略叙事合理；产品演进路线清晰" is filler — delete it.
- **Cross-verify AI-generated transcripts.** Cross-check model names, product names, and key numbers against ≥2 other sources before propagating.
- **Never modify the source artifact.** Read-only on input. The eval is always a new file.
- **Never write `TBD` for cost.** "≈X" is acceptable; admit uncertainty in the assumption clause.
- **Never run un-grounded.** Reading current OKR Tracker before writing the eval is mandatory.
- **Never auto-execute next-step hand-offs.** Surface options, wait for user direction.
- **`(C)` prefix on every evaluation file.** AI provenance is non-negotiable.
- **Verdicts are recommendations, not measurements.** Label them as such. Conditional on cited evidence.

---

## Failure Modes

| Symptom | Fix |
|---|---|
| Source artifact too thin to evaluate | Tell user explicitly: insufficient detail; offer light verdict OR enrichment-first re-write. |
| Eval reading like template inventory | Many tables, filler ("合理", "正确", "标准") in cells, no business hook. Stop. Throw out template. Rewrite as narrative around what actually matters. |
| Multi-stakeholder verdict tables creeping into 概要 | Delete. Use team-roster info for internal reasoning, not document. |
| Process plumbing in deliverable | Move to confirm message. Document is for user; confirm for next agent action. |
| Architecture deep-dive without business hook | Cut every row that doesn't drive a decision. Synthesize, don't catalog. |
| Lens auto-selection picks wrong perspective | Surface in confirm: *"Picked X + Y based on [keywords]. Want a different lens?"* |
| OKR Tracker missing | Write eval but flag absence in 概要. |
| Source in foreign language | Match the source's language for body. |
| Multi-artifact comparison requested | Run separate `/biz` per artifact; THEN comparison meta-eval. Don't MECE three artifacts in one pass. |
| Template residue (校准原则, 转译表, 三阶段嵌入) without need | Default = don't include. Only add if THIS specific eval calls for them. |

---

## Integration with Other Skills

| Trigger | Hand-off |
|---|---|
| Eval surfaces dated commitments | `/task-capture` (≤3 new tasks per write per [[09 Rules/tasks.md]]) |
| Eval reveals new workstream | **Propose** Action file per [[09 Rules/action.md]]; wait for go-ahead |
| Eval finds OKR-altering insight | Surface for next `/okr` Mode B check-in |
| Eval changes project status | Suggest `/weekly-update` to refresh project CLAUDE.md |
| Eval produces re-usable template | Suggest `/preserve` to land principle in CLAUDE.md or as Card |
| Eval is for high-stakes meeting | Source likely from `/meeting-note-deep`; eval extends with business lens |
| Source is a clipping/article | Eval may produce 1-2 Cards as side effect — propose `/source-ingest` |

---

## Cadence Awareness

The skill runs in three modes:

**Manual (`/biz <path>`):** User-invoked, single artifact. Always available.

**Auto-chained** (per CLAUDE.md § Skill Auto-Chain Rules): Fires automatically when `/meeting-note-deep`, `/biweekly-report`, or `/okr` Mode A confirms a business artifact, OR when a business-typed artifact is saved to a watched path. Loop guard + `biz-eval: skip` flag prevent runaway.

**Comparison meta-eval (manual, future):** When 3+ already-evaluated artifacts need cross-comparison. Run `/biz` on each separately first, then a comparison pass over the eval outputs.
