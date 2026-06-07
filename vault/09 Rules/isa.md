---
layer: platform
type: rule
scope: harness-structure
created: 2026-06-07
created-by: claude
companion-rules: "[[09 Rules/methods.md]] · [[09 Rules/decisions.md]] · [[09 Rules/message-tone.md]]"
generator: ".claude/_eval-fixtures/isa_lint.py"
description: "The Ideal State Artifact (ISA) — a per-task definition-of-done: one markdown file that is the spec, the test, the done-condition, and the record at once. Criteria are atomic binary probes; Anti-criteria reuse the brand/voice guards as verification. Idea (not the binary) from danielmiessler/PAI."
---

# ISA — the definition-of-done layer

> **Why this exists.** Methods hold the *shape* of a kind of work; the judgment graph holds *what good looks like in general*; nothing held **what "done" means for THIS task**. Without that, "done" is a vibe and the critic has nothing concrete to check. An **ISA (Ideal State Artifact)** is the missing per-task contract: a single markdown file whose criteria double as verification items.

## What an ISA is

One file per non-trivial / forwardable deliverable — `04 Notes/_isa/isa-<slug>.md`, from `07 Templates/isa.md`. It is at once the **spec**, the **test harness** (criteria-as-probes), the **done-condition** (gate), and the **record**. Keyed on stable `ISC-N` ids so an ephemeral work slice reconciles deterministically back to the master.

**Atomic binary criteria.** Each criterion is an `ISC-N` line with a **probe:** — a command or concrete check that returns pass/fail. Not "the copy is on-brand" (a vibe) but `ISC-3: Anti: 英文残留 in CN body · probe: cn-residue-audit.py exits 0`.

**Three guardrails:**
- **Constraints** bind the *solution space* (budget, format, channel, deadline).
- **Criteria** are the positive done-probes.
- **Anti-criteria** make *out-of-scope* probe-able: `ISC-N: Anti: <forbidden> · probe: <check>`. **This is where the ISA reuses {{USER_NAME}}'s existing negative guards** — every CN-audience artifact's ISA carries `Anti: 英文残留 in body · probe: cn-residue-audit.py`; brand/exec artifacts carry the relevant `message-tone` register Anti. Prose guards become probes.

## Frontmatter

| field | values | notes |
|---|---|---|
| `type` | `isa` | required; scanners filter on this |
| `id` | `isa-<slug>` | required; kebab slug = filename stem |
| `status` | `draft` / `active` / `done` | **done is GATED** |
| `tier` | `E1`..`E5` | stakes; higher = more rigor (optional) |
| `deliverable` | one line / `[[link]]` | what this ISA is the done-contract for |
| `method` | `m-<slug>` or blank | the method that produced it, if any |
| `grounds-in` | `[v-*, f-*]` | judgment nodes the criteria invoke (not encode) |

## Body

`## Goal` (one line) · `## Out of scope` (with `Anti:` items) · `## Constraints` · `## Criteria` (the `ISC-N` probes) · `## Verification` · `## Changelog`.

## The done-gate (hard)

`status: done` is illegal while any `ISC-N` is unchecked. A criterion is closed by `- [x] ISC-N …` (passed) or **tombstoned** — `- [x] ISC-N: [DROPPED] <reason>`. Ids are immutable; never renumber, never delete. `isa_lint.py` enforces this — a forwardable deliverable with an `active` ISA carrying open criteria is not done.

## Changelog (four-piece, append-only)

Each learning entry: `conjectured: … / refuted-by: … / learned: … / criterion-now: …` — a Deutsch-style error-correction trail. `reflect.py` harvests it into the reflection feeder, so an ISA's failures feed the judgment loop.

## Boundaries

- **ISA ≠ decision.** A decision is an *immutable call made*; an ISA is a *living done-contract*. A method run may produce both.
- **Value-free criteria.** Criteria *invoke* judgment nodes / the critic; they don't *encode* values.
- **Register or it doesn't exist** ([[09 Rules/harness-modularity.md]]): this doc + `isa_lint.py` + the `04 Notes/_isa/` surface are declared; `harness_map.py` renders an ISA section.

## Gate

```bash
python .claude/_eval-fixtures/isa_lint.py        # structure + done-gate + Anti-coverage
```
