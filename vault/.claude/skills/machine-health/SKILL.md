---
category: meta
name: machine-health
description: Coordinates harness diagnostics. Use when checking what is broken, validating live paths, running evals, rearming organs, or reviewing middleware/profile health.
model: claude-sonnet-4-6
allowed-tools: Read, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/harness-instrumentation.md]]"
  - "[[09 Rules/harness-surfaces.md]]"
  - "[[09 Rules/skill-eval-gate.md]]"
created: 2026-05-28
created-by: codex
---

# Skill: Machine Health

Coordinate machine diagnostics without turning maintenance output into user-facing noise. This package answers "is the harness alive, and what needs action?"

Machine health includes two governance readings beyond raw liveness:

- **Learning Loop Debt:** judgment queue files, estimated candidate count, `status:new` corrections, and oldest queue age. Yellow debt is a monitor warning; red debt may queue assisted extraction. Promotion remains human-reviewed.
- **Surface Diet:** active skill count, packaged-vs-thin ratio, uncategorized skills, and whether lower-layer crowding leaks into the human-facing cockpit.

## Role

Use `machine-health` when `/operate` routes to "Check the machine", or when the dashboard/status layer reports a delivery, eval, middleware, or profile issue.

## Downstream Skills

| Need | Use |
|---|---|
| Quick liveness card | `/status` |
| Deeper telemetry | `/harness-health` |
| Broad vault/harness sanity | `/sanity` |
| Skill/package structural gate | `/skill-eval` |
| Specific organ recovery | `/rearm` |
| Usage telemetry schema | `/usage-log` |

## State Contract

Read:
- `.claude/_state/harness-pulse.json`
- `.claude/_state/autonomous-log.jsonl`
- `.claude/_state/usage.jsonl`
- `.claude/_state/middleware-events.jsonl`
- `.claude/_state/judgment-queue/`
- `.claude/_state/corrections.jsonl`
- `.claude/_state/harness-manifest.json`
- `.claude/profiles/harness-profiles.json`
- `.claude/_eval-fixtures/eval-runs/`
- `.claude/skills/*/skill-package.yaml`

Write only through the downstream diagnostic or rearm skill that owns the target surface.

## Operating Rules

1. Distinguish configured from live-path verified.
2. Report green/yellow/red with only the findings {{USER_NAME}} needs.
3. Treat eval/lint/map failures as blockers for harness changes.
4. Do not rearm or edit unless requested or a rule explicitly permits it.
5. Surface middleware warnings and Stop-hook blocks as machine health, not user failure.
6. Keep profile visibility clear: which profile is active and which skills/surfaces are live.
7. Surface learning loop debt before it stalls judgment compounding.
8. Treat crowded lower layers as a surface-diet issue only when they leak into cockpit routing or user-facing docs.

## Completion Gate

After changing this package or health-routing state, run:

```bash
python .claude/_eval-fixtures/runner.py machine-health
```

Run `harness_map.py --check` when state/profile registries change.
