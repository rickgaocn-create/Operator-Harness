---
category: meta
name: harness-evolve
description: "L2 apply/QA loop for the harness fix backlog: diagnose fresh, verify with a full-pipeline subagent, gate on coherence and operational overhead, apply bounded tiered fixes, validate and repeat. Trigger on /harness-evolve, close the apply gap, run the L2 loop, or adjudicate the evolve backlog."
model: claude-opus-4-8
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
companion-rules: "[[09 Rules/autonomous-routines.md]]"
sibling-of: "[[.claude/skills/vault-evolve/SKILL.md]]"
last-major-rewrite: 2026-06-03
---

# Skill: Harness Evolve — the L2 apply/QA loop (`/harness-evolve`)

`vault-evolve` is L1: it **diagnoses** the harness every morning and dumps fixes into a 🟡 queue that no one drains. `harness-evolve` is L2: it **closes the apply gap** — it consumes that backlog (and fresh findings), verifies each one adversarially, gates it on whether the fix actually *helps*, applies only what survives within a bounded budget, then QAs the result and repeats. It is the governance/control loop for the earned-autonomy engine (`adjudicator` / `evolution_engine`), in the `harness-*` family alongside `harness-pulse` (reflex) and `harness-health` (read-only dashboard).

> **First principle:** this loop's job is *subtraction under verification*. It exists to drain backlogs and remove contradictions — never to add a surface. A cycle that applies nothing because review refuted the finding is a **success**, not a stall. The difference from L1's rationalized "0-🟢 as designed" is that L2 must *show its refutations* (stage 2 proof), not assert them.

---

## The cycle (one subsystem per run, bounded)

```
1 DIAGNOSE   Fresh-context pass over ONE subsystem. Re-derive findings from live
             files — no anchoring on prior reports. Inputs: vault-evolve 🟡 backlog
             (04 Notes/vault-evolve/_decisions.md carry items) + harness-pulse
             findings + on-demand target. Emit: findings, each with a hypothesis,
             proof-to-seek, and a candidate fix.

2 REVIEW     Spawn an independent full-pipeline subagent (Agent tool). It runs the
             subsystem's ACTUAL pipeline read-only / dry-run and returns, per finding:
             CONFIRMED · REFUTED · PARTIAL  + file:line / command-output proof.
             Drop every finding not CONFIRMED before any edit. (This stage is what
             stops L1's diagnose-without-verify from shipping false positives.)

3 GATE       For each surviving fix, score two deltas and decide:
               • coherence Δ  — fewer contradictions / surfaces / sources-of-truth? (+ / 0 / −)
               • overhead  Δ  — net change in lines · files · tasks · tokens · steps
             REJECT if overhead Δ > 0 UNLESS coherence Δ is large AND named.
             Prefer subtraction. "A 6th dashboard to watch the 5 dashboards" → auto-fail.
             A sanctioned-but-overhead-neutral chore (e.g. re-sync a redundant mirror)
             that perpetuates a flagged redundancy → REJECT the chore, route the
             redundancy itself to 🟡.

4 FIX        Apply only gate-passed fixes, by tier (below). Anti-overcorrection budget:
               ≤3 changes / cycle · reversible-or-additive only · ONE layer per fix ·
               mtime-guard (skip files touched <5 min) · if the fix grew past the
               finding, TRIM it back to the finding.

5 QA         Re-run the stage-2 subagent (or the subsystem's lint/eval) against the
             POST-fix state. Confirm: finding resolved · no regression · overhead
             actually dropped.
               PASS → log + close the finding.
               FAIL / new finding → return to stage 1 for THAT delta only.
             EXIT when: finding resolved · OR 3 iterations reached · OR escalate flag.
```

Three invariants do the safety work: **one subsystem per cycle** (blast radius), **3-iteration cap** (no runaway), **net-non-positive overhead** (no bloat). Violate none.

---

## Apply tiers (authority for stage 4) — tier model chosen 2026-06-03

| Tier | What | Authority |
|---|---|---|
| 🟢 **Autonomous** | Gate-passed fixes that are **reversible** and **net-negative-or-neutral overhead**: dead-trigger repair, index/catalog updates, mirror sync *only when the mirror is endorsed*, advancing `distilled → promoted` on `positive` corrections, comment-out dead wikilinks, frontmatter completion | Apply in-cycle. Log to cycle ledger + `_decisions.md`. |
| 🟡 **Propose** | Anything touching `09 Rules/**`, subagent system prompts, skill body rewrites, auto-chain rules, MEMORY.md, **or any fix whose stage-3 score is "adds surface"** — including questioning whether a redundancy should exist at all | Write to the cycle report; user dispositions via `vault-manager: execute`. Never auto. |
| 🔴 **Manual** | Deletions (skills, subagents, tasks), edits to user-authored prose / `00 Raw/` / `06 Tasks/` / `.obsidian/`, `chain-anchor` renames, anything irreversible | Surface with explicit warning. No keyword applies. |

When a gate-passed fix straddles tiers, the **higher** tier governs. When in doubt → propose, not auto.

---

## Stage 2 — subagent contract

Spawn via the `Agent` tool (`general-purpose`, or a domain agent when one fits). The prompt MUST:
- Name the ONE subsystem and the findings to adjudicate.
- Order it to **run the subsystem's real pipeline read-only / dry-run**, not just read code.
- Demand per-finding `CONFIRMED / REFUTED / PARTIAL + file:line or command output`.
- Instruct it to **try to refute** each finding (adversarial default), and to say plainly when the diagnosis is wrong — a refutation is the most valuable result.
- Forbid all writes, `--sync`/mutating flags, channel sends, and `00 Raw/` access.

The subagent's verdict is binding for stage 3: only `CONFIRMED` findings may carry a fix forward.

## Stage 5 — QA contract

Re-run stage 2 (or the cheapest sufficient check: the subsystem's lint/eval/`bootstrap_lint --check`) on the post-fix state. A fix is **closed** only when QA confirms (a) the finding's proof no longer reproduces, (b) no new finding was introduced, and (c) the measured overhead moved the predicted direction. Any miss → re-open at stage 1, scoped to the delta, against the iteration cap.

---

## Modes

| Mode | Trigger | Behavior |
|---|---|---|
| **Interactive** | `/harness-evolve` | Run one cycle live; show stages 1–5; pause before any 🟡/🔴. |
| **Targeted** | `/harness-evolve <subsystem\|finding-id>` | Run the cycle on a named target (e.g. `M.E`, `feeders`, `learning-loop`). |
| **Autonomous** | `/harness-evolve --autonomous` (scheduled) | Drain the top gate-passable 🟢 fix from the backlog; defer all 🟡/🔴 to the report; never block. Respect the same caps. |

---

## Output — cycle ledger

Append one block per cycle to **`04 Notes/vault-evolve/_l2-log.md`** (sibling to L1's `_log.md`):

```markdown
## L2 cycle · YYYY-MM-DD HH:MM · subsystem: <name>
- Diagnosed:  <n findings>
- Reviewed:   CONFIRMED <a> · REFUTED <b> · PARTIAL <c>   (subagent: <id>)
- Gated:      passed <p> · rejected <r>  (reject reasons: …)
- Applied:    🟢 <x>  ·  Proposed 🟡 <y>  ·  Manual 🔴 <z>
- QA:         PASS <fixes> · re-opened <…> · iterations <i>/3
- Overhead Δ: <±lines/files/tasks>   Coherence Δ: <summary>
- Prevented over-corrections: <list — fixes the gate/review killed>
```

The "Prevented over-corrections" line is mandatory and load-bearing: it is the evidence that the loop is *gating*, not just *acting*.

---

## Hard rules

- **No fix without a CONFIRMED stage-2 verdict.** Refuted/partial findings never reach stage 4.
- **Overhead gate is binding.** A fix that adds net surface fails unless coherence Δ is large and explicitly named. Default to subtraction.
- **Budget caps are hard:** ≤3 changes/cycle · one subsystem/cycle · 3 iterations max.
- **Tier discipline + mtime guard** (per the apply-tier table; never auto-apply to files edited in the last 5 min).
- **QA is mandatory.** No finding closes without a post-fix verification that the proof no longer reproduces.
- **Never edit** `00 Raw/`, `06 Tasks/`, `.obsidian/`, user-authored prose, `chain-anchor` fields.
- **Show refutations.** Every cycle logs what review/gate killed — a silent "applied nothing" is forbidden; state *why*.
- **This loop polices itself.** Before adding any mechanism to this skill, run its own stage 3 on the change. If it adds surface without a named coherence gain, don't.

---

## Failure modes

| Symptom | Fix |
|---|---|
| Stage-2 subagent confirms everything (no refutations ever) | Prompt isn't adversarial enough — restore "try to refute / default to refuted when uncertain." |
| Cycle applies 0 fixes repeatedly with no refutations logged | Either the backlog is genuinely drained (good) or stage 1 isn't reading the carry items — check `_decisions.md` parse. |
| Overhead Δ always reported 0 | Stage 3 isn't measuring — require a concrete before/after count (lines/files/tasks), not a vibe. |
| Iteration cap hit without resolution | Escalate to human with the partial state; do not loop silently. |
| Fix applied but L1 re-proposes it next morning | QA didn't verify against L1's detector — re-run the exact L1 check in stage 5. |

---

## Lineage / why this exists

Per the 2026-06-03 evaluation: L1 (`vault-evolve`) diagnoses daily and accurately but has applied ~1 autonomous fix in 19 scheduled runs, because every substantive fix lands in a human-gated 🟡 queue that carries for weeks (M.E 13 days, correction backlog day 4). The harness had become "a very good doctor not allowed to write prescriptions." L2 is the prescription authority — made safe by independent review (stage 2), an anti-bloat gate (stage 3), bounded application (stage 4), and mandatory QA (stage 5). It complements:

- `vault-evolve` — L1 daily diagnosis; produces the backlog L2 drains.
- `harness-pulse` — real-time reflex; L2 consumes its chronic findings.
- `harness-health` — read-only dashboard; L2's stage 5 may reuse its checks.
- `adjudicator` / `evolution_engine` (earned-autonomy dev plan) — L2 is their control-loop spec.

The promise rests on the same three constraints that keep self-evolution from becoming self-mutation: **verified before applied · gated on net overhead · bounded + QA'd + reversible.**
