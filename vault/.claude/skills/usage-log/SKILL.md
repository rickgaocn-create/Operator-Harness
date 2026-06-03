---
category: meta
name: usage-log
description: Append one JSONL record per tool invocation to .claude/_state/usage.jsonl. Wired via PostToolUse hook in .claude/settings.json — fires automatically, not user-invoked. Documents the instrumentation contract; not a user-facing slash command.
model: claude-sonnet-4-6
last-major-rewrite: 2026-05-21
---

# Skill: Usage Log (auto-fires via hook)

This is **infrastructure**, not a slash command. The PostToolUse hook now enters through **`.claude/hooks/post-tool-middleware.py`**, which calls the usage-log behavior and appends one JSONL record to **`.claude/_state/usage.jsonl`**. The historical **`usage-log.py`** remains as the schema reference / fallback implementation.

## Record schema (JSONL, one record per line)

```json
{
  "ts": "2026-05-21T22:30:15+00:00",
  "session": "c2260ee5-f2",
  "tool": "Edit",
  "file": "{{VAULT_ROOT}}/04 Notes/daily notes/2026-05-21.md",
  "ok": true,
  "ms": 12,
  "err": "(only on failure)"
}
```

| Field | Type | Meaning |
|---|---|---|
| `ts` | ISO datetime (UTC) | When the tool call completed |
| `session` | string (12-char prefix) | Claude Code session ID — group by this for per-session analysis |
| `tool` | string | Tool name: `Edit`, `Write`, `Read`, `Bash`, `Grep`, `Glob`, `Skill`, `Agent`, MCP tools |
| `file` | string | File path / command / first stringy input parameter (truncated to 240 chars) |
| `ok` | boolean | True if tool reported success |
| `ms` | int | Hook overhead duration (NOT tool execution time — see below) |
| `err` | string | Truncated error message (only present on failures) |

## What this measures (and what it doesn't)

**Measures**:
- Tool invocation frequency by type
- File hot-spots (which files get touched most)
- Error rate by tool
- Session size proxy (records per session)

**Does NOT measure** (limitations honest upfront):
- Tool execution time (the `ms` field is hook overhead, not Tool duration)
- Token cost (Claude Code doesn't expose this to PostToolUse hooks today)
- Model used (same limitation)
- Skill context (which slash command was active when the tool fired)

**Why these gaps**: Claude Code's PostToolUse hook payload doesn't include token counts, model name, or invoking skill. To add: requires Claude Code SDK extension OR parsing the transcript JSONL in `~/.claude/projects/<dir>/` post-hoc. See ****`.claude/skills/harness-health/SKILL.md`**** for the transcript-parsing approach used for richer analysis.

## Read path

Use ****`.claude/skills/harness-health/SKILL.md`**** (run `/harness-health`) for queryable views. Raw access:

```bash
# Last 100 records
tail -n 100 ".claude/_state/usage.jsonl"

# Per-tool counts last 24h
grep "$(date -u -d 'yesterday' +%Y-%m-%dT)" ".claude/_state/usage.jsonl" \
  | jq -r '.tool' | sort | uniq -c | sort -rn
```

## Maintenance

- **Rotation**: none. JSONL grows monotonically. Estimated: ~5KB/day at current usage → 1.8MB/year. Not a concern for now; revisit if > 50MB.
- **Hook disable** (for debugging): comment out the PostToolUse block for **`post-tool-middleware.py`** in the active settings file and reload Claude Code.
- **Schema migration**: append new fields; never rename existing ones. Old records stay parseable.

## Failure mode

The hook script **swallows all exceptions**. If logging fails (disk full, malformed payload), the tool call still succeeds. The cost: silent data loss. Trade-off accepted because instrumentation must never block real work.
