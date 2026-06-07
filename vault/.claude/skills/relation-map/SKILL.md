---
category: work
name: relation-map
description: Map 01 Wiki/ relations — find under-connected entries and propose bidirectional 关联文档 links for approval. Wiki analog of /card-lint --mode=bridge. Use /relation-map, "wire up the wiki", "connect [[X]]", "relation map", after a bulk Wiki import, or on the relation-gaps detector output.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
companion-routine: ".claude/routines/relation-gaps.py"
companion-rules:
  - "[[09 Rules/channel-person-wiki.md]]"
---

# Skill: Relation Map (`01 Wiki/` graph weaver)

The **actor** half of the Wiki relationship-mapping pair. The deterministic **detector** (`.claude/routines/relation-gaps.py`) sweeps the graph weekly and writes candidates to `.claude/_state/relation-gaps.json`; **this skill is the judgment layer** that reads those candidates (or scans fresh), decides which are genuine relations, and proposes **bidirectional `## 关联文档` links** for your approval.

It is the `01 Wiki/` analog of `card-lint --mode=bridge` (which is hard-scoped to `02 Cards/`). Same philosophy: **the graph is the goal — links create it; the detector surfaces, you + the model judge, writes happen only after approval.**

> **Why this exists:** bulk imports (e.g. the 2026-05-29 70-file `游戏系统/` drop) land as internally-linked **islands** — nothing in the wider vault points into them, and `index.md` masks the orphan-ness from strict 0-inbound checks. No prior process added relation links to *existing* Wiki entries. This closes that gap.

## When to Use

- **After a bulk Wiki import** (≥5 new entries created without per-entity `source-ingest` flow) — wire the new cluster into the graph.
- **Weekly**, to process the `relation-gaps` detector report.
- User says "wire up the wiki", "connect [[X]]", "relation map", "find relations for [[X]]", "why is this entry orphaned".
- The `relation-gaps` detector fired a Feishu alert / dropped a signal.

**Don't use for:** `02 Cards/` (→ `card-lint --mode=bridge`); dead-link repair (→ `vault-manager: repair-wikilinks`); creating a *new* entity page (→ `source-ingest`).

## Principles

1. **Read-only first, mutate after explicit approval.** Surface candidates → propose patches → approve per-cluster → then write. One pass = one change set.
2. **Never invent a relationship.** A name match is a *candidate*, not a fact. If the connection isn't substantive, drop it — don't manufacture a gloss.
3. **Bidirectional by default.** A relation is two-way: write the link into both files' `## 关联文档`, each with its own directional gloss.
4. **House format only.** Links live in a trailing `## 关联文档` section, sub-bucketed per `[[09 Rules/channel-person-wiki.md]]` — never a flat dump, never frontmatter `related:` as the primary store.
5. **🔴 Isolation is absolute.** NEVER propose a cross-lane link ({{PROJECT_A}} ↔ {{ORG_B}} / {{ORG_A}} / {{ORG_D}}). The detector drops these by construction; you re-check every candidate before writing. A cross-lane link is an isolation leak (`[[02 Cards/{{PROJECT_A}}/C260508-cross-project-references-leak-attention-signal]]`).
6. **Patch, don't rewrite.** Add to the `## 关联文档` section via Edit; if the section is missing, insert it at file end. Never touch body content, 概要, or claims.

## Granularity standard — the {{ORG_G}}版本 bar

A relation node is **not** "two notes share a string." It is a **named, directional, purposeful** connection whose gloss carries the *reasoning* — including how the two entities stay **distinct**. Canonical exemplar (already in the vault, {{USER_NAME}}-confirmed 2026-05-29, in `游戏系统/(C) {{PROJECT_A}}游戏系统-研发与项目管理.md` § {{ORG_G}}版本范围):

> **{{ORG_G}}版本** (a dev/build milestone), **{{ORG_G}}** (a venue), and **2026端午试玩会** (an event) are THREE distinct nodes with distinct timing + purpose — yet coupled: *{{ORG_G}}版本 = the build prepared **for** the 试玩会 **held at** {{ORG_G}}, and named after that venue.* Evidence in the gloss: 进包 5.29 = 招募开启同日; demo 6.12 = 试玩会前一周; build carries a dedicated 「线下试玩模式」.

Every link this skill writes must clear that bar:

1. **Distinguish-but-connect.** Same-named / topically-overlapping entities stay separate nodes; the link explains the relationship, never conflates them ({{ORG_G}}版本 ≠ {{ORG_G}} — a build is not a venue).
2. **Purposeful, not lexical.** The gloss states *how* they relate — built-for / held-at / benchmark-against / source-of / 承接面 — never "both mention X".
3. **Multi-hop where real.** If A relates to C *through* B (build → event → venue), surface the chain, not just the nearest hop.
4. **Carry provenance + the timing/purpose distinction** when that's the crux (mirror the `耦合关系（已确认）` line, with a confirmation date).
5. **A bare string match that can't be articulated this way is dropped**, not dressed up.

This governs Phase 2 (judge) and Phase 4 (gloss). When in doubt, open the {{ORG_G}}版本 block and match its register.

## How It Works

### Phase 0 — Resolve input

1. **Anchor mode** — user says "connect [[X]]" / "find relations for [[X]]" → that one entry is the anchor; scan the rest of `01 Wiki/` for its relations (both directions).
2. **Report mode** (default) — read `.claude/_state/relation-gaps.json`. If missing or stale (>7 days, or after a known bulk import), regenerate first:
   ```bash
   python .claude/routines/relation-gaps.py   # DRY_RUN default; read-only, writes only the report
   ```
3. **Scoped mode** — user names a cluster ("wire up 游戏系统") → filter candidates to that sub-folder.

### Phase 1 — Load candidates

From the report consume two streams:
- **`under_connected`** — entries with cross-cluster inbound < 2. For each, the job is *inbound* repair: find which hub / sibling / competitor files SHOULD point into it.
- **`unlinked_mentions`** — `{source → target}` where the target is named in the source's body but never linked. These are *outbound* repair, high-confidence (exact name/alias match).

Sort by confidence (`high` = name ≥4 chars; exact-name mentions first). The detector is recall-oriented — **your job is precision.**

### Phase 2 — Judge each candidate

For every candidate, decide REAL vs COINCIDENTAL:
- **Real:** the two notes share a substantive entity / topic / dependency (e.g. `异环.md` ↔ `游戏系统-玩法体系` — explicit 对标对象; `TapTap.md` ↔ `游戏设计与卖点` — the editor quote originates there).
- **Coincidental:** a name appears in passing with no relationship worth a graph edge (e.g. a city name, a generic term). Drop silently.
- **Semantic bridges (optional):** for `under_connected` entries with no name-match path, ask `vault-researcher` (smart-connections MCP) for the top semantic neighbors — surface only those with a defensible shared theme. Mirrors `card-lint --mode=bridge` Phase 5.

Write a **one-line directional gloss** per surviving link (the "why"), e.g. `[[(C) {{PROJECT_A}} - 游戏设计与卖点]] — 卖点表的 BD 口径来源`. Never `both mention X` (mechanical) — state the relationship.

### Phase 3 — Isolation re-check (hard gate)

Before proposing, re-verify every candidate: drop any where source-lane ≠ target-lane and both ∈ {{{PROJECT_A}}, {{ORG_B}}, {{ORG_A}}, {{ORG_D}}}. Belt-and-suspenders over the detector's own drop. Log the count dropped.

### Phase 4 — Propose per cluster (picker)

Group by source cluster. For each group:

```
Cluster: {{PROJECT_A}}/游戏系统 (7 entries under-connected)

1. [[{{PROJECT_A}}]] → [[(C) {{PROJECT_A}}游戏系统-总览]]   (hub → KB entry node)
   reverse: [[(C) {{PROJECT_A}}游戏系统-总览]] → [[{{PROJECT_A}}]]
2. [[(C) {{PROJECT_A}} - 游戏设计与卖点]] ↔ [[(C) {{PROJECT_A}}游戏系统-总览]]   (BD 卖点 ↔ 系统 KB; currently one-way)
3. [[TapTap]] → [[(C) {{PROJECT_A}} - 游戏设计与卖点]]   (编辑 "翻天覆地" 引用出处)
...
(Reply: numbers to accept · "all" · "none" · "skip cluster")
```

Cap **≤ 12 proposals per cluster** (cognitive load). If a cluster has more, surface top-by-confidence and note the remainder count.

### Phase 5 — Write (bidirectional, idempotent)

For each accepted link, on BOTH files:
- Locate the trailing `## 关联文档` section. If absent, append one at file end.
- Add `- [[target]] — <gloss>` under the correct sub-bucket (`### 直属关系` / `### 跨 vertical 协同` / `### 平台 / 项目` / a topical bucket like `### 游戏系统` / `### 竞品对照`). Create the sub-bucket if needed; never flat-list.
- **Idempotent:** if the link already exists anywhere in the file, skip.
- Use `aliases:` frontmatter to keep inbound resolution working; if a target lacks an alias a mention uses, note it (don't auto-add without surfacing).

### Phase 6 — Log + close the loop

- Append to today's daily note under `## Lint` (or `## Relation Map`): `- [HH:MM] /relation-map — N entries swept, M links written (K bidirectional), J deferred.`
- The detector report is point-in-time; note in the log which `under_connected` entries were resolved so the next weekly run shows the drop.

## Hard Rules

- **NEVER write a link without Phase 4 approval.**
- **🔴 NEVER create a cross-lane link** ({{PROJECT_A}} ↔ {{ORG_B}} / {{ORG_A}} / {{ORG_D}}) — isolation gate, no exceptions.
- **NEVER flat-list `## 关联文档`** — always sub-bucketed (per `channel-person-wiki.md` hard rule).
- **NEVER rewrite a file** — Edit the `## 关联文档` section only; body / 概要 / claims are untouchable.
- **NEVER fabricate a gloss** — pure character match with no substance → drop, don't dress it up.
- **NEVER link the 60 `_原始转录/` raw transcripts, `scholar/9-Templates/`, or `index.md`** — the detector excludes them; so do you.
- **ALWAYS bidirectional** unless the target is a redirect stub or index (then anchor-side only).
- **ALWAYS log the run to the daily note** — an unlogged sweep didn't happen.

## Integration

| Trigger | Hand-off |
|---|---|
| `source-ingest` bulk import (≥5 new Wiki files) | Auto-chain `/relation-map` scoped to the new cluster so it never lands as an island |
| Detector finds a NEW orphan cluster | Feishu alert → run `/relation-map` next session |
| Relation reveals a missing entity page | `source-ingest` (create the page), then re-run |
| `index.md` stale after writes | `vault-manager: audit` / index regen |

## Failure Modes

| Symptom | Fix |
|---|---|
| Detector report missing/stale | Regenerate: `python .claude/routines/relation-gaps.py` |
| 100+ unlinked-mention candidates first run | Expected graph debt. Triage by `confidence=high` + by cluster; do the gameplay island first, defer the rest. |
| Same coincidental candidate resurfaces weekly | Add target to the source's `## 关联文档` as an explicit non-link note, OR accept it's noise — the detector is recall-tuned. |
| A proposed link is cross-lane | Bug — drop it and check `lane_of()` in the detector. Isolation never yields. |
| Person mention won't resolve (`[[{{PERSON_4}}]]` dead) | Target needs `{{PERSON_4}}` in `aliases:` — surface for approval, don't silent-add. |
