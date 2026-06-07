---
type: decision
date: <% tp.date.now("YYYY-MM-DD") %>
status: decided
reversibility: reversible
owner:
review_on:
supersedes:
superseded_by:
method:
tags: [decision]
---

# <% tp.file.title %>

## Decision
<!-- One sentence: what was decided. -->

## Context
<!-- What situation forced the call? What did you know at the time? -->

## Options considered
- **Option A** —
- **Option B** —

## Rationale
<!-- Why this one. State the trade-off you knowingly accepted. -->

## Consequences / watch for
<!-- Leading indicators that this was right or wrong; when to revisit. -->

## Updates
<!-- Append-only, newest-first. Record how this decision evolved WITHOUT rewriting the call above.
     - YYYY-MM-DD — what changed / what we learned / who. (full reversal → use supersedes/superseded_by instead) -->

## 关联文档
<!-- Outbound links only — the entities/projects/people this decision concerns. Obsidian backlinks +
     the dashboard give the reverse view, so entity pages never carry a stale decision list.
     Sub-bucket, never flat (house format per [[09 Rules/channel-person-wiki.md]]). 🔴 no cross-lane links. -->
### 平台 / 项目
- 
### 相关决策
- 
### 来源
- 

<!--
FIELD NOTES
  status        proposed | decided | superseded
  reversibility reversible | one-way   (one-way = costly/impossible to undo — decide slower)
  review_on     YYYY-MM-DD to resurface this in the dashboard; leave blank if no review needed
  supersedes    [[link]] to a prior decision THIS one replaces (and set that one's status: superseded + superseded_by: [[this]])
  superseded_by [[link]] to the newer decision that replaced this one (set when this becomes status: superseded)
  method        m-<slug> if a decision-method (09 Rules/_methods) produced this call — closes the review→Memory loop (09 Rules/methods.md); blank for hand-made calls
  Updates       evolution log — append, don't rewrite. 关联文档 — outbound entity/project links.
-->
