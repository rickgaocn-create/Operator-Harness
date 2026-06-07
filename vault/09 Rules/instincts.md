---
layer: platform
paths:
  - "02 Cards/instincts/*.md"
companion-rules:
  - "[[09 Rules/cards.md]]"     # parent — instincts sit below Card archetype
  - "[[09 Rules/file-types.md]]"
created: 2026-05-14
created-by: claude (adapt homunculus instinct concept to vault)
audit-trace: "[[(C) 2026-05-14 morning-briefing]] § homunculus 借概念"
---

# Instinct Archetype Rules · 直觉卡片约定

> **Micro-pattern below Card-level.** Observation 的 atomic unit — trigger + action 形态。Pre-Card 的"行为微模式池"，足够具体能被 cluster 但不够 synthesized 成 Card。

## 与 Card 的边界

| 维度 | Card | Instinct |
|---|---|---|
| **结构** | 1 个 idea + Evidence + Mechanism + Application | 1 个 trigger + 1 个 action + Observation |
| **大小** | ≤300 字 | **≤100 字** |
| **来源** | 必须 cite source（daily note / 会议 / artifact） | 可来自纯对话观察，不强制 source |
| **synthesis** | 已 synthesized — 有 mechanism 解释 | 未必 synthesized — "I notice X, may be pattern" |
| **可信度** | 默认 live；archived 时标 disproven | 显式 `confidence: 0.0-1.0` field |
| **生命周期终点** | 持续在用 OR archived | **被 promoted** 成 Card / 09 Rule / Skill |

**Litmus test**：
- "I noticed that when X, I do Y — not sure if pattern" → **Instinct**
- "X 因为 Z 总是 Y — 反复验证了 3 次" → **Card** (synthesized)
- "Whenever X, always do Y" → **09 Rule** or **Skill** (enforced)

## Purpose

Capture atomic behavioral observations **before** they crystallize into Card insights. Homunculus 概念借鉴：模式不靠某天突发顿悟形成，而是累积观察 → cluster → 涌现。让 Claude 和 {{USER_NAME}} 都能 drop 一个微观察"留底"，不必当场决定它是 Card / Rule / Skill 哪种。

**Why separate from `_inbox/`**：`_inbox/` 是任何 Card draft，混杂 fully-formed-but-未归类的 Cards。Instincts 是 explicitly-not-yet-synthesized 的 atomic 微模式，结构不同。

## Folder Structure

```
02 Cards/instincts/
├── (C) README.md           Pillar overview
├── I260514-{slug}.md       Atomic instincts
├── I260514-{slug2}.md
└── ...
```

**Flat structure** — domain 通过 frontmatter `domain:` 字段分类，文件夹不分。理由：instincts 一旦 cluster，可能跨 domain；flat 让 cluster 检测简单。

## Naming Convention

```
I{YYMMDD}-{kebab-case-trigger-action}.md
```

- **I** — file-type prefix (Instinct)
- **YYMMDD** — 6-digit creation date
- **trigger-action** — declarative pattern in 5-8 words

**Examples:**
- `I260514-when-bd-counterpart-pulls-4-lines-mirror-upline-team.md`
- `I260513-trip-bundle-version-cruft-accumulates-in-body.md`
- `I260514-vault-grep-before-questioning-cuts-generic-llm-flavor.md`

✅ Capture both trigger + action in headline. ❌ 避免 `I260514-bd-stuff.md` (无 trigger/action 暗示).

## Frontmatter Contract

```yaml
---
type: instinct
created: 2026-05-14                              # ISO
domain: vault | {{PROJECT_A}} | {{ORG_B}}-Inc | cross-border | ops | meta
trigger: "when {condition}"                       # 完整 phrase
action: "{do this}"                               # 完整 phrase
confidence: 0.5                                   # 0.0-1.0, 0.5 = unverified default
status: draft                                     # draft | live | clustered | promoted | archived
source-context: "[[2026-05-14]]"                  # daily note / 对话 reference
related-instincts: []                             # 累积 cluster 时回填 `[[I...]]`
promoted-to: null                                 # `[[C... ]]` / `[[09 Rules/...]]` / `[[skill]]` 当 promoted
---
```

## Instinct Anatomy

```markdown
# {Trigger-action headline}

> **Trigger:** {when condition}
> **Action:** {do this}
> **Confidence:** 0.X

## Observation

What I noticed. Specific 1-3 bullets. ≤50 字。

## Why It Might Be A Pattern

1-2 行 hypothesis。**Not required**（instinct 允许 "just noticed, no theory yet"）。

## Related

- [[I260...-...]] — 相似 trigger / 相似 action / 同 cluster
- [[C260...-...]] — 已有 synthesized Card（如有）
```

**Keep instincts SHORT** — ≤100 字。如果 > 100 字 → 已经是 Card 不是 instinct，搬到 `_inbox/` 或 domain folder。

## Lifecycle

| Stage | Trigger | Action |
|---|---|---|
| **Capture** | Claude 或 {{USER_NAME}} 注意到某 trigger-action 微模式 | Drop in **`02 Cards/instincts/I{date}-{slug}.md`** · `status: draft` · confidence 0.5 default |
| **Verify** | 同 trigger-action 再次出现 | confidence ↑ 0.1 each occurrence (cap 0.9) · status → `live` 在 0.7+ |
| **Cluster** | `/vault-evolve` daily 扫到 3+ instincts 在同 `domain` + 相似 trigger/action | 全 tag `clustered` + propose promotion path (Card / 09 Rule / Skill) |
| **Promote** | User confirm 提升路径 | 建目标 artifact → 在 instinct frontmatter `promoted-to:` 回填 link → instincts 改 `status: promoted` (不删，作 provenance) |
| **Archive** | Instinct disproven 或被 superseded | `status: archived` + link replacement |

⚠️ **Confidence 不自动改**。`/vault-evolve` 提议改动，user 拍板。

## Operations

| Operation | 怎么做 |
|---|---|
| **Capture** | 对话中 drop 一行 "save this as instinct: when X then Y" → Claude 写 `I{date}-{slug}.md`。或 `/instinct-capture` skill (未来建) |
| **Cluster** | `/vault-evolve` daily 跑：grep `domain:` 字段 + 相似 trigger/action → ≥3 命中 → 列入 daily report **`04 Notes/vault-evolve/{date}.md`** |
| **Promote** | User 在 daily review 决定哪些 cluster promote 成什么。手动 invoke `/skill-new` 或建 Card via `/source-ingest` 或写 Rule |
| **Query** | 任何对话里搜 instinct（grep **`02 Cards/instincts/`** by trigger keyword）— 用于 grill 中的 pattern reference |

## Hard Rules

- **NEVER 在 instinct 里写 multi-conditional trigger.** 一个 instinct = 一个 trigger + 一个 action。复合的拆多个。
- **NEVER 删 instinct** — 即使 promoted 或 archived。promoted 保留作 provenance；archived 保留作"我们试过的假设"。
- **NEVER 把 fully-synthesized insight 写成 instinct** — 那是 Card (**`02 Cards/{domain}/C...`**)。Instinct 的特征是"未必 synthesized"。
- **NEVER auto-promote instinct → Card/Rule/Skill 不 confirm user.** Cluster 检测自动，promotion 永远 user-approved。这是 {{USER_NAME}} 的 hard rule（MEMORY § 2 "NEVER auto-create"）的延伸应用。
- **NEVER 在 daily note 散写 instincts** — drop 到 **`02 Cards/instincts/`**。Daily note 是临时层，instinct 要 survive cross-session。
- **NEVER 改 instinct 的 `trigger` 或 `action` field**（除非纠错 typo）。Confidence 调整 OK；trigger/action 改 = 已经是新 instinct，建新文件。

## Failure Modes

| Symptom | Fix |
|---|---|
| Instinct > 100 字 | 它已经是 Card — 搬到 **`02 Cards/_inbox/`** 改 `type: card` |
| 同样 trigger 出现 3+ 次但还没 cluster proposal | `/vault-evolve` 该跑了；或手动 grep + 在 daily-note 提 cluster proposal |
| Promotion 后忘记标 `promoted-to:` | `/vault-evolve` next run 应捡到（标 status promoted but promoted-to 空 = 不一致） |
| Instinct 与 Card 内容重复 | 留 Card 删 instinct？❌ — 改成 instinct `status: promoted` + `promoted-to: [[Card]]`，保留 |
| Confidence 一直 0.5 没更新 | 60d 仍 0.5 → `/card-lint` 类似 lint 该捡到，propose 升 live 或降 archived |

---

## Origin

Adapted from **homunculus** plugin's "instinct" concept ([humanplane/homunculus](https://github.com/humanplane/homunculus)). Homunculus 自动通过 hooks 捕获 + 自动 approve；本 vault adaptation **保留概念但不装 plugin**：

| Homunculus | Vault adaptation |
|---|---|
| Hooks (UserPromptSubmit + PostToolUse) | 手动 capture（对话中 explicit "save as instinct"）+ Claude 主动 propose |
| Background Haiku observer | `/vault-evolve` daily routine + Claude 当对话出现重复模式时 propose |
| Auto-approve instincts | **User-approve** ({{USER_NAME}} hard rule "NEVER auto-create" 延伸) |
| **`.claude/homunculus/instincts/{personal,inherited}/**` YAML | `**02 Cards/instincts/I{date}-{slug}.md`** Markdown + frontmatter（与 Card / Action archetype 一致）|
| `/homunculus:evolve` 命令 | `/vault-evolve` 已有 daily 节奏 + N≥3 cluster 逻辑 |
| `/homunculus:export` / `:import` | 未实现 — 等需要再加（vault 暂时单用户）|

**Why borrow instead of install**：
- Homunculus 装本体会与 `/vault-evolve` daily routine 冲突 + hooks 加 latency
- Auto-approve 违反 {{USER_NAME}} "NEVER auto-create" hard rule
- 概念本身有价值（micro-pattern 层 between daily-note 和 Card），适合 vault-native 实现

Genesis Card 待后续 promote: `C260514-instinct-archetype-borrowed-from-homunculus.md` (TODO when instinct example accumulates)
