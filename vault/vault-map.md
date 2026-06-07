---
type: vault-navigation
created-by: claude
created: 2026-05-09
last-updated: 2026-05-23
mem-block: nav
description: "Vault routing, rule index, and skills navigation"
limit: 205
limit-unit: lines
load-policy: on-demand
---

# Vault Map

> What lives where, when to use it. On-demand companion to [[me.md]]. **This is the content / navigation map** (the vault's folders + skills); the system front-door is the generated [[HARNESS-MAP]]. Replaces the folder-structure / file-routing / skills-library sections that previously bloated [[CLAUDE.md]].

---

## Architecture · 3 Pillars + Rule Layer

Adopted 2026-04-27. Vault organized around three pillars (Card / Time / Action) with a machine-readable rule layer governing each.

| # | Pillar | Folder | Mode | Captures |
|---|--------|--------|------|----------|
| 02 | **Card** 卡片笔记 | `02 Cards/` | *Knowing* | Atomic insights, principles, lessons — permanent |
| 04 | **Time** 时间笔记 | `04 Notes/{12-week,weekly,daily notes}/` | *Aligning* | OKR cascade: 12-week → weekly → daily |
| 10 | **Action** 任务笔记 | `10 Action/{11 12-Week, 12 Active, 13 Maybe}/` | *Doing* | Active workstreams, rolling logs, decisions |

**The closed loop:**

```
GOALS.md → Time (12-week) → Time (weekly) → Time (daily)
                                              ↓ spawns
                                         Action (workstream)
                                              ↓ atomic items
                                         06 Tasks/ (Operon)
                                              ↓ lessons
                                         Cards (insight)
                                              ↑ informs next cycle
```

**Boundary clarifications:**
- `01 Wiki/` = external facts (someone else's data) · `02 Cards/` = personal synthesis (your insights). Different beasts.
- `03 Projects/` = permanent project artifacts (contracts, briefs, deal memos) — persists across cycles.
- `10 Action/` = rolling workstream logs ("what's happening on this thread this week") — dies on close.
- `06 Tasks/Inbox.md` = atomic Operon-indexed items — finer grain than Action files.
- **Action ↔ Task binding** — `chain-anchor` in Action frontmatter becomes `[主项]` in Operon task lines. Immutable once used. Full mechanic in [[09 Rules/action.md]].

---

## Rule Layer · `09 Rules/`

Machine-enforceable conventions. **Read the matching rule file before any framework-typed file op.** Rules override prose conventions in CLAUDE.md when in conflict.

### Pillar + foundation rules

| File | Domain |
|---|---|
| [[09 Rules/cards.md]] | Card pillar (frontmatter, anatomy, lifecycle, graph health) |
| [[09 Rules/action.md]] | Action pillar + chain-anchor binding |
| [[09 Rules/time.md]] | Time pillar (12-week / weekly / daily cascade integrity) |
| [[09 Rules/tasks.md]] | Task Capture Protocol — batch ceiling, routing, format (replaces retired ticktick.md) |
| [[09 Rules/decisions.md]] | Decision records — `05 Decisions/` log (calls made + rationale); feeds the reflection loop via `reflect.py` |
| [[09 Rules/file-types.md]] | Cross-cutting (`(C)` prefix, frontmatter, naming) |
| [[09 Rules/raw-immutable.md]] | Three-layer KB · `00 Raw/` immutability · `01 Wiki/` index |
| [[09 Rules/memory-os.md]] | Core memory blocks, archive tier, and budget-lint discipline |

### Auxiliary / domain rules

> Read these when the trigger fits — not every file op needs to consult them.

| Category | Files |
|---|---|
| Quality discipline | [[09 Rules/attribution-discipline.md]] (source anchors for quoted claims) · [[09 Rules/sensitivity-guard.md]] (confidential lane policing) · [[09 Rules/instincts.md]] (capture + promote) |
| Style / communication | [[09 Rules/auto-chain-style.md]] (localize-cn / humanize / pragmatic rule data) · [[09 Rules/internal-briefing.md]] (PMO / 主创 / leader audience shape) · [[09 Rules/message-tone.md]] (A1–A11 register matrix) · [[09 Rules/task-naming.md]] (R1–R7 title rules) |
| Workflows / channels | [[09 Rules/channel-person-wiki.md]] (BD channel + contact wiki schema) · [[09 Rules/crm.md]] (person lifecycle overlay on `01 Wiki` — cadence/last_contact/owed; complements channel-person-wiki + relation-map) · [[09 Rules/trip-planning-bundle.md]] (机酒前规划 archetype) · [[09 Rules/trip-application.md]] (机酒已订 → 报销 archetype, xlsx + 邮件 baseline) · [[09 Rules/digest-job.md]] (day-digest section contract) · [[09 Rules/tomorrow-seed.md]] (next-day seed schema) |
| Harness / skills meta | [[09 Rules/autonomous-routines.md]] (Tier 7 routines spec) · [[09 Rules/harness-instrumentation.md]] (usage-log + telemetry schema) · [[09 Rules/harness-surfaces.md]] (canonical live/mirror/generated surface map) · [[09 Rules/memory-os.md]] (core/archive memory contract) · [[09 Rules/operator-intents.md]] (`/operate` wrapper contract) · [[09 Rules/underlays.md]] (Source Graph + Taste Engine v1 contract) · [[09 Rules/skill-routing.md]] (intent → skill mapping) · [[09 Rules/skill-versioning.md]] (skill bump + rollback) · [[09 Rules/skill-eval-gate.md]] (structural eval before versioning) · [[09 Rules/autonomy-tiers.md]] (act-vs-ask tiers — when to act+log vs propose+confirm) |

---

## Folder Structure

```mermaid
flowchart TD
    {{USER_NAME}}["📁 {{USER_NAME}}/ (vault root)"]
    {{USER_NAME}} --> ME["📄 me.md<br/>← Identity, current focus, pointers"]
    {{USER_NAME}} --> VM["📄 vault-map.md<br/>← You are here"]
    {{USER_NAME}} --> CMD["📄 CLAUDE.md<br/>Claude operating instructions"]
    {{USER_NAME}} --> MEM["📄 MEMORY.md<br/>Incident-driven hard rules"]
    {{USER_NAME}} --> GLS["📄 GOALS.md<br/>Strategic tracks + Q2 OKRs"]
    {{USER_NAME}} --> About["📁 About [You]/<br/>Identity depth: personality, patterns"]
    {{USER_NAME}} --> Raw["📁 00 Raw/<br/>Unprocessed intake — log.md, Clippings/, style-samples/"]
    {{USER_NAME}} --> Wiki["📁 01 Wiki/ ★ KB Layer 2<br/>External facts — index.md + entity pages"]
    {{USER_NAME}} --> Cards["📁 02 Cards/ ★ Card pillar<br/>Personal synthesis — atomic insights"]
    {{USER_NAME}} --> Proj["📁 03 Projects/<br/>Permanent project artifacts"]
    Proj --> WY["📁 {{PROJECT_A}}/<br/>BD pipeline: 00→04 Prospects → Delivery"]
    Proj --> Trd["📁 {{ORG_B}}/<br/>M&A pipeline: 00→05 Sourcing → Closed Deals"]
    {{USER_NAME}} --> Notes["📁 04 Notes/ ★ Time pillar<br/>{12-week, weekly, daily notes, meetings, sessions, sanity-reports, auto-reports}"]
    {{USER_NAME}} --> Dec["📁 05 Decisions/<br/>Decision records — {{USER_NAME}}-owned calls + rationale; feeds reflection"]
    {{USER_NAME}} --> Skills["📁 .claude/skills/<br/>Real Claude Code skills (auto-trigger on intent) — index: Skills I Use Daily.md"]
    {{USER_NAME}} --> Tasks["📁 06 Tasks/<br/>Operon-indexed — Inbox / Today / Personal — READ-ONLY"]
    {{USER_NAME}} --> Agents["📁 .claude/agents/<br/>Subagents (canonical) · catalog index at 08 Agents/README"]
    {{USER_NAME}} --> Rules["📁 09 Rules/ ★ Rule layer<br/>Machine-enforceable conventions"]
    {{USER_NAME}} --> Action["📁 10 Action/ ★ Action pillar<br/>Workstream logs — {11 12-Week, 12 Active, 13 Maybe, _archive}"]
    classDef here fill:#2d4a5a,stroke:#88ccee,color:#fff
    classDef pillar fill:#3a5a3a,stroke:#88ee88,color:#fff
    classDef rules fill:#5a4a3a,stroke:#eecc88,color:#fff
    class VM here
    class Cards,Notes,Action pillar
    class Rules rules
```

**Project hubs** (`03 Projects/<name>/CLAUDE.md`) — read on-demand when working in a project; they're pointers (directive · people · live-state links), not an override tier:
- [[03 Projects/{{PROJECT_A}}/CLAUDE.md]]
- [[03 Projects/{{ORG_B}}/CLAUDE.md]]

---

## Skills Index · `.claude/skills/`

> **Generated full inventory** — all skills + agents + judgment nodes + state surfaces, with a drift report: [[HARNESS-MAP]] (regenerate via `python .claude/routines/harness_map.py`). Coined terms: [[09 Rules/glossary]]. Conceptual model: [[04 Notes/_system/(C) harness-map-2026-05-24]].

Canonical reference: [[Skills I Use Daily]] (vault root). Skills migrated 2026-05-11 from `05 Skills/` prose manuals to real Claude Code skills at `.claude/skills/<name>/SKILL.md` with YAML frontmatter — auto-trigger on intent. See [[02 Cards/meta/C260511-vault-skills-converted-to-real-claude-code-skills]] for migration provenance.

### Core memory loop (CPR)

| Skill | Purpose |
|---|---|
| `/compress` | Save session as structured log before close |

### Operations

| Skill | Purpose |
|---|---|
| `/daily-note` | Create/open today's note + active-track status |
| `/meeting-note` · `/meeting-note-deep` | Process meeting transcripts (deep = decision-grade vendor/partnership/board minutes) |
| `/inbox-process` | Triage `00 Raw/` + overdue/stale tasks in `Inbox.md` |
| `/distill` | Personal brain dump (`00 Raw/` free-write) → reconcile into existing workstreams + route Cards/Actions/Tasks. Solo-monologue counterpart to `/source-ingest` (external clippings). v0.1. |
| `/weekly-update` | Full vault refresh — pulse + project status + task sweep |
| `/task-capture` | Operon-native task writer with chain decomposition |
| `/biweekly-report` | OKR-bucketed 双周报 from past 14d Daily memos |
| `/okr` | Author/check-in OKRs (Mode A creation · B KISS review · end-cycle grading) |

### Card operations

| Skill | Purpose |
|---|---|
| `/source-ingest` | Clipping → wiki page + Card draft + bidirectional Related patches + log entry |
| `/card-lint` | Audit `02 Cards/` for orphans, staleness, link-symmetry, frontmatter rot |

### Analysis & audit

| Skill | Purpose |
|---|---|
| `/biz` | Business-grade evaluation (Head-of-X functional lens). **Auto-chains** after `/meeting-note-deep`, `/biweekly-report`, `/okr` Mode A. |
| `/sanity` | Vault audit — drift across 11 watched surfaces. Auto-fixes safe; proposes risky. |
| `/vault-evolve` | **Daily self-evolving routine.** Audit + telemetry + skill drift + subagent learning loop. Scheduled via Windows Task Scheduler 06:00 daily. Accumulates patterns in `[[04 Notes/vault-evolve/_decisions]]`; vault-manager subagent reads ledger to apply learned defaults. See [[02 Cards/meta/C260511-vault-evolve-self-evolving-routine]]. |
| `/grill-me` | Stress-test plans via one-question-at-a-time interview |

### Vault setup

| Skill | Purpose |
|---|---|
| `/brain-setup` | Generate / rebuild [[CLAUDE.md]] via 5-round interview |
| `/new-project` | Scaffold new project folder under `03 Projects/` |

**Rule:** If about to bulk-add tasks inline → invoke `/task-capture`. If about to answer "what changed this week?" by guessing → invoke `/weekly-update`.

---

## Conventions

> Operating conventions (`(C)` prefix, ask-before-editing, bilingual routing, project-hub pointers, precedence hierarchy) are **single-sourced in [[CLAUDE.md]] § Harness Conventions**. Navigation-specific rules only below.

- **Keep `06 Tasks/` to its canonical surfaces** (`Inbox.md` / `Today.md` / `Personal.md`). Operon indexes by `{{}}` syntax not filename, so ad-hoc files aren't invisible — but they fragment the task system. Route by tag per [[09 Rules/tasks.md]]; don't proliferate files here.

---

## Cadence

- **Daily** — write daily note (`/daily-note`); capture cards to `02 Cards/_inbox/`; spawn Action files as workstreams emerge
- **Friday EOD** — weekly review: process card inbox, fill weekly review block, update Action horizons
- **Friday 8am (scheduled)** — `/sanity` pre-weekly-review drift scan
- **Mid-cycle (W19–20, mid May)** — recalibrate Q2 OKRs in [[04 Notes/12-week/2026-Q2.md]]
- **End-cycle (W26)** — batch-harvest cards, archive closed workstreams
- **Monthly OR after >5 new MEMORY entries** — prune [[MEMORY.md]] (≤200 line hard cap)

---

## Core Memory Blocks (kept tight on purpose)

| File | Load policy | Limit | Purpose |
|---|---|---|---|
| [[me.md]] | always-on | 120 | Quick bio, current focus, work preferences, pointers |
| [[CLAUDE.md]] | always-on | 180 | Canonical runtime operating instructions, hard fails, auto-chain |
| [[AGENTS.md]] | always-on | 60 | Codex adapter to canonical [[CLAUDE.md]] |
| [[MEMORY.md]] | conditional | 200 | Incident-driven hard rules — append on incident, prune monthly |
| [[GOALS.md]] | on-demand | 140 | Strategic tracks + current Q OKRs |
| [[vault-map.md]] | on-demand | 205 | Navigation, skills index, conventions |

Contract: [[09 Rules/memory-os.md]]. Depth (`About [You]/`, `09 Rules/`, project CLAUDE.md, skill files, KB) loads on-demand.

---

*This file is maintained by `/sanity` (drift detection) and proposed updates from `/weekly-update` when vault structure changes. Direct edits welcome — flag breaking changes with a one-line note above the affected section.*
