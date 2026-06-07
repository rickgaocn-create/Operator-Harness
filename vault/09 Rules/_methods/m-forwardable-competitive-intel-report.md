---
type: method
id: m-forwardable-competitive-intel-report
name: Forwardable competitive-intel report
task-kind: report/competitive-intel/sentiment
status: draft
deliverable: a standalone, forwardable competitive-intel / sentiment report (tables, both poles, competitor baseline, full source traceability)
calls-skills: [source-ingest, forwardable-quality, interactive-report, localize-cn]
grounds-in: [f-rigor-verification, f-value-mechanism, v-truth-over-comfort]
precipitated-from: the 2026-06-03 competitive-intel/sentiment report run (corrections.jsonl — standalone+polished, both-poles, tabular, methodology-positive "GREAT JOB") + dp-002
created: 2026-06-06
created-by: claude
---

# Forwardable competitive-intel report

## Method
Templates a **team/leadership-facing competitive-intel or 舆情/sentiment report** — the deliverable leaves our hands, so the bar is *standalone + polished, ready to forward as-is*. Value-free: the steps invoke verification rigor and value-mechanism judgment ([[f-rigor-verification]], [[f-value-mechanism]], [[v-truth-over-comfort]]); the analytical calls are the operator's. A run produces a report artifact, not a decision.

## Steps (DAG)

### pull_live
**after:** —
**calls:** source-ingest
**writes:** raw source set (timestamped)
Re-pull the live sources **at generation time** — never from in-context memory of an earlier state. A forwardable artifact freezes whatever it's built from; stale-in → error-out to an external audience.

### classify_quantify
**after:** pull_live
**writes:** classified/scored set
Quantify via **classification at scale**, not cherry-picked quotes. Report share-of-voice / proportions, not anecdotes. Never fabricate a blocked metric — surface the blocker + an unblock path instead.

### competitor_baseline
**after:** pull_live
**writes:** competitor comparison set
Pull a competitor baseline; never report own-IP signal in isolation — a number only means something against a benchmark.

### ground_own_ip
**after:** pull_live
Anchor own-IP positioning in **vault design truth** (00 Raw + Cards/Wiki), not secondhand web framing. Verify any web claim about our own IP against the KB before use.

### both_poles
**after:** classify_quantify
Structure **both 正向 and 负向/风险** with equal quantified rigor (share + representative quotes). A risks-only read misframes a net-positive reception as a problem and hides what's working.

### synthesize
**after:** both_poles, competitor_baseline, ground_own_ip
**writes:** report body
Default multi-attribute / comparative / point-evidence content to **tables** (one row per item; columns = dimension / quant / quote / takeaway). Keep formatting parity across the artifact — don't mix prose-bullets and tables for parallel content. Keep full source traceability.

### polish_forward
**after:** synthesize
**calls:** forwardable-quality, localize-cn
**writes:** the forwardable deliverable
Rewrite any "compared to X" framing into self-contained statements (standalone). Run an explicit formatting pass + a language pass (tighten + professionalize). State method + caveats inside the artifact. Bar = *ready to forward as-is*. CN audience → localize-cn.

## Memory
- 2026-06-03 — **Both poles, equal rigor.** {{USER_NAME}} flagged a report "lacks 正向舆情分析"; a risks-only read of a net-positive signal misframes it and hides the吸量 base. Capture both poles — mirrors the corrections loop's own principle.
- 2026-06-03 — **Tables for parallel data.** Prose+bullets for multi-attribute/comparative content reads as lower-effort and breaks visual parity; default to a table.
- 2026-06-03 — **Standalone + polished is the done bar.** A deliverable that reads as "vs the other report" or carries draft-grade formatting isn't forwardable — leadership see it raw. (positive: "GREAT JOB" on the full methodology.)
- 2026-06-02 — **Re-pull at generation time.** Freshness is verified when you generate, not assumed from earlier context.
