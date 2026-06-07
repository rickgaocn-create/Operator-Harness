---
layer: platform
paths:
  - "02 Cards/**/*.md"
pillar: Card · 卡片笔记
method: Zettelkasten · 卡片笔记法
---

# Card Pillar Rules · 卡片笔记约定

> Atomic insights — the "Knowing" layer. Permanent decay. One card = one idea.

## Purpose

Capture **personal synthesis**, not external facts. External facts live in **`01 Wiki/`**. Cards are *what {{USER_NAME}} learned, decided, or noticed* — extractable patterns reusable across deals, partnerships, and decisions.

**Litmus test:** "Would I want to pull this into the next M&A deal / BD call / board memo?" If no → daily note. If yes → card.

## Folder Structure

```
02 Cards/
├── _index.base              Bases-rendered dynamic Card index (table + cards views)
├── (C) README.md            Pillar overview
├── _inbox/                  Unprocessed / fleeting capture — process weekly
├── {{PROJECT_A}}/                    BD, partnership, channel insights
├── {{ORG_B}}-Inc/                 M&A patterns, JP board dynamics, AIX vendor reads
├── cross-border/            CN↔JP arbitrage principles, cultural mechanics
├── ops/                     Personal performance, workflow, biohacks
├── meta/                    Frameworks about frameworks (e.g., this one)
└── instincts/               Micro-pattern 层 — atomic trigger-action 观察 (below Card-level, see [[09 Rules/instincts.md]])
```

New domain → create folder explicitly, don't dump in `_inbox/` permanently.

**`instincts/` 是 sibling archetype，不是 domain** — atomic trigger-action observations 在 Card-level 以下。File prefix `I{YYMMDD}-` (vs Card 用 `C{YYMMDD}-`)。详 [[09 Rules/instincts.md]]。

The `_index.base` is the agent's catalog and the user's browse-view (open in Obsidian to render). Lint and Ingest skills do not touch it; the Bases plugin renders directly from frontmatter.

## Naming Convention

```
C{YYMMDD}-{kebab-case-headline}.md
```

- **C** — file-type prefix (Card)
- **YYMMDD** — 6-digit creation date (e.g., `260427` = 2026-04-27)
- **headline** — declarative, the card's claim in 3–7 words

**Examples:**
- `C260427-jp-board-reads-memos-backward.md`
- `C260425-mifei-cagr-gap-blocks-2027-ipo.md`
- `C260424-honor-channel-fills-android-gap-not-harmonyos.md`

✅ Headlines state a *finding*, not a topic. ❌ Avoid `C260427-jp-boards.md` (too vague).

## Frontmatter Contract

```yaml
---
type: card
created: 2026-04-27           # ISO date, required
source-project: {{ORG_B}}       # {{PROJECT_A}} / {{ORG_B}} / cross-border / ops / meta
source-note: "[[2026-04-25]]" # daily note / meeting / wiki page that produced this
tags: [m&a, ipo, china]
status: draft                 # draft | live | archived
links: ["[[C260315-...]]"]    # explicit cross-card links
---
```

## ADR Fields · 决策卡 (optional)

A card that records a **standing decision** (architectural / lane / strategy) — not just an insight — sets `adr: true` and carries the decision schema below. These are exactly the fields **`02 Cards/_adr.base`** renders; omit them and the decision is invisible to the ADR views.

```yaml
adr: true
adr-status: accepted        # proposed | accepted | deprecated | superseded
adr-date: 2026-05-13        # ISO date the decision was taken
superseded-by: "[[C…]]"     # ONLY when adr-status: superseded → the replacement card
```

- **`source-project` is the decision's scope key** — use the exact `source-project` token verbatim so `_adr.base` groups cleanly by domain.
- **Supersede, don't archive.** A retired decision keeps `status: live`, sets `adr-status: superseded` + `superseded-by:`, and is never deleted — preserving the decision trail (per the never-delete Hard Rule below). `status: archived` is for disproven *insight* cards, not decision history.
- Browse decisions via **`02 Cards/_adr.base`** — views: All ADRs · Accepted (in force) · Proposed · Deprecated/Superseded · Timeline.

## Card Anatomy

```markdown
# {Card headline — same as filename slug, full sentence}

> One-line claim. The compressed insight.

## Evidence
What I observed. 2-4 bullets. Specific.

## Mechanism
Why this is true. The underlying principle.

## Application
Where to deploy this. Concrete next-use cases.

## Related
- [[C260315-other-card]] — how it connects
```

Keep cards **short**. If it grows past ~300 words, split into multiple atomic cards and link.

## Lifecycle

| Stage | Trigger | Action |
|-------|---------|--------|
| **Ingest** | New source in **`00 Raw/Clippings/`** (clip, article, transcript) | Invoke `/source-ingest` — extract claims → draft Card(s) directly in domain folder → patch related Cards → log to daily note → archive source |
| **Capture** | Insight surfaces mid-conversation (no source file) | Drop in `_inbox/` with rough headline |
| **Refine** | Weekly review (Friday) | Promote from `_inbox/` → domain folder, write Mechanism + Application |
| **Live** | Card reused in actual work | `status: live`, add to `links:` of related cards |
| **Lint** | Monthly · OR >5 new Cards since last pass · OR W26 (end-cycle) | Invoke `/card-lint` — orphan / staleness / link-symmetry / frontmatter audit; user-approved patches only |
| **Archive** | Disproven / superseded | `status: archived`, link to replacement card, do not delete |

## Operations (Ingest · Query · Lint)

The pillar has three named agent operations — without them, the structure is decoration, not a system. See [[02 Cards/meta/C260429-llm-wiki-pattern-validates-three-pillar-bookkeeping-thesis]] for the rationale.

| Operation | Skill | Cadence |
|-----------|-------|---------|
| **Ingest** | `/source-ingest` (**`.claude/skills/source-ingest/SKILL.md`**) | Per-source, ad-hoc |
| **Query** | (implicit in conversation) — when answers are reusable, file them back as Cards | Continuous |
| **Lint** | `/card-lint` (**`.claude/skills/card-lint/SKILL.md`**) | Monthly · W26 · post-ingest-burst |

## Hard Rules

- **Never edit** an existing card's claim without versioning. Append a `## Update YYYY-MM-DD` block.
- **One claim per card.** Multi-claim notes belong in **`01 Wiki/`** or daily notes.
- **Link explicitly.** Tags ≠ links. Cards earn value through the graph, not the tag taxonomy.
- **No cards from prose alone.** Every card cites a source (daily note, meeting, deal artifact).
