---
layer: platform
paths:
  - "**/*.md"
scope: cross-cutting
applies-to-types:
  - meeting-note
  - meeting-summary
  - bd-update
  - market-intel
  - card
  - briefing
  - eval
companion-skills:
  - "[[.claude/skills/meeting-note/SKILL.md]]"
  - "[[.claude/skills/meeting-summary/SKILL.md]]"
  - "[[.claude/skills/attribution-lint/SKILL.md]]"
origin-incident: "[[MEMORY.md]] § 2026-05-21 (沪差汇总 TapTap 都市可玩内容捏造)"
created-by: claude
created: 2026-05-21
---

# Attribution Discipline · 党派归属纪律

> **One-line:** 任何 `**[entity]**：[claim]` 句式必须能从该 entity 的原话引出 literal source line。合成/推断/我方话伪装成对方话 = fabrication。
>
> **Why this is a vault rule, not a skill rule:** 同一失败模式跨 meeting-note / meeting-summary / bd-update / market-intel / card / briefing 多种 artifact type。把规则定在 09 Rules 层，让所有相关 skill 引用而不是内置。

---

## 1. 适用范围

任何文档若出现以下句式 → 受本规则约束：

```markdown
**[某公司 / 某人 / 某机构]**：[一句话陈述]
```

包括但不限于：
- 跨会议反馈汇总表的 `肯定 / 顾虑 / 建议` 列
- BD pipeline 反馈摘要里按客户归属的痛点
- 市场情报文档把信号按竞品归属
- 投资材料把质疑按 LP / 董事归属
- Card 写作把洞察按发言人归属
- 概要 段落的 党派归属 bullets

---

## 2. Pre-write 4-step Checklist

每条 party-prefixed cell / bullet 落笔前必过：

| Step | 检查 | 失败时 |
|---|---|---|
| **1. Source-line test** | 能从 `[entity]` 的原话（妙记 / 转录 / 自记 / 群消息）引出 *literal source line* 支持 `[claim]` 吗？ | 不能 → 改前缀 |
| **2. Single-party test** | `[claim]` 仅从 `[entity]` 的发言能推出来吗？是否要借用 我方 / 第三方 / 另一对方的话才成立？ | 借用 → 改前缀 |
| **3. Paraphrase fidelity** | 我的措辞是忠实压缩，还是加了戏剧化 / 锐化 / 立场化？（例：「demo 只放 3 分钟」→「玩一会儿就没东西了」= 锐化） | 锐化 → 回到原话 |
| **4. Recovery routing** | 不过 1-3 时，重定向到下面 § 3 的合规前缀 | — |

---

## 3. Recovery 路由表

落不到原话时，前缀必须切换为以下之一：

| 前缀 | 何时用 | 示例 |
|---|---|---|
| `**我方判断**：` | 我方综合多源信号得出的判断 | 「我方判断：TapTap 在 6 月 demo 只看到 3-5 分钟都市内容，长板未被展示」 |
| `**项目组观察**：` | 我方对非语言信号 / 节奏 / 体感的解读 | 「项目组观察：B 站商业化线对全球化节奏关心度明显高于 国内运营」 |
| `**我方推断（基于 [signal]）**：` | 从某一具体信号外推的推断，明示外推路径 | 「我方推断（基于 编辑组没承诺 6/19 到场）：6 月美林对 TapTap 优先级不高」 |
| `**我方自陈**：` | 会议中我方自己说的卡点 / 局限 | 「我方自陈：6 月 demo 都市部分仅放 3-5 分钟」 |

⛔ **永不使用** counterparty 前缀承载以上 4 类内容。

---

## 4. Provenance 字段（强制）

`type` 属于 § 适用范围 列出的类型时，frontmatter 必须含 `source_anchors:` 字段：

```yaml
source_anchors:
  - cell: "<逻辑定位，如 玩法.顾虑.TapTap>"
    quote: "<该方原话，引号引语>"
    source: "[[<源会议纪要文件名>]]#<节标题或锚点>"
  - cell: "玩法.顾虑.我方判断"
    synthesis_from:
      - "[[<源 1>]]#<位置> — <信号简述>"
      - "[[<源 2>]]#<位置> — <信号简述>"
```

- 每条 party-prefixed cell 必须有对应 `source_anchors` 条目
- counterparty 前缀的条目使用 `quote:` + `source:`
- `我方判断 / 项目组观察 / 我方推断` 前缀的条目使用 `synthesis_from:` 列出信号来源
- 若 cell 既无 `quote:` 也无 `synthesis_from:` → lint 失败

---

## 5. 文档结构反 fabrication（针对 cross-source 汇总）

**只针对汇总类文档（`type: meeting-summary` 等）**——单会议 meeting-note 不强制：

汇总文档须显式分三层结构：

```markdown
## §1. 各方原话档（按方组织）
### §1.1 TapTap
- **玩法**：「[逐字引语 1]」（[[源]]#位置）
- **战斗**：「[逐字引语 2]」（[[源]]#位置）
### §1.2 B 站联运
- ...

## §2. 跨方综合判断 / 项目组观察
- **§2.1 都市玩法落差**：综合 §1.1[玩法] + §1.2[运营做大] + 我方自陈差异点 → 我方判断 [...]
  > **合成路径**：[显式列出]

## §3. 待办（按公司分类）
...
```

**禁止**：把 §1 原话 和 §2 综合判断 混在同一张反馈表里、共享 party-prefix 格式。这种混合是 fabrication 的认知错位 root cause。

---

## 6. Lint Hook

`type` 在 § 1 适用范围内的文档保存时：
- 由 `/attribution-lint` skill 扫描（手动）或 PostToolUse hook 自动触发
- 检查 `**[A-Za-z一-鿿]+**：` cell 是否：
  - (a) 在 `source_anchors` 中有匹配条目，OR
  - (b) 前缀是 § 3 白名单（我方判断 / 项目组观察 / 我方推断 / 我方自陈）
- 不合规 → 输出违规行 + 修法建议

---

## 7. High-Stakes 标签

文档若 `audience: external` 或 frontmatter 含 `forward-to:` 指向上级 / 决策层 / 跨组织：
- 在文档头部加 `⚠️ 该文档含 N 处合成判断（标 我方判断/项目组观察 前缀），建议人工抽查后再外发`
- N 由 `source_anchors` 中 `synthesis_from` 条目数自动计数

---

## 8. Recovery Protocol（已 ship 的捏造被发现时）

1. **Surface 给用户** — 列出 trace（哪些源信号被合并）
2. **Edit cell** — 改前缀（`**[party]**：` → `**我方判断**：`）+ 重写以反映真实归属
3. **Frontmatter `revision-notes`** — 加修订条：`vN-YYYY-MM-DD: 修正 §X 表中 [位置] 党派归属误标 — 原标 **[party]** 实为 我方判断（合成自 [signal1] + [signal2] ...）`
4. **下游联动** — 若该文档已触发 `/biz` 或被引用，patch 下游文档
5. **MEMORY incident log** — 若为新失败模式，记一条 ≤3 行的总结

---

## 9. 适用边界 / 规则的局限

诚实说：**规则不能 100% 防住跨方污染**。
- 多步推理 + 每步看似合理的合成链，仍可能跨方污染
- Cross-source synthesis 本质 lossy
- 极端情况：某些艺术品（如供董事会的 final memo）**不该由 AI 产出**——只该由实际与会人写
- 本规则降低频率、加 detection layer，但不能替代人脑参与与确认

---

## Origin

- **2026-05-21 incident**：[[03 Projects/{{PROJECT_A}}/04 会议纪要/2026-05-19-沪差0519-反馈与待办汇总]] §一·玩法·顾虑列「**TapTap**：都市部分可玩的东西还是少，玩家玩一会儿就没东西了」—— TapTap 5/18 妙记无任何人说此句，系合成自 我方"6月demo只放3分钟" + 我方"差异点在都市" + B站"运营做大"三个信号，伪装成 TapTap 单方表态。详见 [[MEMORY.md]] § 2026-05-21 条目。
- 该 incident 暴露：现有 **`meeting-note/SKILL.md`** 的 "Never Fabricate Q&A" hard rule 只覆盖 Q&A 句式，未覆盖跨会议汇总表的 party-attributed cell；缺 provenance schema + lint detection + 文档结构分层。
- 本规则一次性把这些缺口都补上，并提到 09 Rules 层防止 skill-local 重复。
