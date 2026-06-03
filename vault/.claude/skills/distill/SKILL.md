---
category: work
name: distill
version: 0.1
description: Distill a personal brain dump from 00 Raw into existing workstreams before creating anything new. Reconcile first, then route Action/Task/Card outputs under review gate.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/raw-immutable.md]]"
  - "[[09 Rules/action.md]]"
  - "[[09 Rules/cards.md]]"
  - "[[09 Rules/tasks.md]]"
---

# Skill: Distill (brain dump → reconciled vault routing)

Take a concentrated free-write — you typed your thinking into a file in `00 Raw/` without organizing it — and turn it into vault state: extract the threads, **reconcile them against the workstreams that already exist**, sharpen the gaps by interview, and route the result across Card / Time / Action pillars under a review gate.

> The value is **reconciliation, not generation.** A good distill mostly *merges into existing Action streams and catches contradictions* — it spawns new files only where no workstream exists. If a run produces a pile of parallel notes, it did the wrong thing.

## When to Use

- You typed a brain dump / 口喷 into `00 Raw/` (e.g. `Mind notes.md`, `braindump-YYYYMMDD.md`) and want it distilled + routed.
- "/distill", "distill my thinking", "process my mind notes", "整理我的脑暴".
- A concentrated thinking session whose output should land across tasks/actions/cards, not just be summarized.

**Don't invoke for:**
- External clipping / article / web content → `/source-ingest` (Card/Wiki KB layer).
- Meeting transcript with attendees → `/meeting-note` or `/meeting-note-deep` (run first; `/distill` is for solo monologue).
- Triage sweep of many `00 Raw/` files + overdue tasks → `/inbox-process`.
- Just capturing atomic todos → `/task-capture`.

## Principles

1. **Reconcile before spawn.** Phase 3 (search existing workstreams) runs before any drafting. Merge into a live Action stream; propose a new Action file only when no workstream owns the thread.
2. **Never silently overwrite a contradicting record.** If the dump conflicts with an existing Action decision/blocker (e.g. "B站 exited the venue" vs "B站 wants on-site QR"), surface the conflict and let the user reconcile. Distillation that hides contradictions is worse than no distillation.
3. **The dump is the source.** Treat it as raw provenance: never edit its body; cite it as `source-note:` in every Card; keep it (don't move/delete). Optional `distilled: YYYY-MM-DD` frontmatter stamp at the end.
4. **Delegate, don't reimplement.** Tasks → `/task-capture` (≤3/surface, no hand-rolled Operon). Cards follow `[[09 Rules/cards.md]]`. Action files follow `[[09 Rules/action.md]]`. Reference the rule, don't duplicate it.
5. **Review gate before Cards/Actions.** Propose the full execution plan; write only on go-ahead (honors the Action Auto-Creation Policy + Card discuss-before-draft).
6. **Catch the user's own flagged errors.** A dump may contain memory/typing slips (the writer often says so). Surface name/date/number uncertainties as accuracy flags — don't propagate them silently.

## How It Works

**Phase 1 — Locate & read.** Default to the explicit path arg, else the most-recent `*.md` in `00 Raw/` root (exclude `Clippings/`, `_processed/`, daily-style `YYYY-MM-DD.md`). Read it whole. If it's actually an external clipping or a meeting transcript → stop and redirect to the right skill.

**Phase 2 — Extract threads → distilled map.** Pull the distinct threads (not topics — what the writer is *trying to figure out / decide / track*). Group into domains. Number them. Note accuracy flags (ambiguous names/dates/numbers).

**Phase 3 — Reconcile against existing state (the core).** For each thread, search before proposing:
```bash
# existing workstreams + chain-anchors
ls "10 Action/11 12-Week" "10 Action/12 Active" "10 Action/13 Maybe"
grep -rl "{thread keyword}" "10 Action" "03 Projects" "04 Notes" 2>/dev/null
```
Build a routing table: `thread → existing workstream (append) | no home (candidate NEW Action) | Card | Task`. Read each matched Action file to learn its `chain-anchor` (tasks must bind to it) and to detect contradictions.

**Phase 4 — Present map + proposed routing + flags.** Show the thread map, the routing table, the contradiction flags, and any accuracy flags. Resolve blocking clarifications first (a contradiction can block routing).

**Phase 5 — Interview (one question at a time).** Highest-leverage thread first. Cover: OKR framing for new-direction threads (force a measurable end-state or mark KR `TBD` honestly); decisions with deadlines; ambiguities the routing depends on. Plain-text numbered pickers per the AskUserQuestion-in-text rule — **never** the AskUserQuestion tool. Skip if the dump is already crisp.

**Phase 6 — Propose execution plan → REVIEW GATE.** Enumerate exactly what will be written/appended (which Streams, which new files, which tasks, which cards). Await go-ahead; accept per-item vetoes.

**Phase 7 — Execute.**
- **Action Streams** — append date-stamped, newest-at-top, per `[[09 Rules/action.md]]`; update Decisions/Blockers where the dump changes them.
- **New Action files** — propose then write (never auto-create); `11 12-Week/` if OKR-tied (else `12 Active/`); declare an immutable `chain-anchor`.
- **Tasks** — hand to `/task-capture` (≤3 per surface, bound to the workstream's `chain-anchor`).
- **Cards** — draft to `02 Cards/_inbox/` per `[[09 Rules/cards.md]]`, `status: draft`, `source-note: "[[<dump>]]"`. **Dedup** against harvest-candidates already parked in the matched Action files — cross-link, don't double-write.

**Phase 8 — Confirm + backlink.** Tight summary table of what landed and where. Optionally stamp the dump `distilled: YYYY-MM-DD`. Suggest follow-ups: `/okr` if a thread is OKR-altering; `/card-lint` once `_inbox` cards accumulate.

## Hard Rules

- **Reconcile before spawn.** No new Action file until Phase 3 confirms no existing workstream owns the thread — and then *propose*, never auto-create.
- **Surface contradictions; never overwrite silently.** The dump is newer but not automatically authoritative — the user reconciles.
- **Never edit the dump's body.** Frontmatter stamp only. Keep the file (don't move/delete) — it's the provenance.
- **Tasks always via `/task-capture`.** ≤3 new per surface per write; bind to the workstream `chain-anchor`.
- **Cards to `_inbox/` by default.** Brain-dump synthesis is fresh/unverified; refine at Friday review or via `/card-lint`. Every card cites the dump.
- **One question at a time; plain-text pickers only.** Never AskUserQuestion (invisible on Discord/AFK).
- **Review gate before any Card/Action write.**

## Integration with Other Skills

| Trigger | Hand-off |
|---|---|
| Thread surfaces atomic todos | `/task-capture` (≤3/surface, chain-anchor bound) |
| Thread has no owning workstream | Propose new Action file per `[[09 Rules/action.md]]`; wait for go-ahead |
| Thread is OKR-altering or defines a new track | `/okr` (Mode A create / Mode B check-in) |
| Dump is actually an external clipping/article | Redirect to `/source-ingest` |
| Dump is actually a meeting transcript | Redirect to `/meeting-note` / `/meeting-note-deep` |
| `_inbox/` cards accumulate (5+) | Recommend `/card-lint` |

## Failure Modes

| Symptom | Fix |
|---|---|
| Dump maps entirely to existing workstreams | That's success — append Streams + confirm, 0 new files. Don't manufacture new files for symmetry. |
| Dump contradicts a live Action record | Flag the conflict in Phase 4; let the user pick which is current. Never silently rewrite. |
| Thread is a pure external fact | Route to `01 Wiki/` via `/source-ingest`, not a Card. |
| Thread too vague to route | Interview harder; if still vague, park as an open question in the nearest workstream, don't force a task. |
| Many threads (6+) | Process highest-leverage first; offer to defer the long tail to a follow-up. |
| A new-direction thread can't yet state a KR | Write the Action file with `okr-link: TBD` + a blocker to create the track; don't fabricate a metric. |

## Notes

- **v0.1** — validated 2026-05-27 on `[[Mind notes]]` (typed dump). Voice→transcript front-end (lark-minutes) intentionally deferred; the typed-dump path is the supported input for now.
- Future structural eval before any version bump: see `[[09 Rules/skill-eval-gate.md]]`.
