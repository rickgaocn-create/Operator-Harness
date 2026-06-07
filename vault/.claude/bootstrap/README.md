---
type: harness-bootstrap
created-by: claude
created: 2026-05-27
platform: windows
---

# Harness Bootstrap — control-plane recovery baseline

> **Why this exists.** The harness's *control plane* — the SessionStart / UserPromptSubmit / Stop / PostToolUse / SessionEnd hooks — runs from the **per-machine** global config (`~/.claude/settings.json` + `~/.claude/hooks/*.ps1`). By design (see root `CLAUDE.md` § Platform), that wiring is **not** committed to the vault repo so the two machines (Windows desktop, macOS laptop) can differ. The side effect: the load-bearing hook **scripts** (≈40 KB of PowerShell logic) lived **nowhere in version control** — if the machine died, they were unrecoverable. This folder closes that gap by snapshotting them as a recovery baseline, without changing the per-machine wiring model.

## What's here

```
bootstrap/
├── README.md                              ← you are here
└── windows/
    ├── settings.hooks.reference.json       ← the hook + plugin WIRING (copy of the live global settings block)
    └── global-hooks/                       ← the hook SCRIPTS (copies of ~/.claude/hooks/*)
        ├── inject-vault-memory.ps1         (SessionStart) inlines me.md + CLAUDE.md when launched outside the vault
        ├── inject-catchup-brief.ps1        (SessionStart) catch-up brief + signal-queue drain
        ├── check-channel-state.ps1         (SessionStart) probes Discord + Feishu inbound bridges
        ├── check-pending-signals.ps1       (UserPromptSubmit) surfaces pending automation signals
        ├── mirror-to-feishu.ps1            (Stop) mirrors the last assistant turn to the active Feishu chat
        ├── vault-evolve-daily.ps1          (scheduled) daily vault-evolve report
        └── {{USER_NAME}}-signal-*.cmd / {{USER_NAME}}-watcher-clippings.cmd  (Task Scheduler shims)
```

The Python hooks (`usage-log.py`, `cn-zero-english-guard.py`, `judgment_capture.py`) already live in the tracked vault (`.claude/hooks/`, `.claude/_eval-fixtures/`), so only the PowerShell control plane needed capturing here.

## Reconstruct the harness on a fresh Windows box

1. Clone the vault to `D:\Administrator\Documents\{{USER_NAME}}` (adjust paths below if different).
2. Install Python 3.12 + `lark-cli`; set up channel credentials (`~/.afk-code/feishu.env`, `~/.claude/channels/`). **Secrets are NOT in this repo** — the scripts read them from those external stores.
3. Deploy the hook scripts:  `Copy-Item .claude\bootstrap\windows\global-hooks\* $env:USERPROFILE\.claude\hooks\ -Force`
4. Merge the `hooks` block from `settings.hooks.reference.json` into `~/.claude/settings.json`; re-enable plugins per `_enabledPlugins_reference`.
5. Re-arm scheduled tasks + routines: `powershell -ExecutionPolicy Bypass -File .claude\_state\setup_all_schedules.ps1` and `.claude\routines\_setup.ps1`.
6. Verify: open a session and confirm the SessionStart brief renders + `check-channel-state` reports the bridges.

## Keeping this baseline current (avoid drift)

The **live** `~/.claude/hooks/*` is what actually runs; this folder is a copy. After editing a global hook, re-sync:

```powershell
Copy-Item $env:USERPROFILE\.claude\hooks\*.ps1, $env:USERPROFILE\.claude\hooks\*.cmd `
  .claude\bootstrap\windows\global-hooks\ -Force
```

## cn-guard wiring (reconciled 2026-05-27)

The `PreToolUse` cn-zero-english-guard previously lived in the vault's **tracked** `.claude/settings.json` with a hardcoded Windows `python.exe` path — violating the `CLAUDE.md` § Platform invariant (*"Shared settings.json stays OS-neutral (no hooks)"*) and broken on macOS (wrong interpreter + `D:\` path). **Resolved:** relocated to the per-machine (gitignored) `.claude/settings.local.json`, where machine-absolute paths are correct; `settings.json` is OS-neutral again. Verified 2026-05-27: `settings.json` carries no hooks, and the guard fires standalone (blocks a CN-residue write → exit 2; passes a clean write → exit 0). The wiring activates next session (hooks load at SessionStart).

**Recovery / per-machine wiring.** The guard SCRIPT (`.claude/hooks/cn-zero-english-guard.py`) is tracked; only the WIRING is per-machine. To re-arm on a fresh box, add a `PreToolUse` `Write|Edit|NotebookEdit` hook to that machine's `.claude/settings.local.json`:
- **Windows:** `<...Python312/python.exe> D:/Administrator/Documents/{{USER_NAME}}/.claude/hooks/cn-zero-english-guard.py`
- **macOS:** `python3 $CLAUDE_PROJECT_DIR/.claude/hooks/cn-zero-english-guard.py`
