---
category: work
name: meeting-note-spec
description: 预热 skill — 写 会议纪要 前先 ask genre + 6 dimension (如默认 spec 不覆盖), 然后路由到对应 genre-specific spec memory。Trigger on `/meeting-note-spec`, `/纪要规格`, 「新开会议纪要」「写纪要前先确认」, 或当用户提到要写新一场会议纪要而 genre 不明显时。如果 genre 已在用户消息明示 + 默认 spec 已 lock, 可跳过直接进 draft。
model: claude-sonnet-4-6
allowed-tools: Read, Edit, Glob, Grep
companion-rules:
  - "[[feedback-meeting-spec-product-feedback]]"
  - "[[feedback-meeting-spec-operations-sync]]"
created: 2026-05-20
created-by: claude
audit-trace: "高培尧 2026-05-20 Option B request — 防止结构反复 flip 的 pre-flight ask。沪差0519 20+ 轮迭代触发。"
---

# Skill: meeting-note-spec（纪要预热）

写 会议纪要 前先 ask genre + 6 dimension（如默认 spec 不覆盖），然后路由到对应 genre-specific spec memory，避免结构反复 flip。

> **目标**：把 5/19-20 沪差0519 trip 20+ 轮迭代成本（结构反复 flip）固化在 pre-flight 5 分钟内，下次 cut 80% 返工。

---

## When to Use

**自动触发**：用户提到要写新一场会议纪要，且符合任一：

- meeting-genre 不明显
- 多场跨 counterparty / 跨 session, 输出形态待定
- 用户主动说 「先想想这次纪要怎么写」「确认下结构」

**手动触发**：

- `/meeting-note-spec`
- `/纪要规格`
- 「新开会议纪要」/ 「写纪要前先确认」

**跳过条件**：

- genre 已在用户消息明示（如「product-feedback 会」「双周 sync」）
- 已存在对应 `feedback_meeting-spec-{genre}.md` memory 且默认 spec 已 lock
- 用户在 session 内已说过本批纪要都按某 spec 走

---

## Workflow

### Phase 1：判 genre

8 个候选（按使用频率排）：

| genre tag | 中文 | 典型场景 | spec memory |
|---|---|---|---|
| **product-feedback** | 产品反馈会 | demo + 接收对方反馈 + 推进合作（沪差0519 三场）| feedback_meeting-spec-product-feedback |
| **roadshow-debrief** | 路演 / deal 速报 | 多 counterparty 路演，deal 推进为主、反馈为辅（内部 pragmatic 速报）| feedback_meeting-spec-roadshow-debrief |
| **operations-sync** | 项目内同步 | {{PERSON_1}}双周 / {{PERSON}} sync / PMO 周会 | feedback_meeting-spec-operations-sync |
| **vendor-evaluation** | 厂商评估 | epic 引擎评估 / Parametrix AI / 美林供应商 | （待 lock） |
| **knowledge-share** | 行业知识 inflow | epic 动画峰会 / 行业讲座 | （待 lock） |
| **ma-screening** | M&A 标的评估 | {{ORG_B}} target deep dive | （待 lock） |
| **partnership-pitch** | 合作提案 outbound | 我方 pitch 异业 / 政府 / KOL | （待 lock） |
| **term-negotiation** | 合同条款谈判 | 与 partner deal 阶段对接 | （待 lock） |
| **strategic-update** | 战略高层信息流 | 投资人 brief / 董事会 | （待 lock） |

判断逻辑（按优先级）：

1. 用户消息中是否直接说 genre？→ 直接采用
2. 检查 frontmatter `meeting-genre:`？→ 直接采用
3. 看 attendees / agenda 推断（demo 类 → product-feedback；内部 leader sync → operations-sync）
4. 如仍不明，问用户

### Phase 2：6 dimension（默认 spec 不覆盖时才 ask）

如 genre 默认 spec 已 lock 且无偏离需求 → 跳过 Phase 2 直接 Phase 3。

如有偏离信号，问以下 6 项：

1. **切分维度**：游戏主题 / 对方功能线 / workstream / 其他
2. **反馈分类**：二元（肯定/顾虑）/ 三元（+建议）/ 不分类
3. **名字粒度**：function-only / counterparty-person 顶部 / 完整层级
4. **优先级**：0/1/2/3 / 🔴🟠🟡🟢 / 无优先级
5. **体裁**：pragmatic（项目内）/ Register B（外部 senior）/ Register C（执行摘要）
6. **输出 count**：单合并 / N 个分场 doc

### Phase 3：读 spec + 出草稿框架

1. Read **`{{USER_HOME}}\.claude\projects\D--Administrator-Documents-{{USER_NAME}}\memory\feedback_meeting-spec-{genre}.md`**
2. 应用 Phase 2 收到的 overrides（如有）
3. 出草稿框架（含 frontmatter + 默认 sections + table 模板）
4. 让用户 confirm 框架后再 fill 内容

### Phase 4：写 + 跨 genre 共享层处理

所有 genre 写完后均经过共享层校验：

- `/localize-cn` — 中文 monolingual，zero 英文 残留校验
- `/humanize` — AI 痕迹消除（如适用）
- `/pragmatic` — 项目内简报风格（如适用）
- 称谓 + 人名规则（高培尧 / 我方）

---

## Genre Routing 决策表

```
用户消息暗示「demo」「反馈」「对方对游戏」「试玩」 → product-feedback
用户消息暗示「路演」多家速报，且主体是 deal 推进（评级 / 商业模型 / 资源 / 名额）→ roadshow-debrief
用户消息暗示「双周」「sync」「内部周会」「进度同步」 → operations-sync
用户消息暗示「厂商」「评估」「go/no-go」「选型」 → vendor-evaluation
用户消息暗示「峰会」「讲座」「会展 inflow」 → knowledge-share
用户消息暗示「M&A」「target」「标的」「deep dive」 → ma-screening
用户消息暗示「提案」「pitch」「合作意向 outbound」 → partnership-pitch
用户消息暗示「条款」「term sheet」「合同 redline」 → term-negotiation
用户消息暗示「投资人」「董事会」「股东信息流」 → strategic-update
```

---

## 与其他 skill 的关系

**上游**：用户对话或路由 `/meeting-note-deep` 时触发 spec ask

**下游**：决定后调相应 spec → fill 内容 → 共享层 (`/localize-cn` + `/humanize` + `/pragmatic`) 校验

**互斥**：与 `/biz` 评估互斥 — `/biz` 是评估输出（vendor-evaluation 触发），不是会议纪要本身

---

## 实际示例

**Case A**：用户说「新一场 TapTap demo 反馈会」

→ Phase 1 推断：product-feedback（demo + 反馈）
→ Phase 2 跳过（默认 spec 已 lock）
→ Phase 3 直接读 product-feedback spec + 出草稿

**Case B**：用户说「{{PERSON_1}}双周 sync 纪要」

→ Phase 1 推断：operations-sync
→ Phase 2 跳过
→ Phase 3 读 operations-sync spec + 出草稿

**Case C**：用户说「跟蜜雪冰城对接初次 pitch」

→ Phase 1 推断：partnership-pitch
→ Phase 2 spec 尚未 lock，需问用户 6 dimension
→ Phase 3 根据 user answer 出草稿 + lock 新 spec memory（feedback_meeting-spec-partnership-pitch.md）

---

## 锚点

- [[feedback-meeting-spec-product-feedback]] — sample 完整 spec
- [[feedback-meeting-spec-operations-sync]] — 第二个 spec
- [[pragmatic-auto-trigger]] — 风格层
- [[localize-cn-auto-trigger]] — 中文校验
- [[humanize-auto-trigger]] — AI 痕迹
