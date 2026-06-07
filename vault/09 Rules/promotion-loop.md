---
layer: platform
type: rule
scope: harness-autonomy
created: 2026-06-06
created-by: claude
companion-rules:
  - "[[09 Rules/autonomy-tiers.md]]"
  - "[[09 Rules/harness-modularity.md]]"
generator: ".claude/routines/promotion_engine.py"
state:
  - ".claude/_state/provisional-promotions.jsonl"
description: "Autonomous-but-verified promotion: move distilled->promoted at model speed via two independent verifiers (recurrence + jury), human audits the batch. The L4 loop's throughput unlock."
---

# Promotion loop — autonomous-but-verified

> **Why this exists.** The judgment learn-loop's `distilled → promoted` step for *corrective* items is human-gated per-item ([[09 Rules/autonomy-tiers.md]] Tier B) — so judgment compounds at **operator speed**, not model speed. The operator is the throughput ceiling on the harness's defensible asset. This closes promotion into an autonomous loop **without weakening the gate**: two independent verifiers confirm each promotion, the human audits the batch. (The frontier move that separates near-frontier from SOTA — automated-RLHF in the artifact layer.)

## The lifecycle (adds one state: `provisional`)

```
new → distilled → PROVISIONAL → promoted        (auto-confirm iff verified)
                      │             ↘ reverted / escalated   (if not)
                      └ landed as a SOFT (advisory) rule on probation + a prediction
```

- **`provisional`** — the rule is landed but **soft/advisory** (never a hard gate) with a `probation_until` + its `prediction_id`, registered in `.claude/_state/provisional-promotions.jsonl`. A wrong provisional cannot block anything — that is what makes auto-landing safe (reversible, Tier A).
- **The dual-verifier gate (the "verified"):** `provisional → promoted` fires only when **both** independent verifiers agree:
  1. **recurrence-clean** — `harness_common.recurrence_hits == 0` over the prediction's eval window (the corrected behavior did not come back), AND
  2. **jury-pass** — the adjudicator cross-family verdict bucket = `passed`.
  Either fails → **auto-revert** the soft rule + mark the prediction `failed` + escalate on the existing `soft → grader → gate` path.
- **Human role → batch audit, not per-item.** A weekly surface lists *auto-confirmed · in-probation · auto-reverted (reason)*; the operator vetoes/overrides in one pass. This is the throughput unlock.

## Tiers (amends [[09 Rules/autonomy-tiers.md]])

| Transition | Tier | Why |
|---|---|---|
| `distilled → provisional` | **A** (act + log) | a soft, reversible, advisory rule on probation — no hard effect |
| `provisional → promoted` | **A iff dual-verifier gate passes**, else **B** | two independent verifiers stand in for the human's per-item confirm; ungated → human |
| `provisional → reverted` | **A** | fail-safe direction — auto-removing a failed soft rule is always safe |
| write to `MEMORY.md` hard rules / a hard gate | **B/C** (unchanged) | escalation past a soft rule stays human; C-tier absolute |

**Posture dial.** Auto-**revert** is ON (fail-safe). Auto-**confirm** is controlled by `.claude/_state/promotion-config.json` `{autoconfirm: bool}` (or env `PROMO_AUTOCONFIRM=1`). **Currently ON** (set 2026-06-06) — earned because the safety is structural, not in keeping it off: a provisional sits a 14-day probation visible in every daily `/vault-evolve` batch audit before it can auto-confirm, and only confirms on dual-verifier pass; auto-revert handles failures. **To revert to propose-only:** set `autoconfirm: false` in that file.

## The engine — `.claude/routines/promotion_engine.py`

Batch, off-interactive-path, 0 model tokens (the jury is separately billed + throttled). Modes:
- `--land` — take `pending-review` distill proposals → `provisional` (register + land soft rule + ensure a prediction). Tier A.
- `--eval` (default) — for each provisional past `probation_until`: run the dual-verifier gate → auto-revert failures · auto-confirm passes (or propose them if `PROMO_AUTOCONFIRM` unset).
- `--audit` — emit the batch-audit report (auto-confirmed / in-probation / auto-reverted) for the weekly human pass.
- `--dry-run` — compute + report, mutate nothing (default until armed).

Reuses: `promotion-predictions.jsonl` (the held-out test set), `harness_common.recurrence_hits` (the matcher), `adjudicator-verdicts.json` (the jury ensemble), `check_promotion_efficacy` (the existing sensor). Built **on** the existing verifiers, not beside them.

## Safety (this is self-modification of the alignment core)
- **Soft-until-confirmed** — a provisional rule is advisory; it can't hard-block, so a wrong one is harmless until verified.
- **Two independent verifiers** — recurrence ∧ jury (a single failure vetoes). Adversarial by construction.
- **Fail-safe direction first** — auto-revert before auto-confirm; the conservative dial ships proposes-only.
- **Batch human veto** with override; caps inherited from [[.claude/skills/harness-evolve/SKILL.md]] (≤3/cycle, reversible-only, one subsystem).
- **C-tier untouched** — no auto outward sends, no auto hard-rule/MEMORY writes.

## Theoretical framing
Automated-RLHF in the **artifact layer**: predictions = held-out verification set, the jury = a reward-model ensemble, recurrence-check = the empirical no-regression test, batch audit = human oversight. Lets judgment compound at model speed while staying inspectable, portable across models, and instantly updatable — the weight-layer's RLHF moved into the symbolic layer.

## Phases
A0 spec + tier amendment (this) → A1 engine + provisional registry (dry-run) → A2 auto-revert live (fail-safe) → A3 auto-confirm live + batch-audit surface in `/vault-evolve`.
