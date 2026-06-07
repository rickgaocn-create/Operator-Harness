---
category: meta
name: precipitate
description: "Turn a finished run or class of instances into a reusable method (composition layer in 09 Rules/_methods/): transcribe topology, generalize by subtraction, write the m-<slug> artifact. Triggers: /precipitate, 'make this a method', 'crystallize this workflow', after a task whose shape recurs."
model: claude-opus-4-8
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
companion-rules: "[[09 Rules/methods.md]]"
sibling-of: "[[.claude/skills/judgment-draft/SKILL.md]]"
created: 2026-06-06
created-by: claude
---

# Skill: Precipitate — mine a method from work already done (`/precipitate`)

`judgment-draft` distills a *value/correction* from a deviation; `precipitate` distills a **method** (composition shape) from a completed run. It is the *generate* half of the method layer ([[09 Rules/methods.md]]) — the capture ritual that fills `09 Rules/_methods/`. Authoring a method from imagination produces an untested artifact that rots (the manual-feeder lesson); precipitating from a real run grounds it in something that happened. Same philosophy as the corrections→judgment loop: **distill from observed behavior, not stated intention.**

> **First principle:** a precipitated method is a *hypothesis about the shape*, not a proven recipe. It ships `status: draft` and earns `validated` only when a real run reuses it. Confidence tracks the source (below).

## When to use
- A task just finished whose shape will recur ("crystallize this").
- A class of similar records exists with no reusable template (e.g. the BD decisions → m-bd-partnership-call).
- `/operate` hit a task-kind with no matching method and the work was non-trivial.

## Source-quality tiers (set expectations; all ship draft)
| Source | Confidence | Why |
|---|---|---|
| **Class of raw instances** (N real records of one kind) | highest | a shape recurring across N is trustworthy; `## Memory` gets cross-instance learnings only visible across runs |
| **Single completed run** | topology exact, shape unproven | you walked the edges so the DAG is right, but n=1 — confirmed only on re-use |
| **Distilled signal** (corrections/rules, one remove from raw) | inherits prior judgment | grounded but a step removed from ground truth — note it in `precipitated-from` |

## The cycle

```
1 POINT      Name the source: one finished run, OR a class of instances, OR distilled signal.
             Read it/them in full. Do NOT invent — if there's no real source, stop.

2 TRANSCRIBE Walk what actually happened and record the dependency EDGES (what fed what).
             A finished run can't flatten — the topology is given. For a class, extract the
             SHARED shape across instances (the recurring fan-in/fan-out, not one path).

3 SUBTRACT   Generalize by removing every instance-specific detail. A step's contract reads
             "condense the cleaned draft", never "condense the Redis post". Concrete outputs
             become run #1's assets, not the method. Keep it VALUE-FREE: steps invoke values
             (grounds-in), they never encode them.

4 VERIFY     Faithfulness pass — a SECOND, independent cold read (spawn a subagent via Agent,
             or re-derive cold yourself). The risk here is INSTANCE-LEAK, not graph-flattening:
             ask of every step "would this read the same for the NEXT instance?" Strip what leaks.

5 WRITE      From 07 Templates/method.md → 09 Rules/_methods/m-<slug>.md (next free M-number).
             Fill the DAG (### <slug> + **after:**), per-step contracts, calls-skills (real moves),
             grounds-in (v-*/f-* invoked), deliverable, precipitated-from, status: draft.

6 SEED       Write ## Memory from what the run(s) revealed, cited to the source instance(s).

7 GATE       python .claude/_eval-fixtures/method_lint.py     (DAG valid, deps resolve, contract complete)
             python .claude/routines/harness_map.py            (render into the front-door)
             python .claude/routines/skill_mirror_sync.py      (only if this run also added a skill)
```

## Hard rules
- **Value-free.** A step sequences moves; it never encodes a value. "model the resource-exchange" ✓; "be truthful" ✗ (that's `_judgment` + the critic). A method that smuggles values is a layer violation.
- **Soft DAG.** `after:` declares dependency *shape*, not execution *order*. The executor may deviate. A rigid pipeline is a bug.
- **No executor.** Precipitate the template artifact only — never build a `runs/` state machine. The agent and `/operate` already execute.
- **Draft on birth.** Always `status: draft`; promotion to `validated` is human-gated, after a real run reuses it.
- **Don't invent.** No real source → no method. Precipitation requires something that happened.
- **Faithfulness is mandatory.** Step 4 is the discovery-pass/adjudicator reflex applied to instance-leak; skipping it ships a leaky skeleton.

## Modes
| Mode | Trigger | Behavior |
|---|---|---|
| **Run** | `/precipitate` after a task | Single completed run → method; topology exact, flag n=1. |
| **Class** | `/precipitate <kind>` | Mine N records of one kind → shared shape; richest Memory. |
| **From signal** | `/precipitate --from <rule/correction>` | Distilled signal → method; note the one-remove in `precipitated-from`. |

## Lineage
The method layer + this ritual were stolen (idea, not binary) from the trace/`make-trace` layer in AIScientists-Dev/Flowtrace, mapped onto the harness as the structural twin of the judgment loop. See [[09 Rules/methods.md]].
