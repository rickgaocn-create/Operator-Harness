---
layer: platform
paths:
  - ".claude/hooks/usage-log.py"
  - ".claude/hooks/post-tool-middleware.py"
  - ".claude/hooks/stop-check.py"
  - ".claude/_state/usage.jsonl"
  - ".claude/_state/middleware-events.jsonl"
  - ".claude/skills/usage-log/SKILL.md"
  - ".claude/skills/harness-health/SKILL.md"
canonical_skill: ".claude/skills/harness-health/SKILL.md"
created: 2026-05-21
last-major-rewrite: 2026-05-21
---

# Harness Instrumentation Rules

> Contract for the Tier 7 observability + Middleware Lite layer. PostToolUse telemetry is lossy; Stop hooks are gates.

## Hard Rules

1. **Instrumentation must NEVER fail tool calls.** Hook scripts that write to **`.claude/_state/*`** MUST swallow all exceptions. A logging failure must not cascade into a tool failure. Verify by running with disk full / malformed payload — the tool call should still succeed.

2. **Hook overhead p99 ≤ 50ms.** Measured by **`/harness-health`** Section 4. If exceeded, optimize the hook OR disable it. Slow hooks degrade every Claude session — non-negotiable.

3. **`.claude/_state/usage.jsonl` is append-only and lossy.** Never rewrite. Records may be dropped (hook failure). Analysis must tolerate gaps. Use git log + transcript-derived counts as cross-checks for high-signal periods.

4. **Stop hooks are gates, not telemetry.** `stop-check.py` may block completion when this session touched files and did not run or explain validation. It must judge only session-tracked edits under `.claude/_state/middleware/`, not the whole dirty worktree.

## Middleware Lite

`post-tool-middleware.py` is the PostToolUse multiplexer. It dispatches usage logging, per-session edit counts, and loop-detection events.

`stop-check.py` is the PreCompletionChecklist analogue. It blocks when foundational edits fail foundational checks, packaged-skill edits fail their `runner.py <skill>` gate, or edited sessions try to finish without detected validation or an explicit no-validation explanation.

`.claude/profiles/harness-profiles.json` is the lightweight HarnessProfile registry. It names live surfaces, enabled hooks/skills, and excluded tools for `vault`, `dashboard`, `fs`, and `afk` modes; status/dashboard surfaces may report it, but it is not a workflow engine.

## Schema discipline

- **Append new fields freely** — old records stay parseable
- **Never rename existing fields** — break downstream queries silently
- **Never delete records** — JSONL is the audit trail; rotation only after explicit threshold (>50MB)

## Retention

- **`.claude/_state/usage.jsonl`**: monotonic append. Estimated 5KB/day → ~1.8MB/year. Trigger review at 50MB. Never auto-truncate.
- **Transcript files** (**`~/.claude/projects/<dir>/*.jsonl`**): owned by Claude Code; harness reads but doesn't manage.

- **`.claude/_state/middleware-events.jsonl`**: monotonic append. Dashboard reads the recent tail; rotate only after explicit review (>50MB).
- **`.claude/_state/middleware/*.json`**: per-session working state for completion gates. Safe to prune for sessions older than 30 days.

## Read access

All reads via **`/harness-health`** skill. Raw `jq` / `grep` access acceptable for ad-hoc but document the pattern in a card if reused.

## Privacy

Records contain file paths (full paths within vault) and truncated error messages. No task content, no contact data. Acceptable for git-tracking.
