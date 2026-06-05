---
layer: instance
type: structure-principle
id: s-collision-free-numbering
name: Collision-free ordering prefixes
status: draft
applies-to: [folders, vault-organization, new-project, reorg-proposal]
created: 2026-05-29
created-by: claude (Phase 0 structure-loop seed)
source: observed (2026-05-29 structural audit)
---

# Structure Principle · Collision-free numbering

**Principle:** Sibling folders must have unique ordering prefixes. A reused number (two `01`, two `09`) breaks sort order and signals a folder bolted on without reconciling the scheme.

**Why it's taste:** {{PROJECT_A}} had two `01` (`01 Pitches` + `01 工作进展`); {{ORG_B}} two `09` (`09 Iteration Logs` + `09 Reports`) — additions made without renumbering. Each collision is a small lie about ordering that compounds.

**Tells when honored:** each numeric prefix appears once per directory; a new folder renumbers or takes the next free index.
**Tells when violated:** duplicate prefixes; `09 Reports` dropped next to `09 Iteration Logs`.

**Operationalized by:** `structure_graph.py` (numbering-collision detection); future vault-manager renumber proposals (human-gated, with link repair).
**Born-from:** 2026-05-29 structural audit.
