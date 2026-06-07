---
layer: platform
type: rule
scope: memory-os
created: 2026-05-28
created-by: codex
status: active
---

# Memory OS

> Phase 1 contract for bounded core memory over the searchable vault archive. This is an anti-bloat and observability layer, not a new consolidator.

---

## Two Tiers

| Tier | Holds | Access | Discipline |
|---|---|---|---|
| **Core** | A few labeled memory blocks that steer sessions. | Per each block's `load-policy`; core does **not** always mean always injected. | Each block declares a hard `limit` and must pass foundational lint. |
| **Archive** | Vault notes, Cards, Actions, Wiki, Tasks, state files, logs, and generated underlays. | Search/read on demand. | Append-tolerant; no promotion into Core without an explicit edit path. |

---

## Core-Block Schema

Each core block is a Markdown file with frontmatter:

```yaml
mem-block: identity
description: "Stable role/context for {{USER_NAME}}"
limit: 120
limit-unit: lines
load-policy: always-on
```

Required fields: `mem-block`, `description`, `limit`, `limit-unit`, `load-policy`.

Allowed `load-policy` values:

| Value | Meaning |
|---|---|
| `always-on` | Loaded at session start for the relevant runtime. |
| `conditional` | Loaded in some runtime/session contexts; otherwise read on demand. |
| `on-demand` | Not startup-loaded; read before the relevant operation. |

Line budgets are measured on the Markdown body, excluding frontmatter.

---

## Phase 1 Boundaries

- This phase adds metadata and lint enforcement only.
- Direct urgent hard-rule patches are allowed, but `foundational-lint.py` must pass afterward.
- No consolidator merge.
- No generated Cards, Actions, Wiki pages, Tasks, or project files.
- No non-destructive rewrite queue.
- No stranded auto-memory symlink or migration.

---

## Current Core Blocks

| Block | File(s) | Load policy | Limit |
|---|---|---|---|
| `identity` | `me.md` | `always-on` | 120 lines |
| `operating-rules` | `CLAUDE.md` | `always-on` | 180 lines |
| `operating-rules-adapter` | `AGENTS.md` | `always-on` | 60 lines |
| `incidents` | `MEMORY.md` | `conditional` | 200 lines |
| `current-focus` | `GOALS.md` | `on-demand` | 140 lines |
| `nav` | `vault-map.md` | `on-demand` | 205 lines |

---

## Guardrails

- Core blocks stay small enough to be reliable startup/context material.
- Archive surfaces stay authored unless an explicit rule says otherwise.
- Cards and Actions are not generated views; their human-authored friction is load-bearing.
- If a core rule duplicates a deeper rule file, keep the core block as an index pointer and let `09 Rules/*` remain authoritative.
- [[CLAUDE.md]] is the canonical operating-rules body. Runtime adapter files such as [[AGENTS.md]] should import or point to it instead of duplicating behavior.
