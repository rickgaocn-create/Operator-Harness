---
category: work
name: source-ingest
description: Ingest external raw input into the Card pillar. Use --type=clipping|article|instinct|conversation. Not for personal brain dumps; use /distill for those.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch
companion-rules:
  - "[[09 Rules/cards.md]]"
  - "[[09 Rules/instincts.md]]"
---
# Skill: Source Ingest (`--type=clipping` default · `article` · `instinct` · `conversation`)

Ingest raw input into the Card pillar. One skill, four types via flag or trigger-phrase inference.

| `--type` | Input | Output | Replaces |
|---|---|---|---|
| **clipping** (default) | File in **`00 Raw/Clippings/**` | 0–N Cards in `**02 Cards/{domain}/`** | (original /source-ingest) |
| **article** | Long-form article (file or URL) | 0–N Cards, more aggressive splitting | (original /source-ingest, tuned) |
| **instinct** | Conversation snippet OR direct trigger+action | 1 file in **`02 Cards/instincts/I{date}-{slug}.md`** | /instinct-capture |
| **conversation** | Current conversation context | Cards or instincts depending on what surfaces | (new) |

## Mode Routing

| Trigger | Mode |
|---|---|
| `/source-ingest` no flag with file path OR file in **`00 Raw/Clippings/`** | clipping |
| `/source-ingest --type=instinct` OR "save as instinct" / "drop instinct" / "记一个 instinct" / "instinct: when X then Y" | instinct |
| `/source-ingest --type=article` OR explicit article cue | article |
| `/source-ingest --type=conversation` OR "ingest this conversation" | conversation |

Genuinely ambiguous → plain text 1-line: *"clipping / article / instinct / conversation?"* and await reply.

---

## Clipping Mode (default — original source-ingest)

Read a raw source (clipping, article, transcript, image-bearing note) and turn it into Card-pillar synthesis: extract claims, draft Cards, update related Cards' bidirectional links, log the ingest in today's daily note. The Ingest half of the **Ingest · Query · Lint** triad ([[02 Cards/meta/C260429-llm-wiki-pattern-validates-three-pillar-bookkeeping-thesis]]).

> **Origin:** Karpathy's "LLM Wiki" pattern — **`00 Raw/Clippings/llm-wiki.md**` (2026-04-29). Without an explicit Ingest operation, `**00 Raw/Clippings/**` accumulates and the synthesis layer (`**02 Cards/`**) starves.

## When to Use

- New file dropped in **`00 Raw/Clippings/`** — web clip, article, gist, podcast notes
- Long meeting transcript or research dump in **`00 Raw/`**
- User says "ingest this", "process this clipping", "card this", "extract the insights from"
- A `<browser_selection>` arrives that's worth permanent capture

**Don't invoke for:**
- Atomic todo capture → `/task-capture`
- Project artifact filing (decks, contracts) → manual move to **`03 Projects/<name>/`**
- Triage-only without synthesis → `/inbox-process`
- Meeting transcripts with action items → `/meeting-note` or `/meeting-note-deep` first; this skill optionally runs after to harvest Cards

---

## Principles

1. **One source can produce 0–N Cards.** Most produce 1–3. If you can't articulate a claim, don't force one.
2. **Cards capture *personal synthesis*, not external facts.** External fact about a counterparty/market → **`01 Wiki/`**, not a Card. Litmus: "Would I pull this into the next deal/call/memo?"
3. **Bidirectional links or no link.** When a new Card cites an existing Card, update the existing Card's `## Related` section. Asymmetric links are graph rot.
4. **Source provenance is sacred.** Every Card cites its source in `source-note:` frontmatter — no anonymous claims.
5. **Log the ingest.** The daily note is the ledger. An ingest that doesn't appear there didn't happen for retrieval purposes.
6. **Discuss before drafting at scale.** 1–2 candidates → draft and show. 5+ candidates → run a checkpoint: which deserve permanence?
7. **Wiki entries are deduped before write, never after.** Any new **`01 Wiki/`** entry must pass the Vault Sanity Sweep (§ Phase 2.5) — alias check, canonical-path check, partial-match read. Duplicates at root-level vs nested path are the 2026-05-13 incident class. Prevent at creation, don't reconcile later.

---

## How It Works

1. Read source · 1.5 Preheat related-card cache · 2. Extract candidate claims · **2.5 Vault Sanity Sweep (wiki dedup)** · 3. Discuss · 4. Search for related Cards · 5. Draft · 6. Patch Related sections · 7. Log to daily · 8. Mark source processed · 9. Confirm

---

## Phase 1: Read the Source

Default target: most recent file in **`00 Raw/Clippings/`** (ignore `_processed/`).

```bash
ls -t "00 Raw/Clippings/" | grep -v "^_" | head -5
```

Or accept explicit path: **`/source-ingest 00 Raw/Clippings/some-file.md`**

Read the full file. If it has embedded image links (`![alt](url)` or `![[image.png]]`):
- Local images → read alongside text per CLAUDE.md "Embedded Images in Notes"
- Remote URLs → fetch via `WebFetch` only if image content is load-bearing (skip decorative)

---

## Phase 1.5: Preheat Related-Card Cache

Before claim extraction, warm the related-card cache so Phase 3 (Search related Cards) doesn't grep cold. Borrowed from **`wiki/hot.md`** pattern in [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian); see [[02 Cards/meta/C260509-claude-obsidian-vs-source-ingest-comparison]].

**What to load:**

1. Infer domain from source path or content cues (`{{PROJECT_A}}` / `{{ORG_B}}-Inc` / `cross-border` / `ops` / `meta`)
2. Glob **`02 Cards/{domain}/**/*.md`** — most-recent 10 by mtime
3. Read **frontmatter + first headline only** (skip body) — keeps context budget tight
4. Note tags + status + linked-card array per card — these drive Phase 3 + Phase 5

**When to skip:**

- Source is single-domain *and* < 3 candidate claims expected (small ingest, no benefit)
- Domain genuinely ambiguous → defer to Phase 3 cold grep with `_inbox/` flag
- Card count in domain ≤ 5 — full read is cheaper than selective preheat

**Why:** Phase 3 hits cold cache otherwise — slow grep, missed bidirectional patches, occasional false-negative on "no related card found" when one existed.

**Output (silent):** working-context summary of N preheated cards. Do not surface to user — this is infrastructure, not a step requiring approval.

---

## Phase 2: Extract Candidate Claims

Scan for **claims** (not topics). Each candidate must:
- State a *finding* in 5–15 words ("X works because Y; therefore Z")
- Be reusable across deals/calls/memos (litmus from `[[09 Rules/cards.md]]`)
- Have specific evidence in the source (cite paragraph or quote)

**Reject as non-Card material:**
- Pure external facts → propose **`01 Wiki/`** entry instead
- "Topics" without a claim ("AI in gaming") → not a Card
- One-off observations with no reusability ("we should call X tomorrow") → daily note or task

Output candidates as a numbered list:

> Found N candidate Cards from `[source]`:
>
> 1. **{slug-headline}** — {one-line claim}. Domain: {{{PROJECT_A}} | {{ORG_B}}-Inc | cross-border | ops | meta}.
> 2. **{slug-headline}** — {one-line claim}. Domain: {…}.
>
> Plus M items that look like external facts → propose **`01 Wiki/`** instead (see Phase 2.5 dedup before naming targets).
>
> Which to crystallize as Cards? (default: all)

Wait for user signal before drafting.

---

## Phase 2.5: Vault Sanity Sweep (Wiki Dedup)

> **Why this phase exists:** 2026-05-13 incident — 4 entity entries (诗悦 / TapTap / 4399 / Bilibili) were written to **`01 Wiki/<name>.md**` at flat root while canonical entries already existed at `**01 Wiki/{{PROJECT_A}}/<category>/<name>.md`**. Caused graph duplication, ambiguous wikilink resolution, manual reconciliation. This phase prevents recurrence.

Run **only for the wiki-bound items** identified in Phase 2 (Cards have date-prefix naming so don't collide). Do NOT skip — silent duplicates are worse than friction at write time.

### Step A — Pre-write existence check

For each candidate wiki entry, normalize the entity name and sweep:

```bash
ENTITY="<entity name>"
# Try CN, EN, and common alias variants
ALIASES=("<English form>" "<short form>" "<alt CN form>")

# Glob all paths mentioning the entity name (whole vault, all depths)
for term in "$ENTITY" "${ALIASES[@]}"; do
  find "." -type f -name "*${term}*.md" 2>/dev/null
done

# Grep frontmatter aliases that already cover it
grep -rln "aliases:" "01 Wiki" "03 Projects" 2>/dev/null \
  | xargs grep -l "${ENTITY}" 2>/dev/null
```

### Step B — Decision tree

| Match condition | Action |
|---|---|
| Exact name match at canonical path | **Merge into canonical.** Add `aliases:` to canonical frontmatter if missing. Do NOT create new file. Patch with the new info from source. |
| Partial / alias / variant-spelling match | Read the match. ≥50% topic overlap → merge into existing. <50% → confirm with user before writing new. |
| No match anywhere | Proceed — but respect vault structure (Step C). |
| Multiple matches at different paths | **Surface to user as duplicate triage** — don't pick a canonical unilaterally. Stop and ask. |

### Step C — Respect canonical path convention

The vault uses nested **`01 Wiki/<project>/<category>/<name>.md**` for project-affiliated entities. The flat root (`**01 Wiki/<name>.md`**) is reserved for project-agnostic or cross-cutting entities (e.g. external skill directories, fund vehicles spanning multiple tracks).

Detection heuristic before writing:

```bash
# Look at sibling entries in the most likely category folder
ls "01 Wiki/{{{PROJECT_A}},{{ORG_B}}}/公司信息/" 2>/dev/null     # orgs
ls "01 Wiki/{{{PROJECT_A}},{{ORG_B}}}/渠道/" 2>/dev/null         # channels
ls "01 Wiki/{{{PROJECT_A}},{{ORG_B}}}/团队/" 2>/dev/null         # people
ls "01 Wiki/{{{PROJECT_A}},{{ORG_B}}}/<other>/" 2>/dev/null      # whichever fits
```

If a sibling category exists, write inside it. Flat-root is a hedge, not a default.

| Entity type | Canonical path pattern |
|---|---|
| Org / company / fund | **`01 Wiki/<project>/公司信息/<name>.md**` or `**01 Wiki/<project>/渠道/<name>.md`** |
| Person | **`01 Wiki/<project>/<category>/<name> (<org>).md`** |
| Cross-cutting (no project home) | **`01 Wiki/<name>.md`** (flat root) — only if confirmed no project association |

### Step D — Output to user (mandatory if duplicates found)

> 🧹 Sanity sweep — `[entity]`:
> - Existing canonical: `<path>` (read it; overlap ≈ X%)
> - Proposed: merge new info into canonical, add `aliases: [...]`, skip creating `<would-have-been path>`
>
> Proceed with merge plan? (Or surface as new entry if topic is genuinely different.)

### Step E — Aliases over rewrites

When merging duplicates, add `aliases:` to the canonical's frontmatter rather than rewriting every inbound wikilink:

```yaml
---
aliases:
  - <Old display name>
  - <English form>
  - <Short form>
---
```

Obsidian's alias system resolves `[[Old Name]]` to the canonical automatically. Only rewrite inbound wikilinks in:

- **`01 Wiki/index.md`** — canonical-path display matters
- Files forwarded externally (deck embeds, board materials) — cleaner display

Research notes, daily notes, card bodies → leave alone; aliases handle them.

---

## Phase 3: Search for Related Cards

For each approved candidate, find related existing Cards:

```bash
grep -rl "tags:.*{tag1}" "02 Cards/" | head -10
grep -rli "{key-noun-from-headline}" "02 Cards/" | head -10
```

Build a map:

| Candidate | Related existing | Relationship |
|---|---|---|
| C260429-{...} | [[C260427-three-pillar-pkm-value-is-the-closed-loop]] | extends / contradicts / refines |

This map drives Phase 5 (bidirectional link patching).

---

## Phase 4: Draft Cards

For each approved candidate, write a Card per `[[09 Rules/cards.md]]` contract.

**Path:** **`02 Cards/{domain}/C{YYMMDD}-{kebab-slug}.md`**

- Domain auto-routed from the candidate's identified domain (Phase 2)
- Skip `_inbox/` for AI-ingested Cards — they have known domain at creation
- Genuinely ambiguous domain → write to `_inbox/` and flag

**Frontmatter (exact contract):**

```yaml
---
type: card
created: YYYY-MM-DD            # today, ISO
source-project: {{PROJECT_A}} | {{ORG_B}} | cross-border | ops | meta
source-note: "[[00 Raw/Clippings/{source-file}]]"  # always cite the source
tags: [tag1, tag2, tag3]
status: live                   # draft if uncertain, live if confident; never default to draft
created-by: claude
links:
  - "[[C{YYMMDD}-{related-card}]]"
---
```

**Body — strictly the 5-section anatomy:**

```markdown
# {Full headline — declarative, the claim restated}

> One-line claim. The compressed insight. ≤ 25 words.

## Evidence
- Specific observation 1 (cite source paragraph / quote)
- Specific observation 2
- Specific observation 3
[2–4 bullets. Skip if source is single-paragraph.]

## Mechanism
{Why this is true. The underlying principle. 2–4 sentences.}

## Application
- Concrete reuse case 1 — where to deploy this
- Concrete reuse case 2
- Generalizable principle (optional)

## Related
- [[C{YYMMDD}-related]] — how it connects (1 line)
- _Future card: {gap noticed during ingest}_  (optional)
```

**Hard quality gates:**
- ≤ 300 words total. Longer → split into two atomic Cards.
- No `## Update YYYY-MM-DD` blocks on creation (those are for future amendments).
- All wikilinks must resolve. Referenced-but-not-yet-existing Card → mark as `_Future card: ..._`, not a dead link.

---

## Phase 5: Patch Related Sections of Existing Cards

For each link from new → existing Card, patch the existing Card's `## Related` section to add the inverse link.

**Use `Edit` (not `Write`) — surgical patch:**

```markdown
## Related
- [[C260427-old-card]] — existing relationship   ← PRESERVE
- [[C260429-new-card]] — {one-line description of inverse relationship}   ← ADD
```

Never reorder existing Related entries. Append new ones at the bottom of the section.

If the existing Card has no `## Related` section, add it before the file ends. If it has `links:` frontmatter, append the new wikilink to the array — keep YAML and prose Related synced.

---

## Phase 6: Log Ingest to Today's Daily Note

Path: **`04 Notes/daily notes/{YYYY-MM-DD}.md`**

- **If exists:** append a single line under `## Ingests` (create section if missing — daily-note template pre-stubs this)
- **If missing:** propose creating via `/daily-note`, OR append the log entry to the most recent daily with a backfill note, depending on user preference

**Log line:**

```markdown
## Ingests
- [HH:MM] `{source-filename}` → [[C{date}-{slug-1}]] · [[C{date}-{slug-2}]] (M cards, K cross-links updated)
```

`[HH:MM]` matches the broader vault convention for timed entries.

---

## Phase 7: Mark Source as Processed

Two options — pick by volume and recovery preference:

**Option A — Move (cleaner, default):**

```bash
mkdir -p "00 Raw/Clippings/_processed"
mv "00 Raw/Clippings/{file}.md" "00 Raw/Clippings/_processed/{file}.md"
```

**Option B — Frontmatter stamp (preserves location):**

Patch source frontmatter to add `processed: YYYY-MM-DD` and `cards: ["[[C{date}-...]]", ...]`. Useful if the source is referenced elsewhere by path.

Default Option A unless the source is linked from another vault file.

---

## Phase 8: Confirm

Tight summary:

> Ingested `[source]`:
> - **N Cards** drafted: [[C{date}-{slug-1}]] · [[C{date}-{slug-2}]]
> - **K Cards** updated (Related sections patched): [[C{older-1}]] · [[C{older-2}]]
> - **Daily note** appended: [[YYYY-MM-DD]] § Ingests
> - Source moved to `_processed/`
>
> Want to chain `/card-lint` to check graph health? (Recommended after every 5–10 ingests.)

---

## Hard Rules

- **Never auto-create Cards without showing candidates first.** Phase 2 is non-skippable — it's how the user keeps the synthesis layer signal-dense.
- **Always cite the source.** No empty `source-note:` fields. If unclear, ask.
- **Bidirectional links only.** A new Card linking to an existing Card *must* trigger a patch on the existing Card's Related section.
- **Domain folder is decided at write time.** Don't dump in `_inbox/` if the domain is obvious — that's a hedge, not a workflow.
- **One claim per Card.** Source produces a 600-word Card → it's two cards stuck together. Split.
- **Bilingual routing follows source.** CN source → CN Card. EN source → EN Card. Don't translate gratuitously.
- **Never edit the source file's body.** Only frontmatter (Option B) or move it (Option A).
- **Wiki entries: sweep before write, never after.** Every **`01 Wiki/`** candidate must pass Phase 2.5. Flat-root vs nested-path duplicates are graph rot. If in doubt, surface as duplicate triage and ask — do not write speculatively.
- **Canonical wiki path is nested by default.** **`01 Wiki/<project>/<category>/<name>.md`** for project-affiliated entities. Flat root only for cross-cutting / no-project-home entities, and only after confirming no project association exists.

---

## Failure Modes

| Symptom | Fix |
|---|---|
| Source produced 0 Cards | Move source to `_processed/` with a note ("no synthesis worth permanence") so it doesn't get re-ingested. Surface to user — sometimes signals a routing miss (should have been Wiki, not Card material). |
| User rejects all candidates | Same as above. Don't insist. |
| Existing Card has unresolved wikilinks | Don't fix unrelated link rot during ingest. Note for `/card-lint`. |
| Source contains both Card material AND atomic todos | Run ingest first, then propose `/task-capture` chain for the todos. Don't bundle. |
| Domain genuinely ambiguous | Default `_inbox/` and flag — better than a wrong-domain commit. |
| Two related sources in queue | Process one at a time. The second ingest will see the first's Cards and link naturally. |
| Phase 2.5 sweep finds a canonical at deeper path | **Default action:** merge into canonical, add `aliases:` for old display name, do NOT write the flat-root entry. Surface the merge plan to user only if ≥50% of the new material is genuinely net-new info (in which case the merge IS the work; otherwise it's a no-op). |
| Phase 2.5 finds multiple canonicals at different paths | Stop and surface to user — duplicate triage is theirs, not Claude's. Two canonicals = pre-existing graph rot, not something to silently fork. |

---

## Integration with Other Skills

| Trigger | Hand-off |
|---|---|
| Ingest produces Cards naming a workstream | `/task-capture` for the workstream's atomic next-steps (≤3 new tasks per write) |
| Ingest reveals a missing Action file | **Propose** spawning Action file (per `[[09 Rules/action.md]]` Auto-Creation Policy); wait for go-ahead |
| Source is a meeting transcript | Run `/meeting-note` or `/meeting-note --deep` first; this skill harvests Cards from the resulting meeting note |
| Ingest reveals OKR-altering insight | Surface for next `/okr` Mode B check-in |
| 5+ ingests since last lint | Recommend chaining `/card-lint` |
| New Card written | Optionally chain `/card-lint --mode=bridge` for cross-domain bridge discovery |

---

## Article Mode (`--type=article`)

Same flow as Clipping mode with these adjustments:

1. **More aggressive splitting**: long-form (>2000 words) tends to contain 5+ distinct claims. Default to surfacing all → user picks. Don't force compression into single Card.
2. **Section-level pass**: read article in chunks by `##` heading. Each section is a candidate-Cards source.
3. **Pull-quote evidence**: Cards from articles benefit from direct quote evidence — include 1-2 verbatim quotes in `## Evidence` per Card, attributed.
4. **Author attribution**: frontmatter `source-author: {name}` if attributable. Useful when Card cites a methodology from a master.
5. **URL preservation**: if source is a web article, `source-note:` should be the URL + local clipping (if any).

All Phase 1-8 from Clipping mode apply; just tune the volume + evidence style.

---

## Instinct Mode (`--type=instinct`)

Drop a micro-pattern observation (trigger + action) to **`02 Cards/instincts/I{date}-{slug}.md`** per [[09 Rules/instincts.md]] template. Pre-Card, atomic, user-approved (no auto-promote).

> **Contract reference:** [[09 Rules/instincts.md]] is source of truth for archetype. When skill ≠ rule file, rule file wins.

### When to use (instinct)

- "save as instinct: when X then Y" / "记一个 instinct" / "drop instinct" / "/source-ingest --type=instinct"
- 对话中发现一个 trigger-action 微模式但还不够成 Card
- Cluster 自动检测前的手动 capture
- `/grill-me` v2 Phase 4 resolution 时 atomic-level pattern surface → propose instinct (legacy — /grill-me now archived; same idea applies in conversation)

**Don't use for:**
- Already-synthesized insight (with mechanism + application) → that's a Card, use `--type=clipping` or `--type=article`
- Multi-conditional rule ("always when X AND Y do Z") → split into multiple instincts, or write a `09 Rule` directly
- Action item ("做 X") → use `/task-capture`
- Daily-note 散记 → daily note `## Quick Capture`

### How It Works (instinct)

#### Instinct Phase 1 — Extract trigger + action

从用户语句或对话上下文抽取：
- **trigger**: "when {condition}" — 1 行
- **action**: "{do this}" — 1 行
- **domain**: vault | {{PROJECT_A}} | {{ORG_B}}-Inc | cross-border | ops | meta（推断；不确定时 ask 1 行 "属于哪个 domain？"）

⚠️ **NEVER use AskUserQuestion** — plain text 单行 ask, 等回复。

#### Instinct Phase 2 — Confidence default 0.5

Initial confidence 0.5 (unverified). 例外:
- 对话中复现 2+ 次 → 起 0.6
- 用户说"我见过 X 次" → calibrate (每次 +0.1, cap 0.9)
- Claude propose 用户接受 → 0.5 保守

#### Instinct Phase 3 — Generate slug

```
I{YYMMDD}-{kebab-case-trigger-action}.md
```

Slug 应 capture trigger + action in 5-8 words.

**Good**: `I260514-when-bd-counterpart-pulls-4-lines-mirror-upline-team.md`
**Bad**: `I260514-bd-stuff.md` (no trigger/action hint)

#### Instinct Phase 4 — Write file

Per [[09 Rules/instincts.md]] template:

```markdown
---
type: instinct
created: {today YYYY-MM-DD}
domain: {domain}
trigger: "{when X}"
action: "{do Y}"
confidence: {0.5 default or calibrated}
status: draft
source-context: "{conversation reference or [[daily-note]]}"
related-instincts: []
promoted-to: null
---

# {trigger-action headline}

> **Trigger:** {when X}
> **Action:** {do Y}
> **Confidence:** {0.X}

## Observation

{1-3 bullets, ≤50 字, specific scenario}

## Why It Might Be A Pattern

{1-2 lines hypothesis, OR leave "Not synthesized yet — first observation"}

## Related

{Search for similar trigger/action keywords in 02 Cards/instincts/ → list hits. If none, write "First observation in this trigger family"}
```

#### Instinct Phase 5 — Update related instincts (if any)

If Phase 4 found similar instincts → patch their `related-instincts:` frontmatter to add new instinct's wikilink. Bidirectional symmetry.

#### Instinct Phase 6 — Confirm

> "Instinct 已落档 [[02 Cards/instincts/I{date}-{slug}.md]]. domain: {x}, confidence: 0.{Y}, status: draft. Cluster 检测会在下次 `/vault-evolve` 跑（{domain} 已有 {N} instincts，再 {3-N} 个就到 cluster 阈值）."

### Instinct Mode hard rules

1. **ONE trigger + ONE action per instinct.** Multi-conditional → split or write a `09 Rule`.
2. **NEVER 设 confidence > 0.7 in initial capture.** 0.5 default; `/vault-evolve` daily 升级 based on reoccurrence.
3. **NEVER drop instinct without `domain:` field.** Cluster detection requires domain grouping.
4. **NEVER drop instinct > 100 字 body.** 超过 = not an instinct, that's a Card — use `--type=clipping`.
5. **NEVER auto-promote instinct → Card/Rule/Skill.** Promotion is always user-approved.
6. **NEVER 用 AskUserQuestion** — plain text 单行 ask.
7. **ALWAYS check related instincts** in Phase 4 (bidirectional `related-instincts:`).
8. **ALWAYS update `[[02 Cards/instincts/(C) README.md]]` seed list** if among first 10 instincts.

### Instinct Mode failure modes

| Symptom | Fix |
|---|---|
| Trigger 模糊 ("when 某些情况") | Plain text ask "trigger 更 specific — what exactly?" |
| Action 是 multi-step / process | Split or recommend `/scaffold --type=skill` |
| Domain 不在 enum 内 | Propose 加新 domain to [[09 Rules/instincts.md]] (user 拍板) |
| 用户说"这个挺重要的"但其实是 Card-level | "Sounds synthesized — use `--type=clipping` for a Card instead?" |
| Slug 撞名 | Add `-v2` suffix OR ask "已有同 slug, overwrite or new?" |
| 用户连续 drop 5+ instincts | Surface "看起来 cluster 已在形成；现在 propose promotion 还是继续 capture?" |

---

## Conversation Mode (`--type=conversation`)

Treat the current conversation as the source. Useful when insight surfaces mid-chat and no separate file exists.

### Phase C1 — Identify the candidate material

Scan the recent conversation turns (user-authored content) for:
- **Claims** (Card material) — "X works because Y" with reusability across deals/calls
- **Instincts** (trigger+action patterns) — "when X happens, I do Y" with confidence < 1.0
- **Wiki material** (external facts about an entity) — route per **`01 Wiki/`** conventions

### Phase C2 — Surface candidates

```
Found in conversation:

📇 Card candidates:
1. {slug-headline} — {claim}. Domain: {x}.
2. ...

🧠 Instinct candidates:
1. when {trigger} → {action}. Domain: {x}.
2. ...

📚 Wiki candidates:
1. {entity} — propose 01 Wiki/{path}/{name}.md

Which to crystallize? (numbers / "all cards" / "all instincts" / "none")
```

### Phase C3 — Dispatch per type

For each accepted candidate:
- Card → Clipping mode Phase 4-7 (draft + bidirectional patch + log)
- Instinct → Instinct mode Phase 3-6
- Wiki → Phase 2.5 sanity sweep + write per [[09 Rules/channel-person-wiki.md]] or relevant template

### Conversation Mode hard rules

1. **NEVER ingest without showing candidates first** — the user must approve each crystallization
2. **ALWAYS source-note: "conversation: {brief context}"** — even though no file, provenance still matters
3. **NEVER bundle Cards + instincts + Wikis silently** — surface each type explicitly so user picks per type
