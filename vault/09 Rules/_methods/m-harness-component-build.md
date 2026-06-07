---
type: method
id: m-harness-component-build
name: Harness component build
task-kind: harness/build/extend
status: draft
deliverable: a registered, validated, cross-platform harness component wired into a reader, reported with executed proof
calls-skills: [harness-evolve, harness-health, sanity, skill-eval]
grounds-in: [f-strategic-systems, f-rigor-verification, f-value-mechanism]
precipitated-from: this session's builds (distill_autotrigger, skill_mirror_sync, lark-cli fix, the method layer) + 09 Rules/harness-modularity.md + portability ratchet
created: 2026-06-06
created-by: claude
---

# Harness component build

## Method
Templates **adding or extending a harness component** (routine / hook / validator / scan / layer). Value-free: the steps invoke strategic-systems and verification judgment ([[f-strategic-systems]], [[f-rigor-verification]], [[f-value-mechanism]]) and the modularity/portability contracts; the design call is the operator's. A run produces a registered, validated component — not a report or a decision.

## Steps (DAG)

### scope_seam
**after:** —
**calls:** sanity, harness-health
**reads:** the live pipeline + harness-manifest.json + the relevant 09 Rules contract
Map what already fires and read the seam the component plugs into. Prefer to *consolidate / reuse an existing surface* over adding one (the one-page budget gate). A check with no paired sync is a nag, not a loop — build the missing half.

### write_component
**after:** scope_seam
**calls:** harness-evolve
**writes:** the component (script / edit)
Cross-platform Python, **discovered paths** (`from _common import VAULT`) — never a `.ps1`, never a hardcoded `D:\` / `python.exe`. Heavy cognition goes **off the interactive path** (batch); read-only diagnostics never write vault content and never fail a tool call.

### register_manifest
**after:** write_component
**writes:** harness-manifest.json row
**Register or it doesn't exist** (Hard Rule 1): add the `organs`/`state`/`docs` row in the *same* change. The component must be usable from its one-line registry row alone.

### wire_consumer
**after:** write_component
Wire it into a reader — a `harness_map` scan, a pulse check, a hook, `/operate`. **Generated AND consumed, or it rots** (the manual-feeder lesson). Shipping a producer with no consumer builds an inert surface.

### validate
**after:** register_manifest, wire_consumer
**calls:** skill-eval, sanity
Run the paired gate yourself: `py_compile` → the component's lint → `portability.py` → `harness_map.py --check` must stay clean (new draft items are *backlog*, not drift). Validate end-to-end; don't defer proof to the operator.

### report
**after:** validate
Report **executed proof**, not a done-claim. Stage the change reversible/tested/no-live-risk and say what was checked — that's what earns the next autonomy increment.

## Memory
- 2026-06-06 — **A check with no paired sync is a nag.** `skill-mirror-parity.py` detected drift but nothing synced it → built `skill_mirror_sync.py`; the methods spec shipped with `method_lint.py` paired. Always build the closing half.
- 2026-06-06 — **Generated AND consumed.** Armed `distill_autotrigger` *into the pulse* (not a lone routine) and wired `scan_methods` *into the map* — so each new surface is read, not inert (the `wire-decisions` lesson applied).
- 2026-06-06 — **Earn the page by absorbing.** The method layer was justified only because it absorbed composition that lived nowhere (flat rules + skill prose), not by adding an orphan surface. If relocating doesn't simplify, cut it.
- 2026-06-06 — **Resolve, don't assume PATH.** A bare `lark-cli` call broke under a scheduled-task PATH; resolve the absolute launcher (env → which → known location) the way `_resolve_system_bin` already did for wmic/powershell.
