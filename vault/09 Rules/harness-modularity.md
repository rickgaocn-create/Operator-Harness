---
layer: platform
type: rule
scope: harness-structure
created: 2026-05-27
created-by: claude
companion-rules: "[[09 Rules/harness-instrumentation]]"
generator: ".claude/routines/harness_map.py"
---

# Harness Modularity Rules

> **Why this exists.** The harness's conceptual surface area was growing faster than its navigational structure: every feature shipped a concept + a state file + a doc, but the spine (`harness-manifest.json`) only grew on the *liveness* axis. The one-page comprehension test ([[04 Notes/_system/(C) harness-map-2026-05-24]]) started failing. These rules keep the index ahead of the inventory — so you never have to hold the whole thing in your head, and a teammate can onboard from the front-door instead of spelunking.
>
> Companion to [[09 Rules/harness-instrumentation]] (the *data-layer* contract); this is the *structure-layer* contract.

## The spine

`.claude/_state/harness-manifest.json` is the single registry of what the harness contains. It has four arrays:

| Array | Registers | Read by |
|---|---|---|
| `organs` | things that *fire* (routine / signal / bridge / hook / grader) | `harness_status.py` (`/status`) |
| `state` | durable state files — the writer/reader/purpose **contract** of each | `harness_map.py` |
| `docs` | orientation docs + their scope + load posture | `harness_map.py` |
| `glossary` | (in [[09 Rules/glossary]], not the manifest) coined terms | humans + onboarding |

`.claude/routines/harness_map.py` scans the live filesystem (skills, agents, judgment nodes, `_state/`) and renders [[HARNESS-MAP]] — the **generated** front-door — between AUTO markers. The map is generated, never hand-maintained, so it cannot drift the way a snapshot doc does.

## Hard Rules

1. **Register or it doesn't exist.** Adding a new organ, durable state file, orientation doc, or coined term? Add its row to the manifest (`organs` / `state` / `docs`) or to [[09 Rules/glossary]] **in the same change**. `harness_map.py --check` flags anything present-but-undeclared as drift; an undeclared component is a comprehension debt, not a feature.

2. **The one-line-contract test (information hiding).** Every component must be *usable from its registry row alone* — id + one-line job + (for state) writer/reader/purpose. If you have to read a component's internals to know how to use it, the interface is leaking: fix the row, don't make the next reader spelunk.

3. **One-page budget gate.** The generated front-door's inventory must fit one screen. When it overflows, the correct move is to **consolidate a module** (merge two overlapping loops, fold a state file into another, retire a stale skill) — **not** to add another orientation doc. New docs are the failure mode, not the fix. Run `harness_map.py` and look: if the map no longer fits, you have a consolidation to do.

4. **Generated content is off-limits to hand-editing.** Anything between `<!-- BEGIN AUTO-MAP -->` and `<!-- END AUTO-MAP -->` is overwritten on every run. Curated content (the manifest rows, the glossary, the Layer model) is where humans edit; the rendered map is downstream.

5. **Drift is a standing surface, not an alarm.** `harness_map.py --check` exits non-zero on drift by design. Some drift is a deliberate backlog (e.g. judgment nodes legitimately sitting at `status: draft` until validated) — that's fine; the point is it's *visible and counted*, not silent. `/vault-evolve` consumes the count for chronic patterns.

## When building any new harness component

- Cross-platform Python with discovered paths (`from _common import VAULT`), never a new `.ps1` and never a hardcoded `D:\` / `python.exe` path (correction 2026-05-26: OS-portability and onboarding are the same problem).
- Heavy model cognition goes **off the interactive path** (batch); the runtime pays only for a small core + relevant retrieval + scripted gates (`f-value-mechanism` — token-cost-per-value).
- Read-only diagnostics never write vault content; instrumentation never fails a tool call ([[09 Rules/harness-instrumentation]] Hard Rule 1).
- Add the manifest row (Rule 1), then run `harness_map.py` to confirm the front-door absorbed it with no new drift.

## Regenerate

```bash
PY="$(python .harness/resolve_runtime.py python)"
"$PY" .claude/routines/harness_map.py          # rewrite 04 Notes/HARNESS-MAP.md
"$PY" .claude/routines/harness_map.py --check  # gate: exit 1 if drift (for /sanity / vault-evolve)
"$PY" .claude/routines/harness_map.py --json   # machine-readable inventory + drift
"$PY" .claude/_eval-fixtures/portability.py    # ratchet: live runtime-control files stay path-agnostic
```
