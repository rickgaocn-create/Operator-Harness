---
type: method
id: m-<slug>
name:
task-kind:
status: draft
deliverable:
calls-skills: []
grounds-in: []
precipitated-from:
created: <% tp.date.now("YYYY-MM-DD") %>
created-by:
---

# <% tp.file.title %>

## Method
<!-- One paragraph: what KIND of task this templates, and the deliverable a run produces.
     Value-free — sequence the moves; do NOT encode values (those live in grounds-in / the critic). -->

## Steps (DAG)
<!-- One ### <slug> per step. slug = ^[a-z][a-z0-9_]{0,62}$. `after:` lists upstream slugs (— = root).
     Declares dependency SHAPE, not execution order — the executor may deviate. -->

### first_step
**after:** —
**calls:**
**reads:**
**writes:**

Contract prose: what this step's cognitive move is, addressed to whoever runs it.

### next_step
**after:** first_step
**calls:**

Contract prose.

## Memory
<!-- Append-only, newest-first. Cross-run learnings, cited to the instances that taught them.
     This is the template-level learning surface; a decision-method also feeds from 05 Decisions review_on. -->
-

<!--
FIELD NOTES
  id            m-<slug> — six digits, collision-free (next free under 09 Rules/_methods/)
  status        draft until a run proves it; promotion to validated is human-gated
  calls-skills  the real skills/commands this composes (the moves)
  grounds-in    v-* / f-* judgment nodes the steps INVOKE — never encode a value in a step
  precipitated-from  the instances this was distilled from (a completed run, a class of records)
  Lifecycle     generated (precipitated) AND consumed (/operate) or it rots — see 09 Rules/methods.md
-->
