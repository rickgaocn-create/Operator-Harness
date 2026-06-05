---
category: meta
name: skill-eval
description: Run the structural eval suite for gated skills. Use before/after non-trivial skill edits to catch path, rule, phrase, and structure drift.
model: claude-sonnet-4-6
allowed-tools: Bash, Read
last-major-rewrite: 2026-05-21
companion-rules: "[[09 Rules/skill-eval-gate.md]]"
---

# Skill: Skill Eval Runner

Static-invariant eval suite for the gated daily-driver and high-blast-radius skills. Catches the class of bug we hit on 2026-05-21 (path rename without skill-side update) in <5 seconds with no Claude tokens spent. Invoke Python through `.harness/resolve_runtime.py` when running the underlying scripts directly.

## Run

```bash
# All 7 skills
/skill-eval

# One skill
/skill-eval daily-note

# Machine-readable JSON (for CI / harness-health Section 2)
/skill-eval --json

# All active skill router descriptions + plugin-syntax protection
PY="$(python .harness/resolve_runtime.py python)"
"$PY" .claude/_eval-fixtures/skill_surface_lint.py
```

Exit codes:
- `0` — all green
- `1` — eval failures (read stdout for ✗ lines)
- `2` — runner error

## What it checks (per skill, per **`.claude/_eval-fixtures/eval-config/<skill>.yaml`**)

1. **Skill file exists + readable** — sanity
2. **read_paths exist** — every path the skill claims to read must be present in the vault (glob patterns skipped; `{today}` files soft-warn if missing)
3. **referenced_rules exist** — every **`09 Rules/<name>.md`** the skill links to must exist
4. **grep_invariants** — regex patterns that must hit ≥N times in the skill file (drift detector for refactor-orphan phrases)
5. **forbidden_phrases** — regex patterns that must NOT appear (e.g. post-rename, the old name must be gone)
6. **required_phrases** — literal substrings that must appear (load-bearing wording)
7. **structural** — line count bounds + max H2 sections (context-cost guardrail)
8. **referenced_filterSets** — Operon filter names referenced in embed blocks must exist in **`.operon/filters/<id>.json`**
9. **fixture_invariants** — checks against frozen snapshot files in **`.claude/_eval-fixtures/snapshot-2026-05-21/`**

Each check returns pass/fail + a short message. Run records persist to **`.claude/_eval-fixtures/eval-runs/run-YYYY-MM-DDTHH-MM-SS.json`** for trend tracking.

**Packaged skills:** when **`skill-package.yaml`** exists beside `SKILL.md`, the runner also checks that it declares the package tier, entrypoint, role, state reads/writes, required evals, and dashboard outputs. Thin skills remain SKILL.md-centric and do not need a manifest.

**Sibling router-surface check:** `skill_surface_lint.py` scans all active skill frontmatter descriptions for router budget (≤300 chars), mojibake-like text, and verifies `09 Rules/harness-surfaces.md` still protects Obsidian/Operon plugin syntax.

## What it does NOT check (and why)

**Behavioral correctness.** Whether `/daily-note` actually produces a good daily note. That needs Claude in the loop; expensive; out of scope here.

**Inter-skill consistency.** Whether `/task-capture`'s tag→file routing agrees with `/inbox-process`'s expectations. Future enhancement.

**Live Obsidian/Operon state.** Whether your live **`.operon/index.json`** reflects the right tasks. **`/harness-health`** covers that.

**Plugin syntax mutation safety.** `skill_surface_lint.py` verifies the protection rule exists, but it cannot prove every future edit preserved every live task line. Before editing plugin-fed lines, read `09 Rules/harness-surfaces.md` and `09 Rules/tasks.md`.

## Workflow

**Before** editing any skill in the daily-driver set (`daily-note`, `sync-day`, `task-capture`, `day-digest`, `replan`, `sanity`, `inbox-process`):

```bash
/skill-eval <name>     # baseline: should pass
```

**After** the edit, before committing:

```bash
/skill-eval <name>     # confirm still passes
git add ...
git commit -m "..."
```

**Failure case**: investigate the ✗ line. If your edit intentionally removed a referenced path (e.g. you removed support for **`06 Tasks/Personal.md`**), update the eval config to match. If you accidentally broke something, fix the skill.

## Adding eval coverage for a new skill

1. Copy **`.claude/_eval-fixtures/eval-config/inbox-process.yaml`** as a starter
2. Edit `skill:`, `skill_path:`, `read_paths:`, `referenced_rules:`, `grep_invariants:`, etc.
3. Run `/skill-eval <new-skill>` — iterate until green against current skill state
4. Commit the config alongside the skill change

## Packaging a core skill

Only daily-driver, stateful, or quality-gate skills become mini-project packages. Add **`skill-package.yaml`** beside `SKILL.md`, keep the skill itself as the user-facing contract, and declare `tier`, `entrypoint`, `role`, `state_reads`, `state_writes`, `required_evals`, and `dashboard_outputs`.

Do not add manifests to thin skills just for symmetry; packaging must reduce operational ambiguity, not create ceremony.

## Companion rule

**`09 Rules/skill-eval-gate.md`** codifies: daily-driver skill edits MUST pass evals before commit.

## Failure modes

If `skill_surface_lint.py` fails, shorten the skill frontmatter `description`, remove mojibake from description only, or restore plugin-syntax protection in `09 Rules/harness-surfaces.md`.

| Symptom | Fix |
|---|---|
| `runner_error` in result | Python or YAML issue. Resolve the interpreter with **`.harness/resolve_runtime.py python`**, then check **`.claude/_eval-fixtures/runner.py`** traceback. |
| All checks fail with `file not found` | Eval config has wrong `skill_path` — usually a path typo |
| `forbidden:<pattern> found N×` | A phrase that shouldn't be there is back (e.g. legacy emoji syntax post-Operon migration). Either remove from skill OR remove from eval config if intentional. |
| Hits=−1 with valid path | Runner couldn't read file. Likely permissions or encoding issue. |
