---
layer: platform
type: rule
scope: operator-intent-layer
created: 2026-05-27
created-by: codex
canonical_skill: ".claude/skills/operate/SKILL.md"
---

# Operator Intents

This contract is the future-model exoskeleton above the current skill layer. Existing skills remain callable; `/operate` maps {{USER_NAME}}'s natural work intents to those skills while preserving gates, provenance, and confidentiality.

## Design Principle

Keep the skills. Hide the ceremony. Stronger models may need less procedure, but they still need clean state, source truth, permissions, and eval gates.

## Default Interface

{{USER_NAME}}'s normal operating surface is **Harness Dashboard + `/operate`**. Direct slash skills remain available for maintenance, recovery, and expert use, but user-facing guidance should teach intents first and command names second.

## Cockpit Roles

| Surface | Role | Rule |
|---|---|---|
| `/operate` | Conversational cockpit | {{USER_NAME}} can state intent naturally; the wrapper routes to existing skills and gates. |
| Harness Dashboard | Visual cockpit | {{USER_NAME}} scans today, tasks, captures, health, automation, judgment, and tokens without opening system files. |
| Daily note | Machine ledger / backing store | Records Top 3, Day Planner, Quick Capture, ingests, and EOD in parser-stable sections. It powers the dashboard and `/operate`; it is no longer the primary human UI. |

When these disagree, prefer live task/status state for action, daily note for day narrative, and generated health/status surfaces for machine liveness.

## Reasoning Budget

Use heavier reasoning on planning and verification, then keep execution simple once the plan is locked. If implementation starts looping, pause, test, or step back before another edit.

## Lifecycle Buckets

| Bucket | Meaning | Current examples |
|---|---|---|
| Keep | Durable spine; do not collapse into the wrapper | `/operate`, `/day-ops`, `/capture-routing`, `/forwardable-quality`, `/machine-health`, `/daily-note`, `/task-capture`, `/source-ingest`, `/status`, `/sanity`, `/skill-eval`, `/attribution-lint` |
| Wrap | Useful workflow, but {{USER_NAME}} should not need to remember the skill name | `/meeting-note`, `/periodic-report`, `/to-internal-briefing`, `/interactive-report`, `/wangyue-pitch-deck`, `/sync-day`, `/replan`, `/inbox-process`, `/day-digest` |
| Distill | Procedure-heavy; extract contract/eval before shortening | `/best-of-n`, `/biz`, `/localize-cn`, `/pragmatic`, `/humanize`, `/meeting-summary` |
| Archive candidate | Low direct use only after evidence | Any skill with 30+ days low use, wrapper coverage, green evals, no routing misses, and rollback snapshot |

## Intent Contracts

### 1. What matters today?

**Allowed skills:** `/day-ops` first; `/status`, `/daily-note`, `/sync-day`, `/replan`, and `/inbox-process` remain downstream or expert-use skills in read-first mode.

**Output shape:** top priorities, why they matter, stale/blocked items, and the next concrete move. Prefer Top 3 unless {{USER_NAME}} asks for a full sweep. Treat the Dashboard Today/Actionable panels and today's daily note as the same cockpit state: dashboard for display, daily note as backing ledger.

**Hard gates:**
- Do not fabricate priorities when live state is missing.
- Do not write tasks or daily-note changes unless explicitly requested.
- If daily/OKR/task surfaces disagree, say which source is newer and where the conflict sits.
- Do not force {{USER_NAME}} back into the daily note unless he is editing or closing the ledger.
- Prefer dashboard summaries over daily-note internals; the daily note may carry long structured ingest logs.

**Confidential lanes:** confidential personal tracks may be surfaced to {{USER_NAME}} privately, but never mixed into audience-facing {{PROJECT_A}} / 3rd outputs.

### 2. Process this

**Allowed skills:** `/capture-routing` first; `/meeting-note`, `/meeting-note-spec`, `/source-ingest`, `/task-capture`, and `/distill` remain downstream or expert-use skills.

**Routing:**
- Transcript or meeting-like input -> meeting workflow.
- Article, clipping, external source -> source ingest.
- Follow-ups or commitments -> task capture.
- Personal brain dump -> distill.

**Hard gates:**
- Ambiguous input asks before writing.
- More than 3 new tasks follows task-capture batch discipline.
- Never auto-create Action files; propose and wait.
- Preserve source text and attribution boundaries.
- Dashboard captures marked ready should be consumed by `/capture-process`; `/operate` may summarize the queue but should not duplicate the consumer.

**Confidential lanes:** detect if the content touches {{FUND}} Lane B or other isolated tracks before routing into shared project surfaces.

### 3. Make this forwardable

**Allowed skills:** `/forwardable-quality` first; `/best-of-n`, `/biz`, `/attribution-lint`, `/localize-cn`, `/pragmatic`, `/humanize`, and `/interactive-report` remain downstream or expert-use skills.

**Output shape:** 概要, decision/use case, evidence, risks, next actions, and audience-fit polish.

**Hard gates:**
- Major forwardable artifacts use `/best-of-n` unless explicitly skipped.
- Counterparty claims need source anchors or must be labeled as our judgment.
- CN-audience work artifacts must pass CN residue rules.
- Project-internal briefings use pragmatic style only when the reader/context fits.
- Do not mix confidential lanes or system diagnostics into business artifacts.

**Confidential lanes:** if audience, channel, or lane is unclear, ask before finalizing.

### 4. Think with me

**Allowed skills/agents:** `strategist`, `vault-researcher`, `/biz` for artifact-shaped business analysis.

**Output shape:** options, tradeoffs, pre-mortem, recommendation, and next move. Keep it decision-oriented.

**Hard gates:**
- Named entities require vault-first recall before confident claims.
- Default to no file writes.
- Do not turn brainstorming into task capture unless {{USER_NAME}} asks.

**Confidential lanes:** keep personal-career and business-lane reasoning isolated unless {{USER_NAME}} explicitly asks for cross-lane synthesis.

### 5. Check the machine

**Allowed skills:** `/machine-health` first; `/status`, `/harness-health`, `/sanity`, `/skill-eval`, and `/rearm` remain downstream or expert-use skills. Use `/rearm` only when a specific organ is identified.

**Output shape:** green/yellow/red verdict, active findings {{USER_NAME}} needs to care about, likely cause, and next action. Suppress implementation noise unless the finding requires maintenance.

**Hard gates:**
- Read-only by default.
- Do not rearm, edit, or regenerate unless requested.
- Distinguish "configured" from "live path verified."
- Map/eval/lint failures are blockers for harness changes, not cosmetic warnings.
- Dashboard Monitor panels are the visual source of this state; `/operate` should explain what matters, not restate every tile.

**Confidential lanes:** health reports can mention lane labels but should not expose sensitive content unless {{USER_NAME}} asks.

## Model-Upgrade Ratchet

When a stronger model becomes available, run shadow comparisons for major workflows:

| Path | Meaning |
|---|---|
| Full skill flow | Current procedure-heavy skill chain |
| Contract-only flow | `/operate` + this rule + existing state/gates |

A skill can be shortened only after repeated contract-only passes against relevant graders. Pruning requires: 30+ days low direct use, wrapper coverage, green evals, no unresolved routing misses, and rollback snapshot.

## Non-Goals

- Do not delete existing skills in v1.
- Do not make `/operate` a silent dispatcher for risky writes.
- Do not weaken attribution, confidentiality, CN residue, or task-capture gates for the sake of convenience.
