---
layer: platform
type: control-plane-map
created: 2026-05-27
created-by: codex
---

# Harness Surfaces

Canonical map for fresh agents. Use this before editing harness mechanics.

## Edit Here

| Surface | Role | Edit rule |
|---|---|---|
| `.claude/skills/<name>/SKILL.md` | Canonical Claude skill definitions | Edit here for skill behavior. Keep frontmatter `description` short; put long history in body or references. |
| `.claude/agents/*.md` | Canonical Claude-side agent definitions | Edit here when Claude agent behavior changes. |
| `.codex/agents/*.toml` | Canonical Codex-side agent adapters | Edit here when Codex agent behavior changes. Keep in sync with Claude intent, but use Codex-native TOML. |
| `.claude/routines/*.py` | Runtime routines and status/map scripts | Edit here for engine behavior. Call `.harness/resolve_runtime.py` for machine-specific values. |
| `.claude/_state/harness-manifest.json` | Organ, state, and docs registry | Register every durable state surface, liveness organ, and orientation doc here. |
| `.harness/*` | Runtime adapter seam | Only resolve runtime-local values. Do not move skills, agents, state, or manifest here. |
| `09 Rules/*.md` | Binding rule layer | Edit when changing file contracts, workflow contracts, or harness governance. |

## Mirrors And Generated Surfaces

| Surface | Status | Rule |
|---|---|---|
| `.Codex/` | Compatibility mirror of `.codex/` on Windows | Do not treat as a separate source of truth. Update only through the same change intent as `.codex/`. |
| `08 Agents/` | Human-facing agent catalog / legacy mirror | Do not maintain behavior here. Point readers to canonical agent definitions. |
| `04 Notes/HARNESS-MAP.md` | Generated inventory | Regenerate with `harness_map.py`; do not hand-edit generated blocks. |
| `.claude/_state/underlays/*` | Generated Source Graph + Taste Engine v1 | Regenerate with `build_underlays.py`; do not hand-edit generated files. |
| `.claude/_state/obsidian-runtime.json` | Generated Obsidian API runtime snapshot | Written by `harness-dashboard`; read as sensor/UI observability only. Do not make scheduled jobs depend on it. |
| `.claude/_eval-fixtures/eval-runs/` | Generated eval history | Read for trends only; do not use as architecture truth. |
| `.claude/_state/*.jsonl` | Runtime logs / append-only telemetry | Do not edit manually unless a rule explicitly says to repair a corrupt line. |

## Deprecated Or Historical

| Surface | Rule |
|---|---|
| `.claude/skills/_archive/` | Historical recovery only. Do not route new work here. |
| `.codex/_backup/` and `.Codex/_backup/` | Migration backup only. Do not edit or cite as live behavior. |
| `.claudian/`, `.agents/`, `.operon/`, `.smart-env/` | External or legacy tool state. Treat as integration surfaces, not harness spine, unless a task explicitly targets them. |

## Windows & Bridges

The harness is engaged through **windows** (the reframe: one harness, many windows). Obsidian is one window, not the system. Bridges are kept (not consolidated) but each is a standing maintenance surface — documented here so the full inventory is visible in one place. Verified live 2026-05-29.

| Window / bridge | Identity | Process probe | Recovery |
|---|---|---|---|
| **Obsidian** | edit + visual cockpit (claudian chat · harness-dashboard · canvas) | — | restart Obsidian |
| **Claude Code CLI** | primary agent window (full tools) | — | — |
| **Discord · afk-claude2** | hardened bridge (claude2#6213) | `node …/.afk-code-claude2/` | `schtasks /End` then `/Run /TN afk-code-claude2-daemon`; auto-memory: `afk-claude2-daemon` |
| **Discord · afk-code (legacy)** | older 2nd install, separate bot | `node …/afk-code/dist/cli` | task `afk-code-daemon`; auto-memory: `afk-claude2-daemon` (NB: 2nd install) |
| **Feishu · Business Morty** | company bot `{{REDACTED}}` (inbound work channel) | `channels/feishu/launch-consumer` | `schtasks /Run /TN feishu-event-consumer-daemon`; auto-memory: `agent-morty-feishu-bridge` · `feishu-reader-architecture` |
| **Feishu/codex · Open Morty** | bot `{{REDACTED}}` → `codex.exe` via `\\.\pipe\codex-afk-feishu-daemon` | `codex.exe -C` | auto-memory: `open-morty-codex-bridge` |

Notes:
- `harness-pulse` alerts only on the **Feishu** lane; Discord keeps its own healthcheck (`afk-code-claude2-healthcheck`). The legacy Discord + codex bridges are informational here, not pulse-alerted.
- Each bridge's full recovery + known-failure modes live in the named auto-memory entry — this table is the index, not the detail.
- Output is **window-aware** (see [[CLAUDE.md]] § Communication Protocols): Obsidian/CLI markdown · Feishu rich-text · Discord plain.

## Fresh-Agent Checklist

1. Read `AGENTS.md`, then this file when the task touches harness mechanics.
2. Use `.claude/_state/harness-manifest.json` to find registered organs, docs, and state.
3. Use `04 Notes/HARNESS-MAP.md` for generated inventory and drift, but regenerate instead of editing it.
4. Edit the canonical surface only; avoid parallel edits in mirrors unless the mirror is the runtime consumer.
5. Run the relevant eval gate after edits: foundational lint for always-loaded files, skill evals for gated skills, portability for runtime surfaces, and `harness_map.py --check` after registry/index changes.

## Frontmatter Description Budget

Skill frontmatter `description` is a router hint, not a changelog.

- Target: 1-2 sentences, usually under 300 characters.
- Include: what the skill does, when to use it, and the most important exclusion if routing is ambiguous.
- Exclude: migration history, long trigger lists, incident provenance, examples, and quality rubrics.
- Put long material in the body, `references/`, companion rules, or eval configs.

## Plugin Syntax Protection

Do not normalize or "clean up" syntax that Obsidian plugins consume. Apparent noise may be a live plugin contract.

Protected examples:

- Operon inline fields: `{{operonId:: ...}}`, `{{status:: ...}}`, `{{priority:: ...}}`, `{{dateDue:: ...}}`, `{{datetimeStart:: ...}}`, `{{datetimeModified:: ...}}`.
- Operon list separators: `; ` inside list fields such as `{{contexts:: a; b}}` and `{{assignees:: {{USER_NAME}}; X}}`.
- Action/task joins: `chain-anchor:`, `[chain-anchor] | [step]`, and related `chain-anchor-note`.
- Obsidian/Dataview code fences: ```dataview``` and ```operon``` blocks.
- Obsidian links, embeds, callouts, block ids, tags, and task checkboxes.
- Legacy task metadata that still sits on live task lines, including old plugin remnants; preserve unless the task rules explicitly authorize a migration.

Before changing any symbol-heavy line in `06 Tasks/`, `10 Action/`, daily notes, or plugin config folders, read `09 Rules/tasks.md`, `09 Rules/action.md`, and the relevant plugin config under `.operon/` / `.obsidian/plugins/`.

Mojibake cleanup rule: fix corrupted prose only when the intended text is clear from context or source history. Never "repair" plugin syntax by guessing.
