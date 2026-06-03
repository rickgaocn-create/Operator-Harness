---
layer: platform
instance-config: "[[09 Rules/_instance/trip-application]]"
paths:
  - "03 Projects/*/03 行程计划/(C) 差旅申请-*.md"
applies-to: 已订票出差的申请表 + 邮件 + 携程订单 + 状态追踪 文档
companion-rules:
  - "[[09 Rules/trip-planning-bundle.md]]"  # 行前计划 archetype
  - "[[09 Rules/internal-briefing.md]]"     # 内部汇报 archetype
created: 2026-05-13
created-by: claude (codify F3 from format audit-2026-05-13-EOD)
audit-trace: "[[(C) 格式 audit-2026-05-13-EOD.md]] § F3"
---

# Trip Application Rules · 差旅申请模板

> trip 已订/已发生 — 申请表 + 邮件备案 + 携程订单 + reschedule 调度的**报销文件**。
>
> **Mechanism = platform** (archetype below). **Concrete defaults = instance** — the xlsx baseline, 行政对接人 + Cc roster, 申请人 identity, 合同主体 live in [[09 Rules/_instance/trip-application]]. Names below ({{PERSON}} / {{USER_NAME}} / {{ORG_D}}) are illustrative; the authoritative defaults are the instance config.

## 适用范围 vs 不适用

**✅ 适用**：trip 已订完 / 已发生 / 进入报销 + 备案预审流程
- 含申请表字段全集、邮件正文、携程订单、行程已确定、reschedule 流出

**❌ 不适用**：
- 行前规划期（未订票，议程未敲定）→ [[09 Rules/trip-planning-bundle.md]]
- 向上请示出差决策 → [[09 Rules/internal-briefing.md]]

## Trigger 词（用户提到这些词 → 本 archetype 立即生效）

用户在 work trip 上下文里提到任何以下措辞 → **默认 = 本 archetype 的 § 0 申请表 xlsx + § 1 标准邮件**：

- 「差旅邮件和 excel」/「差旅邮件 + 申请表」/「申请表和邮件」
- 「(给行政) 提单 / 报备」/「发邮件给{{PERSON}}」
- 「按上次 5/14 那种方式」/「同上次差旅流程」
- 「重新做申请表 / 重新做差旅邮件」

**默认产出物（不需要再问）** — baseline 模板 / 收件人 / Cc / 位置 全在 [[09 Rules/_instance/trip-application]]：
1. **xlsx 申请表**: 按 instance baseline 模板，命名 `差旅预定协助申请表 YYYY-MM-DD_城市_{申请人}_vN.xlsx`
   - **2 sheets**: Sheet1 申请表（字段全集 + 机酒携程截图嵌入）· Sheet2 差旅费支付明细表（≥10 行细目 + SUM 合计 + 报销须知）
   - **位置 + 命名 + `(C)` 规则**: 见 instance config（行政文件 · 无 `(C)` 前缀）
2. **邮件 .md draft**: `(C) 差旅申请邮件 YYYY-MM-DD_城市_{申请人}_vN.md`（格式严格按 instance config 指定的邮件模板）
   - **必含**: 主题三段 + 收件人（instance 行政对接人）+ Cc roster + 五字段 + 目标 1/2/3 + 固定结尾 + 申请表附件 + 已自订情况下追加备案预审说明

**禁止的产出物**（这些不是差旅申请流程）：
- ❌ 「presentation 行程表 xlsx」/「呈上级 review 的 1 页打印版」/「PPT-style 总览」— 那是 internal-briefing 域
- ❌ 自创邮件格式 / 偏离 5 字段结构 / 略过目标 1/2/3

## 命名

```
(C) 差旅申请-YYYY-MM-DD_城市.md
```

> ⚠️ **历史命名 grandfather**：5/13 之前的 `(C) 差旅申请包-...` 文件保留命名。**新文件**用 `(C) 差旅申请-...`（不含"包"字）。

## Frontmatter Contract

```yaml
---
type: trip-application
created-by: claude
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
trip-date: YYYY-MM-DD / YYYY-MM-DD
trip-city: 城市名
trip-purpose: 出差目的（行政可读）
chain-anchor: {anchor}
booking-status: 已支付 / 已订未支付 / 已申请
total-cost: ¥X,XXX                   # 报销总额
sensitivity: contains-pii-links
---
```

## Canonical Section Structure

```markdown
# {城市}差旅申请 · YYYY-MM-DD/DD

> 单页入口：行政提单所需 xlsx + 邮件正文 + 携程订单 + 状态 一处可拿。
> Workstream：`{chain-anchor}` · Trip-planning bundle (如有): [[(C) 差旅计划-...]]

---

## 0 · 出差申请表（vN 终版 · {状态}）

> 📌 现状：{已自费预订 / 走代订流程 / ...}

![[差旅预定协助申请表 ...xlsx]]

### vN 关键字段（来源审计）

| 字段 | 值 | 来源 |
|---|---|---|
| 申请人 | {{USER_NAME}}（{{USER_NAME}}） | [[About Me/identity-documents]] |
| 部门 | {{ORG_D}} | [[About Me/employment.md]] |
| 项目组 | {{PROJECT_A}} | ... |
| 差旅时间 | ... | ... |
| 身份证号 | ... | ... |
| 职级 | ... | ... |
| **合同主体** | **{法人主体}** | MEMORY § Employment Entity |
| 去程机票 | {航班} | xlsx Sheet2 |
| 返程机票 | {航班} | ... |
| 住宿 | {酒店} | ... |
| **费用合计** | **¥X,XXX** | ... |

---

## 1 · 邮件草稿（vN · 标准差旅申请格式）

> **模板源：** [[(C) 差旅申请邮件模板]]
> **本邮件偏离点：** {如有 — 例如已自订情况下附加备案说明}

**主题：** `差旅申请-{名}-{开始日期}-{终止日期}-{地点}`

**收件人 / 抄送：** {{PERSON}}（行政 · {{PERSON}}） / 抄送 直接上级 / 行政人事总监 / 财务 / CEO

**正文：** {标准 5 字段格式 — 出差人 / 同行人 / 出差时间 / 出差地 / 出差事宜}

---

## 2 · 行程表（vN · 实锁版）

按日 + 时段格式，标"已订" / "已发生"：

| 日期 | 时段 | 安排 | 状态 |
|---|---|---|---|
| ... | ... | ... | ✅ |

---

## 3 · 引用 / 关联文件

- [[(C) 差旅申请邮件模板]]
- [[About Me/identity-documents]]
- [[About Me/employment]]
- [[相关 trip 计划文件]]（如有）

---

## 4 · 状态追踪

- [x] xlsx 字段齐全
- [x] 邮件已发
- [ ] 报销 reimbursement 提交

---

## 5 · 携程订单（已支付 ✅ / 已订未支付 ⏳）

每单一段:
- 订单号: ...
- 内容: ...
- 金额: ¥...
- 状态: 已支付 / 待支付

---

## 6 · (可选) 约访 reschedule 调度

如出差议程变了流出 reschedule 微信调度，建本段表格化跟踪:

| # | 对方 | 角色 | 改约时间 | 发出日 | 回复状态 |
|---|---|---|---|---|---|

---

## 7 · Changelog

| 版本 | 日期 | 主要变化 |
|---|---|---|
| v1 | YYYY-MM-DD | 初版 |
| v2 | YYYY-MM-DD | xlsx 字段补齐 |
| v3 | YYYY-MM-DD | 携程下单 + 已支付 |
```

## Hard Rules

- **NEVER** 把"约访稿 / 议程 / 包体策略"等行前规划内容塞进申请表 archetype — 那归 trip-planning-bundle
- **NEVER** 改 `合同主体` 字段without consulting MEMORY § Employment Entity（合同主体 = 报销公司主体，可能 ≠ 项目主体）
- **NEVER** 在 body 散布 vN 版本号 — 集中 § 7 Changelog

## Failure Modes

| Symptom | Fix |
|---|---|
| 邮件字段不全（缺出差目标 1/2/3） | 补到 5 字段全口径 — 同 [[(C) 差旅申请邮件模板]] |
| xlsx 主体填错（项目主体 ≠ 报销主体） | 改 frontmatter `合同主体` 并 patch xlsx |
| 携程订单 link 失效（订单中心刷新过） | 截图嵌入 + 订单号文本 留底 |

---

*此规则源于 [[(C) 格式 audit-2026-05-13-EOD.md]] § F3 — trip 文档目录混了 3 种 archetype*
