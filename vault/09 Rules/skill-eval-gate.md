---
layer: platform
paths:
  - ".claude/_eval-fixtures/**"
  - ".claude/skills/skill-eval/SKILL.md"
canonical_skill: ".claude/skills/skill-eval/SKILL.md"
created: 2026-05-21
last-major-rewrite: 2026-05-21
---

# Skill Eval Gate

> Daily-driver skill edits must pass evals before commit. Tier 7 regression prevention.

## Daily-driver skills (gated)

These 11 skills are the operational core. Touching any of them = run **`/skill-eval <name>`** first.

**Daily-driver tier** (invoked ≥3×/day per `/harness-health`):

- ****`.claude/skills/daily-note/SKILL.md`****
- ****`.claude/skills/sync-day/SKILL.md`****
- ****`.claude/skills/task-capture/SKILL.md`****
- ****`.claude/skills/day-digest/SKILL.md`****
- ****`.claude/skills/replan/SKILL.md`****
- ****`.claude/skills/sanity/SKILL.md`****
- ****`.claude/skills/inbox-process/SKILL.md`****

**High-blast-radius tier** (auto-chain dispatch surface — a regression ripples through 4 chain combinations; gated 2026-05-23):

- ****`.claude/skills/biz/SKILL.md`**** — auto-chains after `/meeting-note-deep`, `/biweekly-report`, `/okr` Mode A
- ****`.claude/skills/humanize/SKILL.md`**** — auto-chains for creative-writing artifacts
- ****`.claude/skills/localize-cn/SKILL.md`**** — auto-chains for CN-audience work artifacts
- ****`.claude/skills/pragmatic/SKILL.md`**** — auto-chains for project-internal briefings
- ****`.claude/skills/best-of-n/SKILL.md`**** — front-of-funnel gate on all major forwardable outputs (N full-pipeline candidates → critic select)

## Hard Rules

1. **Eval before commit.** Any change to a daily-driver SKILL.md OR its companion **`09 Rules/<name>.md`** requires `/skill-eval <name>` pass before `git commit`. Failure = halt + investigate.

2. **Eval after rename.** Any time a path the skill references changes (file rename, folder move, plugin config update), run `/skill-eval` on every skill that references that path. The 2026-05-21 daily-notes button bug was a rename → 3-day silence; the eval would have caught it in seconds.

3. **Update the eval config when intent changes.** If you intentionally remove a `read_path` or `required_phrase` from a skill, update **`.claude/_eval-fixtures/eval-config/<skill>.yaml`** in the same commit. Don't let configs drift from current truth.

4. **No skipping the gate.** Tempting to skip on "trivial" edits. Trivial edits are where regressions hide. Run the gate. It's <5 seconds.

5. **Failures are blockers, not warnings.** A failing eval blocks commit. Either fix the skill, fix the config, or stash the change for triage.

## Adding a skill to the gated set

A skill graduates to gated status when:
- Daily-driver: invoked ≥3×/day per **`/harness-health`**, OR
- High blast radius: writes to multiple files, OR a single bug would silently break the morning routine, OR
- Recent regression: any skill that has caused a user-caught bug joins the gate

## Skill Package Tiers

Skills are tiered, not uniformly packaged:

- **Packaged skills** are mini-projects: daily-driver, stateful, or quality-gate capabilities with `skill-package.yaml`, eval config, explicit state reads/writes, and dashboard outputs.
- **Thin skills** stay `SKILL.md`-centric. Do not add manifests just for symmetry.
- **Archived skills** are historical recovery surfaces outside active routing.

Pilot packaged skills: `/operate`, `/daily-note`, `/skill-eval`.

Current coordinator package batch: `/day-ops`, `/capture-routing`, `/forwardable-quality`, `/machine-health`. These make the AI-facing surface leaner by routing broad operator intents into package organs before thin implementation skills. Touching any packaged skill requires its declared package eval.

Migrate more only in small batches after the current package batch stays green.

To gate a new skill:
1. Write **`.claude/_eval-fixtures/eval-config/<skill>.yaml`** per the schema (see existing configs)
2. Run `/skill-eval <skill>` until green against current skill state
3. Add the skill path to "Daily-driver skills (gated)" list above
4. Commit the config + this rule update together

## Sibling gate — foundational files

The 5 always-loaded files (`me.md`, `vault-map.md`, `CLAUDE.md`, `MEMORY.md`, `GOALS.md`) are not skills but steer every session. They have their own static linter:

```bash
PY="$(python .harness/resolve_runtime.py python)"
"$PY" .claude/_eval-fixtures/foundational-lint.py    # content: dead pointers, caps, staleness, cross-file re-bloat
"$PY" .claude/_eval-fixtures/verify-load.py          # loader: SessionStart hook actually delivers them, inline vs persisted
"$PY" .claude/_eval-fixtures/portability.py          # runtime seam ratchet: no new hardcoded paths in live control-plane files
```

`foundational-lint` checks dead `[[wikilinks]]` / `§ section` refs / paths, line-cap breaches (MEMORY ≤200, CLAUDE ≤280), staleness, and cross-file duplication. `verify-load` runs the real SessionStart inject hook and checks no file loads as `(not found)` (loader referencing a retired file silently drops content — caught the `ticktick.md` case 2026-05-23), the core files are present, and the total fits the inline limit (over it = persisted, not in working memory by default). Run both after editing any foundational file. Also invoked by `/sanity`. Exit 1 = hard failure.

> **Resolved 2026-05-27 (was a standing RED):** `verify-load` size check is now GREEN — `Hard failures: 0`, always-on inline set trimmed to `me.md` + `CLAUDE.md` = **19.5KB (inline OK)**. The ablation the old note called for happened: `MEMORY.md` / `vault-map.md` / `09 Rules/*` are now **on-demand** (read before the relevant op), not always-on. **Watch:** if the always-on inline set regrows past the inline ceiling, this flips back to RED — keep `CLAUDE.md` under its 280-line cap and resist re-inlining on-demand files.

## Engine learn-loop tooling (additive, 2026-05-23)

Not gates — the feedback surfaces that make the engine compound. Additive/read-only; safe to run anytime:

- `"$PY" .claude/_eval-fixtures/judgment-registry.py` — manifest of the encoded-judgment corpus + contradiction-review candidates → `judgment-registry.md`.
- `"$PY" .claude/_eval-fixtures/portability.py` — ratchet check for the live runtime adapter seam; ignores historical/archive/log surfaces by design.
- `"$PY" .claude/_eval-fixtures/promotion_predictions.py` — decision-observability ratchet for promoted corrections; validates `promotion-predictions.jsonl` and surfaces due verdicts.
- `.claude/_state/corrections.jsonl` — the learn arrow: edits/overrides of AI output → candidate rules (see its README).
- `.claude/_state/promotion-predictions.jsonl` — promoted correction → testable prediction → later verdict (`passed` / `failed` / `unobserved` / `inconclusive`).
- `.claude/_state/grader-verdicts.jsonl` — enforce-layer feedback: vault graders emit `VERDICT-LOG:` lines, session appends.

## Behavioral promotion rule

When a correction is promoted into a skill rule, grader rubric, or eval fixture,
do not stop at "encoded." Add a row to
`.claude/_state/promotion-predictions.jsonl` and, when the original failure is
replayable, add a regression case to the relevant skill/rubric gate. Structural
evals catch drift; replay cases catch the old mistake returning under a new
surface.

## Migration notes

- 2026-05-21 — gate created during Tier 7 Phase 1 build. Initial 7 skills covered. 123 checks total, baseline green.
- 2026-05-23 — auto-chain quartet (`biz`, `humanize`, `localize-cn`, `pragmatic`) added under high-blast-radius criterion. Driver: M.10 6-event misfire streak showed chain skills are high-leverage with no eval coverage. Adds 53 checks → 176 total. Baseline green.
- 2026-05-23 — foundational-files linter added (sibling gate above) after a review found dead pointers (`ticktick.md`, `§ Writing Principles`, `writing-style.md`), MEMORY over its 200 cap, and heavy cross-file redundancy in the always-loaded set.
- 2026-05-27 — `best-of-n` added (high-blast-radius: front-of-funnel gate on all major forwardable outputs). Driver: judgment-loop eval + {{USER_NAME}} human correction (full pipeline 7/10 vs stripped priors+best-of-N 3/10). Config: `.claude/_eval-fixtures/eval-config/best-of-n.yaml`.
- Future skills (e.g. `/route` from Phase 5) join the gate as they prove daily-driver status.

## Companion skill

****`.claude/skills/skill-eval/SKILL.md`**** — runner + workflow docs.

## Router Surface Gate

Run this after broad skill maintenance, skill description edits, or mojibake cleanup:

```bash
PY="$(python .harness/resolve_runtime.py python)"
"$PY" .claude/_eval-fixtures/skill_surface_lint.py
```

This gate checks every active skill frontmatter `description` for three things:

- Router budget: descriptions stay at or below 300 characters.
- Encoding hygiene: descriptions do not carry mojibake-like historical text.
- Plugin protection: `09 Rules/harness-surfaces.md` still protects Obsidian/Operon syntax such as `{{operonId}}`, `{{status}}`, `chain-anchor`, and Dataview/Operon fences.

Exit 1 is a hard failure for skill-maintenance work. Fix frontmatter descriptions only unless the user explicitly approves a broader skill-body rewrite.
