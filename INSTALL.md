# Install Guide

How to re-bootstrap the operator harness on a fresh PC. Windows-first; macOS notes at the end.

## 0. Prerequisites

| Tool | Why |
|---|---|
| [Claude Code](https://claude.com/claude-code) | the runtime that executes the harness |
| Python 3.12+ | routines, hooks, judgment-loop, vault-maintenance |
| Node.js 18+ | afk-code bridge, dashboard, lark-cli |
| Obsidian | the vault UI + plugins |
| PowerShell 5.1+ | hooks, daemons, scheduled tasks |
| Git + GitHub CLI (`gh`) | clone / auth |
| [lark-cli](https://www.npmjs.com/) (`@larksuite/cli` or your build) | Feishu integration (optional) |

## 1. Clone & configure

```powershell
git clone https://github.com/<you>/operator-harness.git
cd operator-harness
copy install\config.example.json install\config.json
notepad install\config.json     # set vaultRoot at minimum
```

Config fields are documented inline in `config.example.json`. Leave any machine value `null` to auto-detect. Run with `-DryRun` first to preview:

```powershell
powershell -ExecutionPolicy Bypass -File install\bootstrap.ps1 -ConfigPath install\config.json -DryRun
```

## 2. Install

```powershell
powershell -ExecutionPolicy Bypass -File install\bootstrap.ps1 -ConfigPath install\config.json
```

This copies `./vault` → your vault root and `./claude-global` → `~/.claude`, then substitutes `{{VAULT_ROOT}}`, `{{USER_HOME}}`, `{{PYTHON_EXE}}`, `{{TASK_USER}}`, `{{HOSTNAME}}` everywhere. With `registerScheduledTasks: true` it also registers the 38 scheduled tasks; with `installDaemons: true` it lays down the daemon launchers.

## 3. Personalize (manual)

The installer does **not** touch your identity/secret placeholders. Edit these by hand:

- **`<vaultRoot>\me.md`** — your identity (template).
- **`<vaultRoot>\CLAUDE.md`** — operating instructions; replace `{{USER_NAME}}` / `{{ORG_*}}` / `{{PROJECT_*}}`.
- **`<vaultRoot>\MEMORY.md`** — start your own incident log (template).
- Grep the tree for remaining placeholders: `Select-String -Path <vaultRoot>\* -Pattern '\{\{[A-Z_]+\}\}' -Recurse`.

## 4. Claude Code settings

```powershell
copy claude-global\settings.local.example.json $env:USERPROFILE\.claude\settings.local.json
```

`settings.json` (shared, installed) holds the OS-neutral hook wiring with your paths substituted. `settings.local.json` (gitignored) is where per-machine hooks + permissions live. Review `permissions.defaultMode` — the source used `bypassPermissions`; prefer something stricter to start.

## 5. Channel secrets (optional — for remote control)

None of these ship with tokens. Create them yourself:

- **Discord bridge** (`runtime/daemons/afk-code-claude2`): create `~/.afk-code-claude2/discord.env` with `DISCORD_BOT_TOKEN=` and `DISCORD_USER_ID=`. See [clharman/afk-code](https://github.com/clharman/afk-code) for the bot-setup flow.
- **Feishu consumer** (`claude-global/channels/feishu`): bind a Feishu app with `lark-cli`, then create the `access.json` the launch scripts expect (`open_id` allowlist + app id). Set your app id where `{{FEISHU_APP_ID}}` appears.
- **WeChat ingest** (`vault/.claude/skills/daily-wechat-ingest`): set `WEFLOW_BASE` / `WEFLOW_TOKEN` / `ANTHROPIC_API_KEY` env vars; edit `priority_chats.json` with your real chats.

## 6. Obsidian

Open the vault in Obsidian and enable the community plugins referenced in `.obsidian` (claudian, dataview, templater, smart-connections, operon, harness-dashboard). `.mcp.json` wires the smart-connections + playwright MCP servers.

## 7. Verify

Launch Claude Code from inside the vault and confirm the `SessionStart` hooks fire (you should see "Loading vault memory…", "Probing channel state…"). Run a routine manually, e.g.:

```powershell
& $pythonExe "<vaultRoot>\.claude\routines\harness_status.py"
```

## Build the afk-code bridge (if using remote control)

`runtime/afk-code` is source only. To build:

```powershell
cd runtime\afk-code
npm install
npm run build      # produces dist/
```

It's a fork of clharman/afk-code with an added `src/feishu/` module. Prefer cloning upstream and re-applying the `feishu/` overlay if you want upstream updates.

## macOS

macOS is a **first-class install** via the port in [`macos/`](macos/README.md). Automation uses **launchd** (generated from the same 38 task XMLs by `install/macos/taskxml_to_launchd.py`), hooks are ported to `python3` in `macos/hooks/`, and remote-control daemons run as bash launchers under launchd KeepAlive.

```bash
bash install/bootstrap.sh --vault-root "$HOME/Documents/RG" --dry-run        # preview
bash install/bootstrap.sh --vault-root "$HOME/Documents/RG" --register-agents # install + schedule
```

Full parity table, mac-only extras (native notifications, clipboard capture), and known partial ports: **[`macos/README.md`](macos/README.md)**. The one capability that does not cross over is WeChat ingest (it reads the Windows WeChat client DB).
