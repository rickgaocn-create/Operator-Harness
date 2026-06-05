---
category: work
name: pragmatic
description: Apply project-internal briefing style for known PMO/leadership readers. Use after CN internal artifacts; skip external senior, investor, creative, and technical docs.
model: claude-sonnet-4-6
allowed-tools: Read, Edit, Glob, Grep
companion-rules:
  - "[[09 Rules/auto-chain-style.md]]"
  - "[[09 Rules/file-types.md]]"
companion-memory:
  - "[[register-b-business-document-headers]]"
  - "[[register-c-executive-summary-voice]]"
created: 2026-05-19
last-restructure: 2026-05-21
created-by: claude
audit-trace: "2026-05-19 高培尧 request — 从{{PERSON}} TapTap 编辑评价示例提炼出"对话式记录"子风格。2026-05-21 split: 13 条规则的完整内容移到 [[09 Rules/auto-chain-style.md]] § Pragmatic，SKILL.md 留 dispatch + workflow（Phase 3.2.c restructure）"
---

# Skill: 对话式记录风格（pragmatic / {{PERSON}}风格）

> **Genre Dispatch（2026-05-20 加入）**：本 skill 是跨 genre 共享的「风格层」。具体的会议纪要结构 spec 由 genre-specific memory 控制：
> - product-feedback genre → [[feedback-meeting-spec-product-feedback]]
> - operations-sync genre → [[feedback-meeting-spec-operations-sync]]
> - roadshow-debrief genre（路演 / deal 速报）→ [[feedback-meeting-spec-roadshow-debrief]] + **Deal-debrief 模式**
> - 其他 genre 由 `/meeting-note-spec` 路由
>
> 本 skill 的 13 条规则在 genre spec 内被引用 / 启用 / 跳过，不直接产生 doc 结构。
>
> **Deal-debrief 模式（2026-05-26 加入）**：当内容主体是 BD / deal 推进（评级、商业模型、资源、名额、金额、竞品、组织关系）而非产品反馈时，13 条按"接收反馈"提炼的规则会删掉价值（删 insider 判断、拆碎数字簇、硬套情绪分类）。此时叠加 [[09 Rules/auto-chain-style.md]] § Deal-debrief 模式：覆盖规则 1/2/5/7/8 + 硬信息逐字保留。仅内嵌的产品反馈块用三元。

把报告式总结转成对话式记录 — 让已知项目背景的同事一眼看到 takeaway，不要 editorial 解读层，不要装饰物。

> **质量基线**：{{PERSON}}或同级别项目内 senior 读到时，感觉像同事直接说给他听的简报，不是 AI 帮你润色过的报告。

> **规则数据：** 13 条核心规则 + 风格对照表完整内容在 [[09 Rules/auto-chain-style.md]] § Pragmatic。本 SKILL.md 只放 dispatch + workflow。

---

## When to Use

**自动触发：** 任何面向**项目内已知背景读者**的简报型 work artifact 完成时自动 chain。

适用：
- 项目内会议纪要（PMO / 主创 / 部门 leader 阅读，非外部传阅）
- 项目内简报 / 速记 / 速览
- 群内 update（飞书 / 微信 / 邮件正文）
- 决议记录（项目组内）
- 「速报」「快报」类输出

**手动触发：**
- `/pragmatic <path>`
- 「{{PERSON}}风格」/ 「对话式记录」/ 「pragmatic 一下」/ 「去 editorial 层」/ 「去装饰」

**不适用（skip auto-chain）：**
- 面向外部 senior / 投资人 / 董事会 / 跨部门 stranger 的报告（用 Register B 报告式）
- CV / 投递材料 / pitch deck / 长篇 narrative（用 humanize + 完整段落）
- 技术文档 / 架构 doc / 设计 doc
- OKR Tracker / 业务评估文档（需保留量化 risk matrix）
- 任何 frontmatter `pragmatic: skip` 或 `pragmatic-passed: YYYY-MM-DD`
- 结构化数据 / 表格 / 代码

---

## 工作流

### Phase 1 — 识别 audience

判断目标读者：
- 项目内 senior / 已知背景 → pragmatic 适用
- 外部 senior / 投资人 / 陌生 audience → 不适用，保留报告式

### Phase 2 — 段落级判断 + audience 层判断

**段落级**：不是整篇必须 pragmatic。一份会议纪要可能：
- 「对方反馈」「关键信息」段 → pragmatic 风格
- 「待办 + 截止日 + owner」段 → 保留报告式（操作性需要 owner / due-date 标签）
- 「跨场基线」「校正字段表」段 → vault staging only（见 [[09 Rules/auto-chain-style.md]] § Pragmatic 规则 10）

**audience 层**：判断当前文档是 vault 版还是 shareable 版

```
触发 shareable 层规则（[[09 Rules/auto-chain-style.md]] § Pragmatic 规则 10）的信号:
  · 文档要 push 到飞书 doc 共享
  · 文档要发群
  · 文档要给 PMO / 上级看
  · frontmatter 出现 `report-to:` / `share-to:` 字段
  → 用 shareable 版规则 (剪 staging)

否则保留 vault 全量（含 staging）
```

### Phase 3 — 应用 13 条规则

**先判内容主体**：deal / 路演推进为主 → 叠加 § Deal-debrief 模式（覆盖规则 1/2/5/7/8 + 硬信息保留），按 [[feedback-meeting-spec-roadshow-debrief]] 结构出段；产品反馈为主 → 直接 13 条。

逐条应用 [[09 Rules/auto-chain-style.md]] § Pragmatic 规则 1–13。简要 dispatch：
1. 改分类标签 → 「正向 / 没那么正向」 或 三元「肯定 / 顾虑 / 建议」（游戏反馈）
2. 删 editorial / context 补充句
3. 改用对方原话方式表达
4. 删 emoji / bold / em-dash / 括号注 / wikilink
5. 短句化（≤ 30 字 / 条），中文标点收尾
6. Section header 用职能（「商务侧」/「{{PROJECT_A}}侧」）非姓名 + 职位
7. 用「关键信息」非「关键决议」
8. 删 editorial parentheticals 与角色补充注
9. 概要 排序 = 现状 → 待关注 → todo
10. shareable 版剪 staging artifacts
11. 不开 recap section
12. 游戏反馈用三元（肯定 / 顾虑 / 建议）
13. 游戏反馈按主题切，非游戏反馈按功能切

### Phase 4 — 防重 + shareable 版标题

完成后 stamp frontmatter：

- vault 版：`pragmatic-passed: YYYY-MM-DD`
- shareable 版（推飞书 / 群）：`pragmatic-shareable-passed: YYYY-MM-DD`

**shareable 版标题模板**（推飞书 doc / 群发时用）：

```
格式: {chain context} · {counterparty} · {date}

✗ 「TapTap 全口径会面纪要」     (无 chain, 无 date)
✓ 「5月路演会面纪要 · TapTap · 2026-05-18」 (chain 最前, date 最后)
```

chain context 从 frontmatter `chain-anchor` 翻成人话：
```
沪差0519           → 5月路演
T260427-mixue      → 蜜雪联动
T260508-xpeng-mona → 小鹏MONA联动
```

vault 内 filename 保留原格式（`YYYY-MM-DD-counterparty.md`），shareable 标题独立生成。

---

## 与其他 skill 的协同

- 与 `/localize-cn` 协同：localize-cn 是英文残留校验，pragmatic 是风格转换。**顺序**：先 localize-cn 再 pragmatic。
- 与 `/humanize` 协同：humanize 处理 AI 痕迹（任何语言），pragmatic 处理报告式 → 对话式转换。顺序：先 humanize 再 pragmatic。
- 与 `/biz` 互斥：biz 评估必须 Register B 报告式 + 量化 risk matrix，pragmatic 风格不适合 biz 输出。

完整 chain 顺序矩阵见 [[09 Rules/auto-chain-style.md]] § Order when multiple chains apply。

---

## 经典示例（{{PERSON}} TapTap 编辑评价原文 · 2026-05-19 BD trip）

```
正向的：
1. 觉得产品翻天覆地，不是同一个游戏
2. 对于游戏的框架了解了，认为有潜力  
3. TapTap 发布会有内容应该可以上，但希望有更明确的时间点曝光
4. 商务总监会和编辑老师商量下评级的调整时间点

没那么正向的：
1. 完成度面，都市玩法部分可玩不多，还是希望实际来玩包体，玩的时间更长一些需要
2. 战斗部分觉得手感还是有点飘，前滑后滑很多
3. 角色-boss-月灵画面上的融合度有问题
```

每条都满足 13 规则核心子集 — 直接 takeaway / 保留口语 / 无装饰 / ≤ 30 字 / 中文标点。

---

## 链入

源样本：{{PERSON}} ({{USER_NAME}}) 2026-05-19 TapTap 编辑评价摘录
canonical rules: [[09 Rules/auto-chain-style.md]] § Pragmatic
companion memory: [[register-b-business-document-headers]]（报告式参考）· [[register-c-executive-summary-voice]]（执行摘要口吻）
