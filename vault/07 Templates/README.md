---
type: meta
created-by: claude
created: 2026-05-12
---

# 99 Templates

> Templates referenced by Obsidian core plugins (Daily Notes, Templates) and Templater. Pure Mustache (`{{date:FORMAT}}`) so they work without Templater configuration.

## Registered Templates

| Template | Plugin | Output Path | Trigger |
|----------|--------|-------------|---------|
| [[Daily Note]] | Daily Notes (core) | `04 Notes/daily notes/{YYYY-MM-DD}.md` | Daily Notes button / hotkey |

## Canonical Contracts

- **Daily Note** mirrors [[09 Rules/time.md]] § Daily frontmatter contract — substitutions via `{{date:FORMAT}}` Mustache placeholders (moment.js format strings under the hood).
- Equivalent skill path: `.claude/skills/daily-note/SKILL.md` (`/daily-note` invocation). Both produce same scaffold so the button and the skill stay interchangeable.

## Substitution Reference

| Placeholder | Resolves to (today: Tue 2026-05-12) |
|---|---|
| `{{date:YYYY-MM-DD}}` | `2026-05-12` |
| `{{date:dddd}}` | `Tuesday` |
| `{{date:ddd}}` | `Tue` |
| `{{date:WW}}` | `20` (ISO week, Monday-start) |
| `{{date:GGGG-[W]WW}}` | `2026-W20` (parent weekly link) |
| `{{date:GGGG-[Q]Q}}` | `2026-Q2` (parent quarter link) |
| `{{date:GGGG/[Q]Q/[W]WW}}` | `2026/Q2/W20` (cascade tag) |
| `{{date:E}}` | `2` (ISO weekday: Mon=1, Sun=7 → Day X/7 banner) |

## Adding New Templates

1. Drop `{Name}.md` here with `{{date:FORMAT}}` placeholders (no Templater dependency unless needed).
2. Register in the table above.
3. If a core plugin should auto-use it, update the relevant `.obsidian/{plugin}.json`.
