---
category: work
name: localize-cn
description: Clean Chinese work artifacts for CN-audience delivery. Remove English residue while preserving approved proper nouns, acronyms, paths, URLs, and code.
model: claude-sonnet-4-6
allowed-tools: Read, Edit, Glob, Grep
companion-rules:
  - "[[09 Rules/auto-chain-style.md]]"
  - "[[09 Rules/file-types.md]]"
companion-memory:
  - "[[feedback_cn-monolingual-and-name]]"
created: 2026-05-19
last-restructure: 2026-05-21
created-by: claude
audit-trace: "2026-05-19 {{USER_NAME}} request — TapTap 会议纪要中英混杂多. 2026-05-21 split: 静态 wordlist 移到 [[09 Rules/auto-chain-style.md]] § Localize-CN，SKILL.md 留 dispatch + workflow（Phase 3.2.c restructure）"
---

# Skill: 中文本地化校验（localize-cn）

确保**面向中文读者**的工作文档保持中文 monolingual 风格，仅保留必要白名单条目（专有名词、品牌、版本号、技术缩写、文件路径）。

> **质量基线**：{{PERSON_1}} / {{PERSON}} / 路奇 / 任何 {{PROJECT_A}} / {{ORG_C}}发行 / 诗悦内部读者读到时，**无明显英文残留**，无 chat-residue 风格。读起来像内部 BD 同事写的，不像 AI 生成。

> **规则数据：** 7 类英文残留 + 白名单完整表格在 [[09 Rules/auto-chain-style.md]] § Localize-CN。本 SKILL.md 只放 dispatch + workflow。

---

## When to Use

**自动触发（默认开启）：**

每当 Claude 完成任一面向**中文读者**的 work artifact 时，自动 chain `/localize-cn` 作为收尾步骤。

适用：
- 会议纪要 → **`03 Projects/*/04 会议纪要/**/*.md`**
- 双周报 / 周报 → **`03 Projects/*/09 Reports/**/*.md`**
- OKR Tracker → **`03 Projects/*/(C) Q*OKR Tracker*.md`**
- 内部汇报 / 决议文档 → 任何 `type: meeting | biweekly-report | okr-tracker | deal-memo | partnership-proposal` 且目标读者非英文受众
- {{PROJECT_A}}、{{ORG_B}} 内部 audience 任意文档（在 frontmatter declare 或 path 表明）
- 任何**显式标注**「报送 / 抄送 / 内部汇报对象 = 中文同事」的 artifact

**手动触发：**
- `/localize-cn <path>`
- 「中文化这个」/「localize 一下」/「去 chat-residue」/「去英文残留」

**不适用（skip auto-chain）：**
- CV / 投递材料 EN 版（**`10 Action/12 Active/CV-*-EN.{md,html}`**）
- {{ORG_D}} / 国际投资人 audience 任意文档（Lane B 隔离）
- JP board / 日本 stakeholder 材料
- 任何 frontmatter `localize-cn: skip` 的文件 — escape hatch
- 任何 frontmatter `localize-cn-passed: YYYY-MM-DD` 近期的文件 — 防重
- 结构化数据 / 表格 / 代码 / 文件路径 / 命令行
- 内部 vault 主张（Cards / Action 文件 / Skills SKILL.md 本身）
- 任意明确 EN/JP 受众的内容

---

## 工作流

### Phase 1 — 识别 audience + register

读 frontmatter 或顶部段落判断：
- 目标读者全部中文 → 严格 monolingual + 称谓 高培尧
- 目标读者混合 → 仅修主体文字，专业术语保留
- 目标读者全部英文 → 跳过

### Phase 2 — 扫描 + 提议（按 [[09 Rules/auto-chain-style.md]] § Localize-CN 的 7 类）

逐项 grep：
- 🔴 必修：称谓 {{USER_NAME}}（除签名外）/ 章节标题英化 / 动词残留 ≥ 5 处
- 🟡 应修：英文 jargon 影响阅读 / 状态词
- 🟢 软修：偶发用法（一次性英文短语）

每个 hit 对应 09 Rules 文件中的具体表格行。

### Phase 3 — 应用

- 自动触发：必修 🔴 silently 应用 + 列 🟡 / 🟢 摘要
- 手动调用：先 diff 给用户，确认后应用

### Phase 4 — 防重 + 上报

完成后 stamp frontmatter `localize-cn-passed: YYYY-MM-DD`。

输出一行完成：

```
✅ localize-cn 完成 · X 🔴 / Y 🟡 / Z 🟢 修正 · M 项白名单保留
```

---

## Anti-patterns（不要做）

- **不强行翻译白名单条目**（专有名词翻译会失精确）
- **不破坏 frontmatter** 键名（YAML 键须英文，仅修值）
- **不动文件路径 / 命令行 / 代码块**
- **不强加中文标点替换** — `()`、`,` 在专业引用上下文中合理
- **不重复跑** — 见 frontmatter `localize-cn-passed:` 防重

---

## 与其他 skill 的协同

- 与 `/humanize`：humanize 处理 AI 痕迹（任何语言），localize-cn 处理中文残留（仅 CN audience）。**顺序：先 humanize 再 localize-cn。**
- 与 `/biz`：先 biz 输出业务评估，再 localize-cn 校 CN 风格。
- 与 `/meeting-note`：meeting-note 输出后，CN audience 路径上自动 chain localize-cn。
- 与 `/pragmatic`：localize-cn 先（去残留），pragmatic 后（转风格）。

完整 chain 顺序矩阵见 [[09 Rules/auto-chain-style.md]] § Order when multiple chains apply。

---

## 链入

源 rule: [[MEMORY.md]] § Writing Principles · CN Output Monolingual + 高培尧 Name Rule
canonical wordlist: [[09 Rules/auto-chain-style.md]] § Localize-CN
companion rule: [[09 Rules/file-types.md]] · [[09 Rules/cards.md]]
