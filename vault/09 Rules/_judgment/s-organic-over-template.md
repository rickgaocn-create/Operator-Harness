---
layer: instance
type: structure-principle
id: s-organic-over-template
name: Organic structure over imposed template
status: draft
applies-to: [folders, vault-organization, reorg-proposal, new-project]
created: 2026-05-29
created-by: claude (Phase 0 structure-loop seed)
source: observed (2026-05-29 structural audit)
---

# Structure Principle · Organic over template

**Principle:** Let folder structure emerge from where work actually accumulates; prune imposed templates that don't match reality. A designed pipeline whose stages stay empty is debt, not scaffolding.

**Why it's taste, not just a rule:** the {{PROJECT_A}} `Prospect→Negotiate→Deliver` funnel and the {{ORG_B}} `Sourcing→Board→Close` funnel were imposed top-down. {{PROJECT_A}} instead grew organic (`01 工作进展` / `04 会议纪要` / `09 Reports`) and the funnel folders went empty (`00 Prospects` / `02 Negotiations` / `04 Delivery` = 0 files); {{ORG_B}} carries **8 empty funnel dirs**. Real structure beat the template every time.

**Tells when honored:** structure mirrors where files land; empty scaffolding is pruned, not kept "for later."
**Tells when violated:** a documented pipeline with empty stages; months-old "we'll fill it" dirs.

**Operationalized by:** `structure_graph.py` (orphan + template-drift detection); future vault-manager reorg proposals.
**Born-from:** 2026-05-29 structural audit — see [[s-no-stale-snapshots]], [[s-co-locate-by-workstream]].
