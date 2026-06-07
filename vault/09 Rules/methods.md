---
layer: platform
type: rule
scope: harness-structure
created: 2026-06-06
created-by: claude
companion-rules: "[[09 Rules/decisions.md]] · [[09 Rules/harness-modularity.md]]"
generator: ".claude/_eval-fixtures/method_lint.py"
description: "The method/composition layer — reusable task-kind templates that sit between skills (moves) and judgment (values). Twin of the judgment loop; born from instances, consumed by /operate."
---

# Methods — the composition layer

> **Why this exists.** Skills are the *moves*; the judgment graph is *what good looks like*. Nothing held **how the moves string together for a kind of task** — so each report, each BD call, each debrief got re-assembled from scratch even though the shape was already in your head. A **method** is that missing layer: the reusable DAG for a kind of task. (Stolen, deliberately, from the trace layer in AIScientists-Dev/Flowtrace — the idea, not the binary.)

## What a method is (and is not)

A method is the **structural twin of a judgment node**, one artifact over: instances → precipitate → distill → human-gated promote → method node → `/operate` consumes → `review_on` verifies. Same loop the corrections→judgment graph already runs, different artifact.

| Layer | Holds | Lives in |
|---|---|---|
| Skills | the moves (what executes) | `.claude/skills` |
| **Methods** | **the shape of the work (the DAG)** | **`09 Rules/_methods/m-*.md`** |
| Judgment | what good looks like (values → critic gate) | `09 Rules/_judgment` |

**Hard boundary — methods are value-free.** A method *sequences moves that invoke* values; it never *encodes* a value. "model the resource-exchange" is a step; "be truthful" is **not** — that belongs to `_judgment` and the critic. A method that smuggles in values steals the alignment core's job and muddies it. The critic stays sovereign over output; the method only scaffolds the path.

**Soft, not a workflow.** The DAG declares dependency-*shape* (`after:`), never execution *order*. The executor (you, an agent) reads it as a structured reference and may skip, reorder, or replace steps — same as "rules are the floor, judgment decides." A method that hardens into a rigid pipeline is a bug.

**Template ≠ instance (opposite update semantics).** A method *evolves* ("using is modifying" — its `## Memory` accrues). A `05 Decisions/` record is an *immutable* instance (supersede, don't retro-edit). Never merge the two surfaces; a decision-method's **deliverable is a 05 Decisions record**, but the method and the record live apart.

## Format

One file per method, `09 Rules/_methods/m-<slug>.md`, from `07 Templates/method.md`. Semantic-slug naming, sibling to the `v-`/`f-`/`s-` judgment nodes (atemporal concept — see [[09 Rules/file-types.md]] naming criterion). Flat frontmatter (simple-parser-friendly — no nested YAML):

| field | values | notes |
|---|---|---|
| `type` | `method` | required; scanners filter on this |
| `id` | `m-<slug>` | required; semantic kebab slug = filename stem, self-describing |
| `name` | 2–6 words | display |
| `task-kind` | `domain/shape/...` | what kind of task this templates |
| `status` | `draft` / `validated` | draft until a run proves it; promotion is human-gated |
| `deliverable` | one line | what a run produces (e.g. "a 05 Decisions/ record") |
| `calls-skills` | `[a, b, c]` | the moves it composes — must be real skills/commands |
| `grounds-in` | `[v-*, f-*]` | judgment nodes the steps invoke (not encode) |
| `precipitated-from` | free text | the instances it was distilled from |

Body: a `## Steps (DAG)` section, then one `### <slug>` per step with an `**after:** dep1, dep2` line (`—` = root/entry), plus optional `**calls:** / **reads:** / **writes:**` and prose contract. Then `## Memory` — append-only, cross-run learnings, cited to instances.

## Lifecycle (generated **and** consumed — or it rots)

The `wire-decisions-crm-into-loop` lesson (2026-06-05): *manual feeders rot.* A method must be both:

1. **Generated** — *precipitated* from instances, not hand-authored from nothing. Strip instance detail by subtraction ("condense the cleaned draft", not "condense the Redis post"); the concrete outputs stay as the instance, the shape becomes the method. Faithfulness check: a second cold pass confirms every step is real and nothing was invented (the discovery-pass / adjudicator reflex).
2. **Consumed** — `/operate` matches a task-kind → retrieves the method skeleton → structure-reuse + content-regeneration. If nothing reads it, don't build it.

**Decision-methods *can* close a review loop — but the apex auto-edge is NOT yet wired (be honest about this).** A run drops a `05 Decisions/` record stamped `method: m-<slug>`; `.claude/_eval-fixtures/method_review_feed.py` surfaces method-linked decisions and flags the review-due ones. Folding a reviewed outcome into the producing method's `## Memory` is a **human-gated write**. `reflect.py` harvests the decision's rationale/consequences into the *reflection* feeder, but does **NOT** currently route to a method's `## Memory` — that auto-fold is a future wire, not a present fact. The instance store, the surfacing feeder, and the review trigger exist; the automatic fold does not.

## Modularity (Hard Rules apply — [[09 Rules/harness-modularity.md]])

- **Register or it doesn't exist.** This doc + the methods surface are declared in `harness-manifest.json` (`docs`). `harness_map.py` scans `09 Rules/_methods/` and renders a Methods section.
- **One-line-contract test.** A method is usable from its registry row: `id · name · task-kind · deliverable`.
- **Earns its page by absorbing, not adding.** Methods take the multi-step composition currently smeared across flat judgment rules (e.g. a forwardable-report rule that's really a DAG) and skill prose. If relocating doesn't simplify the rule, the method isn't needed — cut it.
- **No executor.** The harness already executes (the agent, `/operate`). A method is the template artifact only; never build a `runs/` state machine.

## Gate

```bash
PY="$(python .harness/resolve_runtime.py python)"
"$PY" .claude/_eval-fixtures/method_lint.py        # DAG valid, deps resolve, contract complete
"$PY" .claude/routines/harness_map.py              # render the Methods section into HARNESS-MAP
```
