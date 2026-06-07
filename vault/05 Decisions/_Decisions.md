---
type: dashboard
tags: [dashboard, decision]
---

# Decisions Log

New decision: use the `decision` template (07 Templates/decision.md). One file per
decision, filed here. These views are read-only and update themselves.

## Due for review
```dataview
TABLE status, reversibility, review_on
FROM "05 Decisions"
WHERE type = "decision" AND review_on AND review_on <= date(today)
SORT review_on ASC
```

## Recent
```dataview
TABLE date, status, reversibility
FROM "05 Decisions"
WHERE type = "decision"
SORT date DESC
LIMIT 20
```

## One-way (irreversible) — handle with care
```dataview
TABLE date, status
FROM "05 Decisions"
WHERE type = "decision" AND reversibility = "one-way"
SORT date DESC
```

## Superseded
```dataview
TABLE date, supersedes
FROM "05 Decisions"
WHERE type = "decision" AND status = "superseded"
SORT date DESC
```

## By entity / topic (computed — never stale)
> Reverse view: every entity/project the decisions point at, with the decisions touching it.
> No materialised backlinks — this is computed from outbound links each load.
```dataview
TABLE rows.file.link AS "decisions"
FROM "05 Decisions"
WHERE type = "decision"
FLATTEN file.outlinks AS entity
GROUP BY entity
SORT length(rows) DESC
```

## Supersession chains
```dataview
TABLE supersedes AS "replaces", superseded_by AS "replaced by", status
FROM "05 Decisions"
WHERE type = "decision" AND (supersedes OR superseded_by)
SORT date DESC
```

## ⚠️ Integrity checks
> Broken supersession (marked superseded but no forward link):
```dataview
TABLE date, status
FROM "05 Decisions"
WHERE type = "decision" AND status = "superseded" AND !superseded_by
```
> Detached decisions (no outbound links — isolated from the graph; should be empty):
```dataview
TABLE date, owner
FROM "05 Decisions"
WHERE type = "decision" AND length(file.outlinks) = 0
```

## By method (review → Memory feedback loop)
> Decisions produced by a decision-method ([[09 Rules/methods]], `09 Rules/_methods`). When one hits `review_on`, fold the judged outcome into the producing method's `## Memory`. Headless equivalent: `method_review_feed.py`.
```dataview
TABLE method, status, reversibility, review_on
FROM "05 Decisions"
WHERE type = "decision" AND method
SORT method ASC, review_on ASC
```
