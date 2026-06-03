---
category: meta
name: scaffold
description: Scaffold new vault artifacts with --type=skill|channel-person|trip|project. Use when creating a skill, channel/person wiki, trip bundle, or project folder.
model: claude-opus-4-7
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/channel-person-wiki.md]]"
  - "[[09 Rules/trip-planning-bundle.md]]"
created: 2026-05-14
created-by: claude
audit-trace: "2026-05-14 prune pass — merged /skill-new + /channel-person-wiki-new + /trip-plan-new + /new-project into single dispatcher"
---
# Skill: Scaffold (unified artifact instantiator)

One entry, four targets. Pick `--type` (or let the trigger phrase reveal it) and the skill dispatches to the right scaffolder.

| `--type` | Target | Canonical rule |
|---|---|---|
| `skill` | **`<vault>/.claude/skills/{name}/SKILL.md`** | vault skill conventions (4 canonical sections, CN+EN trigger phrases) |
| `channel-person` | **`01 Wiki/{{PROJECT_A}}/渠道/{Name} ({Org}).md`** | [[09 Rules/channel-person-wiki.md]] |
| `trip` | **`03 Projects/{{PROJECT_A}}/03 行程计划/(C) 差旅计划-{YYYY-MM-DD}_{城市}.md`** | [[09 Rules/trip-planning-bundle.md]] |
| `project` | **`03 Projects/{Project Name}/`** (folder + scoped CLAUDE.md + COMMANDS.md) | project template duplicate |

> Contract source-of-truth lives in the rule files for `channel-person` / `trip`. Skill body below restates only the interview + write steps; the rule file wins on field semantics.

## When to Use

- `/scaffold --type={skill|channel-person|trip|project}` explicit
- Inferable trigger phrases:
  - **skill** — "/skill-new", "新建 skill", "起一个 skill", "scaffold skill", "write a skill"
  - **channel-person** — "/channel-person-wiki-new", "建档 {name}", "新建渠道人物 wiki", "{name} 建档"
  - **trip** — "/trip-plan-new", "起 trip plan", "新建差旅计划", "出差计划 {城市} {日期}"
  - **project** — "/new-project", "new project", "start a project for X", "scaffold X project"

**Don't use for:**
- Editing existing artifact — use Edit
- Sub-agent — those live in `<vault>/.claude/agents/`, different format
- Card / instinct — use `/source-ingest --type=clipping|article|instinct|conversation`

## How It Works

### Phase 0 — Resolve `--type`

1. Explicit flag wins. If `/scaffold --type=trip` → `type = trip`.
2. Trigger phrase inference per § When to Use mapping.
3. Genuinely ambiguous → ask plain-text 1-line: *"哪种？skill / channel-person / trip / project"* — wait for reply.

### Phase 1 — Dispatch

Each type runs its own subroutine below. Hard rules from the canonical rule file always win over restated steps here.

---

## Type · skill

Scaffold a new Claude Code skill at **`<vault>/.claude/skills/{name}/SKILL.md`**. Adapted from Matt Pocock's `/write-a-skill` + GBSOSS `/skill-from-masters`.

### S1 — Masters Discovery (vault-first)

> Skills built on vault-curated masters > generic LLM defaults. Vault is already ingested; grep first, fall back to web later.

1. **Identify domain** from initial prompt (interview / bd / m&a / design / okr / etc.)
2. **Grep vault**:
   ```bash
   grep -rli "{domain}" "02 Cards/" --include="*.md"
   ls "01 Wiki/{{PROJECT_A}}/行业基础/"
   grep -rli "{domain}" "02 Cards/instincts/"
   ```
3. **Surface to user as plain text** (NOT AskUserQuestion):
   ```
   Domain: {x}
   Vault 已 ingested:
   1. [[Card]] — one-line
   2. ...
   Vault 暂缺:
   - {master} — propose future ingest
   选哪些 anchor 进新 skill？(列号 / 全选 / 加入新的)
   ```
4. **Capture selected methodologies** → working memory for S4 draft.
5. **Optional instinct stub** — user mentions ungested master → drop `I{date}-need-to-ingest-{slug}.md` per [[09 Rules/instincts.md]].

### S2 — Gather Requirements (4 questions, plain text)

1. Skill name (kebab-case, no collision)
2. Core action (1 sentence)
3. Trigger phrases (5-10 CN+EN mix)
4. Anti-triggers (when NOT to use)

### S3 — Conflict Check

```bash
ls "<vault>/.claude/skills/" | grep -i "{candidate}"
grep -A2 "^description:" <vault>/.claude/skills/*/SKILL.md | grep -i "{trigger}"
```

If existing → propose Edit instead OR rename candidate.

### S4 — Draft SKILL.md

Path: **`<vault>/.claude/skills/{name}/SKILL.md`**. **4 canonical sections required** (When to Use / How It Works / Hard Rules / Failure Modes). Methodologies from S1 baked in as Hard Rules + Phase steps + Failure Modes.

```markdown
---
name: {name}
description: {what + 5-10 trigger phrases CN+EN}
allowed-tools: Read, Edit, Glob, Grep, Bash[, Write][, WebFetch]
[source: https://... if adapted]
[companion-rules: "[[09 Rules/...]]"]
---
# Skill: {Display Name}

{1-paragraph overview}

## When to Use
- {triggers}
**Don't use for:** ...

## How It Works
### Phase 1 — ...

## Hard Rules
1. **NEVER ...**
2. **ALWAYS ...**

## Failure Modes
| Symptom | Fix |
|---|---|
```

### S5 — Skills Index update

Append to `[[Skills I Use Daily]]` under matching category. Mark `Imported / External` if adapted from upstream.

### S6 — Confirm

> "已建档 [[<vault>/.claude/skills/{name}/SKILL.md]]. Triggers: {list 5}. Hard rules: {N}. Index 已更新."

---

## Type · channel-person

Instantiate **`01 Wiki/{{PROJECT_A}}/渠道/{Name} ({Org}).md`** per [[09 Rules/channel-person-wiki.md]].

### C1 — Interview (plain text, NOT AskUserQuestion)

1. 真名 / 花名 / 公司 (e.g., `钟馨 / Bubble / Bilibili`)
2. 部门 / 角色
3. Mobile / 微信 / email / QQ / 办公地址 (partial OK)
4. 直属上级 / 平级 / 下级 — `[[wiki]]` or `待补`
5. priority `P0|P1|P2|P3`
6. 概要 — 一句话战略定位 + 当前关键议题

### C2 — Resolve Path

```bash
TARGET="01 Wiki/{{PROJECT_A}}/渠道/{真名 if known else 花名} ({Org}).md"
```

真名 first, aliases 含花名. Exception: 花名 是绝对工作名 (e.g. `47`) → 花名 命名 + 真名 alias.

If target exists → STOP, propose Edit.

### C3 — Write

Per [[09 Rules/channel-person-wiki.md]] § Canonical Section Structure (5 sections: 基本信息 / 组织位置 / 战略定位 / 当前关联议题 / 待补信息 + 关联文档). frontmatter must include `priority` / `status` / `source_reliability`.

### C4 — Platform Wiki Patch (soft)

如 platform wiki 存在 → append 一行 link to § 关联文档. 如不存在 → skip.

### C5 — Confirm

> "已建档 [[{path}]]. {Name}, {Role}, P{x}. 待补 §五 列了 N 项."

---

## Type · trip

Instantiate **`03 Projects/{{PROJECT_A}}/03 行程计划/(C) 差旅计划-{YYYY-MM-DD}_{城市}.md`** per [[09 Rules/trip-planning-bundle.md]].

### T1 — Interview (plain text)

1. 起 / 止 日期 ISO
2. 城市
3. chain-anchor (default `{城市拼音缩写}差{MMDD}`; immutable per [[09 Rules/action.md]])
4. 同行 travelers
5. trip-purpose (1 line ≤80 chars)
6. Hard anchors (已锁场) — optional
7. Soft anchors (待约) — optional

### T2 — Resolve Path

```bash
TARGET="03 Projects/{{PROJECT_A}}/03 行程计划/(C) 差旅计划-{YYYY-MM-DD}_{城市}.md"
```

If exists → STOP, propose Edit.

### T3 — Write

Per [[09 Rules/trip-planning-bundle.md]] § Canonical Section Structure. 9 sections (概要 / 行程概览 / 飞前节点 / 约访草稿 / 议程 / 出差预订 / 协同手册 / 引用 / 状态追踪 / Changelog). frontmatter must include `chain-anchor`, `trip-date`, `trip-city`.

### T4 — Confirm + Next Steps

> "已建档 [[{path}]]. Hard anchors: {N} 场, Soft: {M} 场, 同行: {count} 人. 下一步：(1) 补 §3 约访稿 (2) align 阵容 (3) 包体 lock."

---

## Type · project

Scaffold a new project under **`03 Projects/{Project Name}/`**.

### P1 — Duplicate template

```bash
cp -R "03 Projects/(PROJECT TEMPLATE)" "03 Projects/{Project Name}"
```

### P2 — Interview (plain text — one at a time, NOT AskUserQuestion)

1. Project name
2. What is this project? (1 paragraph)
3. What does "shipped" look like? (prime directive)
4. Key people (or "just me")
5. Process from start → done (becomes numbered folders)
6. Project-specific rules (optional)

### P3 — Folder structure

Remove `00 Duplicate/`, placeholder CLAUDE.md, placeholder COMMANDS.md. Create numbered process folders from P2.5 answer; suffix utility folders (`XX System/`, `XX Skills/`, `XX Attachments/`, `XX Iteration Logs/`).

Default if process unclear:
- `00 Ideas/` (input)
- `01 In Progress/` (process)
- `02 Done/` (output)

### P4 — Write scoped CLAUDE.md

Structure: project name + 1-paragraph overview / Claude's Role (prime directive from Q3) / Process / Key People / Folder Structure / Rules & Conventions (`(C)` prefix for AI-authored, edit-permission for human files, + Q6 specifics) / Current Status. Use `<!-- TODO: ... -->` for unknowns.

### P5 — Write COMMANDS.md (stub)

```markdown
# Commands & Skills

## Skills (in XX Skills/)
_No project-specific skills yet._

## Commands
_No project-specific commands yet._
```

### P6 — Update root CLAUDE.md

1. Folder Structure: add project under **`03 Projects/`** tree
2. My Current Projects & Overviews: add subsection w/ Status: Just created + 1-line description

### P7 — Seed Kanban (if applicable)

If interview surfaced dated commitments → scaffold **`03 Projects/{Project}/Tasks.md`** with 6-lane shape per [[09 Rules/tasks.md]]. Ask before seeding. Context tag `#{project-slug}`. Batch ceiling ≤ 3 per write.

### P8 — Confirm

Show folder structure + CLAUDE.md summary + Kanban scaffold + TODO list.

---

## Hard Rules (all types)

1. **NEVER use AskUserQuestion** — Discord 不渲染。Plain text 单行问 + 等回复。
2. **NEVER skip Phase 0 type-resolution** — 模糊时 ask, 不自作主张。
3. **NEVER overwrite existing artifact** — 如目标 path 已存在，STOP + propose Edit。
4. **NEVER skip the canonical rule file** — channel-person / trip / skill 都有 09 Rules contract；本 skill 是 instantiator，rule file 是 truth source。
5. **NEVER fabricate `source:` frontmatter** — skill type only fills source if 真实有 upstream。
6. **ALWAYS cross-reference 09 Rules** when writing framework-typed files (Card / Action / wiki / daily / trip / skill).
7. **ALWAYS update [[Skills I Use Daily]]** for `--type=skill` runs. Index miss = skill 对未来 Claude 不可见。
8. **ALWAYS drop instinct stub** in skill-type S1 if user names an ungested master.
9. **NEVER name trip bundles `(C) 差旅申请包-...`** — that prefix is grandfather; new files use `(C) 差旅计划-...` per [[09 Rules/trip-planning-bundle.md]].
10. **NEVER 用花名命名 channel-person wiki** unless 花名是工作场绝对主称 (e.g. `47`).

## Failure Modes

| Symptom | Fix |
|---|---|
| Target file already exists | STOP, propose Edit instead, do not overwrite |
| Type genuinely ambiguous | Ask plain-text 1 line, wait for reply |
| Skill name collision | Propose `{name}-v2` or specialize naming |
| Trigger phrase overlap with existing skill | Narrow trigger to specific noun |
| 4-canonical-section heading unknown content | Write `暂无 — Phase X 已覆盖` placeholder; keep heading |
| chain-anchor 冲突 (trip) | Add `v2` suffix or rename anchor entirely |
| Multi-person trip, 不知协同手册写啥 | § 6 留 stub, 飞前 1 周补 |
| 项目 process 不清晰 | Default 3 folders + TODO in CLAUDE.md |
| User mentions master not in vault (skill) | Drop instinct stub `I{date}-need-to-ingest-{master}.md` |
| Phase 0 grep returns 0 results (skill, empty vault) | Propose `/source-ingest` web master fetch OR proceed without (acceptable for novel skill) |

---

*One scaffolder, four targets. Was 4 skills (`/skill-new` + `/channel-person-wiki-new` + `/trip-plan-new` + `/new-project`); now 1 dispatcher + 4 typed subroutines. Trigger phrases all preserved.*
