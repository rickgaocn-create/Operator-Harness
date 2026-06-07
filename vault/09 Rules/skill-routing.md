---
layer: platform
paths:
  - ".claude/skills/route/SKILL.md"
  - ".claude/_state/routing-misses.jsonl"
canonical_skill: ".claude/skills/route/SKILL.md"
created: 2026-05-21
last-major-rewrite: 2026-05-21
---

# Skill Routing Rules

> Heuristics for the intent router (**`/route`**). When skill descriptions overlap, these tie-breakers apply.

## Scoring components

| Signal | Default weight | Rationale |
|---|---|---|
| Description keyword overlap (token Jaccard) | 1.0 | Claude Code's default match basis — establishes baseline |
| Trigger-phrase exact match (in "Trigger on" clause) | 2.0 | High-confidence — author wrote the trigger explicitly |
| Read-path overlap (intent mentions file/folder skill reads) | 1.5 | Strong signal of relevance |
| Companion-rule match (intent matches phrasing in a 09 Rules file) | 1.2 | Rule files are canonical contracts |
| Recent-use boost (skill ran in same session this turn) | 0.5 | Continuation likelihood |
| Description length penalty (longer descriptions match noise easier) | -0.2 per 100 chars over 200 | Counters false-positive matches |

## Tie-breakers (when top 2 within 0.3 of each other)

1. **Operational beats reasoning** for short/imperative intents (`/sync-day` over `/vault-evolve` for "sync this")
2. **Reasoning beats operational** for open-ended intents (`/vault-evolve` over `/sanity` for "what's broken")
3. **Recently-edited skills score lower** by 0.3 — fresh-edit risk
4. **Versioned-rolled-back skills score lower** by 0.5 for 7 days post-rollback — recovery period
5. **Surface ALL candidates** if still tied after tie-breakers — user picks

## Miss-promotion threshold

- 3+ routing misses for the same intent pattern within 30 days → propose instinct card via **`/vault-evolve`**
- Card describes the routing heuristic that would have prevented the miss
- Promotion to this rule file requires ≥2 confirming incidents OR explicit user approval

## Recent-use detection

Read **`.claude/_state/usage.jsonl`** for `tool="Skill"` records within the current `session` id. Any skill that ran this session gets the recent-use boost.

If `usage.jsonl` is unavailable (hook disabled, file missing), skip recent-use boost — don't fail.

## Domains exempt from routing

These skill domains have unambiguous slash commands and don't go through router:

- Code-side: `/code-review`, `/run`, `/verify`, `/security-review`
- Built-in: `/help`, `/clear`, `/config`, `/model`
- Plugin-namespaced: `feishu:*`, `enterprise-search:*`, `legal:*`, `pdf-viewer:*`

Router applies to vault-domain operator skills only (the ones in **`.claude/skills/<name>/`**).

## Hard Rules

1. **Router surfaces, doesn't dispatch.** Always shows the top-N + reasoning; user invokes.
2. **Log every miss.** **`.claude/_state/routing-misses.jsonl`** — append-only, never deleted.
3. **Default to "ask back" over "guess".** If top candidate scores < 1.5, ask the user instead of recommending.
4. **No routing for explicit slash commands.** If user typed `/<name>`, respect it. Router only fires on natural-language intent OR explicit `/route <intent>`.
