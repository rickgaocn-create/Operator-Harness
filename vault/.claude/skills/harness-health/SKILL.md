---
category: meta
name: harness-health
description: Read-only harness dashboard: token cost, per-skill counts, error rates, stale + daily-driver skills. Trigger on /harness-health, "harness health", "harness metrics", "how is my harness", "show me usage", or weekly during /vault-evolve.
model: claude-sonnet-4-6
allowed-tools: Read, Glob, Grep, Bash
last-major-rewrite: 2026-05-21
companion-rules: "[[09 Rules/harness-instrumentation.md]]"
---

# Skill: Harness Health Dashboard

Read-only diagnostic surface for the **operator harness**. Pulls from three data sources, renders a markdown table view. Never writes (except the one-off `harness-baseline.json` on first run).

## Data sources

Middleware Lite adds `.claude/_state/middleware-events.jsonl` beside usage telemetry. The dashboard already surfaces the recent tail; `/harness-health` should include it when doing deeper diagnosis.

Surface Diet adds a lightweight crowding view: active skills, packaged skills, thin skills, uncategorized skills, stale skills, and package coverage. Crowding is only yellow when it leaks into user-facing surfaces or package coverage stays low; old thin skills are not a failure by themselves.

Learning Loop Debt adds judgment-compounding visibility: judgment queue files, estimated candidates, `status:new` corrections, oldest queue age, and next action. Yellow debt stays in Monitor; red debt can queue extraction. Do not auto-promote judgment into rules.

1. **`.claude/_state/usage.jsonl`** — per-tool-call records (see **`.claude/skills/usage-log/SKILL.md`**)
2. **`.claude/projects/*/sessions/*.jsonl`** — Claude Code transcript files (token counts, model, skill context) live here when present; richer than the hook log
3. **git log** — skill file churn / commit cadence

## Run

```bash
/harness-health              # default: last 7d view
/harness-health --window 30  # 30-day window
/harness-health --baseline   # write current state to .claude/_state/harness-baseline.json (Phase 0 anchor)
/harness-health --diff       # compare current vs baseline (Phase 2 cost-cut validation)
```

## Output (markdown table)

### Section 1 — Token & cost (last N days)

| Metric | Current | Baseline | Δ |
|---|---|---|---|
| Sessions | <n> | <n0> | ±% |
| Total tool calls | <n> | <n0> | ±% |
| Median session duration | <ms> | <ms0> | ±% |
| Estimated cost (USD)* | <$> | <$0> | ±% |

*Cost = transcript-derived input + output tokens × model rate. Falls back to "n/a" when transcripts unavailable.

### Section 2 — Per-skill activity

| Skill | Runs | Median ms | Errors | Last run | Model tier |
|---|---|---|---|---|---|
| daily-note | 12 | 240 | 0 | 2026-05-21 | sonnet-4.6 |
| sync-day | 8 | 180 | 1 | 2026-05-21 | sonnet-4.6 |
| ... | ... | ... | ... | ... | ... |

Sorted by Runs desc. Highlights:
- **🔥 Daily drivers** (Runs > 3/day): worth eval coverage
- **❄️ Stale** (Last run > 30d): review or archive candidate
- **🚨 Error-prone** (Errors > 0): debug priority

### Section 3 — Skill file churn (git log last 30d)

| File | Commits | Last commit | Edit-after-commit count |
|---|---|---|---|
| **`09 Rules/tasks.md`** | 9 | 2026-05-21 | 2 |
| **`.claude/skills/sync-day/SKILL.md`** | 7 | 2026-05-21 | 0 |
| ... | ... | ... | ... |

Top 10 by commits. High `Edit-after-commit` = likely instability (committed then edited back; consider rollback or refactor).

### Section 4 — Hook performance

| Hook | Total invocations | Median overhead ms | P99 ms | Failures |
|---|---|---|---|---|
| usage-log.py | <n> | <ms> | <ms> | <n> |
| cn-zero-english-guard.py | <n> | <ms> | <ms> | <n> |

Target: hook overhead p99 < 50ms each. If exceeded → optimize or disable.

### Section 5 — Health alerts (only when triggered)

🚨 **Inbox drift**: **`06 Tasks/Inbox.md`** has 24 open items (threshold 20). Run `/inbox-process`.
🚨 **Stale skill**: `/scaffold` not run in 45 days. Archive candidate.
🚨 **Cost spike**: 7-day cost up 80% vs baseline. Investigate which skill regressed.
🚨 **Migration cruft**: **`.smart-env/multi/`** has 312 files. Cleanup advised.

(No emoji noise when no alert fires — silent on green.)

### Section 6 - Surface Diet

| Metric | Current | Signal |
|---|---|---|
| Active skills | <n> | yellow if >50 and package coverage <20% |
| Packaged skills | <n> | package organs + daily-driver packages |
| Thin skills | <n> | delegated implementation surface |
| Uncategorized skills | <n> | yellow if any active skill lacks `category` |
| User-facing index | cockpit-first? | yellow if old command sprawl returns |

### Section 7 - Learning Loop Debt

| Metric | Current | Signal |
|---|---|---|
| Judgment queue files | <n> | yellow >5, red >15 |
| Estimated candidates | <n> | yellow >25, red >75 |
| New corrections | <n> | yellow >= distill threshold |
| Oldest queue age | <age> | yellow >24h, red >72h |
| Next action | extraction / distill / review | promotion remains human-reviewed |

## How

```bash
# Section 1 — counts + cost from transcripts (if available)
session_dir="$HOME/.claude/projects/C--Windows-System32-WindowsPowerShell-v1-0"
[ -d "$session_dir" ] && \
  find "$session_dir" -name "*.jsonl" -mtime -7 -exec wc -l {} \; \
    | awk '{sum += $1} END {print "Lines (proxy for messages):", sum}'

# Section 2 — per-skill from usage.jsonl + skill frontmatter
jq -s 'group_by(.tool) | map({tool: .[0].tool, runs: length, ok: map(select(.ok)) | length})' \
  ".claude/_state/usage.jsonl"

# Section 3 — git churn
git log --since='30 days ago' --name-only --pretty=format: \
  | grep -E "\.claude/skills/|^09 Rules/" \
  | sort | uniq -c | sort -rn | head -20

# Section 5 — alerts
inbox_open=$(grep -c "^- \[ \]" "06 Tasks/Inbox.md" 2>/dev/null || echo 0)
[ "$inbox_open" -gt 20 ] && echo "🚨 Inbox drift: $inbox_open open"
```

The skill SHELLS these out; never invokes destructive operations. Read-only.

## Failure modes

| Symptom | Fix |
|---|---|
| `usage.jsonl` missing | PostToolUse middleware not active → re-check **`.claude/settings.json`** PostToolUse block |
| Transcript dir missing | Claude Code persists transcripts to `~/.claude/projects/<cwd-encoded>/` — verify path matches your Claude Code config |
| Per-skill row shows `null` for tier | Skill doesn't have `model:` frontmatter yet → Phase 2 incomplete for that skill |

## Companion rule

**`09 Rules/harness-instrumentation.md`** codifies: instrumentation must be non-blocking, must NEVER fail tool calls, retention policy for usage.jsonl.
