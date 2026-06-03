---
type: agents-index
created-by: claude
created: 2026-05-11
last-updated: 2026-05-11
---

# 08 Agents — Subagent Index

> **Subagents** run in isolated context threads, invoked by the main Claudian conversation. They keep heavy context (vault sweeps, web research, lens-specific reviews) off the main thread. Read-only by default — they report; main thread acts.
>
> **Canonical store:** [.claude/agents/*.md](../.claude/agents) — Claudian only loads from here. This `08 Agents/` folder is the **discoverability + documentation layer**, not the source of truth.
>
> ⚠️ **Per-agent mirror files here are DEPRECATED (2026-05-24).** The `08 Agents/<name>.md` operator manuals were dual-maintained with the canonical defs and drifted (e.g. stale ticktick refs in both). Going forward: **edit only `.claude/agents/<name>.md`** — fold operator notes there as an `## Operator notes` section. This README (the catalog/index) stays; the per-agent mirrors are kept read-only for reference and slated for removal once their content is confirmed folded into canonical. **Do not create new `08 Agents/<name>.md` files.**
>
> **Hierarchy:** `.claude/agents/<name>.md` = operational definition (loaded by Claudian) · `08 Agents/README.md` = this index (vault-visible navigation).

---

## Active Subagents

| Agent | Trigger | What it does | Tools | Docs · Canonical |
|-------|---------|--------------|-------|------------------|
| **vault-researcher** | You mention any named entity | Globs the vault, returns a brief with wikilink sources | Read · Glob · Grep | [[vault-researcher\|docs]] · [canonical](../.claude/agents/vault-researcher.md) |
| **biz-doc-critic** | After saving a business artifact (pre-`/biz`) | Register B/C compliance · CN monolingual · naming · cross-project isolation · MECE | Read · Grep | [[biz-doc-critic\|docs]] · [canonical](../.claude/agents/biz-doc-critic.md) |
| **bd-prospect-researcher** | "Research [company] for {{PROJECT_A}} BD" | Web + vault sweep → 法人单位 / 决策人 / 契合点 / 建议邀请人 / Conversion 目的 | Web + Read | [[bd-prospect-researcher\|docs]] · [canonical](../.claude/agents/bd-prospect-researcher.md) |
| **ma-target-screener** | "Screen [brand] for {{ORG_B}}" | 4-dim scorecard (JP fit · margin · AI · 弱日元 arbitrage) → go / park / reject | Web + Read | [[ma-target-screener\|docs]] · [canonical](../.claude/agents/ma-target-screener.md) |
| **strategist** | `strategist: <q>` / `--mode pre-mortem` / `--mode synthesis` | Three modes — options · pre-mortem · cross-track synthesis. Peer-level voice; no framework regurgitation | Web + Read | [[strategist\|docs]] · [canonical](../.claude/agents/strategist.md) |
| **vault-manager** | `vault-manager: <op>` (audit / propose-move / repair-wikilinks / execute) | File ops + structural reasoning. **Edit-capable, two-phase (PROPOSE → EXECUTE on confirm)** | Read · Edit · Bash | [[vault-manager\|docs]] · [canonical](../.claude/agents/vault-manager.md) |

> **Two layers per agent:**
> - **Docs** (`08 Agents/<name>.md`) — operator manual: what to expect, sample interactions, edge cases. Read this when learning or recalling how to use the agent.
> - **Canonical** (`.claude/agents/<name>.md`) — system prompt the agent itself reads. Edit via Claudian Subagent UI or directly. Changes take effect on next invocation.
>
> **vault-manager is the only edit-capable agent.** Two-phase protocol (PROPOSE / EXECUTE) is non-negotiable to prevent parallel-write collisions with the main thread.

---

## How They Get Invoked

### Auto-invocation (description-driven)

Each subagent's frontmatter `description:` field tells Claudian when to fire it proactively. The strong descriptions (`Use PROACTIVELY when...`) trigger the main thread to delegate without explicit instruction.

In practice:
- Mention **小鹏汽车** in chat → `vault-researcher` auto-fires before the main thread answers
- Save a meeting note → `biz-doc-critic` can be chained before `/biz`
- Say "research 蜜雪冰城" → `bd-prospect-researcher` auto-fires

### Explicit invocation

You can also call them directly by name in chat — main thread will delegate. Useful when:
- You want to control which agent runs
- You're testing a new agent
- You want parallel agents on the same input (e.g., run `bd-prospect-researcher` + `ma-target-screener` on the same brand for cross-track read)

---

## How to Edit

The canonical files live in `.claude/agents/*.md`. Obsidian hides dot-prefixed folders by default, so you have two options:

1. **Claudian UI** — Settings → Subagents → click any agent → edit name / description / tools / disallowed tools / skills / system prompt. The UI writes back to `.claude/agents/<name>.md`.

2. **Direct file edit** — open `.claude/agents/<name>.md` via Claudian's file picker, or unhide dot-folders in Obsidian's settings (Settings → Files & Links → "Detect all file extensions" doesn't reveal dot-folders; use file explorer or VSCode to edit if needed).

When editing system prompts, the YAML frontmatter fields are:

```yaml
---
name: <kebab-case-id>          # must match filename
description: <when to use>      # description-driven auto-invocation
tools: Tool1, Tool2             # comma-sep; empty = all
disallowed_tools: Tool3         # optional
skills: skill-name              # optional, comma-sep
model: inherit                  # or sonnet/opus/haiku
---
```

---

## Adding New Subagents

**Before adding**, ask:

1. **Does this need context isolation?** If the task is light and one-shot, a skill (`.claude/skills/<name>/SKILL.md`) is better — it runs in main thread, no context tax. Subagents earn their slot when (a) heavy context (large file reads, web research) or (b) specialized voice/lens.
2. **Does it already exist as a skill?** Check [[Skills I Use Daily]] and `ls .claude/skills/` first. Don't duplicate `/biz`, `/meeting-note-deep`, `/sanity`, `/grill-me` etc.
3. **Read-only?** Default to yes. Edit-capable subagents are riskier (parallel writes, lost main-thread context).

**Template** — create `.claude/agents/<name>.md`:

```yaml
---
name: <kebab-case-name>
description: Use PROACTIVELY when <condition>. Returns <output shape>. <Read-only? Y/N>.
tools: Read, Glob, Grep
model: inherit
---

# <Display Name>

You are <role>. Your job: <one-sentence mission>.

This agent exists because of <incident or rule reference>.

## Trigger
<When to invoke>

## Steps / Sweep order
<Mandatory order if applicable>

## Output format
<Schema>

## Hard rules
<Bullets>
```

Then:
1. **Create the vault-visible doc** at `08 Agents/<name>.md` using the same structure as the existing four (`type: subagent-doc` frontmatter · What it does · When to invoke · Sample interactions · Hard rules · Output format · Edge cases · Lineage · Change log · Canonical link · Related).
2. **Add a row** to the "Active Subagents" table at the top of this README.
3. **Flag in `vault-map.md`** if the addition is structurally relevant (e.g., new agent category, new dependency chain).
4. **Test** with a sample invocation before relying on auto-invoke.

**Drift check:** when canonical behavior changes (system prompt edit), update the matching `08 Agents/<name>.md` change log. The two layers must agree on *what the agent does*; they can differ in *how they say it*.

---

## Design Principles

- **Subagents report, main thread acts.** Subagents are research/audit lenses. Writes (file edits, task captures, deal memos) happen in the main thread where the user can see them.
- **Tight outputs.** Each subagent has a max word budget. Density beats coverage.
- **Cite sources.** Every fact in every output has a vault wikilink or URL.
- **No editorializing.** Subagents surface; user decides.
- **Cross-project isolation.** {{PROJECT_A}} agents don't reference {{ORG_B}} context and vice versa.

---

## Pointers

- **Slash commands:** [[Skills I Use Daily]] · [[vault-map.md]] § Skills Index
- **Rule layer:** [[09 Rules/file-types.md]] · [[09 Rules/tasks.md]]
- **Memory (incident-driven):** [[MEMORY.md]]
- **Auto-chain rules:** [[CLAUDE.md]] § Skill Auto-Chain Rules
