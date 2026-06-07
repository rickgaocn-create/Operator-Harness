---
layer: platform
type: reference
scope: harness-glossary
created: 2026-05-27
created-by: claude
---

# Harness Glossary · coined-term index

> The ~20 terms you must hold to read this harness. One line each + where the authoritative definition lives. This is the onboarding dictionary — a teammate reads this + [[04 Notes/_system/(C) harness-map-2026-05-24|the Layer model]] + [[HARNESS-MAP|the generated front-door]] and can navigate without spelunking. **Platform-layer** (the machine's vocabulary, not {{USER_NAME}}-specific) → it transfers with the engine.
>
> Rule: a coined term that isn't in here yet is a comprehension debt. New machinery registers its term here (see [[09 Rules/harness-modularity]]).

## Architecture · the three pillars + task layer

| Term | One line | Authoritative def |
|---|---|---|
| **Pillar** | The vault's three modes of knowledge work: Card (Knowing) / Time (Aligning) / Action (Doing). | [[vault-map]] |
| **Card** (卡片笔记, `C{YYMMDD}-`) | An atomic, permanent personal insight — *your* synthesis, distinct from `01 Wiki/` external facts. | [[09 Rules/cards]] |
| **Action** (`T{YYMMDD}-`) | A rolling workstream log; dies on close. Spawned by daily notes, harvested into Cards. | [[09 Rules/action]] |
| **Time pillar** | The OKR cascade: 12-week → weekly → daily, each parented to the one above. | [[09 Rules/time]] |
| **Operon** | The task index: `06 Tasks/` lines are indexed by `{{operonId}}` syntax, not by filename. | [[09 Rules/tasks]] |
| **chain-anchor** | The immutable join key binding an Action file to its `[主项]` task lines. Never renamed once used. | [[09 Rules/action]] |
| **Instinct** (`I{YYMMDD}-`) | A pre-synthesized micro-pattern (trigger+action only); clusters of 3+ promote to a Card/Rule/Skill. | [[09 Rules/instincts]] |

## Memory loop

| Term | One line | Authoritative def |
|---|---|---|
| **CPR** | The session memory loop: `/compress` (save) · `/preserve` (write durable learnings) · `/resume` (load). | [[vault-map]] § skills |
| **Memory OS** | Two-tier memory contract: bounded Core blocks over the searchable Archive tier. | [[09 Rules/memory-os]] |
| **Core block** | A labeled, line-budgeted memory file with `mem-block`, `limit`, and `load-policy`; core does not automatically mean always injected. | [[09 Rules/memory-os]] |
| **Archive tier** | Search/read-on-demand substrate: vault notes, Cards, Actions, Wiki, Tasks, state files, logs, and generated underlays. | [[09 Rules/memory-os]] |
| **Always-on core** | Startup-loaded subset of Core; current policy is runtime-specific and recorded per block. | [[09 Rules/memory-os]] |
| **Cockpit stack** | `/operate` is conversational cockpit; Harness Dashboard is visual cockpit; daily note is ledger/backing store. | [[09 Rules/operator-intents]] |

## Judgment engine (the alignment core)

| Term | One line | Authoritative def |
|---|---|---|
| **Judgment graph** | The typed node set in `09 Rules/_judgment/` — your values + frameworks that gate output. | [[04 Notes/_system/(C) harness-map-2026-05-24]] |
| **Source Graph** | Generated grounding underlay: entities, claims, workstreams, decisions, open questions, task bindings, and source anchors. | [[09 Rules/underlays]] |
| **Taste Engine v1** | Narrow generated judgment underlay from `_judgment/v-*`, `_judgment/f-*`, and `corrections.jsonl` only; no Cards-as-principles. | [[09 Rules/underlays]] |
| **Value node** (`v-`) | A generative drive distilled from observed behaviour (e.g. [[09 Rules/_judgment/v-truth-over-comfort\|truth-over-comfort]]). | `09 Rules/_judgment/v-*.md` |
| **Framework node** (`f-`) | A procedure that operationalizes one or more values (e.g. [[09 Rules/_judgment/f-rigor-verification\|rigor-as-verification]]). | `09 Rules/_judgment/f-*.md` |
| **Correction** (the learn arrow) | A logged divergence between what the AI produced and what {{USER_NAME}} changed it to — the highest-signal judgment data. | [[.claude/_state/corrections-README]] |
| **raw → distilled → promoted** | A correction's lifecycle: captured → reviewed/clustered → encoded as a rule / rubric line / node. | [[.claude/_state/corrections-README]] |
| **Promotion prediction** | A promoted correction's falsifiable follow-up: trigger signature + forbidden behavior + expected behavior + later verdict. | `.claude/_state/promotion-predictions.jsonl` |
| **Harvest / mined** | Scripted backlog mining of the corpus into candidates, in three tiers: `logic` / `prior` / `domain`. | [[.claude/_eval-fixtures/README]] |
| **Distill / proposal** | A model pass that turns candidates/corrections into `status: pending-review` node proposals (human approves before encoding). | [[.claude/_eval-fixtures/README]] |
| **Judgment lens** | The application arm: given an output context, returns the frame set (lenses + vantage prompts) to shape an angle. | [[.claude/_eval-fixtures/README]] |
| **Grader / rubric / VERDICT-LOG** | A subagent (biz-doc-critic / bd-prospect / ma-screening) that scores an artifact against a rubric and logs a verdict. | `.claude/agents/rubrics/` |

## Runtime + health

| Term | One line | Authoritative def |
|---|---|---|
| **Organ** | Any harness component that *should be firing* (routine / signal / bridge / hook / grader), registered in the manifest. | [[.claude/_state/harness-manifest.json]] |
| **harness-pulse vs /status** | The liveness reflex: `harness-pulse` PUSHES every 3h; `/status` is the on-demand PULL of the same verdict. | [[.claude/skills/status/SKILL]] |
| **Operator intent layer** | The thin `/operate` wrapper that maps {{USER_NAME}}'s natural work intents to existing skills while preserving gates. | [[09 Rules/operator-intents]] |
| **Underlay** | Read-only generated machine substrate under authored vault surfaces; supports `/operate` without replacing Cards/Actions/Wiki/Tasks. | [[09 Rules/underlays]] |
| **Tier-7 routine** | A scheduled/event-driven background job (inbox-drift, harness-pulse, eod-snapshot, …) under the routine spec. | [[09 Rules/autonomous-routines]] |
| **Safety tiers** 🟢🟡🔴 | Change authority: 🟢 auto (additive only) · 🟡 propose-then-apply · 🔴 manual (deletions, prose, user files). | [[.claude/skills/vault-evolve/SKILL]] |
| **vault-evolve** | The daily self-evolution routine: usage telemetry + drift + the correction→node promotion loop. | [[.claude/skills/vault-evolve/SKILL]] |
| **skill-eval-gate** | The structural-invariant check a daily-driver skill must pass before versioning. | [[09 Rules/skill-eval-gate]] |
| **Layer 1 / 2 / 3** | YOU (instance, swappable) · MACHINE (shared product) · RUNTIME (how it executes). The transfer seam. | [[04 Notes/_system/(C) harness-map-2026-05-24]] |
| **`(C)` prefix** | Provenance overlay marking an AI-generated file (distinct from the `C-/T-/I-` *type* prefixes). | [[09 Rules/file-types]] |
