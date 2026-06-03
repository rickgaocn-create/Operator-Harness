---
layer: platform
type: rule-layer
domain: 00-raw-knowledge-base
created-by: claude
created: 2026-05-09
overrides: prose conventions in CLAUDE.md when in conflict
---

# Rule · Raw Source Immutability

> Machine-enforceable rules for [[00 Raw/]] and the three-layer KB pattern (Raw → Wiki → Index). Read before any op on **`00 Raw/Clippings/**`, `**01 Wiki/`**, or invoking `/source-ingest`.

---

## The Three-Layer KB

| Layer | Folder | Mutability | What lives here |
|---|---|---|---|
| **Raw** | **`00 Raw/Clippings/`** | **Immutable after ingest** | Original snapshots of articles, papers, threads, screenshots. Never modify. |
| **Wiki** | **`01 Wiki/`** | LLM-maintained | Synthesized entity pages, concept pages. Updated by `/source-ingest` as new sources connect. |
| **Index** | **`01 Wiki/index.md**` + `**00 Raw/log.md`** | Append-only catalog | Master catalog (Wiki) + chronological operations log (Raw). |

---

## Hard Rules

### Raw layer

1. **Never modify** a file in **`00 Raw/Clippings/`** after creation. Period.
2. **Never delete** a raw source. If superseded, mark `superseded: true` in frontmatter; keep the file.
3. **Filename = `YYYY-MM-DD <slug>.md`** for clippings. Date is ingest date, not source publication date (publication date goes in frontmatter).
4. **Frontmatter required** on every clipping: `source-url`, `source-type`, `ingested: YYYY-MM-DD`.
5. **Archive after ingest** — once `/source-ingest` has processed a clipping and written wiki updates + log entry, the clipping moves to **`00 Raw/_processed/{YYYY-MM}/`** (not deleted).

### Wiki layer

6. **Each entity = one file.** Don't create a second file for the same entity; update the existing page.
7. **`(C)` prefix** on Claude-created wiki pages (e.g., `(C) ByteDance.md`). User-created entries are bare names. Per [[09 Rules/file-types.md]].
8. **Bidirectional Related sections.** When updating entity A's page with a fact that mentions entity B, patch B's Related section too.
9. **Citations required.** Every fact in a wiki page must point to a source via wiki-link to the raw clipping or `[source-name](url)` for non-archived sources.

### Index layer

10. **`01 Wiki/index.md` is the navigation hub.** Updated when new entity page created, when entity page is significantly revised (>50% rewrite), or via `/sanity` audit.
11. **`00 Raw/log.md` is append-only.** One row per ingest operation. Never edit prior rows.

---

## Audit Hooks

`/sanity` Phase 2 watches:

- **Stuck files** (>7d in **`00 Raw/Clippings/`** without ingest) → 🟡 propose `/source-ingest`
- **Dead wikilinks** in **`01 Wiki/`** → 🔴 auto-comment-out `<!-- broken: [[name]] -->`
- **Orphan archives** (wiki page with zero inbound wikilinks) → 🟡
- **Index drift** (entity page exists but not in [[01 Wiki/index.md]]) → 🟡 propose update
- **Log drift** (clipping in `_processed/` but no row in [[00 Raw/log.md]]) → 🟡

---

## Failure Modes

| Symptom | Recovery |
|---|---|
| User edited a raw clipping | Restore from git if possible. Otherwise note in frontmatter `tampered: true` and treat as evidence rather than ground truth. |
| `/source-ingest` failed mid-way (wiki updated, log not appended) | Manual append to **`00 Raw/log.md`**; don't re-run ingest (would create duplicate Cards). |
| Two entity files exist for same entity | Merge into the older file; archive the newer to **`01 Wiki/_archive/`** with `superseded: true`; update [[01 Wiki/index.md]]. |
| Wiki page makes a claim with no source citation | 🟡 in next `/sanity` — propose source backfill or removal of unsupported claim. |

---

## See Also

- [[01 Wiki/index.md]] · [[00 Raw/log.md]]
- `/source-ingest` skill (**`.claude/skills/source-ingest/SKILL.md`**)
- `/sanity` skill (**`.claude/skills/sanity/SKILL.md`**)
- [[09 Rules/file-types.md]] — `(C)` prefix rules
- [[09 Rules/cards.md]] — Card pillar (personal synthesis layer that consumes Wiki facts)
