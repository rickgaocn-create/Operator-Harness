---
type: rubric
applies-to: M&A screening briefs for {{ORG_B}} CN→JP rollout candidates
grader: ma-screening-grader
producer: ma-target-screener
max-iterations: 3
---

# M&A Screening Brief Rubric (binary checks)

> Grader reads ONLY the brief + this rubric + {{ORG_B}} CLAUDE.md filter definition. Never the screener's scratchpad. Returns PASS / FAIL per check.

## Hard checks (any FAIL = brief rejected)

| # | Check | Pass criterion | Fail signal |
|---|---|---|---|
| H1 | **All 4 scorecard dimensions filled with 1–5** | JP Market Fit / Margin Profile / AI Leverage / Weak-Yen Arbitrage each have an integer 1–5 score AND a single-sentence sourced rationale | Any "N/A", "depends", "3 (default)", or score without sourced rationale |
| H2 | **Composite drives verdict** | Composite = sum of 4 scores. Verdict label matches: 17–20 → Move to DD · 13–16 → Park · ≤12 → Reject. No verdict-rationale mismatch | Composite says 14 but verdict says "Move to DD"; or verdict given without composite shown |
| H3 | **Investment thesis is specific** | 3-sentence-max thesis names: (a) the play mechanism (license / acquire / partner / JV), (b) JP channel/distribution, (c) one concrete operational lever (e.g., AI demand-forecast, CN supply-chain arbitrage) | "Expansion potential" / "synergistic fit" / "promising opportunity" without naming HOW |
| H4 | **Red flags sourced** | Each red flag references a source (filing / news / industry analysis) OR is labeled as inferred from category benchmark | "Regulatory risk" stated without naming the regulation or jurisdiction |
| H5 | **JP-perspective competitive scan** | Competitive landscape includes JP local incumbents in the target's category | Competition analyzed only from CN-domestic perspective; "no major competitors" without naming what was checked in JP |
| H6 | **No invented financials** | Public financials cited with source; private companies use category benchmarks with explicit range + reasoning | A revenue figure or margin number without source for a private company |
| H7 | **Cross-project isolation** | No {{PROJECT_A}} BD context, no 诗悦网络 references, no {{ORG_D}} framing | {{PROJECT_A}} / 诗悦 / {{ORG_D}} mentioned in {{ORG_B}} screening brief |

## Soft checks (FAIL = nit; ≥3 nits OR any hard fail → NEEDS REVISION)

| # | Check | Pass criterion | Fail signal |
|---|---|---|---|
| S1 | **Recommended Next Step specificity** | DD priorities named (财务 / 法律 / 渠道 / IP) for Move-to-DD; revisit-trigger condition named for Park; terminal one-line reason for Reject | "Further analysis needed" without naming WHAT analysis |
| S2 | **Internal-archive checked** | Brief mentions whether enterprise-search hit Gmail/Drive for prior {{ORG_B}} touches with the target (even if empty) | Jumped straight to web research without checking internal |
| S3 | **Language routing** | Default 中文 unless source intel is primarily EN. Board-facing JP framing reserved for `03 Proposals/` (out of scope) | Screening brief written in JP "for board" (premature — board sees proposals, not screens) |
| S4 | **Word count ≤600** | Brief body (excluding sources) is ≤600 words | Over-padded; {{ORG_B}} audience reads scorecards, not essays |
| S5 | **Sources include public filings if available** | Public company → IPO doc / 年报 / 季报 cited. Private → industry analysis + category benchmarks | Only company website + Wikipedia (i.e., low-quality source mix) |

## Output schema

```yaml
verdict: PASS | NEEDS_REVISION
artifact: <brief path or session content>
iteration: 1 | 2 | 3
hard_fails:
  - check: H1
    issue: "AI Leverage = '3 (default)' without rationale"
    fix_hint: "Force a verdict: either rationale for why AI is irrelevant (score 1) or a defensible 2/4/5 with named mechanism"
soft_issues:
  - check: S2
    issue: "No mention of enterprise-search internal-archive pass"
    fix_hint: "Add Phase 1.5 internal-archive check and note results"
next_action: continue | revise | escalate
```
