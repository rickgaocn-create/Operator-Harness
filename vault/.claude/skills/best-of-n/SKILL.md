---
category: work
name: best-of-n
description: Generate multiple full-pipeline candidates for major forwardable outputs, then grade and merge. Use before proposals, strategy memos, pitches, BD plans, or upline reports.
model: claude-sonnet-4-6
allowed-tools: Task, Read, Edit, Glob, Grep
companion-rules:
  - "[[09 Rules/auto-chain-style.md]]"
created: 2026-05-27
created-by: claude (codify eval finding, corrected by {{USER_NAME}} human judgment)
audit-trace: "判断源 — judgment-loop/evals/RESULTS.md 多轮对照 + 【人工 ground truth 修正 2026-05-27】。LLM 判官(盲判/priors/full-OS)曾误判 harness pipeline ≈ priors+best-of-N;{{USER_NAME}}亲评推翻:full pipeline 7/10,剥到 priors+best-of-N 3/10。两个修正:(1) best-of-N 是叠在【完整 pipeline】上的可靠性乘数,不剥框架;(2) LLM 判官在质量排序上不可信,故择优交给人,LLM 只做"滤废稿+抽强 move"两件可靠的地基活。"
---

# Skill: Best-of-N 重大输出可靠性门

> **概要：** 重大输出别交第一稿,也别把 pipeline 剥薄。用 **完整 harness pipeline** 并行跑 N 版 → 滤废 → **你**择优/合并。pipeline(priors + judgment 框架 + critic + grounding)是质量基准(人工评 7/10);但它有 **run-to-run 方差** —— best-of-N 抬高下限(多跑几次捞最好、滤掉偶发弱版)。**择优是人做的,不是 LLM 做的**(见下)。

> **两条经测的硬约束:**
> 1. **真杠杆是 priors** —— 没 priors 的 best-of-N 只产出"读着像样但与现实冲突"的稿。必须先上 priors。
> 2. **LLM 判官在质量排序上不可信** —— 同实验里把 3/10 评成 ≈ 7/10。所以 **重大件的终选交给你,不交给 LLM**;LLM 只做它可靠的:滤废稿(二元规则核查)+ 抽强 move。

---

## When to Use

**自动触发(AUTO-CHAIN):** 任何 **重大、对外 / 对上、forwardable** 的产物在定稿前 —— 对外提案 / 合作方案 / pitch / deal 框架 / 战略 memo / 决策建议 / BD 打法 / 对上汇报 / 投资人材料。判据:"发出去改不回来"且影响大的单件。

**手动触发:** `/best-of-n <task 或 path>`、「多稿择优」、「出几版选最好」、「并行起草」。

**跳过(skip):** 日常 / 低风险 / 结构化产物(任务、纪要速记、表格、daily note、群内 update、代码);frontmatter 已有 `best-of-n-passed:` 或 `best-of-n: skip`;成本不值的小件(N× pipeline token 只为重大单件花)。

---

## 工作流

### Phase 1 — 先上 priors(不可省;真杠杆)
把与本输出相关的私有事实拉进上下文:相关实体 wiki(对手/渠道/伙伴)、真实决策链、先例(置换/联运/合同惯例)、**待核实项**。检索 **准确性 > 广度** —— 拉错/拉旧的 prior 会让 pipeline 自信地产出与现实冲突的稿。priors 是地基,best-of-N 是地基之上的择优。

### Phase 2 — 用【完整 pipeline】并行跑 N 份独立候选(默认 N=3)
- 用 `Task` 起 **N 个互不可见的** drafter(隔离是关键 —— 同上下文连写 N 稿会互相锚定,失去意义)。
- **每个 drafter 跑完整 harness pipeline**:同 priors + judgment 框架(发散 lens)+ 各自综合 + grounding。不要把任何一份降级成 plain priors 稿(那正是被人工评成 3/10 的版本)。

### Phase 3 — 择优:人是判官,LLM 只做地基活
LLM 判官经测在质量排序上不可信(把 3/10 评成 ≈ 7/10)。所以 `biz-doc-critic` 在这步 **只做两件它可靠的事**,不做终选:
1. **滤废稿(二元判定)** —— 逐份查"是否违反 grounding / 待核实 / 与某条 prior 冲突"。是/否的规则核查 LLM 远比细粒度排序可靠。废稿(编数字、现金合同思维、违 priors)直接淘汰。
2. **抽各稿独有的强 move** —— 把 N 份里彼此不同的杀手 move 列成一张短清单(各版常各有一两个)。

**然后由你(人)在"过滤后的候选 + move 清单"上选 / 合并** —— 重大件上你是判官。合并往往优于单选(拼各稿最强 move)。
- grounding gate 是硬线:留下的每个动作点名 具体方/数字/日期/第一步;待核实不写对上/对外。

### Phase 4 — winner 进既有 finish chain
你选定/合并出的 winner 走既有链:`biz` / `localize-cn` / `pragmatic` / `humanize`。完成后 stamp `best-of-n-passed: YYYY-MM-DD`。

---

## 与既有 gate 的关系

| 阶段 | 机制 | 作用 |
|---|---|---|
| **前(本门)** | best-of-n:N 份完整 pipeline 候选 → 滤废+抽 move →【人】择优 | 抬高下限 + 人定终稿 |
| 后 | biz-doc-critic | 对 winner 评分/改(它的常规用法) |
| 后 | localize-cn / pragmatic / humanize | 风格/语言打磨 winner |

best-of-N **在生成端**(完整 pipeline 跑 N 版 → 滤废 → 人择优),既有 transform **在打磨端**。注意:biz-doc-critic 在本门 Phase 3 **只滤废+抽 move,不做终选** —— 终选是人。

---

## 边界(诚实)

- 这门买的是 **可靠性** —— 捞 pipeline 最好的一次、滤掉它偶发的弱稿。pipeline 本身(含框架)才是质量基准,best-of-N 是乘数。**不要据此剥掉判断框架**(那是 LLM 判官的错误结论,已被人工评分 7/10 vs 3/10 推翻)。
- **终选必须是人。** LLM 判官(含 biz-doc-critic)在重大件上只能滤废+抽 move,不能定好坏 —— 实验证明它把烂稿评得跟好稿一样高。这门把你从"逐稿写"解放成"在筛过的候选上拍板",不是把你撤出。
- 实验是 LLM 判官(非真人 / 非真实成交)下的结论 —— best-of-N 抬下限的稳健性可信;细微排序不可信,所以才把终选交给你。
