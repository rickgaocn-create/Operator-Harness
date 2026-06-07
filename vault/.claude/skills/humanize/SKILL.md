---
category: work
name: humanize
description: Remove AI-writing tells from creative prose, pitch copy, CV narrative, brand copy, and long-form messages. Auto-chain for creative artifacts; skip structured data and raw capture.
model: claude-sonnet-4-6
allowed-tools: Read, Edit, Glob, Grep
companion-rules:
  - "[[09 Rules/auto-chain-style.md]]"
  - "[[me.md]]"
created: 2026-05-19
last-restructure: 2026-05-21
created-by: claude
audit-trace: "2026-05-19 {{USER_NAME}} request — file the humanizer capability + auto-trigger on creative-writing finalization. Sourced patterns from blader/humanizer + op7418/Humanizer-zh. 2026-05-21 split: 29-pattern check + CN AI 套话 table 移到 [[09 Rules/auto-chain-style.md]] § Humanize（Phase 3.2.c restructure）"
---

# Skill: Humanize (strip AI-writing tells from creative artifacts)

Strip the signatures that make AI-generated text obvious — significance inflation, telltale vocabulary, em-dash overuse, inline-header pull-quote pattern, formulaic structure — from any creative-writing artifact before it ships.

> **Quality bar**: a reader who knows the LLM tells would not flag the artifact as AI-written. Reads like the user wrote it, not like an assistant tidied it.

> **Pattern catalogue:** 29 patterns (Content / Language / Style / Tone) + CN AI 套话 table in [[09 Rules/auto-chain-style.md]] § Humanize. This SKILL.md holds dispatch + workflow only.

---

## When to Use

**Manual invocation:**
- `/humanize <path>` or `/humanize` (with text in chat)
- "humanize this" / "去 AI 痕迹" / "humanizer pass" / "make this sound human" / "remove AI tells"
- After hand-editing a Claude-drafted artifact, before shipping

**Auto-trigger (default ON):** After any creative-writing artifact is finalized by Claude, run this skill as the LAST step before declaring completion. Specifically:

- CV / personal narrative drafts (especially **`10 Action/12 Active/CV-*.{md,html}`**)
- Pitch deck body copy (**`03 Projects/*/Pitches/**/*.md`**, `*-pitch*.{md,html}`)
- Brand / marketing copy (**`03 Projects/*/05 System/(C) brand-*`**, brochures, taglines)
- Long-form messages drafted by Claude (≥4 paragraphs)
- Narrative reports (Q-end retros, year-end memos, founder letters)
- Blog drafts, public-facing posts
- Any output where user said "make this for [external reader]" or "this is for sending"

**Do NOT use for** (skip auto-chain):
- Frontmatter-heavy structured notes (Cards, Action files, OKR trackers, daily notes)
- Meeting raw capture (`/meeting-note` Plain mode — already structured, not creative)
- Tables, lists, code blocks, file paths
- Internal-only Inbox tasks ({{USER_NAME}} reads them, no audience polish needed)
- Eval output of `/biz` itself (loop guard)
- Any file with `humanize: skip` in frontmatter (escape hatch)
- Any file with `humanize-passed: YYYY-MM-DD` recent (de-dup)

---

## How It Works

### Phase 1 — Identify artifact + audience

Read the artifact. Identify:
- **Audience** (internal {{USER_NAME}} / {{PROJECT_A}} team / external investor / Japanese stakeholder / general public)
- **Register** (B = business / C = executive summary voice / casual / formal)
- **Target tone** (matter-of-fact / persuasive / narrative / report)

Audience and register set the bar. Investor-facing CV is held tighter than internal Inbox draft.

### Phase 2 — Pattern scan + fix proposal

Walk the 29-pattern checklist in [[09 Rules/auto-chain-style.md]] § Humanize. For each match, propose a fix INLINE with line reference:

```
L42: "the most intimate on-site IP supervision structure of its kind"
     → "Significance inflation. Replace with verifiable claim."
     → suggested: "the deepest on-site IP supervision structure ... at the time"

L67: "**The bet.** In ACG, ..."
     → "Inline header pattern. Drop the prefix."
     → suggested: "In ACG, ..."

L88: "transformative" (used 3x in the section)
     → "Telltale vocab + promotional. Replace with specific descriptor each time."
```

Group fixes by severity:
- **🔴 must-fix**: opens reader's "AI-written" detector (inline headers, "delve", em-dash floods)
- **🟡 should-fix**: notably off-register (rule-of-three, mild inflation)
- **🟢 nice-to-have**: minor polish (single "actually", one Title Case heading)

### Phase 3 — Apply (with diff)

- If artifact has `humanize: auto-apply` in frontmatter → apply 🔴 + 🟡 automatically, leave 🟢 as comments
- If user invoked manually → present diff, ask for go-ahead
- If auto-chain triggered → apply 🔴 silently, surface 🟡 + 🟢 as one-line summary

After each edit, log the change in frontmatter `revision-notes:` if the artifact supports it.

### Phase 4 — Verify

Re-scan post-edit. Confirm no new tells introduced. Output one-line completion stamp:

```
✅ humanize pass complete · X 🔴 / Y 🟡 / Z 🟢 fixed · M residual flagged for human judgment
```

---

## Anti-Patterns (don't do)

- **Don't soften factual claims** that happen to use "the most" or "the largest" if they're verifiable and source-cited.
- **Don't strip technical vocabulary** if audience is technical (engineering, finance ICs read jargon as register marker).
- **Don't replace named entities** with generic ones to avoid name-dropping (those are facts).
- **Don't strip register markers** appropriate for a specific audience (JP keigo, formal CN business, etc.).
- **Don't loop** — if artifact already passed `/humanize` (frontmatter `humanize-passed: YYYY-MM-DD` recent), don't re-run unless content changed materially.

---

## Auto-Chain Contract

When auto-triggered (post any creative-writing artifact finalization):

1. Confirm artifact qualifies (per "When to Use" path/type list)
2. Announce: *"🔁 Auto-chaining /humanize on [name]. Add `humanize: skip` to frontmatter to opt out for future runs."*
3. Run Phase 1–4
4. Stamp frontmatter with `humanize-passed: YYYY-MM-DD` to prevent re-run
5. Return to caller with completion line + residual-flag summary

If artifact has `humanize: skip`, announce skip and stop.

Complete chain order matrix in [[09 Rules/auto-chain-style.md]] § Order when multiple chains apply.

---

## Linked

- Pattern catalogue (29 patterns + CN AI 套话): [[09 Rules/auto-chain-style.md]] § Humanize
- Source patterns: [blader/humanizer](https://github.com/blader/humanizer) (English) + [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) (Chinese)
- Companion rule: `[[me.md]]` (voice / register references)
