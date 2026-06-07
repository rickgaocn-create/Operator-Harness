---
category: work
name: isa
description: Scaffold and gate an Ideal State Artifact (ISA) — a per-task definition-of-done whose criteria are binary probes. Use when starting a non-trivial/forwardable deliverable or to check it done. Anti-criteria reuse the CN-residue and brand-voice guards.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/isa.md]]"
  - "[[09 Rules/methods.md]]"
created: 2026-06-07
created-by: claude
---

# Skill: ISA (definition-of-done)

Per [[09 Rules/isa.md]]. Three moves.

## Scaffold
For a non-trivial or forwardable deliverable, create `04 Notes/_isa/isa-<slug>.md` from `07 Templates/isa.md`. Fill Goal + Constraints from the task; draft 3–7 atomic `ISC-N` criteria, each with a real `probe:`. **Auto-include the Anti-criteria the audience demands** — CN-audience → `ISC: Anti: 英文残留 in body · probe: cn-residue-audit.py`; exec/brand → the relevant message-tone register Anti. If the deliverable came from a method, set `method:` and pull its `grounds-in`.

## CheckCompleteness (the gate)
Run `python .claude/_eval-fixtures/isa_lint.py --json`. Report open criteria; **block `status: done`** while any ISC is unchecked or un-tombstoned. Surface each failing probe with how to satisfy it. A forwardable deliverable is not done until its ISA passes.

## Reconcile
After the deliverable ships, run each criterion's probe, check off passed ISCs (`- [x]`), tombstone dropped ones (`[DROPPED] reason`, never renumber), and append a four-piece Changelog entry for anything refuted. `reflect.py` harvests the Changelog into the reflection feeder.
