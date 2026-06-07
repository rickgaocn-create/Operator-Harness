---
type: rubric
applies-to: business artifacts (meeting notes, deal memos, biweeklies, OKRs, deal briefs, vendor evals, partnership proposals)
grader: biz-doc-critic
producer: /biz, /meeting-note-deep, /biweekly-report, /okr (Mode A)
max-iterations: 3
---

# Business Doc Rubric (binary checks)

> Grader reads ONLY the artifact + this rubric — never the producer's scratchpad. Each check returns PASS / FAIL with line ref. Verdict = PASS if all checks PASS; FAIL with revision hints otherwise.

## Hard checks (any FAIL = artifact rejected)

| # | Check | Pass criterion | Fail signal |
|---|---|---|---|
| H1 | **Register B section headers** | Headers are noun phrases (e.g., `## 评估依据`, `## 前置风险`, `## 执行建议`) | Parenthetical reader hints (`（30秒）`, `（三点）`), conversational imperatives (`请二位独立反馈`), bullet-style modifiers (`摘要 · 一句话判断`), first-person framing (`我对这个案子的看法`) |
| H2 | **Register C executive summary** | Sections titled `总体判断 / 执行摘要 / 核心判断 / BLUF` use first-person team voice (`我看下来…`, `对我们 BD 这边而言…`) | Third-person analyst summary (`X 由 A 与 B 两条管线构成`), AI-framework boilerplate, no human take |
| H3 | **CN monolingual body** | 中文-default doc body contains zero English words EXCEPT whitelisted (proper nouns, industry acronyms BD/MAU/PV/KOL/IP/SDK/MCP/AI, version numbers, file paths, code, URLs) | `这个 deal 的 timing 不错`, `做个 follow-up`, any inline English where a CN word a 取締役 would understand exists |
| H4 | **User-name routing** | CN/JP docs use `高培尧` or role-based reference (`BD负责人`, `プロジェクトリード`). EN/casual cross-border may use `{{USER_NAME}}` | `{{USER_NAME}}` in CN/JP work body |
| H5 | **Cross-project isolation** | {{PROJECT_A}} docs reference only {{PROJECT_A}} context. {{ORG_B}} docs reference only {{ORG_B}} Cross-border docs ({{ORG_B}} invests in {{PROJECT_A}} partner) may bridge but must flag explicitly | {{PROJECT_A}} internal doc cites {{ORG_B}} work/role/people, or vice versa, without explicit cross-border framing |
| H6 | **No fabricated completion stamps** | Any `✅ YYYY-MM-DD` markers are pre-existing (not introduced by this artifact's draft) | New `✅` stamps in artifact body that weren't in producer input |
| H7 | **MECE on decompositions** | All decompositions (risks / segments / stakeholders / OKR branches / vendor categories) pass MECE — no overlap, no "其他" catch-all | Two buckets overlap, OR a `其他` / `Misc` / `Other` bucket masks a missing cut |

## Soft checks (FAIL = nit; ≥4 nits OR any hard fail → NEEDS REVISION)

| # | Check | Pass criterion | Fail signal |
|---|---|---|---|
| S1 | **Banned Register B phrasings** | Body prose uses `行业已知现状` / `此项` / `结合` / `故` / `可…` | Chat-residue connectors: `所以` / `那么` / `加上我自己…` / `这块儿` / `这事儿` / `还有就是` |
| S2 | **Excessive 我建议 / 我们应该** | ≤2 instances per page; replace with `建议…` / `宜…` / `应当…` | ≥3 instances or every section opens with `我建议` |
| S3 | **Provenance frontmatter** | `(C)`-prefix files have `created-by:` + `source-meeting:` (if applicable) + `audience:` | Missing provenance frontmatter on `(C)` file |
| S4 | **Wikilinks resolve** | Every `[[link]]` resolves to an existing vault file | Dead wikilink |

## Output schema (grader returns this)

```yaml
verdict: PASS | NEEDS_REVISION
artifact: <path>
iteration: 1 | 2 | 3
hard_fails:
  - check: H1
    line: 12
    quote: "## 几条真实风险（30秒）"
    rule: "Register B header — no parenthetical reader hints"
    fix_hint: "Replace with `## 前置风险`"
soft_issues:
  - check: S1
    line: 22
    quote: "所以建议二阶段"
    fix_hint: "`所以` → `故`"
mece_warnings:
  - section: "## 风险矩阵"
    issue: "`其他` bucket — catch-all"
    suggestion: "Re-cut into 财务 / 法律 / 操作 / 政策"
next_action: continue | revise | escalate
```

`next_action` logic:
- `continue` — PASS, artifact ready
- `revise` — NEEDS_REVISION, hard_fails non-empty, iteration < 3
- `escalate` — NEEDS_REVISION at iteration 3, return to user with summary
