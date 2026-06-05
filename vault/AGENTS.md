---
type: operating-instructions
created-by: claude
mem-block: operating-rules
description: "Codex adapter to canonical Claude operating instructions"
limit: 60
limit-unit: lines
load-policy: always-on
---

# {{USER_NAME}} — Codex Adapter

> [[CLAUDE.md]] is the canonical operating-rules block. This file exists so Codex runtimes can find the {{USER_NAME}} harness contract without duplicating it.

@CLAUDE.md

---

## Adapter Rules

1. Read [[CLAUDE.md]] in full and apply it as the operating contract.
2. Treat "Claude" in [[CLAUDE.md]] as "Codex" when it refers to the current agent.
3. Use Codex-native tool and editing constraints from the active session, but do not duplicate canonical harness behavior here.
4. If this file and [[CLAUDE.md]] disagree, [[CLAUDE.md]] wins except for Codex runtime mechanics.

## {{USER_NAME}} Workspace

When the user mentions {{USER_NAME}}, {{USER_NAME}}, the harness, the Obsidian vault, or "load {{USER_NAME}} vault context first", use `D:\Administrator\Documents\{{USER_NAME}}` as the primary workspace (the harness root).
