---
type: rubric
applies-to: BD prospect briefs for {{PROJECT_A}}
grader: bd-prospect-grader
producer: bd-prospect-researcher
max-iterations: 3
---

# BD Prospect Brief Rubric (binary checks)

> Grader reads ONLY the brief + this rubric + (optionally) the {{PROJECT_A}} 资源底牌 reference. Never the researcher's scratchpad. Returns PASS / FAIL per check.

## Hard checks (any FAIL = brief rejected)

| # | Check | Pass criterion | Fail signal |
|---|---|---|---|
| H1 | **法人单位 specificity** | Names the operating CN legal entity, not parent brand. Statutory rep (法人代表) named if discoverable; if not, route to find it is named | `蜜雪集团` instead of `蜜雪冰城股份有限公司`; missing entity entirely; "Group / Holdings" only |
| H2 | **核心决策人 — real names or route** | Either specific name + role + source, OR explicit route (`市场总监 (姓名待查 — 推荐路径: LinkedIn + 脉脉 + 最近 PR 署名)`) | Invented names (`李总`, `市场部`, `相关负责人`), or no decision-maker section at all |
| H3 | **资源底牌 mapping is bidirectional** | Names ≥2 of the 6 资源 types they NEED from {{PROJECT_A}}, AND the Conversion 目的 names what {{PROJECT_A}} NEEDS FROM THEM (concrete, not "合作") | Conversion 目的 = "我们能给品牌曝光" or any sentence describing what {{PROJECT_A}} OFFERS (giver/taker confusion) |
| H4 | **建议邀请人 named** | Specific role + person at {{PROJECT_A}} side who should make the outreach, with reason for picking them | Missing 建议邀请人 OR generic (`{{PROJECT_A}} BD 团队`) |
| H5 | **Citations on every factual claim** | Each fact (entity name, financial figure, recent PR, decision-maker) has a source URL or vault wikilink | Unsourced claims, especially decision-maker names |
| H6 | **Cross-project isolation** | No {{ORG_B}} context, no JP M&A framing, no 跨境 references unless brand is explicitly cross-border (e.g., 小鹏 expanding to JP) | {{ORG_B}} / {{FUND}} mentioned in {{PROJECT_A}} BD brief |
| H7 | **No fabricated entities** | If vault sweep + internal-archive + web all return nothing, the brief states this explicitly and recommends a research path | Inventing financials, made-up subsidiaries, or vague "industry data" without source |

## Soft checks (FAIL = nit; ≥3 nits OR any hard fail → NEEDS REVISION)

| # | Check | Pass criterion | Fail signal |
|---|---|---|---|
| S1 | **Verdict emoji** | Single 🟢 / 🟡 / 🔴 at top, no go/no-go editorial commentary in body | Body argues for/against; verdict omitted |
| S2 | **Bilingual handling** | CN entity → 中文 throughout (entity names, role titles, conversion goal). EN labels only where source is EN-native | CN entity reported in EN, role titles in EN |
| S3 | **Internal-archive checked** | Brief mentions whether enterprise-search hit existing Gmail / Drive / Calendar touches (even if empty) | No mention of internal-archive step; jumped straight to web |
| S4 | **Word count ≤500** | Brief body (excluding sources) is ≤500 words | Over-stuffed brief; {{PROJECT_A}} audience won't read past 800 |

## Output schema

```yaml
verdict: PASS | NEEDS_REVISION
artifact: <brief path or session content>
iteration: 1 | 2 | 3
hard_fails:
  - check: H1
    issue: "Reported 蜜雪集团; operating entity is 蜜雪冰城股份有限公司 per 企查查"
    fix_hint: "Replace 法人单位 with the operating subsidiary"
soft_issues:
  - check: S3
    issue: "Brief skipped internal-archive step; jumped from vault to firecrawl"
    fix_hint: "Add Phase 1.5 enterprise-search pass and note results"
next_action: continue | revise | escalate
```
