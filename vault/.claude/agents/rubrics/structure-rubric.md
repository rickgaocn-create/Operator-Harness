---
type: rubric
applies-to: reorg proposals (folder create/rename/merge/split/delete, file moves)
grader: structure-critic
producer: vault-manager (PROPOSE phase), structure_graph.py findings
max-iterations: 3
---

# Structure Reorg Rubric (binary checks)

> The grader reads ONLY the proposed reorg diff + the structure-graph + the `s-*` taste nodes — never executes anything. Each check returns PASS / FAIL with the offending item. Verdict = APPROVE if all hard checks PASS; REVISE otherwise. **A reorg never auto-applies — APPROVE means "ready to show {{USER_NAME}} for confirm," not "execute."**

## Hard checks (any FAIL = proposal blocked)

| # | Check | Pass criterion | Fail signal |
|---|---|---|---|
| H1 | **Blast radius quantified** | Every move/rename/delete states its inbound-link count and a link-repair plan (rewrite targets) or "0 inbound links" | A mutation with unknown/unstated inbound links |
| H2 | **No content destroyed unrelocated** | Any deleted/merged file with unique content names where that content goes (archive, port, or "confirmed redundant with X") | A delete of a file whose content isn't a verified duplicate (the 08 Agents mirror trap: looked like a dup, was +100 lines) |
| H3 | **Reversible** | Vault is git-backed OR the diff archives originals under `_archive/`; no hard, unrecoverable delete | `rm` of unique content with no recovery path |
| H4 | **Reduces measured drift** | Predicted post-reorg `structure_graph.py` finding count < current; names which findings clear | A move that leaves drift flat or creates new collisions/orphans |
| H5 | **Respects structure taste** | Aligns with [[s-organic-over-template]] · [[s-collision-free-numbering]] · [[s-co-locate-by-workstream]] · [[s-no-stale-snapshots]] | Imposes a fresh empty template; restores a hand-maintained folder map; scatters a workstream |
| H6 | **Human-gated** | The proposal executes only on explicit per-item confirm; no auto-apply, no "I'll just do it" | Any step that mutates before confirm |

## Soft checks (≥2 → REVISE)

| # | Check | Fail signal |
|---|---|---|
| S1 | **Minimal** | Reorg touches more than the drift requires (scope creep) |
| S2 | **Stable anchors** | Renames a `chain-anchor`-bearing folder without preserving the anchor join |
| S3 | **One reason per move** | A move bundles unrelated rationales — split it |

## Output schema (grader returns this)

```yaml
verdict: APPROVE | REVISE
items:
  - action: delete | rename | merge | move | rewrite
    target: <path>
    inbound_links: <int>
    repair: <plan or "none needed">
    clears: [<structure-graph finding ids>]
    checks: {H1: PASS, H2: PASS, ...}
next_action: present-for-confirm | revise | escalate
```
