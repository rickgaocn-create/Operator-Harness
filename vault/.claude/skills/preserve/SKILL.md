---
category: meta
name: preserve
description: Preserve session-level learnings into durable operating memory. Use when a correction or preference should shape future sessions, especially after /compress.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
# Skill: Preserve Learning

Extract permanent insights from the current session and write them into CLAUDE.md. Use this for things that should shape *every* future session, not just this one. CLAUDE.md is loaded into context at every session start — anything written here changes the baseline.

## When to Use

- A strategic pattern, convention, or decision is worth permanent memory
- Claude got something systematically wrong and should be corrected going forward
- OKR milestone hit or goal revised — update the Goals section
- After `/compress` when something rises above session-level importance
- User says "add this to your memory", "update CLAUDE.md", "remember this"

## What Belongs Here vs. Session Log

| Preserve → CLAUDE.md | Compress → Session Log |
|---|---|
| Project conventions & BD patterns | Specific decisions from today |
| Strategic insights that generalize | Solutions to one-off problems |
| Updated OKRs / milestones / goals | What we discussed this session |
| Things Claude should always know | Session-specific context |
| Hard lines or new rules | Temporary blockers |

The litmus test: *Will this be true and useful 6 months from now?* If yes → preserve. If no → compress (or lose it on purpose).

---

## Phase 1: Identify Permanent Insights

> "What from this session should Claude always know going forward?"

Common candidates:
- **Goals / OKRs** — milestone hit, KR updated, timeline shifted
- **Claude's Role** — a workflow that worked or didn't
- **Hard Lines** — new non-negotiables surfaced in practice
- **Projects** — new partner landed, deal status changed, key insight about a target
- **Strengths / Weaknesses** — a behavioral pattern noticed in operation

---

## Phase 2: Auto-Archive Check

```bash
wc -l CLAUDE.md
```

If CLAUDE.md exceeds **280 lines**, trigger auto-archive before adding new content. The threshold matters because CLAUDE.md is loaded every session — past ~280 lines, attention to early sections degrades and the file becomes slow to read in full.

1. Identify archivable content: completed milestones, resolved blockers, stale project details, old Weekly Update entries
2. **Never archive:** Who I Am, Claude's Role, Hard Lines, Folder Structure, active OKRs, the Skills Library, the Task Capture Protocol
3. Move archivable content to `CLAUDE-Archive.md` (create if needed, append if exists). Preserve it; don't delete.
4. Re-read CLAUDE.md after the archive — confirm it's lean and the structure still scans.

---

## Phase 3: Write the Update

Make targeted edits to the specific section. Don't restructure. Don't rewrite surrounding content. Append or update in place.

Show the proposed change first:

> "Adding to CLAUDE.md under [Section Name]:
> [proposed text]
> OK to write?"

Write only after confirmation.

---

## Phase 4: Confirm

> "Preserved: [brief description] → [[CLAUDE.md]] § [section]. File is now [n] lines."
