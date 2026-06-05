---
layer: platform
paths:
  - "**/*.md"
scope: cross-cutting
---

# File-Type Conventions · 文件类型约定

> Cross-cutting conventions that apply across all three pillars.

## File-Type Prefix Map

| Prefix | Pillar | Meaning | Example |
|--------|--------|---------|---------|
| `C{YYMMDD}-` | Card (02) | Atomic insight (synthesized) | `C260427-jp-board-reads-memos-backward.md` |
| `I{YYMMDD}-` | Card · instincts (02) | Micro-pattern (atomic, pre-synthesized; trigger+action only) — see [[09 Rules/instincts.md]] | `I260514-grep-vault-before-grilling-cuts-llm-flavor.md` |
| `T{YYMMDD}-` | Action (10) | Workstream / task track | `T260427-mna-screening-v1.md` |
| `2026-Q{n}` | Time (04) | 12-week anchor | `2026-Q2.md` |
| `2026-W{nn}` | Time (04) | Weekly cascade | `2026-W17.md` |
| `2026-MM-DD` | Time (04) | Daily log | `2026-04-27.md` |
| `(C) ` | Any | AI-generated (Claude provenance overlay) | `(C) {{ORG_D}} 基金投资建议书.md` |

The framework prefixes (`C-`, `T-`) declare *file type*. The `(C) ` prefix declares *authorship*. They can coexist when needed (rare — most framework-typed files {{USER_NAME}} drives himself).

## Frontmatter Standards (All Files)

Required across all framework-typed files:
```yaml
---
type: {card | action | 12-week | weekly | daily}
created: YYYY-MM-DD              # ISO format, no exceptions
---
```

Recommended additions per pillar live in the pillar-specific rule files (`cards.md`, `action.md`, `time.md`).

## Wikilink Conventions

- **Internal links:** `[[note-name]]` or `[[folder/note-name]]` for disambiguation
- **Card-to-card:** Always use full headline — `[[C260427-jp-board-reads-memos-backward]]`
- **Action-to-Card:** Action files cite Cards in `## Linked Cards` section
- **Time-to-Action:** Weekly files cite Actions in `## Active Tracks` section
- **Daily-to-Weekly:** `> Parent: [[2026-W17]]` at top of every daily note

Tags ≠ Links. Tags categorize; links create the graph. Default to links; use tags sparingly.

## Folder-Pillar Map

| Folder | Pillar / Role | Rule file |
|--------|---------------|-----------|
| **`00 Raw/`** | Inbox (pre-pillar) | — |
| **`01 Wiki/`** | External intel (not a pillar) | — |
| **`02 Cards/`** | **Card pillar** (Knowing) | `cards.md` |
| **`03 Projects/`** | Project workspaces (artifact persistence) | — |
| **`04 Notes/12-week/`** | **Time pillar — 12-week** | `time.md` |
| **`04 Notes/weekly/`** | **Time pillar — weekly** | `time.md` |
| **`04 Notes/daily notes/`** | **Time pillar — daily** | `time.md` |
| **`.claude/skills/<name>/SKILL.md`** | Claude Code skills (real, YAML-fronted) | — |
| **`06 Tasks/`** | Inbox capture + cross-project "Today" board + Personal Kanban | `tasks.md` |
| **`03 Projects/<name>/Tasks.md`** | Per-project Kanban — atomic tasks | `tasks.md` |
| **`10 Action/`** | **Action pillar** (Doing) | `action.md` |

## Root-Level Discipline for Major System Folders

> Every major system folder has a **root allow-list**. Anything at the folder root that isn't on the list is a *stray* — surfaced as a 🟡 proposal by `/vault-evolve` and `/sanity`, never auto-moved. Resolution flow: `vault-manager audit` → PROPOSE move (with wikilink rewrite plan) → user confirms → EXECUTE.

| Folder | Root allow-list (only these may live at root) | Default destination for strays |
|---|---|---|
| **`00 Raw/`** | (governed by `raw-immutable.md`; out of scope for this rule) | — |
| **`01 Wiki/`** | `index.md` (master index) | requires entity folder · always propose, never auto-route |
| **`02 Cards/`** | `_index.base`, `_adr.base`, `(C) README.md`, `_card-lint-log.md` | `_inbox/` (no domain frontmatter) · domain folder (`{{PROJECT_A}}` / `{{ORG_B}}-Inc` / `cross-border` / `ops` / `meta` / `instincts`) by frontmatter |
| **`03 Projects/`** | (none — content under project subfolder) | requires project assignment · always propose, never auto-route |
| **`04 Notes/`** | (none — content lives in subfolders) | by prefix: `2026-Q*` → `12-week/` · `2026-W*` → `weekly/` · `YYYY-MM-DD` → `daily notes/` · generated system/infra/architecture/log → `_system/` · external intel / research → `Research/` · meeting transcripts → `Session Logs/` · auto-generated reports → `auto-reports/` |
| **`06 Tasks/`** | `Today.md`, `Personal.md`, `Inbox.md` (closed fixed-surface set) | no strays expected — any other file is anomaly, propose for triage |
| **`08 Agents/`** | `README.md` + `<agent-name>.md` (flat by design) | flat — allow-list is "any `.md` file at root" |
| **`09 Rules/`** | `<rule-name>.md` (flat by design) + `_archive/` · `_instance/` · `_judgment/` subfolders | flat — allow-list is "any `.md` file at root" |
| **`10 Action/`** | `README.md` | Action files declare horizon → `11 12-Week/` · `12 Active/` · `13 Maybe/` · `_archive/` |

### How strays are resolved

- **Detection:** `vault-manager audit` scans each row's folder root and flags violations against the allow-list.
- **Routing:** the "Default destination" column is the *suggested* target; ambiguous cases (e.g., a `04 Notes/` root file with no recognizable prefix) are surfaced as 🟡 propose-only — never silently moved.
- **Move mechanics:** vault-manager's existing PROPOSE → EXECUTE flow handles the actual move + wikilink rewrite across the vault. Generator scripts referencing moved paths (e.g., `.claude/routines/harness_map.py`) must be updated in the same batch.
- **Sanity backstop:** `/sanity` mirrors the same check on its watched-surface list; `/vault-evolve` Phase 2 (structural audit) surfaces accumulated strays for batch review.

### Hard rules

- **NEVER** auto-move a stray. Always surface as proposal — user is the authority on destination.
- **NEVER** add to a root allow-list without justification documented inline (e.g., "front-door index, analogous to `vault-map.md`").
- **NEVER** create a new subfolder to avoid the proposal flow — if a stray doesn't fit any existing destination, surface it as a propose-only finding and let the user decide whether to create a new bucket.

---

## Cross-Pillar Flow Reference

```
GOALS.md ──→ 04 Notes/12-week/2026-Q2.md
                    ↓
            04 Notes/weekly/2026-W{nn}.md
                    ↓
            04 Notes/daily notes/{date}.md
                    ↓ (spawns)
            10 Action/12 Active/T{date}-{slug}.md
                    ↓ (atomic items via chain-anchor)
            03 Projects/<project>/Tasks.md (Kanban, urgency-laned)
              ↕ raw drops via 06 Tasks/Inbox.md
                    ↓ (lessons harvested)
            02 Cards/{domain}/C{date}-{slug}.md
                    ↑ (informs next cycle)
            (back to top)
```

## Hard Rules (All Files)

- **ISO dates only.** `YYYY-MM-DD` in frontmatter, `YYMMDD` in file prefixes. Never `MM/DD/YYYY`.
- **Lowercase kebab-case for slugs.** `jp-board-reads-memos-backward`, not `JP_Board_Reads_Memos_Backward`.
- **Bilingual where natural.** CN for {{PROJECT_A}} / {{ORG_B}} execution context, JP for Tokyo board outputs, EN for cross-border / framework / meta. Don't mix in one file without reason.
- **Provenance is sacred.** Task Collector owns completion stamps (`✅ YYYY-MM-DD`) — Claude doesn't fabricate them. Legacy TickTickSync metadata (`%%[ticktick_id::]%%`, `[link](...)`) in old task lines is inert post-Operon-migration; leave it (stripping risks the line's `{{operonId}}` / structure) — never hand-edit task-line internals.

## Version Log Convention (F4 codify · 2026-05-13)

> 文档多次大改时，**版本日志放文末 `## Changelog`**，body 不留 `v1` / `v2` / `v3` / `v4` 等版本号。

### 触发条件

只在 trip-planning-bundle / trip-application / internal-briefing 等**长寿命**单文档需要多次大改时启用。短寿命文档（一日笔记 / 临时草稿）无需此 section。

### 标准格式

```markdown
---
（文件末尾）

## Changelog

| 版本 | 日期 | 主要变化 |
|---|---|---|
| v1 | 2026-05-13 | 初版（行程 5/19-21） |
| v2 | 2026-05-13 | 行程调整 5/18-20 |
| v3 | 2026-05-13 | TapTap 5/18 15:00 锁定 + 47 锁 |
| v4 | 2026-05-14 | {{PERSON_5}} 14:00 全口径锁 |
```

### Hard Rules

- **NEVER** 在 body 段落或 section 标题里出现 `v3 重写` / `v4 更新后` / `v2.1` 等版本号
- **NEVER** 在 frontmatter 留 `version: 4` 字段 — 版本号只在 § Changelog 表格里
- **可以** 在 body 标题里加日期标签（如 `## 4 · 议程（2026-05-13 重写）`），但**不加 v 数字**
- **可以** 在 `last-updated: YYYY-MM-DD` frontmatter 字段反映最近改动日期（已有惯例）

### Why this matters

- 散布 vN 标记 → AI 跨次回读文件时需要重建版本时间线，浪费 context
- body 越改越混乱，新读者无法判断"哪段是最新"
- Changelog 集中 → 一目了然变更轨迹，方便回溯
- 与 vault 既有 `情报更新日志` (wiki) / `Changelog` 命名一致

---

## Chain-Anchor Immutability + Visual Dissonance (F5 codify · 2026-05-13)

> [[09 Rules/action.md]] 已规定 `chain-anchor` immutable once used。当行程后期日期变了（如 `沪差0519` 用于 5/18-20 trip），anchor 与文件名 / 显示日期不一致 — **按规则正确，但需 UI hint 减少人读困惑**。

### 标准做法

frontmatter 加 `chain-anchor-note` 字段：

```yaml
chain-anchor: 沪差0519
chain-anchor-note: "immutable per 09 Rules/action.md; 实际 trip-date 见下方字段"
trip-date: 2026-05-18 / 2026-05-20
```

或在 trip bundle 文件顶部 概要 上方加一行 UI hint：

```markdown
> ⚠️ chain-anchor 保留为 `沪差0519`（[[09 Rules/action.md]]：immutable once used；尽管行程调整为 5/18，anchor 不动）
```

### Hard Rules

- **NEVER** 因为行程日期变了就改 `chain-anchor` — 会破坏 Action ↔ Task binding 的 join
- **ALWAYS** 在 chain-anchor 与实际 trip-date 不一致时加 hint（frontmatter `chain-anchor-note` 或 概要 顶部备注），让人读不困惑
- 同理：Sheet Plus / 附件文件名 用 anchor 命名（如 `沪差0519-行程网格.sheet`）即使 trip 改期也保留 — 在 trip bundle § 6 加一行 hint 解释
