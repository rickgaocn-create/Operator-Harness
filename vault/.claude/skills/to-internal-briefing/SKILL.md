---
category: work
name: to-internal-briefing
description: Turn current conversation context into a one-page internal briefing for an upline or decision-maker. Do not interview; synthesize existing context and vault facts.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
source: https://github.com/mattpocock/skills/blob/main/skills/engineering/to-prd/SKILL.md
adapted-by: claude (2026-05-14 from /to-prd, adapted to vault internal-briefing archetype)
audit-trace: "[[(C) 2026-05-14 morning-briefing]] § Matt skills adapt — focus 2+4"
---
# Skill: To Internal Briefing

Take the **current conversation context** + 相关 vault state and synthesize a 1-page internal briefing for an upline. Output follows [[09 Rules/internal-briefing.md]] template — strict structure, decision-points-driven.

> **DO NOT interview the user** — just synthesize what you already know. If critical info missing, single-line ask, then synthesize.

> **Source canon:** Matt Pocock's `/to-prd`. **Vault adaptation:** output archetype is "internal briefing for upline sign-off" (decision points + 阵容 + 风险), not engineering PRD. Template lives in [[09 Rules/internal-briefing.md]].

## When to Use

- User says "/to-internal-briefing" / "起一份给{对象}的汇报" / "把刚才聊的整理成汇报材料"
- Conversation has reached a decision-pending state requiring upline sign-off
- BD trip / deal / partnership escalates beyond user's decision权限
- Risk event surfaces that needs upline FYI

**Don't use for:**
- 对外 deck / pitch — that's `/biz` or `/design` for slides
- Daily / weekly update — that's `/daily-note --close` / `/weekly-update`
- Meeting note — that's `/meeting-note` / `/meeting-note-deep`
- Card / wiki update — that's `/source-ingest`

## How It Works

### Phase 1 — Synthesize From Context (no interview)

1. **Identify the workstream + chain-anchor** from conversation. If unclear, **single-line ask**: "这份汇报关联哪个 workstream / chain-anchor？"
2. **Identify the upline target** ({{PERSON}} / 何宗寰 / 路奇 / 团长等). Read [[01 Wiki/{{PROJECT_A}}/公司信息/团队/{name}.md]] for § 三 协同路径 (when need sign-off) + § 四 待补 (沟通偏好).
3. **Identify what changed** — what specifically triggers the escalation. State this in 1 sentence (will go in 概要 "触发").
4. **Extract decision points** from conversation. Each Q with multiple plausible answers = a `Q{n}`. Aim for **3-4 Qs** (>5 = split into two briefings).
5. **For each Q, draft 2-4 方案 ABCD** with 利/弊 + recommend one. (This is Matt's PRD "implementation decisions" adapted to BD multi-option).

### Phase 2 — Read [[09 Rules/internal-briefing.md]] Template

Strict adherence:
- frontmatter contract (type / audience / purpose / chain-anchor / sensitivity / decision-points-count)
- 概要 (升级触发 + 表格 + 阵容建议)
- 一、为什么需要{对象}拍板（援引 wiki § 三 协同路径）
- 二、{议题}速览
- 三、关键决策点 Q1-QN（每个含 ABCD 方案 + {{USER_NAME}} 建议）
- 四、风险与备份
- 五、{{USER_NAME}} 自承诺（具体动作 + 时点）
- 六、附件 / 参考
- 七、{对象}汇报路径建议（援引 wiki § 四 沟通偏好）

### Phase 3 — Write Output File

Path: **`03 Projects/{project}/03 行程计划/(C) {chain-anchor} 内部汇报-{对象}.md**` (trip 类) 或 `**03 Projects/{project}/04 流程文档/(C) {chain-anchor} 内部汇报-{对象}.md`** (其他)

如果路径不明，**single-line ask** target dir。

### Phase 4 — Cross-Reference Patches

- 在被汇报 workstream 的主文档（trip bundle / Action / etc.）加一行 link 指向新建汇报
- 不动其他文件（特别 wiki — 汇报是 transient artifact，不要污染长寿命 wiki）

### Phase 5 — Confirm + Next Steps Prompt

> "汇报已落档 [[{path}]]. 决策点 Q1-Q{N}. 推荐方案 in-baked. 建议路径：(1) 企微发图 (2) 15 min 短会面谈。要不要现在直接复用？"

## Hard Rules

1. **NEVER interview the user beyond a single-line ask for path / target / chain-anchor.** Synthesize from context (Matt's core rule).
2. **NEVER write Q without ABCD 方案 + {{USER_NAME}} 建议.** 上级讨厌"全开放问题"，建议 baked-in，他可以 push back. （per [[09 Rules/internal-briefing.md]] hard rules）
3. **NEVER copy-paste full conversation into the doc.** Synthesize. 1 page max body. 长 detail → "详 [[trip bundle § N]]"。
4. **NEVER fabricate {{USER_NAME}} 自承诺.** § 五 must reflect actual conversation commitments, not aspirational ones.
5. **NEVER edit other wikis / 长寿命 docs** in this skill. Internal briefing is transient artifact; cross-references via wikilinks only.
6. **ALWAYS援引 upline 的 wiki § 三 协同路径** in § 一 (why need this person's sign-off). 如 wiki 不存在，停 → 建议先 `/channel-person-wiki-new` 或 manual 建 team wiki。
7. **ALWAYS align with [[09 Rules/internal-briefing.md]]** — if rule file and skill disagree, rule file wins.

## Failure Modes

| Symptom | Fix |
|---|---|
| Conversation context 不够 synthesize | Single-line ask "这次升级触发是什么？" — 然后 synthesize；不滚雪球面 interview |
| Upline wiki 不存在 | 停 → "[[{upline}]] wiki 不存在，先建一份基本档案？需要 § 三协同路径 + § 四沟通偏好 才能定汇报路径" |
| 决策点 > 5 个 | 拆 2 份汇报：一份阵容/预算/接待，一份风险/合规。两份都按本 skill |
| 用户说"我有 3 个 method 想 brainstorm" | 不是本 skill 场景 — 那是 `/grill-me` 或 `/biz`；本 skill 是 synthesis，不是 generation |
| chain-anchor 冲突 | 沿用 conversation 已 establishing 的 anchor；如新议题，propose 新 anchor 待 user confirm |

---

*Vault-adapted from Matt Pocock's [/to-prd](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-prd/SKILL.md). Output archetype shifted from "engineering PRD" to "internal briefing per [[09 Rules/internal-briefing.md]]". User-stories format dropped (irrelevant to BD); Q1-QN decision points format kept (matches今天手写的{{PERSON}}汇报 pattern).*
