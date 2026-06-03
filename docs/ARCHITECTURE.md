# Architecture

The harness is four layers stacked on Claude Code + an Obsidian vault.

## 1. The vault (knowledge + rules)

The Obsidian vault is the persistent state. Numbered folders hold content (excluded from this repo); the framework lives in:

- **`CLAUDE.md`** — the always-on operating instructions (role, tone, thinking frameworks, hard fails, auto-chain rules). Imported in full at session start via `@import`.
- **`me.md` / `MEMORY.md`** — always-on identity + an incident-driven hard-rules index.
- **`09 Rules/*`** — 35 machine-enforceable rules (file types, cards, actions, time cascade, task capture, skill routing/versioning, autonomy tiers, sensitivity guard, …). These bind: a rule overrides prose when they conflict.
- **`07 Templates/`, `08 Agents/`** — note templates and the subagent catalog.

## 2. The control plane (`vault/.claude/`)

- **`skills/`** — 52 skills, each a `SKILL.md` (triggers, phases, tool spec) plus optional `scripts/`. Skills are invoked by name and can auto-chain (e.g. finalize a business doc → `/biz` → critic grader loop).
- **`routines/`** — 16 autonomous Python jobs (`harness-pulse`, `eod-snapshot`, `inbox-drift`, `reflect`, `build_underlays`, …) run on a schedule; `_common.py` holds shared logging/caps/dry-run plumbing.
- **`agents/`** — 8 subagents (researchers, critics, screeners, a vault-manager) with rubrics, auto-invoked by description.
- **`hooks/`** — Python guards (`cn-zero-english-guard`, `usage-log`, `post-tool-middleware`, `stop-check`).
- **`bootstrap/`, `contexts/`, `profiles/`** — per-OS settings reference, session context profiles, role profiles.

## 3. Lifecycle hooks (`claude-global/hooks/` → `~/.claude`)

Wired in `settings.json`, these fire on Claude Code lifecycle events:

| Event | Hook | Role |
|---|---|---|
| SessionStart | `inject-vault-memory.ps1` | inline the vault core (me/CLAUDE/MEMORY) |
| SessionStart | `inject-catchup-brief.ps1` | drain the signal queue, surface catch-up |
| SessionStart | `check-channel-state.ps1` | probe which channels (Discord/Feishu/WeChat) are live |
| UserPromptSubmit | `check-pending-signals.ps1` | inject queued signals before the turn |
| Stop | `stop-check.py` + `mirror-to-feishu.ps1` | exit checks; mirror the reply to Feishu |
| PostToolUse | `post-tool-middleware.py` | middleware intercept |
| SessionEnd | `judgment_capture.py` | log judgment events for the learning loop |

The `.cmd` "signal feeder/watcher" shims (`RG-signal-*`, `RG-feeder-*`, `RG-watcher-*`) are the entry points scheduled tasks call to drop a signal into the queue.

## 4. Runtime & remote control (`runtime/`)

- **`afk-code/`** — the AFK bridge (fork of clharman/afk-code + a custom Feishu module): lets you drive a Claude Code session from Discord/Feishu/Slack/Telegram on your phone.
- **`daemons/`** — 24/7 launchers with exponential-backoff restart + healthchecks (orphan/wedge detection) for the Discord bridge and the Feishu event consumer.
- **`judgment-loop/`** — a stdlib-only Python loop: capture corrections → distill → encode into rules. Closes the feedback loop between "Claude got corrected" and "a rule now prevents it."
- **`harness-dashboard/`** — an Obsidian plugin UI rendering harness health.
- **`scheduled-tasks/`** — 38 Windows Task Scheduler definitions: the daily/weekly cadence (note creation, ingests, digests, vault maintenance, Tier-7 autonomous routines, daemon supervision).

## Portability (`vault/.harness/`)

`resolve_runtime.py` + `adapter-contract.md` abstract machine specifics (platform, vault root, python command, state paths, scheduler) so one shared `master` runs on both Windows and macOS; OS-specific skills are tagged `platform: windows|macos`.

## Data flow (a day in the life)

```
Task Scheduler ─▶ RG-signal-*.cmd ─▶ signal queue ─┐
                                                    ├─▶ SessionStart hooks drain queue ─▶ Claude acts
phone (Discord/Feishu) ─▶ daemon ─▶ Claude Code ────┘                         │
                                                                              ▼
                              corrections ─▶ judgment-loop ─▶ new 09 Rules/ entry ─▶ binds next session
```
