---
layer: platform
type: rule
scope: harness-autonomy
created: 2026-05-29
created-by: claude
companion-rules:
  - "[[09 Rules/autonomous-routines.md]]"
  - "[[.claude/agents/rubrics/structure-rubric.md]]"
---

# Autonomy Tiers

> **Why this exists.** Treating *every* action as confirm-gated makes the operator the bottleneck on low-value, reversible work — overhead that reads as "performative busyness" (a hard line in [[me.md]]). This tiers actions so Claude **acts** on the safe/reversible and **asks** only where it matters. Lowers {{USER_NAME}}'s confirm-frequency without lowering safety.

## The tiers

| Tier | Action class | Posture |
|---|---|---|
| **A — act + log** | Read-only diagnostics; rebuilds of regenerable derived state (`structure-graph.json`, underlays, `HARNESS-MAP`, pulse verdict); idempotent zero-blast cleanups (dedup a pending signal, refresh a cache, prune a verified-empty dir with 0 inbound links); **drafting** to a review surface (`_inbox/`, `_pending/`, a proposal file). | **Do it, log it, mention it.** No confirm. {{USER_NAME}} can review/undo from the log. |
| **B — propose → confirm** | Any write to vault *content* (Cards / Actions / Tasks / project artifacts / Wiki); file move/rename/delete with ≥1 inbound link; foundational-file or rule/skill edits; promotions (correction → rule, instinct → Card); anything that changes a gate. | **Propose the diff + blast radius; execute per-item on confirm.** (The `structure-critic` H6 / NEVER-auto-create discipline.) |
| **C — never auto (and hold even on an in-the-moment ask that crosses it)** | Outward-facing sends (channel messages, emails, commits, pushes); confidential-lane crossings; completion/"done" claims without executed proof; fabricated stamps/quotes; >3 tasks per write. | **Always human.** If a request crosses a red line, flag + offer options + wait ([[MEMORY]] hard rules). |

## Operating rule

- **Default a NEW action to the *most cautious* plausible tier**, then justify moving it down. Unsure between A and B → treat as B.
- **Reversibility is the hinge.** Git-backed + zero-content-loss + zero/repaired inbound links → eligible for A. Any unique-content loss or unrepaired link → B (the 08-Agents-mirror lesson: looked like a dup, carried +100 unique lines).
- **Tier A still leaves a trail.** Acting without confirm ≠ acting silently — log to the relevant surface (autofix log, proposal file, or a one-line mention) so the operator can audit and revert.
- **Batch B/C decisions** rather than dripping them per session (see the weekly review cadence; the SessionStart brief surfaces the count, not each item).

## Verified-autonomous promotion (governed exception — [[09 Rules/promotion-loop.md]])

The blanket "promotions are Tier B" rule has **one governed exception**: a `distilled → promoted` step that passes the **dual-verifier gate** (recurrence-clean ∧ jury-pass) may auto-confirm as **Tier A** — two independent verifiers stand in for the human's per-item confirm. The intermediate `distilled → provisional` (a *soft, advisory, reversible* rule on probation) is Tier A; `provisional → promoted` is Tier A **only through the gate**, else Tier B. Auto-**revert** of a failed provisional is always Tier A (fail-safe). Hard-rule / `MEMORY.md` / gate escalation stays B/C. The human audits promotions in a **weekly batch**, not per-item. Mechanism + safety: [[09 Rules/promotion-loop.md]].

## What this is NOT

- Not a license to auto-mutate content (that stays B).
- Not a replacement for the hard rules (C is absolute).
- Not a new enforcement organ — it's a posture the existing agents (vault-manager, the graders) and skills apply. Register no new state; this rule *is* the contract.
