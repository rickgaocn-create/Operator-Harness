# Results — harness output-quality eval

Run 2026-05-26. Per the pre-registration in `PREREG.md`. Generators+critics = Sonnet (same persona, isolated subagents); judge = Opus (fresh blind context, scrambled order). Weighted = 2·decision + 2·fit + 1·insight + 1·trap (max 60).

> **n = 2 of the planned 3** — Task 3 was not run (session-limit interruptions; deviation from pre-reg, disclosed). Margins among the structured arms are within noise, so the directional read is already stable.

## Per-task weighted scores

| Arm | Task 1 (瑞声 structuring) | Task 2 (试玩会 conversion) | mean |
|---|--:|--:|--:|
| A — single-shot baseline | 39 | 39 | **39.0** |
| B — best-of-N (compute control) | 47 | 55 | **51.0** |
| C — generic-frame divergence (adhd method) | 53 | 49 | **51.0** |
| D — harness-lens divergence | 46 | 53 | **49.5** |

Per-dimension (judge, blind): T1 D=7/8/9/7, C=9/9/8/9, B=8/8/7/8, A=7/7/5/6 · T2 D=9/9/9/8, B=9/10/8/9, C=8/8/9/8, A=7/7/5/6 (decision/fit/insight/trap).

## Verdict vs pre-registered criteria

- **PRIMARY — D > A on ≥2/3 tasks: MET.** Harness beat the bare baseline on both tasks, by a wide margin (mean 49.5 vs 39.0, ~+27%).
- **RIGOR — D ≥ B (not just compute): FAILED.** Best-of-N at equal compute edged the harness on *both* tasks (51.0 vs 49.5). The harness's judgment frames did not beat unstructured extra sampling.
- **RIGOR — D ≥ C (your frames ≥ generic frames): NOT MET (split/tie).** Lost T1 (46 vs 53), won T2 (53 vs 49); mean 49.5 vs 51.0.

**Bottom line:** the robust effect is **structure/compute ≫ single-shot** (any of B/C/D beats A by ~25–40%). The harness's *specific judgment-graph frames* show **no measurable edge** over generic-frame divergence or plain best-of-N at matched compute — they cluster inside a 1.5-point band (49.5–51.0).

## The load-bearing caveat (what this did and did NOT test)

All four arms received the **same public brief with zero private information.** So this eval tested the harness's **framing/lens layer as generic reasoning lenses** — and that layer is exactly the part we'd already reasoned is *commoditizing* (frontier models do multi-lens reasoning well). The result **empirically confirms that**: as reasoning scaffolds, the judgment-graph frames ≈ generic frames ≈ best-of-N.

It did **NOT** test the **durable layer** — private priors / calibrated taste (counterparty intel, what 瑞声 really wants, who decides, what's failed before). No arm had access to any of it. The only test that could show a harness edge is one where **one arm is fed {{USER_NAME}}'s private priors and the others are not.** That's the eval that matters next; this one cleanly rules out the framing layer as a source of edge.

## A′ test — single frame-informed pass (added 2026-05-26)

Tests the *ambient* harness (one draft shaped by the graph's lead frame), vs A (unframed single shot) and B (best-of-N). Fresh 4-way blind judge per task (A, A′, B, D); compare within-batch (LLM judges score relatively, so absolutes shifted ~2pts from the earlier batch).

| Arm | Task 1 | Task 2 | swing (variance) |
|---|--:|--:|--:|
| A′ — single framed pass | 37 | 51 | **14** |
| A — single unframed pass | 40 | 46 | 6 |
| D — harness divergence | 50 | 52 | 2 |
| B — best-of-N | 52 | 53 | **1** |

**Finding — the "higher consistency" hypothesis is inverted.** A single frame is a *concentrated bet*: when the lead frame fits the problem (T2 strategic-systems) it lifts a cheap single pass to ≈ best-of-N (51 vs 53); when it mis-fits (T1 resource-exchange, pushed abstract) it drops *below the unframed baseline* (37 vs 40). A′ is the **highest-variance** arm (swing 14); best-of-N is the **most consistent** (swing 1), because it doesn't bet on one frame.

**Relocates the value:** the edge isn't *having* frames (they ≈ generic ≈ best-of-N, and a wrong one hurts) — it's *selecting* the right frame for the problem. The lens picked T1's lead by crude tag-match and chose poorly; a human's read of "this problem needs concreteness, not grand framing" would override it. Frame-selection is the judgment act; the frame inventory is not the moat. For reliability, best-of-N dominates.

## Private-priors test (B vs B+) — the decisive one (added 2026-05-26)

The test the lens eval couldn't run: one arm fed a **facts-only private-priors packet** from the vault (decision chain, precedent deals, relationship state, open loops, 待核实 markers — **facts, not conclusions**), the other the bare public brief. Same best-of-N machinery (3 gen + critic), same model, blind pairwise judge with an explicit "reward specificity only when it sharpens, not name-dropping" guard.

| Arm | Task 1 (瑞声) | Task 2 (试玩会) | margin |
|---|--:|--:|---|
| B — best-of-N, no private context | 45 | 40 | — |
| **B+ — best-of-N + private priors** | **53** | **52** | slight / **clear** |

**B+ won both tasks** (+8, +12). Two findings:
1. **Private priors are the edge.** Across the whole arc, *frames-as-lenses* never beat best-of-N (≈ tie/loss); *private facts injected* beat it consistently. This is the empirical backing for "judgment = private priors + standards, not reasoning lenses." The moat is **retrieval + injection of private context into a best-of-N draft**, not the lens.
2. **Priors also reduce fabrication.** On Task 1 the judge dinged the context-blind control for *"fabricating precision (invents dates/numbers)"* while B+ — knowing the 待核实 discipline — stayed honest. Private facts don't just improve fit; they suppress confident hallucination.

**The new variable:** here I hand-curated the priors packet. In production the bottleneck becomes **automated retrieval** — pulling the *right* vault facts for a given draft. Retrieval quality now determines whether this edge holds. That is the layer worth building.

## Capstone test — full harness vs priors+best-of-N (the one that matters)

"Private priors beat no-priors" is near-tautological. The decision-relevant test: does the **full harness** (priors + judgment lens frames + critic + grounding gate + standards, integrated) beat the **simple baseline** (priors + best-of-N)? Same priors in both arms; the only difference is the harness's judgment machinery. Blind pairwise judge.

| Task | Full harness | Priors + best-of-N |
|---|--:|--:|
| T1 (瑞声) | 47 | 46 |
| T2 (试玩会) | 49 | 49 |

**Tie on both (+1, 0; both "slight").** The harness's judgment apparatus adds **no measurable output-quality edge** over injecting the right private context into best-of-N. The grounding gate (Fix-1) gave a marginal *executability* nudge; the frames/lens/critic added nothing the priors+best-of-N didn't already reach.

**Conclusion of the whole arc:** for single-artifact output quality, the harness reduces to **"retrieve the right private context → best-of-N."** The elaborate judgment-generation machinery (graph / lens / critic) is not pulling weight beyond that. The proposed "build a big priors-injection moat" is therefore **not justified** — the moat is just *good retrieval into a best-of-N prompt*, which is far simpler.

**What this does NOT condemn (scope of the test):** this measures single-memo quality only. It says nothing against the parts the test didn't cover and which may still earn their keep:
- the **capture discipline** that keeps the private context *current* (a stale wiki retrieves stale priors → the edge decays);
- the **artifact-production skills** (turning a Feishu 纪要 into a structured vault entity);
- standards-enforcement / consistency across many artifacts over time.
The finding is narrow and sharp: the *judgment-generation apparatus* is not the value; *maintained private knowledge + retrieval + best-of-N* is.

## One-shot test — full harness (1 pass) vs priors+baseline (1 pass) (added 2026-05-26)

Strips out best-of-N: both arms a single pass, same priors; only difference is whether the harness's judgment layer (lens frames + standards + grounding gate) is baked into that one pass.

| Task | Full harness (1 shot) | Priors + baseline (1 shot) |
|---|--:|--:|
| T1 (瑞声) | **53** | 46 |
| T2 (试玩会) | 48 | **54** |

**Split — harness +7 on T1, baseline +6 on T2.** Bigger, opposite swings than the pipeline tie → **the judgment layer in a single pass is high-variance.** T1 the lenses surfaced a non-obvious insight (2026-vs-2027 phased-payoff timing mismatch); T2 the multi-lens guidance spread the pass thin while the plain baseline went deep on one sharp mechanism.

**Combined with the pipeline tie:** the harness judgment layer is not a *reliable* quality lever — pipeline → tie; one-shot → ~50/50 and noisier. best-of-N's value is variance-reduction (sample + pick), which is exactly why the pipeline version is the safe play and one-shot-harness is a gamble. The lenses' one genuine upside: they occasionally surface a non-obvious angle (T1) — but unreliably, and at a variance cost.

## Replicate study (R=3, T1) — CORRECTS the capstone "tie" (added 2026-05-26)

The capstone (single run each) showed a tie and I concluded "judgment machinery = dead weight." That was an overclaim from a single draw. Replicating the pipeline comparison R=3 on T1, scoring all 6 finals blind in one batch:

| Arm | runs (/60) | mean | range |
|---|---|--:|--:|
| Full harness pipeline | 49.6, 48.2, 51.3 | **49.7** | 48.2–51.3 |
| Priors + best-of-N | 48.0, 48.4, 43.8 | **46.7** | 43.8–48.4 |

**Harness edges it by ~3 pts (~6%); 8/9 pairwise run-comparisons favor the harness; its whole distribution sits above.** NOT a tie. The earlier conclusion was a single-draw artifact.

**Mechanism = higher floor, not higher ceiling.** Harness runs are tight (no duds); best-of-N had one weak run (43.8). The grounding gate + structured synthesis prevent the weak/abstract draft that plain best-of-N occasionally ships. This reconciles the whole arc: harness *one-shot* = high-variance (split); harness *pipeline* = floor-raised (small consistent edge); best-of-N = good but un-gated downside.

**Revised conclusion:** the harness pipeline is **not** dead weight — it buys a small, consistent quality edge over priors+best-of-N, primarily as reliability (fewer bad outputs). BUT the edge is **modest (~6%)** and shown on **one task** (T1, whose frames suit a BD-structuring problem; the one-shot test had T2 favoring the plain baseline). Whether ~6% justifies the pipeline's complexity vs the simplicity of priors+best-of-N is a real cost/benefit call, and generalization needs T2 replication. The corrected headline: **priors are the big lever; the judgment pipeline adds a modest reliability edge on top — real, not zero, not large.**

## T2 replicate (R=3) + the noise-floor finding — RE-corrects the T1 edge (added 2026-05-26)

Replicated the pipeline comparison on T2 (R=3 per arm), scoring all 6 finals blind in one batch.

| Arm | runs (/60) | mean | spread |
|---|---|--:|--:|
| Full harness pipeline | 41.4, 51.5, 46.6 | **46.5** | 10.1 |
| Priors + best-of-N | 43.6, 48.9, 48.5 | **47.0** | 5.3 |

**T2 = tie on the mean; harness is the higher-variance arm (best AND worst single memos).** The T1 "+3 / ~6% harness edge" did NOT replicate.

**The decisive methodological finding:** the harness-T2 rep1 memo is *identical text* reused from the capstone. It scored **52 there, 41.4 here** — a **~10-point batch swing for the same artifact.** That noise floor is *larger than every harness-vs-best-of-N delta in this whole eval.* 

**Pooled across both tasks (6 runs each): harness 48.1 vs best-of-N 46.9 — a 1.2-pt gap, deep inside ±10-pt noise.**

### Final, de-escalated verdict (correcting BOTH earlier overclaims)
- Capstone (1 run) → I said "dead weight." Overclaim.
- T1 replicate (3 runs) → I said "modest edge, I was wrong." **Over-correction** — read a single task/batch as signal.
- T2 replicate + batch-noise → **the honest answer: harness pipeline and priors+best-of-N are statistically indistinguishable** at this judge precision (±~10) and sample (n=2 tasks). No reliable edge either way; harness possibly higher-variance.
- **The ONE robust effect in the entire study: priors ≫ no-priors (+8, +12, consistent).** That is the only lever that moved the needle beyond noise.

**Actionable:** the keep/cut decision on the judgment pipeline should NOT rest on output quality (it's a measurement-floor wash). It rests on other grounds (cost, the capture discipline that keeps priors live, your own clarity). Invest in priors + retrieval; treat the judgment pipeline as quality-neutral.

## Priors-lens re-judgment — the sharpest signal (added 2026-05-26)

Re-judged the 3 key finals per task with an Opus judge given the **priors as ground truth** (playing "{{USER_NAME}} who knows the real facts"), scoring real-fit-to-actual-situation. Still blind to authorship. Weighted = 2·realfit + 2·decision + insight + trap.

| Arm | T1 | T2 |
|---|--:|--:|
| Priors + best-of-N | 47 | 53 |
| Full harness pipeline | 53 | 39 |
| No-priors best-of-N | **27** | **26** |

**Finding 1 (big, robust): the no-priors arm craters under a reality-aware judge.** It doesn't just lack grounding — it *contradicts reality*: T1 no-priors proposed cash-contract thinking (履约保证金/排他合同) violating {{ORG_A}}'s non-cash norm; T2 no-priors fabricated 文旅局/版号/CPA/embargo. Blind judge rated these ~40 ("plausible"); reality-aware judge rates them ~26 ("wrong"). **Priors are worth ~20-23 pts, not ~10 — and a big part of that is error-avoidance** (priors stop confident recommendations that are wrong for the actual situation). Far above the ~10-pt noise floor → trust it.

**Finding 2 (unchanged): harness pipeline vs priors+best-of-N is still split/within-noise** (harness +6 T1, priors+BoN +14 T2). On T2 the harness's frame-driven abstraction ("素材军火库/资产生成机器") got dinged for *missing* the concrete warm loops (好游快爆专访/王鹤桥/TapTap node) that priors+best-of-N nailed — frames can abstract *away* from reality on relationship-heavy work.

**Net, most ground-truth-anchored conclusion of the whole eval:** priors are the lever, and the case is *stronger* than the blind eval showed — working without them yields outputs that are confidently wrong for the real situation. The judgment-frame pipeline remains quality-neutral-to-slightly-negative on top of priors. (Caveat: judge is Opus-as-{{USER_NAME}}, the closest proxy yet but still not human-{{USER_NAME}}.)

## Full-harness judge (max-circularity stress test) — added 2026-05-27

Escalated the judge to run {{USER_NAME}}'s ENTIRE operating system (priors + 5 values + 9 frameworks + standards), grading outputs built with that same system. **Circular by construction** — value-aligned outputs win partly tautologically — so this is a coherence check, the LEAST independent judge of the three. Same memos as the priors-lens run.

| | priors-lens | full-OS judge |
|---|--:|--:|
| T1: harness / priors+BoN / no-priors | 53 / 47 / 27 | 53 / 48 / 33 |
| T2: priors+BoN / harness / no-priors | 53 / 39 / 26 | 52 / 45 / 42 |

**Result: rankings IDENTICAL to the priors-lens judge — T1 harness wins, T2 priors+BoN wins.** The maximal-circularity judge (running the harness's own values) lifted the harness's T2 score (39→45) but could NOT flip a single ranking. The split/mirror pattern (frames help structuring T1, hurt relationship-execution T2) is now stable across THREE judge lenses (blind, priors, full-OS).

Notable self-indictment: on T2 the full-OS judge dinged the *harness's own* output for *"LOI/分润现金味重, 置换纪律略松"* — its frames drifted toward cash-contract logic, violating {{USER_NAME}}'s exchange-over-spend value, while plain priors+best-of-N stayed truer. The frames don't even reliably produce *more value-aligned* output.

**Verdict, now stable across every judge we can build:** (1) priors ≫ no-priors, robust under all lenses (no-priors condemned for contradicting reality AND violating truth-over-comfort). (2) The judgment pipeline is NOT a reliable quality edge over priors+best-of-N — it cannot win even with the deck maximally stacked for it. (3) This is the instrument's ceiling: three judge lenses agree; only human-{{USER_NAME}} scoring or real outcomes could add more.

## ⚠️ HUMAN GROUND TRUTH — supersedes the LLM-judged comparative verdict (2026-05-27)

{{USER_NAME}} (the only judge that counts) scored the T1 front-runners by hand:
- **Full harness pipeline: 7/10**
- **Priors + best-of-N: 3/10** ("would have to rewrite the priors+N output entirely")

**This INVERTS every LLM judge.** All three LLM lenses (blind / priors-as-truth / full-OS) rated the harness pipeline and priors+best-of-N as *roughly equal / no reliable edge*. The human rates them **usable vs rewrite-from-scratch.**

**Corrected verdict (this section supersedes the LLM comparative conclusions above):**
1. **The judgment pipeline is NOT quality-neutral — it's the quality bar.** The frames/critic/grounding produce a 7/10 vs a 3/10 stripped draft. The LLM "no edge" finding was an artifact: LLM judges reward surface plausibility a real operator sees straight through.
2. **best-of-N's role is a reliability MULTIPLIER on the full pipeline** (run the 7/10 pipeline N× → pick/merge best to catch its run-to-run variance), NOT a replacement that strips it to priors-only. The `best-of-n` skill was corrected accordingly.
3. **What still plausibly holds:** priors-first (the 3/10 still had priors; priors are foundational). But hold even that lightly given how wrong the LLM judge proved.

**Meta-lesson (the real one):** an elaborate multi-day, ~150-subagent LLM-judge battery reached the *wrong comparative answer*; one human sentence corrected it. For output-*quality* questions, get the human's score EARLY — here LLM-as-judge wasn't merely noisy, it was *actively misleading*. The disciplined version of this whole exercise was: generate 2-3 real outputs, have {{USER_NAME}} score them, done.

## Honest limitations
n=2 (underpowered, no CIs); margins among B/C/D within noise. Single judge model (Claude family; mitigated by judge≠generator model + blinding + scrambled order). Judge-rated quality is a **proxy** for real outcomes, not the outcome. Harness arm used top-3 lens frames; the real harness also carries a baseline floor (corpus-grounding/rigor) folded loosely into the critic.
