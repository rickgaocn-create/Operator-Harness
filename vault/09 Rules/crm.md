---
type: rule
created-by: claude
created: 2026-06-05
description: "Person-lifecycle overlay (CRM) on Wiki person notes. Complements relation-map (graph topology); this rule governs cadence/contact state, not links."
---

# CRM — person lifecycle overlay

A cadence + contact-state layer on top of existing `01 Wiki` person notes. **Orthogonal to `relation-map`**: relation-map weaves the `## 关联文档` graph (who connects to whom); CRM tracks *when you last touched someone and what you owe them*. Neither owns the other's fields.

## Enrolment (opt-in)

A person is in the CRM only when their note carries `crm: true`. Default is `false` — most Wiki people stay plain reference notes. Enrol only people you actively tend (investors, partners, key press/BD). Fields (from `07 Templates/person.md`):

| field | meaning |
|---|---|
| `crm` | `true` to track; `false`/absent = reference only |
| `relationship` | investor / partner / team / press / vendor / … |
| `cadence` | desired touch frequency as a duration: `7d`, `30d`, `90d` |
| `last_contact` | `YYYY-MM-DD` of most recent real contact |
| `next_followup` | `YYYY-MM-DD` you intend to reach out |
| `owed` | what **you** owe them now; blank = nothing open |

## Capture (what the note pipeline stamps)

When a meeting/contact note involves an **enrolled** person:

- **Bump `last_contact`** to the note's date, and append one line to that person's `## Log` (newest first): `- YYYY-MM-DD — <one-line what happened>`.
- If an **{{USER_NAME}}-owed** action item targets that person, set `owed` to the deliverable and `next_followup` to the action's `dateDue`. Clear `owed` when the deliverable ships.

Only stamp enrolled (`crm: true`) people — never auto-enrol. Patch the frontmatter in place; don't rewrite the bio.

## Surfacing

`01 Wiki/People/_CRM.md` renders follow-ups due, contacts past cadence, and open loops. The daily digest echoes "follow-ups due / gone quiet" so they don't rot in a dashboard nobody opens.

## Discipline

- Opt-in only; don't CRM-ify the whole Wiki.
- State in frontmatter, history in the note's `## Log` — no separate interaction files.
- Patch, don't paraphrase the person's existing note.
