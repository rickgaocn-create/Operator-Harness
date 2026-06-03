# Context Modes — soft session lenses

On-demand personas that bias **tool-choice + posture** for a session. Invoked via `/mode <name>` (works AFK over Discord/Feishu). **Not** auto-loaded — never injected at SessionStart, so the always-on layer stays lean.

## Binding contract (load-bearing)

A mode is the **weakest layer.** The hierarchy is unchanged:

> `09 Rules/**` → project `CLAUDE.md` → root `CLAUDE.md` → `MEMORY.md` → **mode**

A mode **never** overrides a hard rule, the judgment graph (`09 Rules/_judgment/`), or an auto-chain (`best-of-n` → `biz` → `localize-cn` / `pragmatic` / `humanize`). It only breaks ties in *which tool you reach for first* and *what you emphasize*. On any conflict, the rule/graph wins and the mode yields — say so out loud.

## Modes

| file | lens |
|---|---|
| `bd.md` | BD / deal operating lens |
| `research.md` | vault-first grounding lens |
| `afk.md` | remote-operator lens |

## Mechanism

- **Primary — `/mode <name>` (soft, works AFK):** the `/mode` skill reads the persona and the model adopts it for the session. Persists while it stays in context. This is the path for bridge sessions (Discord/Feishu), which can't take launch flags.
- **Optional — launch flag (hard, interactive only):**
  `claude --append-system-prompt "$(cat .claude/contexts/<name>.md)"`
  Use **`--append-system-prompt`**, never `--system-prompt` (that *replaces* the default and would strip the vault load). ⚠️ Verify this flag on your CLI version before relying on it — the `/mode` skill needs no flag and is the recommended path.

One mode at a time. `/mode off` clears the active lens.
