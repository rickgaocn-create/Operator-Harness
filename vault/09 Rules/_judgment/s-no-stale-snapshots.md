---
layer: instance
type: structure-principle
id: s-no-stale-snapshots
name: Never hand-maintain a structure snapshot
status: draft
applies-to: [folders, docs, project-claude-md, reorg-proposal]
created: 2026-05-29
created-by: claude (Phase 0 structure-loop seed)
source: observed (2026-05-29 structural audit)
---

# Structure Principle · No hand-maintained structure snapshots

**Principle:** Never hand-maintain a description of structure (a "Folder Structure" block, a folder map) inside a doc. Generate it from the live tree, or omit it and point at the generated graph. Hand-maintained maps drift and become actively misleading.

**Why it's taste:** project CLAUDE.md files hand-maintained folder maps that described **non-existent** folders and contradicted the live tree — a map of a building never built. This is the same failure the harness already learned at the meta layer ([[09 Rules/harness-modularity]]: "generated content is off-limits to hand-editing; new docs are the failure mode"); structure is just the content-tree instance of it.

**Tells when honored:** structure is read from `structure-graph.json`; docs reference it, never restate it.
**Tells when violated:** a `## Folder Structure` block a human edits; a doc claiming folders that don't exist.

**Operationalized by:** `structure_graph.py` (stale-snapshot + template-drift findings); mirror of [[09 Rules/harness-modularity]] Rule 4.
**Born-from:** 2026-05-29 audit (project CLAUDE.md folder maps) — see [[s-organic-over-template]].
