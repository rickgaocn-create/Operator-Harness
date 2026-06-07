---
category: work
name: meeting-note
description: Turn meeting input into a structured vault note. Plain mode handles normal syncs; --deep handles high-stakes/forwardable meetings and auto-chains to /biz after save.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/tasks.md]]"
  - "[[09 Rules/decisions.md]]"
  - "[[09 Rules/crm.md]]"
  - "[[09 Rules/attribution-discipline.md]]"
companion-skills:
  - "[[.claude/skills/meeting-summary/SKILL.md]]"
  - "[[.claude/skills/attribution-lint/SKILL.md]]"
created: 2026-05-14
last-restructure: 2026-05-21
created-by: claude
audit-trace: "2026-05-14 merged /meeting-note + /meeting-note-deep into single skill with --deep flag. 2026-05-21 split into SKILL.md (this · ~140 lines) + references/{deep-mode-core, source-verification, deep-variants, nda-and-bilingual, anti-patterns}.md per Phase 3.2.b restructure (was 641 lines)."
---

# Skill: Meeting Note (unified · plain default · `--deep` for board-grade)

Turn meeting input into a structured vault note. Default = plain mode (5-phase log). Add `--deep` for board-grade SCORARO-grammar 概要 memo with full Variant A/B/C/D mode support, NDA handling, source verification, 中英混用 governance.

## Mode Routing

| Trigger | Mode |
|---|---|
| `/meeting-note` (no flag) OR plain triggers | **Plain** — internal sync, 1:1, quick partner call, casual intake |
| `/meeting-note --deep` OR `/meeting-note-deep` OR any deep trigger phrase | **Deep** — board-grade memo |
| Auto-detect → **Deep** when *any* of: external counterparty at BD/C-level · commercial terms on table · strategic alternatives in play · output will forward to {{PERSON}}/董事会/JP board · ≥3 structured Q&A exchanges |
| Cross-meeting synthesis (≥2 source notes) | **Switch to [[.claude/skills/meeting-summary/SKILL.md]]** — that skill enforces attribution discipline structurally |

If auto-detect flips to deep but user invoked plain — surface plain-text 1-line: *"Looks board-grade — switch to `--deep`?"* and await reply.

---

## Plain Mode (default · inline)

Turn a transcript / voice memo / bullet notes into a structured vault note with proper frontmatter. Surface {{USER_NAME}}'s action items as tasks in **`06 Tasks/Inbox.md`**. Counterparty's items stay in the note only.

### When to Use (plain)

- After any meeting — user pastes transcript, voice memo dump, or bullet notes
- "Process this meeting", "log this call", "capture this", "meeting note for [X]"
- Internal sync, 1:1 catch-up, quick partner call without commercials

### Plain · 5 phases

#### Phase 1: Extract details
From the dump, extract:
- **Date** — default today if not stated
- **Attendees** — who was there, counterparty org
- **Project track** — {{PROJECT_A}}, {{ORG_B}}, or other
- **Meeting type** — BD call, internal sync, partner review, govt relations, M&A diligence, vendor eval

Ask only when something is genuinely unrecoverable from context. Don't assume.

#### Phase 2: Route to folder
| Track | Destination |
|---|---|
| {{PROJECT_A}} BD / partnership | **`03 Projects/{{PROJECT_A}}/Meetings/YYYY-MM-DD-[counterparty].md`** |
| {{ORG_B}} M&A / AIX | **`03 Projects/{{ORG_B}}/Meetings/YYYY-MM-DD-[counterparty].md`** |
| Cross-project / other | **`04 Notes/Meetings/YYYY-MM-DD-[topic].md`** |

Create the `Meetings/` subfolder if missing.

#### Phase 3: Format the note

```markdown
---
type: meeting
date: YYYY-MM-DD
project: [{{PROJECT_A}} | {{ORG_B}} | other]
attendees: [name1, name2]
counterparty: [org or person name]
meeting_type: [bd | internal | partner | govt | ma | vendor]
status: completed
---

# Meeting: [Counterparty] — YYYY-MM-DD

## Context
[One sentence: why this meeting was called and what was on the table]

## Key Points
- 

## Decisions Made
- 

## Action Items
- [ ] [owner]: [action] #context-tag 📅 YYYY-MM-DD

## Next Steps / Follow-up
- 

## Raw Notes
[Paste original notes or transcript here]
```

#### Phase 4: Surface {{USER_NAME}}-owned action items
For each action item where **{{USER_NAME}} is the owner**, propose appending to **`06 Tasks/Inbox.md`** per `/task-capture` rules — same line format, context tag, priority, due date. Show what will be written before appending; confirm.

Counterparty-owned items stay in the meeting note's `## Action Items` section only.

#### Phase 4.5: Surface decisions & CRM touches
- **Decisions** — if `## Decisions Made` holds an {{USER_NAME}}-owned call (decided / go-no-go / a chosen option among alternatives / a reversal), propose a decision file per [[09 Rules/decisions.md]] (one file in `05 Decisions/`, from `07 Templates/decision.md`, ≤3 per write, confirm before writing). Counterparty decisions stay in the note.
- **CRM** — for each attendee whose `01 Wiki` note has `crm: true`, per [[09 Rules/crm.md]]: bump `last_contact` to the meeting date and append a `## Log` line; if an {{USER_NAME}}-owned action targets them, set `owed` + `next_followup`. Enrolled people only — never auto-enrol.

#### Phase 5: Confirm
> "Meeting note saved: [[path/to/note.md]]. [n] action items queued to Inbox. [d] decisions logged. [c] contacts updated."

---

## Deep Mode (`--deep` · references-based)

Process a high-stakes business meeting (vendor negotiation, partnership pitch, M&A diligence, board-adjacent) into a **scannable, 概要-forward** minute that can be forwarded to leadership without further editing.

**Origin:** Template extracted from `【{{ORG_C}}商务】EPIC Games-Unreal Engine 商务洽谈会议纪要` (2026-03-18) — praised by {{PERSON}} as "very clear." The structure encodes SCORARO grammar (Situation → Complication → Answer → Rationale → Action) into a 4-section layout.

### Deep · phase index (load references as needed)

| Phase | Action | Reference to load |
|---|---|---|
| 0 | Read this dispatch + Phase 1 prep | (this file) |
| 1 | Extract header. **If source includes AI-transcript OR multi-speaker summit with official agenda → load:** | [[references/source-verification.md]] |
| 1.5 | Detect meeting mode (Q&A / one-way / we-present / hybrid / industry-summit). Apply Variant A/B/C/D selection. **Load:** | [[references/deep-mode-core.md]] |
| 2 | Route to canonical folder. **Load Phase 2 section in:** | [[references/deep-variants.md]] |
| 3 | Fill the template (核心结论 → Variant section 1 → §2 战略背景 → §3 痛点匹配表 → §4 行动计划). **Load:** | [[references/deep-variants.md]] |
| — | If meeting includes NDA content OR significant CN/EN mixing → load: | [[references/nda-and-bilingual.md]] |
| 4–6 | Surface action items / Wiki cross-link / Confirm. **In:** | [[references/deep-variants.md]] |
| 7 | Auto-chain `/biz` + Outcomes-pattern grader loop. **In:** | [[references/deep-variants.md]] |
| Pre-save | Self-audit against anti-patterns. **Load:** | [[references/anti-patterns.md]] |

### Hard rules (always applied in deep mode — summarized; details in references)

- **Never Fabricate Q&A.** Use Variant B if user didn't actually ask questions. ([[references/deep-mode-core.md]] § HARD RULE)
- **Party-Attribution Discipline.** Any `**[party]**：[claim]` must trace to that party's literal source. Cross-source synthesis → switch to `/meeting-summary`. Canonical: [[09 Rules/attribution-discipline.md]].
- **Decisions + CRM.** {{USER_NAME}}-owned decisions → `05 Decisions/` per [[09 Rules/decisions.md]]; enrolled-attendee (`crm: true`) contact state → per [[09 Rules/crm.md]]. Surface alongside the Phase 4 action items.
- **Voice Register C** for executive summary sections. ([[references/deep-mode-core.md]])
- **Source Verification** for AI-transcripts + official agendas. ([[references/source-verification.md]])
- **NDA marking** in frontmatter + section headers if applicable. ([[references/nda-and-bilingual.md]])

---

## Quick decision tree

```
User invokes / triggers meeting-note
  │
  ├─ ≥2 source meeting notes? → switch to /meeting-summary (HARD)
  │
  ├─ Plain mode (no --deep flag, no deep auto-detect)
  │    → 5 phases inline above. Done.
  │
  └─ Deep mode (--deep flag OR auto-detect flips)
       → Load deep-mode-core.md (modes + register C + hard rules)
       → If AI-transcript / summit → also load source-verification.md
       → Load deep-variants.md (template + phases 2-7)
       → If NDA / bilingual concerns → also load nda-and-bilingual.md
       → Pre-save: load anti-patterns.md for self-audit
       → Save → Phase 7 auto-chain /biz → biz-doc-critic grader loop
```
