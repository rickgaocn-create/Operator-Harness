---
layer: platform
paths:
  - "03 Projects/{{PROJECT_A}}/03 行程计划/(C) 差旅计划-*.md"
  - "03 Projects/{{ORG_B}}/**/差旅计划-*.md"
applies-to: 行前差旅计划文件（trip 尚未开始，作为前期规划+约访+议程 bundle）
companion-rules:
  - "[[09 Rules/trip-application.md]]"   # 申请表 archetype（行后或行中报销用）
  - "[[09 Rules/internal-briefing.md]]"  # 内部汇报 archetype（升级请示决策用）
created: 2026-05-13
created-by: claude (codify F3 from format audit-2026-05-13-EOD)
audit-trace: "[[(C) 格式 audit-2026-05-13-EOD.md]] § F3"
---

# Trip Planning Bundle Rules · 行前差旅计划模板

> Trip 尚未发生 — 所有"行程 / 约访稿 / 议程 / 包体节奏 / 状态追踪"的**单页规划入口**。

## 适用范围 vs 不适用

**✅ 适用**：trip 锁定日期前后、未发生时的**规划期**
- 行程草拟 / 约访 / 议程编排 / 出差预订 / 包体节奏 / 协同手册（如多人）

**❌ 不适用**：
- 已订完票、走报销流程 → 用 [[09 Rules/trip-application.md]] 申请表 archetype
- 给上级请示决策的汇报 → 用 [[09 Rules/internal-briefing.md]] 内部汇报 archetype

## 命名

```
(C) 差旅计划-YYYY-MM-DD_城市.md
```

- 关键字 `差旅计划`（明示 archetype）
- `YYYY-MM-DD` = trip 起始日 ISO 格式
- 城市 = 中文（"上海" 不是 "SH"）

**Examples:**
- `(C) 差旅计划-2026-05-18_上海.md` ✅
- `(C) 差旅计划-2026-05-25_厦门.md` ✅
- `(C) 差旅申请包-...` ❌ — "申请包" 是申请表 archetype 命名，不要混

> ⚠️ **历史命名 grandfather**：2026-05-13 之前用 `(C) 差旅申请包-...` 通配命名的所有 trip 文档（包括 5/14 / 5/18 / 5/25 三份）暂时保留命名，不要批量改 — 改名 = 链接断 + AI 历史误读。**只新文件按新规则命名**。

## Frontmatter Contract

```yaml
---
type: trip-planning-bundle
created-by: claude
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
biz-eval: skip                          # 默认 skip（行前不评估）
trip-date: YYYY-MM-DD / YYYY-MM-DD       # 起 / 止
trip-city: 城市名                        # 中文
trip-purpose: 一行 概要                  # ≤80 字
chain-anchor: {anchor}                   # immutable，see [[09 Rules/action.md]]
chain-anchor-note: "{anchor 的 immutable 提醒（如行程后期调整后 anchor 与实际日期不一致）}"  # 可选
travelers:                               # 多人时用 list
  - 高培尧 ({{USER_NAME}}) - 商务 / BD
  - 顾诗尧 (小K) - 市场负责人
sensitivity: contains-pii-links          # 含敏感 PII 时声明
---
```

## Canonical Section Structure

```markdown
# {城市}差旅计划 · YYYY-MM-DD/DD

> 单页入口：行程 + 约访稿 + 议程 + 预订 + 引用 一处可拿。
> Workstream：`{chain-anchor}` · Action 文件 [[T...]] (如有)

---

## 概要

{n} 天 / {m} 晚 {城市}。**{n} 个 hard anchors** (or "anchors 全部锁定"):

| # | 时段 | 会面 | 召集人 | 同席阵容 | 时长 |
|---|---|---|---|---|---|
| 1 | 🔒 ... | ... | [[人]] | ... | ... |

**Soft anchors (待约)**:
- ...

⚠️ **关键洞察 / 节奏约束**：
- ...

---

## 1 · 行程概览

| 日期 | 时段 | 安排 | 对接人 | 状态 |
|---|---|---|---|---|

(行程草拟 → 实锁后回填)

⚠️ **关键节奏（v{N} 更新后）**: → ❌ **不要在 body 散布版本号**（v1 / v2 / v3 等）。版本日志放文末 § Changelog。

---

## 2 · 飞前节点（XX-XX）

> 包体 lock / 资料准备 / 内部 sync up 的倒推任务表。

- [ ] **YYYY-MM-DD EOD** — {milestone}
- ...

---

## 3 · 约访草稿（复制即发）

按对接人为序：

### ① {对方姓名 + 全口径标签} · ✅/⏳/⏸ {状态}

{已发约访稿 / 会前确认稿 / 待发草稿，markdown 代码块格式}

### ② ...

---

## 4 · 议程 · 必问 · 期望产出

按会议时间顺序排列。每场:

### 🅐 {会面名} ({时段} · 锁定状态)

| Section | 议程 | 必问 | 主导 |
|---|---|---|---|
| 0:00-0:15 | ... | ... | ... |

**期望产出**：① ...

---

## 5 · 出差预订（待办）

- [ ] 机票
- [ ] 酒店
- [ ] xlsx 申请表（如批量延后则注明）

---

## 6 · (可选) 协同手册 / 行程网格 / 包体策略

多人 trip → 协同手册（议程分工 + 应急流程 + 接待规格）
有 Sheet Plus 计划 → 行程网格嵌入位
游戏项目 → 包体携带策略

---

## 7 · 引用 / 关联文件

### 三个 / N 个🔒 锁定场的对接人
- 🔒 [[...]] — ...

### 同席候选 / 备选
- ...

### 平台档案
- ...

### 项目 / 流程
- ...

---

## 8 · 状态追踪

### 已完成
- [x] ...

### 飞前节点（YYYY-MM-DD 到 YYYY-MM-DD）
- [ ] **🔴** 紧急
- [ ] **🟡** 重要
- [ ] **🟢** 一般

### 行中
- [ ] DD AM/PM ...

### 行后
- [ ] Cards 落档 + wiki 校准

---

## 9 · Changelog

> 版本变更日志。**body 不留版本号**，所有 vN 标记集中于此。

| 版本 | 日期 | 主要变化 |
|---|---|---|
| v1 | YYYY-MM-DD | 初版 |
| v2 | YYYY-MM-DD | {变化} |
| ... | ... | ... |
```

## Hard Rules

- **NEVER** 在 body 段落里用 "v3 重写" / "v4 更新后" 这类版本标记 — 集中在 § 9 Changelog。section 标题可以加日期（如 `## 4 · 议程 ... (2026-05-13 更新)`）但**不加 v 数字**
- **NEVER** 用 `(C) 差旅申请包-...` 给新文件命名（grandfather 老文件，但新文件用 `(C) 差旅计划-...`）
- **NEVER** 混 archetype（不要在 trip-planning-bundle 里写"申请表字段"或"决策点 Q1-Q4"）— 那些归 trip-application / internal-briefing
- **NEVER** 漏写 `chain-anchor` — Action ↔ Task binding 依赖
- **NEVER** 因为行程日期变了就改 `chain-anchor`（[[09 Rules/action.md]] anchor immutable）

## Soft Rules

- 概要 表里"召集人"列必须 wiki link `[[人 (Org)]]`
- "对接人"列遵循同样规则
- § 9 Changelog 第一行（v1 初版）必填，作为可读的"何时产生"记录
- 飞前节点 § 2 不强制有，但游戏项目（带包体）/ 政企（带函）/ 异业（带物料）建议要

## When Refactoring Existing Trip Bundle

针对 5/13 之前的 `(C) 差旅申请包-2026-05-XX_城市.md` 文件:
1. 不改名（链接保留）
2. 但**可以分批回填新模板的 section 结构** (概要 / § 9 Changelog) — 单点 Edit 不要 rewrite
3. 把 body 里散落的 vN 标记搬到 § 9

## Failure Modes

| Symptom | Fix |
|---|---|
| 行程后期调整后 chain-anchor 与实际日期不一致（如 5/19 → 5/18） | 加 `chain-anchor-note: "anchor 永久保留, 实际见 trip-date"` frontmatter；body 不动 anchor |
| 多次重写 body 散布 v1-v4 标记 | 集中到 § 9 Changelog；body 标题改成"YYYY-MM-DD 更新" |
| 概要 与 § 1 行程概览重复 90% 信息 | 概要 只列状态 + 时段；§ 1 列完整执行细节（航班 / 住宿 / 通勤） |
| 单人 trip vs 多人 trip 一律加 § 6 协同手册 | 单人 trip 跳过 § 6 |

---

*此规则源于 [[(C) 格式 audit-2026-05-13-EOD.md]] § F3 — trip 文档目录混了 3 种 archetype*
