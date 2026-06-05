---
layer: platform
type: rule
scope: memory-retrieval
created: 2026-06-02
created-by: claude
companion-rules:
  - "[[09 Rules/memory-os.md]]"
  - "[[04 Notes/_system/(C) memory-layer-addendum-2026-06-02]]"
---

# Retrieval Scheduler · 三层按需检索

> **Why.** Treating every query as "load the relevant vault context" wastes the deep, cost-bearing path on questions that don't need it. This tiers retrieval and **escalates to the expensive tier only on a trigger** — making the existing *vault-first / grep-before-guess* rules **cost-aware** instead of relying on memory each time. Borrows HyMem's dynamic retrieval scheduling (arXiv 2602.13933; their reported ~92.6% compute cut). Pairs with [[09 Rules/memory-os.md]]'s core/archive split.

## The three tiers

| Tier | Source | Cost |
|---|---|---|
| **T0 — core** | always-on inline (me.md + CLAUDE.md, @import) | free |
| **T1 — cheap index** | MEMORY index · vault-map · Card headlines · the SessionStart brief | already loaded; no extra cost |
| **T2 — deep** | semantic search over `.smart-env` (Smart Connections embeddings) + grep + reading full Cards/docs | cost-bearing — selective |

## The decision (default T1; escalate to T2 only when a trigger fires)

Stay on **T0+T1** for conversational, opinion, or anything answerable from core + the index. **Escalate to T2** when ANY:

1. the query names an **entity not in T0/T1** → grep/semantic-search first (the existing **grep-before-guess** rule, [[02 Cards/meta/C260508-vault-first-before-guessing-entity]])
2. it asks for **specifics / numbers / literal quotes** (grounding required — no paraphrase from memory)
3. it's an **own-work factual** question ({{PROJECT_A}} / 诗悦 / {{ORG_B}}) → **vault-first** (consult `00 Raw` + Cards/Wiki before answering or web)
4. it spans **>1 domain**, or the T1 answer would be **a guess**

## Hard rules

- **Never** answer an own-work factual / entity / specifics question from T0+T1 memory alone — that's the failure the vault-first + grep-before-guess rules exist to prevent; escalate to T2.
- **Never** skip T2 to save cost when a trigger fired — the scheduler optimizes cost *subject to* grounding, not over it.
- T2 is **read-only retrieval** — no writes, no autonomy. (Implementation helper: `.claude/routines/deep_retrieve.py`, to build.)

## Skill selection (record-aware) — the skill-memory edge

When choosing which skill to apply, prefer skills with the better track record. `skill_memory.preferred_skills()` (`.claude/_eval-fixtures/skill_memory.py`) returns skills best-first by success-rate; consult it as a tiebreaker, not a gate. This is the coherence-review edge that was *documented-but-absent* — selection is now record-aware. It only re-orders preference; a skill **graduating** B→A still routes through the adjudicator (never a second verdict-writer). Refinement flags (a skill's success-rate falling below threshold) surface via the same module.

## What this is NOT

- Not a new memory store — it schedules retrieval over the existing core/archive.
- Not a license to under-retrieve — when in doubt between T1 and T2, escalate (grounding > cost), same cautious-default spirit as [[09 Rules/autonomy-tiers.md]].
- Not a skill autonomy path — record-aware *selection* only; graduation stays adjudicator-gated.
