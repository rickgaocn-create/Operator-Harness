---
type: reference
parent-skill: meeting-note
loads-when: "self-audit before save · or when grader (biz-doc-critic) flags a hard fail"
created: 2026-05-21
---

# Deep Mode · Anti-Patterns (reject these)

> Load as the self-check pass before writing the meeting note to disk. Each item is a hard fail signal.

- ❌ **Trusting AI-generated transcripts as canonical without cross-verification.** 智能纪要 / 妙记 / 飞书 AI 纪要 routinely mishears proper nouns (SeedDance → CDS / C-Dance; FORCE → force) and may garble numbers. The disclaimer at the top of these documents is real; cross-check ≥2 sources for model names, product names, and quantitative claims before propagating. → See [[references/source-verification.md]].
- ❌ **Fabricating Q&A that didn't happen** → leadership-grade artifacts depend on truthful sourcing. If user didn't actually ask, use vendor-showcase mode (Variant B) instead. → See HARD RULE in [[references/deep-mode-core.md]].
- ❌ **Synthesized paraphrase under counterparty's name** (`**TapTap**：…` / `**B 站**：…` 等) → See HARD RULE in [[references/deep-mode-core.md]] + canonical [[09 Rules/attribution-discipline.md]]. Cross-party synthesis / 我方 admissions / inference-from-gap go under `**我方判断**：` or `**项目组观察**：`, never under a counterparty prefix.
- ❌ 商务条款写成散文 → 必须上分档表格.
- ❌ 对方承诺不落日期 → 回问，否则标注 `⏳ 时间待定`.
- ❌ 行动计划没 Owner → 必须具体到人，不写"团队负责".
- ❌ 核心结论 > 5 条 → 没抓到 概要，回到 SCORARO 的 Answer 层.
- ❌ 痛点 × 优势表只有 2 列 → 缺"核心收益"列，等于只描述没结论.
- ❌ 没有当前决策状态 → 整份纪要的战略价值归零.
- ❌ 模式判断错误（用 Q&A 模式记单向 showcase）→ 强制用 Variant B 重写 section 1.
