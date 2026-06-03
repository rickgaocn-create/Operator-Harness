---
layer: platform
instance-data: "01 Wiki/{{PROJECT_A}}/{渠道,政企,异业合作}/ (the relation graph)"
paths:
  - "01 Wiki/{{PROJECT_A}}/渠道/*.md"
  - "01 Wiki/{{PROJECT_A}}/政企/*.md"
  - "01 Wiki/{{PROJECT_A}}/异业合作/人物/*.md"
applies-to: 渠道/政企/异业合作 个人对接人 wiki（"{Name} ({Org})" 命名）
companion-rules:
  - "[[09 Rules/file-types.md]]"
  - "[[02 Cards/{{PROJECT_A}}/C260513-bilibili-org-chart-three-verticals-under-EK]]"
created: 2026-05-13
created-by: claude (codify F2 from format audit-2026-05-13-EOD)
audit-trace: "[[(C) 格式 audit-2026-05-13-EOD.md]] § F2"
---

# Channel Person Wiki Rules · 渠道人物档案约定

> 渠道 / 政企 / 异业合作 **个人对接人**的 wiki 模板。机器协议在 frontmatter + 固定 section anchor，body 留给人自由写。
>
> **This file = the schema (platform).** The actual contact instances it governs **are your relation graph** in `01 Wiki/{{PROJECT_A}}/{渠道,政企,异业合作}/` — that *is* the instance layer for this rule (no separate `_instance/` file; the wikis are the data). Example names below (李响 / 钟馨 / 47) are illustrative; a teammate keeps this schema and builds their own relation graph.

## 适用范围

适用于所有"和某个 person 对接的"档案文件：渠道 BD (TapTap 李响 / B 站 钟馨等) / 政企 (王鹤等) / 异业合作个人 (诗琳 / 林总等)。**不适用于**：渠道平台档案 (TapTap.md / Bilibili.md 等) — 那是组织档案，另设。

## 命名

```
{Name} ({Org}).md
```

- **Name** — 真名（如已知）或最常用花名（如花名是工作场主称呼，如 "47"）
- **Org** — 公司 / 渠道 (英文优先 if 国际化平台，中文 if 国内品牌)

**Examples:**
- `钟馨 (Bilibili).md` ✅
- `李响 (TapTap).md` ✅
- `47 (Bilibili).md` ❌ — 47 是花名，应用真名 张思琪 + alias 含 "47"

## Frontmatter Contract

```yaml
---
title: {Name} ({alias}) — {Org} {Role}   # H1 简短形式
aliases:                                   # 必填，所有可能的称呼
  - {花名}
  - {真名}
  - "{Org} {Name}"                         # 含 Org 的搜索关键词
tags:
  - {Project}                              # {{PROJECT_A}} / 3rd / 异业 etc.
  - 渠道                                   # 或 政企 / 异业合作
  - {Org}                                  # 平台 tag
  - {Department}                           # 联运商务 / 营销中心 / 品牌方 etc.
  - 人物档案                               # 固定 tag for 个人 wiki
created: 2026-05-13                        # ISO
created-by: claude                         # claude / user / 团队
updated: 2026-05-13
status: active                             # active / dormant / departed / unknown
priority: P0                               # P0 决策主线 / P1 关键 / P2 执行 / P3 备选
source_reliability: 用户一手 (聚卡片 ...)   # 来源 + 可信度一句话
---
```

## Canonical Section Structure

**所有 section 都是顶层 `## `（"二级"）；下面如有细分用 `### `（"三级"）**。**编号汉字数字 + 顿号**（一、 二、 三、），与 09 Rules 全 vault 一致。

```markdown
# {Name} ({alias}) — {Org} {Role}

> **概要：** 一句话定位人 + 战略层级 + 当前关联议题（不超过 3 行）。

---

## ⚠️ 信息来源说明

- {字段}: 一手 / 推断 / 待补 — 标可信度
- (3-5 行，建立信息可信度边界)

---

## 一、基本信息

| 项 | 内容 | 来源 |
|---|---|---|
| 真名 | … | 🟢 / 🟡 / ❓ |
| 花名 | … | … |
| 公司 | … | … |
| 部门 / 角色 | … | … |
| Mobile / 微信 | … | … |
| Email | … | … |
| 办公地址 | … | … |
| 直属上级 | [[…]] | … |
| 直属下级 | [[…]] | … |
| 平级同事 | [[…]] | … |
| 职级 / 决策权限 | … | … |

> 来源图例：🟢 一手 · 🟡 推断 · ❓ 待补

---

## 二、组织位置

简短描述 ta 在 org chart 中的位置 + escalation 路径。**必须有**（即使是简单几行也写出来，方便 AI 跨文件做组织图谱推断）：

- ta 上级 / 下级 / 平级
- 上级的上级（升级路径）
- 与跨 vertical 同事的关系（如有）

可选：ASCII org chart 片段（如有助于理解，e.g. 联运商务 vertical 的全图）

---

## 三、战略定位

**这一段是 BD/M&A 视角的"为什么这个人重要"**：

- 角色（决策侧 / 执行侧 / 资源调配）
- 决策权限边界（什么 ta 能签 / 什么需 escalate）
- 议题归口（找 ta 聊什么对 / 聊什么错配）
- 与其他对接人的关系（特别是跨 vertical 不能跨议题 commit）

如果有"角色定位 vs 战略定位"两种内容（一个偏 org，一个偏 BD），统一为 `三、战略定位`，**不要**用 `角色定位` 这个 synonym（避免漂移）。

---

## 四、当前关联议题

时序为序：

- {trip / 事件名}（{日期}）— {归口 ta 的议题点}
- {另一议题}（{日期}）— {…}

议题"附带的子点"（如约访话术 / hypothesis 等）→ 作为 subsection 放这里，**不要**新建顶层 section。

例外（许可的额外顶层 section）：
- `三 hypothesis`（如人物身份/关系不明，hypothesis 论证占大段）

---

## 五、待补信息（优先级排序）

```markdown
- [ ] **P0** {最关键的待补} — {影响后续决策的原因}
- [ ] **P1** …
- [ ] **P2** …
```

- 状态用 `[ ]` / `[x]`（用户/Claude 在 confirm 后切换 `[x]` + 在行尾加 `~~原文~~ → 新结论` 说明）
- 优先级 P0-P3 一致使用

---

## 关联文档

**必须 subsection 化**：

```markdown
### 直属关系
- [[{上级 wiki}]] — 直属上级
- [[{下级 wiki}]] — 直属下级
- [[{平级 wiki}]] — 平级同事

### 跨 vertical 协同
- [[{平级跨线 wiki}]] — 跨线 align 对象

### 平台 / 项目
- [[{平台 wiki}]] § X 组织架构 — 全图
- [[{相关 trip bundle}]]
- [[{相关 cards}]]

### 工作群 (如有)
- [[{微信群 / 邮件组 wiki}]]
```

---

## (可选) 情报更新日志

只在长档案 + 多次更新时启用：

| 日期 | 更新内容 | 来源 |
|---|---|---|
| YYYY-MM-DD | … | 用户一手 / 群消息 / xxx |
```

## Hard Rules

- **NEVER** 用 `角色定位` 或 `职责` 替代 `战略定位` 作为 § 三 标题 — synonym 漂移是本文件存在的主要起因
- **NEVER** 把"约访话术 / hypothesis 论证"作为顶层 § 四 单独 section — 它们是 § 四 / § 三的 subsection 内容
- **NEVER** 漏写 § 二 组织位置 — 即使只有"上级是 X、下级无"两行也要写，方便跨文件 AI 推断
- **NEVER** 在 frontmatter 缺 `priority` / `status` / `source_reliability` — AI 用这 3 字段做 triage
- **NEVER** 不 subsection 化 § 关联文档 — flat list 在档案多了之后视觉混乱（每个 wiki 都该有"直属/跨vertical/平台项目"三档）

## When Updating Existing Wiki Drifting From Template

- 改 § 标题（如 `角色定位` → `战略定位`）— 用 Edit 单点改，不要重写全文
- 加缺失 § 二 组织位置 — 插入 § 一 后面
- 重组 § 关联文档 → subsection — 重写这一段即可

## Failure Modes

| Symptom | Fix |
|---|---|
| § 二 章节缺失（drift） | 补一段简短的 ASCII 上下级关系 |
| § 三 用了 `角色定位` 标题 | Edit 改成 `战略定位` |
| 顶层多了 `约访建议` / `hypothesis` 等 section | 移到 § 三 / § 四 子级 |
| 同样的人有两份 wiki（如花名/真名各一） | merge 到真名为主文件，花名 wiki 改成 redirect stub |

---

*此规则源于 [[(C) 格式 audit-2026-05-13-EOD.md]] § F2 — 12 份本会话产出渠道 person wiki 的 section 命名漂移*
