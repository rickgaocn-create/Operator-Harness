---
category: meta
name: mode
description: Adopt a soft session lens such as bd, research, or afk without overriding rules. Use /mode to bias emphasis for the session; use /route to pick a skill.
model: claude-sonnet-4-6
allowed-tools: Read, Glob
companion-rules:
  - "[[09 Rules/autonomous-routines.md]]"
created: 2026-05-27
created-by: claude
---

# Skill: /mode — soft session lens

> **概要:** `/mode bd|research|afk` reads `.claude/contexts/<name>.md` and adopts it as a soft posture for the rest of the session (tool-favoring + emphasis). It is the **weakest layer** — 09 Rules, CLAUDE.md, the judgment graph, and every auto-chain still bind and override on conflict. Soft (the model holds it in context), not a system-prompt change.

## Workflow
1. **Parse the arg.** `bd` / `research` / `afk` → read `.claude/contexts/<name>.md`. `off` / `clear` → drop the active lens, revert to default. No arg or unknown → list available modes (glob `.claude/contexts/*.md`, skip `_README`) and name the active one if known.
2. **Confirm in ONE line:** `Mode: <name> active — favoring <top 2-3 tools>; posture: <one phrase>. (soft lens — rules/graph still bind)`.
3. **Operate under it** for the rest of the session: when a tool choice or emphasis is genuinely ambiguous, bias toward the persona's *Tools to favor* + *Posture*. On ANY conflict with a 09 Rule / CLAUDE.md / judgment node / auto-chain, the rule wins — apply it and say so.

## Hard rules
- **A mode never overrides a hard rule, the judgment graph, or an auto-chain.** It only breaks ties in tool-selection + emphasis. Binding order: `09 Rules > CLAUDE.md > MEMORY > mode`.
- **On-demand only.** Never auto-loaded at SessionStart (keeps the always-on layer lean). One mode at a time.
- **Soft, not hard.** Sets posture by holding the persona in context; does not alter the system prompt. For a hard interactive launch see `.claude/contexts/_README.md` (the `--append-system-prompt` variant — verify the flag first; never `--system-prompt`).
- **Not `/route`.** `/route` picks WHICH skill to fire for one request; `/mode` sets the session's tool-favoring posture. If the user wants "which skill should I run," hand off to `/route`.

## Available modes
- `bd` — relationship/deal lens (Feishu reach, vault-researcher-first, prospect intel)
- `research` — vault-first grounding lens (grep, subagents, context7/web)
- `afk` — remote-operator lens (deliver the artifact, `/status`-led)

> Add a mode = drop a new `.claude/contexts/<name>.md` following the soft-lens contract in `_README.md`. `/mode` discovers it automatically.
