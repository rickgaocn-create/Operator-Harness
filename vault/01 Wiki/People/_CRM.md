---
type: dashboard
tags: [dashboard, crm]
---

# CRM — relationships to tend

Person notes stay where they are (anywhere in the vault). These views key off
`type: person` + `crm: true`, not folder location — so filing is cosmetic. Flip a
person's `crm: true` to enroll them; leave it false and they stay plain reference.

## Follow-ups due
```dataview
TABLE owed, last_contact, next_followup
WHERE type = "person" AND crm AND next_followup AND next_followup <= date(today)
SORT next_followup ASC
```

## Gone quiet (past their cadence)
```dataview
TABLE last_contact, cadence, org
WHERE type = "person" AND crm AND last_contact AND (date(today) - last_contact) > dur(cadence)
SORT last_contact ASC
```

## Open loops — I owe something
```dataview
TABLE owed, next_followup
WHERE type = "person" AND crm AND owed AND owed != ""
SORT next_followup ASC
```

## Everyone tracked
```dataview
TABLE org, relationship, last_contact, cadence
WHERE type = "person" AND crm
SORT last_contact ASC
```
