---
category: meta
name: judgment-draft
description: Draft corrections from the judgment-queue for human approve/veto (the extraction step as a review gate). Use when the brief shows pending judgment candidates / "distill due", or on "/judgment-draft" / "drain the judgment queue". Drafting is Tier-A (auto); promotion stays human.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/autonomy-tiers.md]]"
  - ".claude/_state/corrections-README.md"
---

# Skill: Judgment Draft (queue → drafted corrections → approve/veto)

Turns the judgment-extraction chore from *"extract from scratch"* into *"approve a clean draft."* This is the missing step between `judgment_capture.py` (which flags raw candidates into `judgment-queue/`) and `corrections.jsonl` (the approved learn-arrow store). It lowers the operator's recurring load **and** feeds the under-fed loop.

> **Tier discipline ([[09 Rules/autonomy-tiers.md]]):** drafting to a staging surface is **Tier A** (act + log, no confirm). Moving a draft into `corrections.jsonl` and any promotion to a rule is **Tier B** (human approve). Never auto-promote.

## When to use
- The SessionStart brief shows `N jdg` candidates or `distill due (N new)`.
- "/judgment-draft", "drain the judgment queue", "draft the corrections".
- After a session with notable {{USER_NAME}} corrections, to capture them before they evaporate.

## How it works

**Phase 1 — Read + filter.** Read every `.claude/_state/judgment-queue/*.json`. Apply the precision filter from `judgment_capture.py` (`is_noise`): drop hook/system self-talk (`Stop hook feedback`, foundational-lint output, briefs), bare acks, and the agent's own channel-voice. Recall is already wide upstream; here precision matters.

**Phase 2 — Dedup.** Read `corrections.jsonl`. Drop any candidate already captured (match on session + the gist of `ai_output`/`correction`). A queue file may be partially hand-captured already.

**Phase 3 — Draft.** For each surviving genuine candidate, write ONE line to `.claude/_state/corrections-drafts.jsonl` (the staging surface — isolated so unreviewed drafts never reach the live store or inflate the `new` backlog) in the `corrections.jsonl` schema, with `status: "draft"`:
`{ts, session, skill, ai_output, correction, why, candidate_rule, touches:{values,frameworks}, polarity, status:"draft"}`.
Judge each: is this a real **values / taste / prior** signal, or noise/restatement? Only draft genuine judgment events.

**Phase 4 — Present for approval (terse, batched).** Show the whole batch at once, one line each: `polarity · candidate_rule — why (≤12 words)`. This is the operator's only decision surface — keep it scannable (conclusion-first). Ask: keep which / drop which / edit which.

**Phase 5 — Apply on confirm (Tier B).** For kept drafts: move the line into `corrections.jsonl` with `status: "new"` (enters the normal new → distilled → promoted lifecycle). Drop rejected. Then delete the fully-consumed `judgment-queue/*.json` files. Confirm what landed.

## Hard rules
- **Drafts are isolated.** Write to `corrections-drafts.jsonl`, never directly to `corrections.jsonl`. Only approved drafts move over, as `status:new`.
- **Never auto-promote.** This skill produces `new` corrections at most; turning a correction into a rule/Card/rubric is the separate human-gated distill/promotion flow.
- **Filter before drafting.** Run the `is_noise` precision pass; don't draft hook self-talk or acks.
- **Dedup against `corrections.jsonl`** before drafting — no double-capture.
- **Batch, don't drip.** Present all drafts in one pass for one approval, not one-at-a-time.
- **Clear consumed queue files** only after their candidates are dispositioned (kept or explicitly dropped).

## Failure modes
| Symptom | Fix |
|---|---|
| Drafted noise (hook output, acks) | `is_noise` filter not applied — re-run Phase 1 filter |
| Draft duplicates an existing correction | Phase 2 dedup missed it — drop the draft |
| Drafts written straight to `corrections.jsonl` | Wrong — drafts go to `corrections-drafts.jsonl`; move on approval only |
| Queue file deleted before approval | Never delete in Phase 1–4; only Phase 5 after disposition |
