---
category: meta
name: resume
description: Brief the session on active OKRs, current priorities, recent decisions, and open tasks. Use /resume at session start or when returning after a break.
model: claude-sonnet-4-6
allowed-tools: Read, Glob, Grep, Bash
---
# Skill: Resume Session

Brief Claude on the current state of the vault — active OKRs, this week's plan, recent decisions, overdue tasks — so the session starts informed instead of cold. Run this first, before diving into work.

## When to Use

- Starting any new work session
- Picking up after a break
- `resume [n]` — load last n session logs (default: 3)
- `resume [topic]` — filter sessions to ones mentioning a topic (e.g. `resume {{PROJECT_A}}`)
- `resume 5 BD` — last 5 sessions filtered to BD content

## How It Works

1. Pull current state from CLAUDE.md (already in context) + Time pillar files
2. Scan recent session logs for context
3. Surface overdue / high-priority open tasks
4. Deliver a tight briefing — under 30 seconds to read — and ask what's first

---

## Phase 1: Pull Current State

CLAUDE.md is already loaded. Pull from it:
- **Active OKRs** — {{PROJECT_A}} + {{ORG_B}} Q2 key results
- **Current Projects** — status of each active track
- **Weekly Update block** — last manual update (legacy; being phased toward the weekly file's Friday Review)

Then load Time pillar context:

```bash
ls -t "04 Notes/weekly/"*.md 2>/dev/null | head -1   # current week file
ls -t "04 Notes/12-week/"*.md 2>/dev/null | head -1  # current quarter file
```

From the current week file, extract `## This Week's 1-3 Big Rocks` — that's the operative plan, not whatever's stale in CLAUDE.md.

---

## Phase 2: Scan Session Logs

```bash
ls -t "04 Notes/Session Logs/"*.md 2>/dev/null | head -10
```

If the folder doesn't exist, skip. Otherwise read the most recent 3 logs (or n if specified). Extract from each:
- **Topics / Projects** covered
- **Decisions Made**
- **Key Learnings**
- **Pending Tasks** still open

If a topic filter was given:

```bash
grep -rl "[topic]" "04 Notes/Session Logs/" 2>/dev/null | head -5
```

---

## Phase 3: Check Open Tasks

Skim **`06 Tasks/Inbox.md`** for:
- **Overdue** — `📅` date before today
- **High priority** — `⏫` or `🔼`

Don't read the file line-by-line — just flag the actionable blockers. The briefing's job is to call out what should drive today.

---

## Phase 4: Deliver Briefing

Output should be scannable in under 30 seconds:

```
## Session Briefing — YYYY-MM-DD

**This week:** [[YYYY-Www]] — Big Rocks: [from weekly file]
**Last session:** [date] — [one-line summary]
**{{PROJECT_A}} track:** [current OKR status / next node]
**{{ORG_B}} track:** [current OKR status / next node]
**Pending decisions:** [from Weekly Update block / weekly file]
**Overdue tasks:** [list, or "none"]
**Recent decisions to know:** [2-3 bullets from session logs]

---
What are we working on today?
```

The "This week" line is what makes this briefing different from raw CLAUDE.md — it grounds the session in the live cascade, not in possibly-stale strategic copy.
