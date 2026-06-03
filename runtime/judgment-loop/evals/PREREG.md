# Pre-registration — harness output-quality eval (locked before generation)

Date: 2026-05-26. Locked before any output was generated or seen.

## Hypothesis
Shaping an open-ended strategy output with the harness's judgment-graph frames (lens-driven
divergence) produces a *better artifact* than (a) a single-shot baseline, (b) equal-compute
unstructured best-of-N, and (c) generic-frame divergence (the "adhd" method).

## Arms (same model = Sonnet, same senior-BD-operator persona; method is the only variable)
- **A — single-shot baseline.** One operator, one pass → final memo.
- **B — best-of-N (compute control).** 3 independent operators each write a memo → critic selects/merges. *The control the OP omitted: isolates "method" from "more compute".*
- **C — generic-frame divergence (the adhd method).** 3 isolated generators, generic frames (adversarial / biological-systems / inversion) → 5-6 ideas each → critic scores·clusters·deepens → memo.
- **D — harness-lens divergence.** Same machinery as C, but frames = the judgment graph's top-3 frames for the task (from `judgment_lens`). *Isolates: does YOUR private judgment content beat generic frames?*

N=3 generators for B/C/D (matched compute). Generators isolated (no cross-anchoring).

## Tasks (3 real {{PROJECT_A}} BD/strategy problems; open-ended)
1. **瑞声 partnership structuring** — design the {{PROJECT_A}}×瑞声 (AAC) haptics + channel/异业 partnership structure & highest-leverage angles.
2. **试玩会 conversion** — maximize high-value BD conversion (channels/政企/异业/media) from the single 6/19-21 端午试玩会.
3. **Differentiated positioning** — sharpest BD/channel positioning angles for {{PROJECT_A}} vs 异环/无限大/鸣潮/终末地 (beyond generic "高品质二游").

D-arm frames (locked from lens): T1 = v-resource-exchange·f-strategic-systems·f-value-mechanism; T2 = f-strategic-systems·v-resource-exchange·f-2080; T3 = f-2080·f-mece·f-multi-lens.

## Judge (blind)
Separate model (Opus), fresh context, "skeptical senior operator" persona. Sees the 4 final memos
per task **anonymized + randomized**; does not know which is which. Scores each 0–10 on:

| Dimension | Weight | Why |
|---|---|---|
| Decision-usefulness / actionability | ×2 | the thing that matters for shipping |
| Fit to real context & constraints | ×2 | does private judgment actually show up (vs generic advice) |
| Strategic insight / non-obviousness | ×1 | sharp vs textbook |
| Trap detection | ×1 | flags seductive dead-ends |

Weighted score = 2·action + 2·fit + 1·insight + 1·trap (max 60). Judge also gives a blind overall ranking.
**Breadth/novelty deliberately NOT scored as a win condition** — they're divergence gimmes (the OP's tautology).

## Pre-registered success criteria
- **Primary:** D's weighted mean > A's on ≥ 2 / 3 tasks.
- **Rigor:** D ≥ B (edge isn't just compute) AND D ≥ C (your frames ≥ generic frames).
- **Honest nulls (reported plainly if they occur):** D ≈ A → harness doesn't improve outputs. D ≈ C → divergence helps but your graph adds nothing over generic frames. D ≈ B → it's just compute.

## Caveats (stated up front)
n=3 (underpowered, no CIs). Single judge model, Claude family (same-family bias; mitigated by judge≠generator model + blinding). Judge-rated quality is a **proxy** for real outcomes (deals won), not the outcome itself. Orchestrated by the assistant (mitigated: blind separate judge; {{USER_NAME}} validates a subset).
