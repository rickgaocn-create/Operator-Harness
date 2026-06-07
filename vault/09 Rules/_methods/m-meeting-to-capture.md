---
type: method
id: m-meeting-to-capture
name: Meeting to capture
task-kind: capture/meeting/tasks-decisions
status: draft
deliverable: {{USER_NAME}}/org-owned tasks + decisions extracted from a meeting/source, wired to entities, proposed before write
calls-skills: [meeting-note, task-capture, capture-routing, relation-map]
grounds-in: [f-rigor-verification, f-strategic-systems]
precipitated-from: 09 Rules/tasks.md + 09 Rules/decisions.md capture protocol + meeting-note skill hand-offs
created: 2026-06-06
created-by: claude
---

# Meeting to capture

## Method
Templates turning a **meeting / transcript / brain-dump** into the right captured artifacts — tasks *and* decisions — under the capture discipline. Value-free: invokes verification + strategic-systems judgment ([[f-rigor-verification]], [[f-strategic-systems]]); the calls and routing are the operator's. A run proposes files; the operator confirms before they're written.

## Steps (DAG)

### ingest_source
**after:** —
**calls:** meeting-note
**reads:** the meeting / transcript / source note
Turn the raw source into structured notes (meeting-note Phase 4.5 surfaces action items + calls made).

### extract_owned
**after:** ingest_source
Pull only **{{USER_NAME}}/org-owned** action items and calls made. **Ownership filter (hard):** counterparty (对方侧) items stay in the source note, never become files.

### split_task_decision
**after:** extract_owned
Route each item: a thing to *do* → a **task**; a *call made* + reasoning → a **decision**. Never double-log — tactical/workstream-internal decisions go to the Action file's `## Decisions` table, strategic/forwardable ones to `05 Decisions/`.

### draft_tasks
**after:** split_task_decision
**calls:** task-capture
Draft tasks via task-capture: Operon `{{}}` syntax, chain-anchor, route by context-tag. **Batch ceiling ≤3 per write.**

### draft_decisions
**after:** split_task_decision
Draft decisions from `07 Templates/decision.md` (headings verbatim — `reflect.py` parses them), set `reversibility` + `review_on`. **≤3 per write.** A decision-shaped call may hand off to [[09 Rules/_methods/m-bd-partnership-call]].

### wire_relations
**after:** draft_tasks, draft_decisions
**calls:** relation-map
Weave outbound entity/project links (🔴 lane-isolation: never cross {{PROJECT_A}} ↔ {{ORG_B}} / {{ORG_A}} / {{ORG_D}}). Compute inbound via Dataview, don't materialize backlinks.

### propose_confirm
**after:** wire_relations
**Propose, then write.** Show the proposed task/decision files; confirm before writing. Never fabricate a task or decision the operator didn't make.

## Memory
- 2026-06-06 — **Ownership filter is hard.** Only {{USER_NAME}}/org-owned items become files; counterparty decisions/action-items stay in the source. (09 Rules/decisions.md, tasks.md)
- 2026-06-06 — **No double-logging.** One decision, one home — tactical → Action `## Decisions` table; strategic/forwardable → `05 Decisions/`; the Action table *links*, never copies.
- 2026-06-06 — **Batch ceiling ≤3** per write for both tasks and decisions; more → surface for triage, don't dump. Preserves capture quality.
- 2026-06-06 — **Propose, then write.** Capture is a decision surface; never auto-fabricate.
