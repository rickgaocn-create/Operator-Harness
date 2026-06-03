---
layer: platform
pillar: Harness engineering · cross-platform
created: 2026-05-26
created-by: claude
---

# Harness Portability Rules · cross-platform by default

> The harness must run on any OS and let a new user onboard onto their own. Windows-dependence is a weakness. Engine and config are separate; the engine is path-agnostic and OS-agnostic.

## Principles

1. **Engine vs config.** The engine (skills, hooks, rules, judgment-loop) is user- and OS-agnostic. Per-user / per-machine specifics — vault location, identity, secrets, interpreter, OS scheduler — live in a thin config the engine *discovers*, never hardcodes.

2. **No new hardcoded paths (the ratchet).** Any script built or touched discovers its paths — derive the vault root from `__file__` (`os.path.dirname` / `parents[n]`), or read one env/config value. Never bake `D:\…`, `C:\Users\…`, or a `python.exe` path into a script. See [[T260526-harness-cross-platform]].

3. **No new OS-locked languages for hooks.** New hooks are cross-platform Python — not PowerShell / `.cmd` / `.sh`. Existing `.ps1` are ported opportunistically, not big-bang.

4. **Vault-resident config + memory.** Anything the harness must carry across machines lives in the **synced vault**, not in non-syncing global dirs (`~/.claude/projects/<slug>/memory/`). A `<slug>` keyed to a machine path does not travel — that's a portability bug, not a store.

5. **Scheduling via a per-OS adapter.** One job manifest; a thin adapter emits launchd / cron / Task Scheduler. No scheduler-specific assumptions baked into the jobs.

## Why

OS-portability and new-user onboarding are the same problem — solved once by separating a path-agnostic engine from discovered config. Backlog + live diagnosis: [[T260526-harness-cross-platform]]. Building principle also logged in `.claude/_state/corrections.jsonl`.
