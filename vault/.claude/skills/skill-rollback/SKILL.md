---
category: meta
name: skill-rollback
description: List, snapshot, or restore archived skill versions. Use for emergency rollback after a bad edit, or snapshot before a major rewrite.
model: claude-sonnet-4-6
allowed-tools: Bash, Read
last-major-rewrite: 2026-05-21
companion-rules: "[[09 Rules/skill-versioning.md]]"
---

# Skill: Skill Rollback

Skill versioning + rollback for the operator harness. Pairs with **`/skill-eval`** for safe experimentation.

## Run

```bash
# List archived versions for a skill
/skill-rollback list daily-note

# Snapshot CURRENT SKILL.md as next archive version (call BEFORE editing)
/skill-rollback bump daily-note

# Restore most recent archived version (safety-archives current first; runs eval gate)
/skill-rollback rollback daily-note

# Restore specific version
/skill-rollback rollback daily-note v2
```

## Convention

```
.claude/skills/<name>/
├── SKILL.md                              ← live
└── SKILL.archive/
    ├── v1-pre-2026-04-22.md              ← oldest archive
    ├── v2-pre-2026-05-13.md
    └── v3-pre-2026-05-21.md              ← most recent (= what `rollback` defaults to)
```

Naming: `v<N>-pre-<YYYY-MM-DD>.md`. `N` monotonically increases; date is when the snapshot was taken (i.e., when the *next* edit was about to happen, hence "pre").

## Workflow

### Before a major rewrite

```bash
/skill-rollback bump daily-note         # archive current as v<next>
# ... edit SKILL.md ...
/skill-eval daily-note                  # validate the edit
git commit ...
```

### After a bad edit

```bash
/skill-rollback rollback daily-note     # restore most recent good version
# eval runs automatically; if green → done
git commit -m "rollback: daily-note → previous good state"
```

### After multiple bad edits (skip the most recent archive)

```bash
/skill-rollback list daily-note         # see all versions
/skill-rollback rollback daily-note v2  # explicit version pick
```

## Safety guarantees

1. **No silent destruction** — `rollback` ALWAYS snapshots the current live version first (as the next vN), so even if you rollback the wrong way you can roll forward.
2. **Eval gate** — if the skill has **`.claude/_eval-fixtures/eval-config/<name>.yaml`**, the eval runs after restore using the Python interpreter resolved by **`.harness/resolve_runtime.py`**. Failure surfaces a warning AND the skill is left in the restored state (not auto-reverted) — the user owns the next move.
3. **No git interaction** — rollback writes the filesystem; git commit is the user's call. This separates the destructive op (filesystem) from the durable op (git) so a botched rollback is easy to `git restore`.

## When NOT to use

- **Daily small edits** — don't bump on every typo fix. The convention is "major rewrite" — anything that materially changes behavior, structure, or contracts. The trial-log for the Operon migration is a good baseline: v1 → v2 was the right cadence.
- **Skills without eval coverage** — rollback works but you lose the gate. Acceptable; just know what you're doing.

## Companion rule

**`09 Rules/skill-versioning.md`** — convention details + when to bump.

## Failure modes

| Symptom | Fix |
|---|---|
| `no archived versions` | First rollback for this skill needs a prior bump. Use `bump` to create v1, OR copy SKILL.md manually as **`SKILL.archive/v0-<date>.md`**. |
| Eval fails after restore | Restored version is also broken (likely both pre- and post-edit had the same drift). Forward-fix instead: edit live + re-eval. |
| Want to undo a rollback | `rollback` archives the pre-restore state automatically. Use `/skill-rollback list <name>` to find the auto-archive (will be the highest vN). |
