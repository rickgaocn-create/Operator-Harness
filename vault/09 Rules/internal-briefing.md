---
layer: platform
instance-config: "[[09 Rules/_instance/internal-briefing]]"
paths:
  - "03 Projects/*/03 行程计划/(C) *内部汇报*.md"
  - "03 Projects/*/04 流程文档/(C) *汇报*.md"
applies-to: 向上级或决策者请示的内部汇报文档（升级路径 + 决策点 + 风险）
companion-rules:
  - "[[09 Rules/trip-planning-bundle.md]]"
  - "[[09 Rules/trip-application.md]]"
created: 2026-05-13
created-by: claude (codify F3 from format audit-2026-05-13-EOD)
audit-trace: "[[(C) 格式 audit-2026-05-13-EOD.md]] § F3"
---

# Internal Briefing Rules · 内部汇报文档模板

> 给上级 / 决策者请示的**1-page** 汇报文档。决策点 + 阵容 + 风险 + 自承诺。
>
> **Mechanism = platform** (this file). **Audience roster = instance** — who you brief upward + their reporting preferences live in [[09 Rules/_instance/internal-briefing]]. Names below (诸葛 / 何宗寰 / 路奇) are illustrative; the authoritative roster is the instance config.

## 适用范围

**✅ 适用**：
- 出差升级（trip 因外部信号升级为项目级代表团 → 请上级 sign-off 阵容 + 预算 + 接待）
- 合作框架请示（合作量级超个人决策权 → 升级请示）
- 风险预警（重大风险或政策变化需上级知会）
- 关键节点回报（CBT2 / 二测 / 上线等里程碑前后）

**❌ 不适用**：
- 行前规划（议程草拟、约访稿） → [[09 Rules/trip-planning-bundle.md]]
- 申请表 / 报销 → [[09 Rules/trip-application.md]]
- 会议纪要（事后记录） → 会议纪要 archetype

## 命名

```
(C) {chain-anchor} 内部汇报-{对象}.md
```

- `{chain-anchor}` = 关联的 workstream anchor（如 `沪差0518` / `蜜雪联动`）
- `{对象}` = 主送人称呼（如 `诸葛` / `何宗寰` / `路奇`）

**Examples:**
- `(C) 沪差0518 内部汇报-诸葛.md` ✅
- `(C) 蜜雪联动 内部汇报-诸葛.md` ✅
- `(C) 出差汇报.md` ❌ — 模糊，不知道哪个 trip / 谁

## Frontmatter Contract

```yaml
---
type: internal-briefing
created-by: claude
created: YYYY-MM-DD
last-updated: YYYY-MM-DD
biz-eval: skip
audience: {主送人} ({姓名}) · {角色} · {层级}      # 主送人 + 角色; roster → _instance/internal-briefing
purpose: 一句话 概要 — 为什么要发这份汇报
chain-anchor: {anchor}                              # 关联 workstream
sensitivity: internal-only
decision-points-count: 4                            # Q1-Q4
---
```

## Canonical Section Structure

```markdown
# {Trip / Workstream} 内部汇报 · 致{对象}

> 一页可发 / 可面谈 / 可作为管理层群内通知底稿。**核心请示**：{1-3 个最关键决策点}

---

## 概要

{trip / workstream} 由「{原状态}」升级为「{新状态}」。

**触发**：{为什么 escalate — 外部信号 / 内部变化 / 风险触发}

| # | 时段 / 节点 | 内容 | 召集人 / 对方 | 阵容 |
|---|---|---|---|---|

⚠️ **{为什么我方需 mirror / 升级}** → 建议**{升级动作}**：

- {同行/出席阵容建议}

---

## 一、为什么需要{对象}拍板这次

按 [[{对象 wiki}]] § 三 协同路径：

| 场景 | 是否需{对象}签字 |
|---|---|
| ... | ✅ / ❌ |

本次：
- {议题}（{时间}）= {为什么需上级签字}

---

## 二、{议题}速览

| 场 | 核心议题 | 我方期望产出 |
|---|---|---|

详 [[trip plan / workstream bundle]] § N。

---

## 三、关键决策点（请{对象} sign-off）

### Q1 · {第一个决策题}（最关键）

| 方案 | 利 | 弊 |
|---|---|---|
| A. ... | ... | ... |
| B. ... | ... | ... |
| C. ... | ... | ... |
| D. ... | ... | ... |

**{{USER_NAME}} 建议**：方案 **X** — {推荐理由}

### Q2 · {第二个决策题}

…

### Q3 · {第三个决策题}

…

### Q4 · {第四个决策题 / 接待 / 礼品}

…

---

## 四、风险与备份

1. **{风险 1}**：{说明} → fallback {方案}
2. **{风险 2}**：...
3. **{风险 3}**：...
4. **{次要议题 / 行政}**：批量处理建议

---

## 五、{{USER_NAME}} 自承诺

- {对象} sign-off 完成后 24h 内：
  - {动作 1}
  - {动作 2}
- {时间节点} 之前已完成：{已动作}
- {trip / 节点} 期间：{自承诺动作}
- 回穗后 1 周内：{后续 deliverable}

---

## 六、附件 / 参考

- [[trip plan bundle]]
- [[{对象} wiki]]
- [[相关 cards]]
- [[相关 wiki]]

---

## 七、{对象}汇报路径建议

按 [[{对象 wiki}]] § 四 待补：**沟通偏好（文字简报 vs 面谈 vs 语音）{已知 / 未知}**。

**{{USER_NAME}} 建议路径**：
1. 先**企业微信发本简报截图 / 链接**（让 ta 先看 概要 + 阵容建议）
2. **15 min 短会面谈**（决策 Q1-Q4）
3. 决策结果记录在 [[03 Projects/{project}/CLAUDE.md]] 或 daily-note
```

## Hard Rules

- **NEVER** 把"约访话术 / 议程细节 / 行程订单"塞进 internal-briefing — 那些归 trip-planning-bundle / trip-application
- **NEVER** 漏写 § 三决策点的 ABCD 方案 + {{USER_NAME}} 建议 — 上级最讨厌"全开放问题"，建议把推荐 baked-in
- **NEVER** 在 § 五 {{USER_NAME}} 自承诺写不实际承诺（"无条件交付"等）— 写**具体动作 + 时点**

## Soft Rules

- 概要 表必须有，让上级 30s 内 grasp
- § 七 汇报路径建议 = 给 Claude 后续提示用，可省略；如保留，至少标对方 wiki § 四 待补里"沟通偏好"是否已确认
- 决策点数量典型 3-4 个；> 5 个 = 拆两份汇报

## Failure Modes

| Symptom | Fix |
|---|---|
| 决策点没明确"{{USER_NAME}} 建议方案 X" | 强制加 — 上级喜欢有 default，他可以 push back |
| 概要 段落 > 5 行 | 压缩到表格 + 1 行升级理由 |
| 没标 sensitivity = internal-only | 加 — 防止内部汇报被外泄 |

---

*此规则源于 [[(C) 格式 audit-2026-05-13-EOD.md]] § F3 — trip 文档目录混了 3 种 archetype*
