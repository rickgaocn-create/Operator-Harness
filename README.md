# Operator Harness

A personal **operator harness** — a Claude-Code-driven operating system for knowledge work, built on top of an Obsidian vault. It turns Claude Code into a persistent "chief of staff": a rule layer, a skill library, autonomous routines, multi-channel remote control (Discord / Feishu), and a learning loop that promotes recurring corrections into machine-enforceable rules.

This repository is a **sanitized, portable snapshot** of that system — everything needed to re-bootstrap it on a fresh PC, with all secrets and personal content removed. See [`SECURITY.md`](SECURITY.md) for exactly what was scrubbed.

> **Status:** machinery only. Personal vault *content* (notes, projects, identity, contacts, incident history) is **not** included — only the framework, scripts, skills, rules, hooks, and the scaffolding to run them. The 3-pillar workspace folders (`00 Raw` … `10 Action`) ship as **empty scaffolding**: a role-README per folder plus self-updating dashboards, so the structure is there to drop your own content into. Identity files (`me.md`, `MEMORY.md`) ship as fill-in templates.

---

## What's inside

```
operator-harness/
├── vault/                 # the Obsidian-vault framework (the "brain")
│   ├── .claude/           #   control plane: skills, routines, agents, hooks, bootstrap, contexts, profiles
│   ├── .harness/          #   OS-portability layer (runtime adapter: resolve paths/python/scheduler per machine)
│   ├── .codex/            #   autonomous-agent definitions + guard hooks
│   ├── 00 Raw … 10 Action #   3-pillar workspace — SCAFFOLDING ONLY (role-README per folder + empty dashboards;
│   │                      #   your content excluded): 00 Raw · 01 Wiki · 02 Cards [Card] · 03 Projects ·
│   │                      #   04 Notes [Time] · 05 Decisions · 06 Tasks · 10 Action [Action]
│   ├── 07 Templates/      #   Obsidian note templates (card / decision / person / …)
│   ├── 08 Agents/         #   subagent catalog
│   ├── 09 Rules/          #   40 machine-enforceable framework rules (the binding rule layer)
│   ├── CLAUDE.md          #   operating instructions (the system prompt for the harness)
│   ├── AGENTS.md          #   Codex adapter to CLAUDE.md
│   ├── vault-map.md       #   folder routing + rule index + skills navigation
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
│   └── scheduled-tasks/   #   39 Windows Task Scheduler definitions (.xml) — the automation backbone
├── install/               # bootstrap.ps1 (Windows) + bootstrap.sh (macOS) + launchd generator
├── macos/                 # macOS port: python hook ports, daemon launchers, native WeChat reader
├── windows/               # Windows-only extras: native WeChat reader bridge (SQLCipher-4, replaces WeFlow)
└── docs/                  # architecture notes
```

**By the numbers:** 48 skills · 16 autonomous routines · 8 subagents · 40 rules · 17 hooks · 39 scheduled tasks.

---

## Architecture in one paragraph

Claude Code runs with a set of **lifecycle hooks** (`SessionStart` / `UserPromptSubmit` / `Stop` / `PostToolUse` / `SessionEnd`) that inject the vault's memory at startup, probe which remote channels are live, drain a signal queue, mirror replies to Feishu, and log usage + judgment events. The **vault** holds the rule layer (`09 Rules/*`), a library of **skills** (each a `SKILL.md` + optional scripts), and **autonomous routines** scheduled via Windows Task Scheduler. Remote control comes from **daemons** (an AFK Discord/Feishu bridge + a Feishu event consumer) that let you drive Claude Code from your phone. A **judgment loop** captures corrections and distills them into new rules over time. The `.harness/` adapter abstracts machine-specific paths so the same `master` runs on Windows and macOS.

---

## Quick start

> **Prerequisites:** [Claude Code](https://claude.com/claude-code), Python 3.12+, Node 18+, Obsidian.
> **Windows:** PowerShell 5.1+ + Task Scheduler (use `install/bootstrap.ps1`).
> **macOS:** launchd + `python3` (use `install/bootstrap.sh`; see [`macos/README.md`](macos/README.md) for the port). WeChat ingest now has a **native reader on both platforms** — a stdlib-light SQLCipher-4 bridge that replaces the WeFlow Electron app (`windows/wechat/`, `macos/wechat/`).

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
