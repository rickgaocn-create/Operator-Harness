---
type: rule
created-by: claude
created: 2026-06-05
description: "Routing + format contract for decision records (05 Decisions). Companion to tasks.md. Decisions are a first-class judgment artifact and feed the reflection loop."
---

# Decisions — capture & routing rule

One file per {{USER_NAME}}-owned decision, in `05 Decisions/`. Decisions are not tasks (a task is a thing to *do*; a decision is a *call made* + the reasoning behind it). They are captured in parallel with tasks, by the same skills, under the same discipline.

## When to capture

Capture a decision when a note or conversation contains an explicit, {{USER_NAME}}-owned **call**: "决定 / 定了 / 拍板", "decided", "go / no-go", "we'll commit to", a chosen option among alternatives, a reversal of a prior decision. A mere opinion, an open question, or a counterparty's decision is **not** captured.

**Ownership filter (hard):** only decisions **{{USER_NAME}} or our org owns** become files. Counterparty decisions stay in the source note, never in `05 Decisions/` — same rule as `对方侧` action items in `tasks.md`.

**Capture sources:** the same skills that capture tasks also capture decisions — `/meeting-note` (Phase 4.5), `/distill` (brain-dump reconciliation), and direct conversation. Route the same way regardless of which path surfaced it.

## Boundary with the Action pillar (no double-logging)

`10 Action/` files carry a `## Decisions` table ([[09 Rules/action.md]] § File Anatomy). That is **not** the same surface as this folder — split by scope, and never copy a decision into both:

| Decision is… | Home |
|---|---|
| Tactical, internal to one live workstream, dies when that workstream archives ("skip 鸿蒙 channel first") | the Action file's `## Decisions` table — stays there |
| Strategic / forwardable / cross-workstream / irreversible / worth a durable record + reflection (a 1000万 spend, a partnership downgrade) | a standalone `05 Decisions/` file |

If a strategic `05 Decisions/` call is relevant to an active workstream, **link** to it from the Action file's `## Decisions` table (`see [[05 Decisions/...]]`) — do not duplicate the content. One decision, one home; the Action table points, it doesn't copy.

## File + format

- Path: `05 Decisions/YYYY-MM-DD-<slug>.md`, one file per decision, from `07 Templates/decision.md`.
- Frontmatter contract (stable — Dataview + `reflect.py` key off these):

  | field | values | notes |
  |---|---|---|
  | `type` | `decision` | required; the reflection harvest filters on this |
  | `date` | `YYYY-MM-DD` | when the call was made |
  | `status` | `proposed` / `decided` / `superseded` | |
  | `reversibility` | `reversible` / `one-way` | one-way weighs higher in reflection; decide those slower |
  | `owner` | person/role | |
  | `review_on` | `YYYY-MM-DD` or blank | surfaces in the dashboard + daily digest when due |
  | `supersedes` | `[[link]]` or blank | set the prior decision's `status: superseded` |
  | `method` | `m-<slug>` or blank | the decision-method ([[09 Rules/methods.md]]) that produced this call, if any; closes the review→Memory loop |

- Body uses the template's headings verbatim — **do not rename** `## Decision`, `## Rationale`, `## Consequences / watch for`. `reflect.py:gather()` parses those exact headings to feed the reflections feeder.

## Correlation, supersession & amendment (keeping decisions live)

A decision is not an island. Three mechanisms keep it wired into the vault and able to evolve — without rewriting history or materialising links that rot.

### Link outward (correlation)

Every decision carries a trailing `## 关联文档` section linking to the **entities / projects / people it concerns** plus its source note — sub-bucketed per [[09 Rules/channel-person-wiki.md]] house format (`### 平台 / 项目`, `### 相关决策`, `### 来源`), never flat. Same convention `relation-map` weaves, so decisions are first-class graph citizens.

- **Outbound only.** Link from the decision to the entity (`[[Bilibili]]`), not from the entity back to the decision. Obsidian's backlinks pane and the dashboard's Dataview give the reverse view **live** — so `[[Bilibili]]` never carries a hand-maintained decision list that goes stale when a decision is superseded. This is the deliberate answer to "links rot": materialise outward, compute inward.
- **🔴 Isolation gate.** Never link cross-lane ({{PROJECT_A}} ↔ {{ORG_B}} / {{ORG_A}} / {{ORG_D}}) — same hard rule as `relation-map`.
- **Gloss, don't dump.** `- [[{{PROJECT_A}}]] — 本决策所属发行项目`, not a bare link.

### Supersede (bidirectional — replacing a past call)

When a newer decision **replaces** an older one, wire both ends; never edit or delete the old call (it's the audit record):

- New decision **B**: `supersedes: [[A]]`, and link A under `### 相关决策`.
- Old decision **A**: `status: superseded` + `superseded_by: [[B]]`, and an `## Updates` line noting the replacement.

Both fields set = the chain is navigable both directions. The dashboard flags any `status: superseded` with an empty `superseded_by` as a broken chain.

### Amend (evolving a call that isn't fully replaced)

When a decision's premise shifts but it's not overturned, append a dated entry to the decision's `## Updates` (newest-first) — what changed, why, who. The original `## Decision` / `## Rationale` stay untouched. Amendments feed reflection too (`reflect.py` harvests `## Updates`).

### Who edits decisions

The judgment loop **reads** decisions (via `reflect.py`) and **surfaces** interactions — review-due, same-entity clusters, broken supersession — through the dashboard. It does **not** silently rewrite decision history. Supersession and amendment are **human-gated** edits, like every other learn-loop write. A decision is a record of a call made at a time; you supersede or annotate it, you don't retro-edit it.

## Discipline (mirrors the tasks hard floor)

- **Propose, then write.** Show the proposed file(s); confirm before writing. Never fabricate a decision the operator didn't make.
- **Batch ceiling: ≤3 new decisions per write.** More than that → surface for triage, don't dump.
- **Supersede, don't delete.** A reversed decision keeps its file; set `status: superseded` and link forward.

## Loop integration

Files here feed the judgment loop automatically: `reflect.py` harvests each decision's rationale + consequences as a reflection signal (salience 0.7, or 0.85 for one-way). No extra step — just keep the heading names intact. Decisions due for review (`review_on <= today`) surface in `05 Decisions/_Decisions.md` and the daily digest.

### Method feedback loop (decision-methods)

When a **decision-method** ([[09 Rules/methods.md]], e.g. `09 Rules/_methods/m-bd-partnership-call`) produces a call, its `record_and_wire` step stamps `method: m-<slug>` on this file. That closes a loop the flat learn-loop can't: when the decision hits its `review_on` and the outcome is judged, the learning folds back into the **producing method's `## Memory`** — *the method gets sharper as its decisions are reviewed.* `.claude/_eval-fixtures/method_review_feed.py` surfaces method-linked decisions grouped by method and flags the review-due ones; the Memory write itself is **human-gated**, like every learn-loop write (this loop surfaces, it does not silently rewrite).

## Language

Follow the source note's audience. A {{PROJECT_A}} / {{ORG_B}} business decision written for a CN audience is a CN work artifact and gets `/localize-cn` like any other; an internal system/harness decision may stay EN (as the rule layer does).
