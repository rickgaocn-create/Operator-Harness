---
type: identity
created-by: human
created: 2026-01-01
last-updated: 2026-01-01
mem-block: identity
description: "Who the operator is, stable context, and how to work with them"
limit: 120
limit-unit: lines
load-policy: always-on
---

# Me — {{USER_NAME}}

> Portable identity. Always-loaded by Claude at session start. This is a **TEMPLATE** — replace every bracketed placeholder with your own context. Depth lives in pointers below; load on-demand only when the task requires it.

---

## Quick Bio

> One paragraph: who you are, your current roles, your mission. Keep it dense and concrete — this is the single highest-leverage context the assistant has about you.

[Your bio here. Roles, what you're optimizing for, the strategic phase you're in.]

---

## Current Focus

> **Single-sourced, not copied here** (avoids staleness). Strategic tracks + current-quarter OKRs live in [[GOALS.md]]; week-level priorities in the current `04 Notes/weekly/` file. Read those for "what am I on right now."

- Track 1 — [name]
- Track 2 — [name]
- Track 3 — [name]

---

## How to Work With Me

- **Communication:** Low-latency, high-density. Conclusion first. Format to the active window (Obsidian / CLI markdown · Feishu rich-text · Discord). No long intro/outro paragraphs. Specific options, not generic web top-10.
- **Tone:** Pragmatic, sophisticated, slightly witty. Peer not subordinate. No AI-fluff or affirmations.
- **Decision-making:** Evidence-based. Authoritative sources for legal/regulatory queries. Skip industry basics — assume fluency in [your domains].
- **Output format:** Default to structured OKRs or actionable tables. SCORARO short-form for analyses (Conclusion up top, Rationale middle, Action bottom).
- **Default reply language:** [e.g. English in conversation; work artifacts follow bilingual routing].
- **On my errors:** no apology or self-flagellation — brief acknowledgment + the fix + a structural preventer (instinct / rule / check).

---

## Personal Context

> Optional. Key people, recurring signals the assistant should interpret correctly, standing constraints. Keep only what changes how the assistant should act.

- [Person / relationship / standing context]

---

## Hard Lines

- **Zero concept-fluff** — no granular executable roadmap = distraction, not strategy
- **No low-integrity arbitrage** — short-term gains that rot long-term partnership health are not wins
- **No performative busyness** — workflows exist for strategic leverage, not appearances

---

## ⛔ Confidential Lanes (strict isolation · every session enforce)

> List any workstreams that MUST NOT cross-reference each other or shared comms channels. Audit gate on every operation. Delete this section if not applicable.

- [Confidential lane, if any]

---

## Pointers

- **Goals & current OKRs:** [[GOALS.md]]
- **Vault structure & skills index:** [[vault-map.md]]
- **Operating instructions:** [[CLAUDE.md]]
- **Hard rules (incident-driven):** [[MEMORY.md]]
