---
layer: platform
paths:
  - ".claude/skills/*/SKILL.md"
  - ".claude/skills/*/SKILL.archive/**"
  - ".claude/skills/skill-rollback/SKILL.md"
canonical_skill: ".claude/skills/skill-rollback/SKILL.md"
created: 2026-05-21
last-major-rewrite: 2026-05-21
---

# Skill Versioning Rules

> When and how to snapshot skill files for safe experimentation + rollback.

## Convention

```
.claude/skills/<name>/
├── SKILL.md                              ← live
└── SKILL.archive/
    └── v<N>-pre-<YYYY-MM-DD>.md          ← archived snapshots
```

`v<N>` monotonically increases. `<date>` is when the snapshot was taken (NOT when the archived version was originally written — that's tracked by the archived file's own `last-major-rewrite:` frontmatter).

## When to bump (snapshot current as next archive)

A bump (`/skill-rollback bump <name>`) is appropriate when ANY of the following are true:

1. **Major rewrite ahead**: about to restructure phases, change input/output contract, rename load-bearing concepts
2. **Migration boundary**: the skill is being adapted for a system-wide change (Operon migration, plugin swap, model tier shift)
3. **Recovery insurance**: you're about to do something experimental and want a known-good baseline to revert to
4. **Pre-promotion**: a long-running branch of edits is about to land — bump first so the pre-branch state is captured

Don't bump on:
- Typo fixes
- One-line clarifications
- Comment additions
- Frontmatter-only edits (unless changing `model:`, `allowed-tools:`, or the `description:` `Trigger on` clause — those are contracts; see Hard Rule 6)

## Cadence guideline

A daily-driver skill (`daily-note`, `sync-day`, `task-capture`, `day-digest`, `replan`, `sanity`, `inbox-process`) typically should have 2-4 archived versions per quarter. Fewer = under-snapshotting (rollback options limited); more = over-snapshotting (noise + repo bloat).

A low-frequency skill (`scaffold`, `wangyue-pitch-deck`) might have 0-1 archives total — bump only at genuine inflection points.

## Eval gate integration

When a skill has **`.claude/_eval-fixtures/eval-config/<name>.yaml`** AND `/skill-rollback rollback` runs, the eval suite runs after restore. Behavior:

- **Eval green**: rollback succeeds silently
- **Eval red**: warning surfaced; skill remains in restored (failing) state. User chooses: forward-fix OR rollback to a different version

The rollback never auto-reverts a failed restore — that would mask a real problem. The user owns the next move.

## Naming

- ✅ `v3-pre-2026-05-21.md`
- ✅ `v10-pre-2026-06-15.md`
- ❌ `v3.md` (no date)
- ❌ `pre-2026-05-21.md` (no version number)
- ❌ `v3-pre-may21.md` (non-ISO date)

`/skill-rollback list <name>` sorts by numeric version (extracted from `v<N>` prefix). Naming consistency is what makes that work.

## Hard Rules

1. **Bumps and rollbacks are filesystem operations, not git operations.** They write `.md` files. Git commit is the user's call. This separation makes botched rollbacks recoverable via `git restore`.

2. **Rollback ALWAYS snapshots current state first.** Even if rollback target is wrong, the pre-rollback state is recoverable (as the next-highest archived vN).

3. **Never delete an archive.** Archived versions are the audit trail of skill evolution. Delete only when the skill itself is being archived (skill-level retirement, not version-level).

4. **Archive files inherit eval coverage.** A skill's eval-config doesn't care which `SKILL.md` it's checking — the runner reads the live file. So restoring an old version + running eval = same check as evaluating the new version. This is intentional: rollback validity = current-eval-spec validity.

5. **Major-version frontmatter discipline**: bumped live versions should update `last-major-rewrite:` to today's date. Archived versions keep their original `last-major-rewrite:` for historical accuracy.

6. **Never strip a skill's `Trigger on …` clause when tightening its `description`.** The `description` is router metadata for AI eyes, not user docs — [[09 Rules/skill-routing.md]] weights the `Trigger on` phrase match at **2.0** (the highest routing signal). A "make it human-readable" pass may shorten the summary, but MUST preserve the trigger phrases (slash commands, NL aliases incl. CN, autonomous-task notes). Dropping them silently degrades natural-language auto-triggering while slash commands + scheduled jobs keep working — so the regression is **invisible until something doesn't fire**. Origin: 2026-05-27 — a readability pass stripped triggers from `daily-emit` / `daily-note` / `day-digest`; caught only on manual diff.

## Migration

- 2026-05-21 — convention created during Tier 7 Phase 3 build. Backfill schedule:
  - Daily-driver skills (7): bump v1-pre-2026-05-21 on next edit each
  - Low-frequency: bump opportunistically when next touched
  - No retroactive bumps required (the convention starts from here forward)
