# Operator Harness

A personal **operator harness** — a Claude-Code-driven operating system for knowledge work, built on top of an Obsidian vault. It turns Claude Code into a persistent "chief of staff": a rule layer, a skill library, autonomous routines, multi-channel remote control (Discord / Feishu), and a learning loop that promotes recurring corrections into machine-enforceable rules.

This repository is a **sanitized, portable snapshot** of that system — everything needed to re-bootstrap it on a fresh PC, with all secrets and personal content removed. See [`SECURITY.md`](SECURITY.md) for exactly what was scrubbed.

> **Status:** machinery only. Personal vault *content* (notes, projects, identity, contacts, incident history) is **not** included — only the framework, scripts, skills, rules, hooks, and the scaffolding to run them. Identity files (`me.md`, `MEMORY.md`) ship as fill-in templates.

---

## What's inside

```
operator-harness/
├── vault/                 # the Obsidian-vault framework (the "brain")
│   ├── .claude/           #   control plane: skills, routines, agents, hooks, bootstrap, contexts, profiles
│   ├── .harness/          #   OS-portability layer (runtime adapter: resolve paths/python/scheduler per machine)
│   ├── .codex/            #   autonomous-agent definitions + guard hooks
│   ├── 09 Rules/          #   35 machine-enforceable framework rules (the binding rule layer)
│   ├── 07 Templates/      #   Obsidian note templates
│   ├── 08 Agents/         #   subagent catalog
│   ├── CLAUDE.md          #   operating instructions (the system prompt for the harness)
│   ├── me.md / MEMORY.md  #   identity + incident-rules — TEMPLATES, fill in your own
│   └── .mcp.json          #   MCP servers (smart-connections, playwright)
├── claude-global/         # what lives in ~/.claude on the machine
│   ├── hooks/             #   17 lifecycle hooks (.ps1 + .cmd shims): vault-memory inject, catch-up brief,
│   │                      #   channel-state probe, signal queue, Feishu mirroring, vault-evolve
│   ├── vault-maintenance/ #   weekly hygiene jobs (inbox decay, card archive, metabolism metrics)
│   ├── channels/          #   Discord + Feishu launch/health scripts (no tokens)
│   ├── rules/             #   global rules (e.g. Context7 usage)
│   └── settings.json      #   hook wiring (paths parameterized)
├── runtime/               # PC-side runtime & automation
│   ├── judgment-loop/     #   Python learning loop (capture → distill → encode corrections)
│   ├── harness-dashboard/ #   Obsidian dashboard UI (compiled)
│   ├── afk-code/          #   AFK bridge SOURCE (fork of clharman/afk-code + custom Feishu module)
│   ├── daemons/           #   24/7 daemon launchers + healthchecks (Discord / Feishu)
│   └── scheduled-tasks/   #   38 Windows Task Scheduler definitions (.xml) — the automation backbone
├── install/               # bootstrap.ps1 installer + config template + task registration
└── docs/                  # architecture notes
```

**By the numbers:** 52 skills · 16 autonomous routines · 8 subagents · 35 rules · 17 hooks · 38 scheduled tasks.

---

## Architecture in one paragraph

Claude Code runs with a set of **lifecycle hooks** (`SessionStart` / `UserPromptSubmit` / `Stop` / `PostToolUse` / `SessionEnd`) that inject the vault's memory at startup, probe which remote channels are live, drain a signal queue, mirror replies to Feishu, and log usage + judgment events. The **vault** holds the rule layer (`09 Rules/*`), a library of **skills** (each a `SKILL.md` + optional scripts), and **autonomous routines** scheduled via Windows Task Scheduler. Remote control comes from **daemons** (an AFK Discord/Feishu bridge + a Feishu event consumer) that let you drive Claude Code from your phone. A **judgment loop** captures corrections and distills them into new rules over time. The `.harness/` adapter abstracts machine-specific paths so the same `master` runs on Windows and macOS.

---

## Quick start

> **Prerequisites:** Windows 10/11, [Claude Code](https://claude.com/claude-code), Python 3.12+, Node 18+, Obsidian, PowerShell 5.1+. (The framework is Windows-first; the `.harness/` layer has macOS hooks but the scheduled jobs assume Task Scheduler + PowerShell.)

```powershell
git clone https://github.com/<you>/operator-harness.git
cd operator-harness
# 1. copy & edit the config (vault location, etc.)
copy install\config.example.json install\config.json
notepad install\config.json
# 2. run the installer (substitutes machine paths, copies vault + ~/.claude, optionally registers tasks)
powershell -ExecutionPolicy Bypass -File install\bootstrap.ps1 -ConfigPath install\config.json
```

Then **personalize**: fill in `vault/me.md`, `vault/CLAUDE.md`, `vault/MEMORY.md`, and configure your own channel tokens (see [`INSTALL.md`](INSTALL.md)).

Full step-by-step: **[`INSTALL.md`](INSTALL.md)** · what was removed and the placeholder legend: **[`SECURITY.md`](SECURITY.md)**.

---

## License

MIT (this repository's own scripts/docs). `runtime/afk-code/` is a source snapshot of a fork of [clharman/afk-code](https://github.com/clharman/afk-code) with a custom Feishu module added — it carries its own upstream `LICENSE`; track upstream for updates rather than treating this snapshot as canonical.
