---
category: work
name: card-lint
description: Audit and repair the Card graph. Use /card-lint for hygiene, /card-lint --mode=bridge for cross-domain links after new Cards, and /card-lint --mode=stale for inbox/draft cleanup.
model: claude-sonnet-4-6
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
# Skill: Card Lint (`--mode=hygiene` default · `bridge` · `stale`)

Audit + evolve the Card graph (**`02 Cards/`**). Three modes, one skill:

| Mode | Purpose | Trigger |
|---|---|---|
| **hygiene** (default) | Orphans / stale / broken links / frontmatter drift / missing refs | `/card-lint`, "lint cards", monthly cadence, W26 |
| **bridge** | After a new Card, find latent cross-domain bridges | `/card-lint --mode=bridge`, "find connections for [[X]]", auto-chain after `/source-ingest` |
| **stale** | Focused lifecycle pass on `_inbox/` + `status:draft` past TTL | `/card-lint --mode=stale`, "_inbox 清理", quarterly |

The Lint half of the **Ingest · Query · Lint** triad ([[02 Cards/meta/C260429-llm-wiki-pattern-validates-three-pillar-bookkeeping-thesis]]).

> **Why:** the 3-pillar rule layer makes capture clean, but entropy still grows — cards drift to `_inbox/` and rot, status fields go stale, links break, headlines become topics instead of claims. Without periodic lint, the synthesis layer becomes write-only and the closed loop opens.

## When to Use

- **End of each 12-week cycle (W26 of every quarter)** — non-negotiable; this is the batch-harvest checkpoint
- **Monthly** — light pass on the 1st (or after >5 new Cards since last lint)
- **After a `/source-ingest` burst** — chain when 5+ Cards added in one session
- User says "lint cards", "audit cards", "card health", "card review"

**Don't invoke for:**
- Project status check → `/weekly-update`
- Task triage → `/inbox-process`
- OKR check-in → `/okr` Mode B

---

## Principles

1. **Read-only first, mutate after explicit approval.** A lint run reports problems and proposes fixes; the user approves each cluster before any write.
2. **Lint never invents claims.** A Card with thin Mechanism / Application is a flag — not a prompt for Claude to fill in.
3. **Status flips are conservative.** Demoting `live` → `archived` requires evidence (superseded link or user confirmation), not just age.
4. **The graph is the goal.** Tags categorize; **links create the graph.** Lint prioritizes link health over tag tidiness.
5. **One pass = one report.** Don't chain auto-fixes during a lint run — surface findings, write a single change set, confirm, then write.

---

## How It Works

### Phase 0 — Resolve mode

1. Explicit flag wins: `/card-lint --mode=bridge` → bridge mode
2. Trigger phrase inference: "find connections for [[X]]" / "新 Card 写完了" → bridge; "_inbox 清理" / "stale" → stale; otherwise → hygiene
3. Auto-chain context (e.g., `/source-ingest` just spawned a new Card) → bridge mode with that Card as anchor
4. Genuinely ambiguous → plain text 1-line: *"hygiene (full lint) / bridge (cross-domain links) / stale (lifecycle only)?"* and await reply

Dispatch to the matching subroutine below.

---

## Hygiene Mode (default — full lint)

Phases 1–8 below comprise the hygiene routine. Same pipeline pre-2026-05-14 prune — orphans, stale, broken links, frontmatter drift, headlines.

1. Scan all Cards · 2. Build graph + frontmatter map · 3. Run checks · 4. Cluster findings · 5. Propose fixes · 6. Execute approved fixes · 7. Log lint event · 8. Confirm

---

## Phase 1: Scan All Cards

```bash
ls "02 Cards/_inbox/" "02 Cards/{{PROJECT_A}}/" "02 Cards/3rd-Inc/" "02 Cards/cross-border/" "02 Cards/ops/" "02 Cards/meta/" 2>/dev/null
find "02 Cards/" -name "C*.md" | wc -l
```

If count < 10 → lint is overkill, run a light human-readable summary instead and exit.

---

## Phase 2: Build Graph + Frontmatter Map

For each Card file, extract:
- Filename + path (= domain)
- Frontmatter: `type · created · source-project · source-note · tags · status · links`
- Body section presence: `## Evidence` `## Mechanism` `## Application` `## Related`
- Outbound wikilinks (body): `[[C{date}-...]]` references
- Outbound non-Card wikilinks (Wiki, Action files, daily notes)
- Word count

Build two indices:
- **Forward map:** Card → outbound links
- **Reverse map:** Card → inbound links

The reverse map is what makes orphan detection cheap.

---

## Phase 3: Run Checks

Accumulate findings keyed by Card.

### Check 1 — Frontmatter integrity

| Issue | Detection | Severity |
|---|---|---|
| Missing `type: card` | YAML lacks field | 🔴 |
| Missing `created:` | YAML lacks field | 🔴 |
| `created:` not ISO `YYYY-MM-DD` | Regex check | 🔴 |
| Missing `source-note:` | Empty or absent | 🟡 |
| Missing `tags:` | Empty list | 🟡 |
| `status:` not in {draft, live, archived} | Value mismatch | 🟡 |
| `links:` array exists but body Related section absent | Cross-check | 🟡 |
| `links:` and Related body diverge | Set difference | 🟡 |

### Check 2 — Body anatomy

| Issue | Detection | Severity |
|---|---|---|
| Missing `## Evidence` / `## Mechanism` / `## Application` / `## Related` | Section header absent | 🟡 |
| Headline is a topic, not a claim | Heuristic: no verb in H1, or H1 < 4 words | 🟢 (advisory) |
| Word count > 300 | Card too long — split candidate | 🟡 |
| Word count < 50 | Card too thin — likely incomplete | 🟢 |

### Check 3 — Graph health

| Issue | Detection | Severity |
|---|---|---|
| **Orphan** — no inbound links from other Cards | Reverse-map empty | 🟡 (some orphans are fine) |
| **Hub** — >10 inbound links | Reverse-map size | 🟢 (informational) |
| Broken outbound wikilink (target file missing) | File-existence check | 🔴 |
| Asymmetric link (A → B, B has no link to A) | Set comparison | 🟡 |
| Self-link | Filename match | 🔴 |
| Reference to Card by old filename (rename rot) | Best-effort fuzzy match | 🟡 |

### Check 4 — Lifecycle staleness

| Issue | Detection | Severity |
|---|---|---|
| Card in `_inbox/` for >14 days | `today - created > 14d AND path = _inbox/` | 🟡 |
| `status: draft` for >30 days | Same logic | 🟡 |
| `status: live` but never linked from anywhere (orphan + live) | Combination | 🟡 |
| `status: archived` but no `## Update` block explaining why | Heuristic | 🟢 |

### Check 5 — Domain coherence

| Issue | Detection | Severity |
|---|---|---|
| Card in `{{PROJECT_A}}/` but `source-project: {{ORG_B}}` (or vice versa) | Path vs frontmatter mismatch | 🟡 |
| Card in `_inbox/` but has clear domain in tags | Suggest promotion | 🟢 |
| Tag set inconsistent across same-domain Cards | Cluster analysis (post-MVP) | 🟢 |

### Check 6 — Source ledger (cross-pillar)

| Issue | Detection | Severity |
|---|---|---|
| `source-note:` points to nonexistent file | File-existence check | 🟡 |
| Cards reference an Action file that's been archived | Cross-check **`10 Action/_archive/`** | 🟢 |
| Concept mentioned in 3+ Cards but lacks its own Card | Heuristic: noun-phrase frequency | 🟢 (suggestion) |

---

## Phase 4: Cluster Findings into a Report

Group by severity then by check:

```markdown
# Card Lint Report — YYYY-MM-DD

**Scanned:** N Cards across {N1 in {{PROJECT_A}}, N2 in 3rd-Inc, ...}
**Health summary:** 🔴 R critical · 🟡 Y warnings · 🟢 G suggestions

---

## 🔴 Critical (R)

### Frontmatter integrity
- [[C{date}-{slug}]] — missing `created:` field
- [[C{date}-{slug}]] — broken outbound link to `[[C{date}-{nonexistent}]]`

## 🟡 Warnings (Y)

### Stale lifecycle
- [[C{date}-{slug}]] — in `_inbox/` for 23 days; promote to {domain}/ or archive
- [[C{date}-{slug}]] — `status: draft` for 45 days

### Asymmetric links
- [[C{date}-A]] → [[C{date}-B]], but B has no inverse link
  → Patch B's `## Related` section

### Source-note rot
- [[C{date}-{slug}]] — `source-note:` points to deleted file `00 Raw/old.md`

## 🟢 Suggestions (G)

### Hub Cards (informational)
- [[C260427-three-pillar-pkm-value-is-the-closed-loop]] — 4 inbound links (healthy hub)

### Concepts to consider as new Cards
- "warm-network" — appears in 3 Cards, no dedicated Card

### Headline drift
- [[C{date}-{slug}]] — H1 reads as a topic ("JP boards"), consider rewriting as a claim
```

---

## Phase 5: Propose Fixes (Cluster-by-Cluster)

Walk through each cluster:

> **Cluster 1 — Asymmetric links (3 found):**
> Each is a one-line patch to the target Card's `## Related` section.
> Approve all / approve some / skip?

For approved clusters, prepare exact patches. **Don't write yet.** For each patch, show:
- File path
- Old text (what's there now)
- New text (what will replace it)

---

## Phase 6: Execute Approved Fixes

Apply patches via `Edit`. Hard rules:

- **Never bulk-rewrite a Card.** Patch the specific section.
- **Never change a Card's claim** (H1 or `> one-line` blockquote). Headline drift is surfaced, never silently rewritten.
- **Status demotions (`live` → `archived`)** require an appended `## Update YYYY-MM-DD` block with reason. Never silent.
- **Domain moves (file path changes)** are surfaced for user approval, not auto-executed — they break wikilinks elsewhere.

---

## Phase 7: Log the Lint Event

Append to today's daily note (**`04 Notes/daily notes/{YYYY-MM-DD}.md`**) under `## Lint`:

```markdown
## Lint
- [HH:MM] /card-lint pass — N cards scanned, R critical / Y warnings / G suggestions; M patches applied; K items deferred.
```

Also append to `[[02 Cards/(C) README.md]]`'s lifecycle log if a "Lint history" section exists; otherwise, propose adding one (one-time setup).

---

## Phase 8: Confirm

```
Lint complete — 02 Cards/ scanned (N cards):
  🔴 R critical: {fixed K, deferred R-K}
  🟡 Y warnings: {fixed M, deferred Y-M}
  🟢 G suggestions: {logged for user review, no fixes applied}
Report saved to [[YYYY-MM-DD]] § Lint.
Next recommended lint: {month-from-now or W26 marker}.
```

---

## Bridge Mode (`--mode=bridge`)

After a new Card is written, sweep **`02 Cards/`** across **all domains** to find latent cross-domain bridges — Cards in different domains sharing tags / entities / mental models / failure patterns. Surface bridge candidates + propose bidirectional `## Related` link additions.

> **Why**: 单 domain 内 Cards 互链是 hygiene。**跨域 bridge 是 emergent leverage** — 一个 {{PROJECT_A}} BD 教训 might inform {{ORG_B}} M&A negotiation；一个 ops biohack pattern might apply 到 cross-border arbitrage。手动想不到 — 系统化 sweep 才行。

### Bridge Phase 1 — Identify Anchor Card

Three modes:
1. User says "find connections for [[C260513-...]]" → 用 that Card
2. User just wrote a Card in conversation OR via `/source-ingest` → 用 latest **`02 Cards/`** mtime
3. User says "新 Card 写完了" 无 specific link → ask plain text 1 line "哪张？" 等回复

读 anchor Card 完整内容 (frontmatter + Evidence + Mechanism + Application + Related)。

### Bridge Phase 2 — Extract Anchor Signals

从 anchor Card 提取:
- **Tags** (frontmatter `tags`)
- **Source-project** (`source-project: {{PROJECT_A}} | {{ORG_B}} | cross-border | ops | meta`)
- **Wikilinks in body** (`[[entity]]` / `[[other Card]]`)
- **Headline keywords** (filename slug)
- **Key concepts** in Mechanism / Application (manually extract nouns + verbs)
- **Failure pattern signature** (if Card mentions failure mode, capture the mode signature)

### Bridge Phase 3 — Sweep 02 Cards/ Across ALL Domains

```bash
ls "02 Cards/{{PROJECT_A}}/C*.md" "02 Cards/3rd-Inc/C*.md" "02 Cards/cross-border/C*.md" \
   "02 Cards/ops/C*.md" "02 Cards/meta/C*.md" "02 Cards/_inbox/C*.md" 2>/dev/null
ls "02 Cards/instincts/I*.md" 2>/dev/null
```

For each non-anchor Card, score similarity:

| Signal | Weight | Example |
|---|---|---|
| **Shared tag** | ⭐⭐⭐ | both tagged `negotiation` or `vault-design` |
| **Shared wikilink** in body | ⭐⭐⭐ | both reference `[[C260427-jp-board-reads-memos-backward]]` |
| **Shared entity** | ⭐⭐ | both mention 钟馨 OR EPIC OR vendor X |
| **Headline keyword overlap** | ⭐⭐ | "pushback" / "3-vertical" / "evening surge" 在 anchor + candidate 都出现 |
| **Mechanism keyword overlap** | ⭐⭐ | core concepts (specific to Card body, not generic words like "因为") |
| **Failure mode signature** | ⭐⭐⭐ | both Cards discuss similar failure pattern |
| **Same source-project ≠ candidate** | -⭐ | same-domain Cards 被 weight down — bridge interest 是跨域 |
| **Different source-project** | +⭐⭐⭐ | 跨域是核心目标 — boost score |

### Bridge Phase 4 — Filter Candidates

Surface only candidates 满足:
- **Score ≥ threshold** (default 3 signals matched, ≥ 1 must be cross-domain or shared-entity)
- **Not already in anchor's Related: section** (de-dup)
- **Top 5 by score** (cognitive load cap)

If 0 candidates → "本 Card 没找到 latent bridges. Possibly genuinely standalone." (acceptable, 不强行 link)

### Bridge Phase 5 — Hypothesize "Why These Connect"

每个 candidate, AI 写 1-2 行 hypothesis:
- 不是 "both mention X" (机械)
- 是 "both share underlying pattern: when [trigger], [common response/outcome]" (semantic)

Example:
- Anchor: `[[C260513-bilibili-org-chart-three-verticals-under-EK]]` ({{PROJECT_A}})
- Candidate: `[[C260427-jp-board-reads-memos-backward]]` (3rd-Inc)
- Hypothesis: "两 Card 都关于 'unitary appearance hides multi-vertical reality' — one in JP corp governance, one in CN platform BD. Bridge: org navigation 通用 method."

### Bridge Phase 6 — Propose Related Link Additions

```
Anchor: [[C260513-...]]

Found 3 latent bridges (cross-domain):

1. → [[C260427-...]] (3rd-Inc)
   Hypothesis: ...
   Add to anchor's Related? Add to candidate's Related?

2. → [[C260508-...]] (meta)
   Hypothesis: ...

3. → [[I260514-...]] (instinct)
   Hypothesis: ...

(Reply with number(s) to accept; "all" or "none".)
```

User picks → write to files.

### Bridge Phase 7 — Bidirectional Link Write

For each accepted bridge:
1. Add wikilink to anchor's `## Related` section (with 1-line hypothesis)
2. Add reverse wikilink to candidate's `## Related` section (mirror hypothesis)
3. If candidate is an instinct → patch `related-instincts:` frontmatter array instead

Idempotent — if already linked, skip.

### Bridge Mode hard rules (in addition to common hard rules below)

- **NEVER add link without explicit approval** — Phase 6 picker required
- **NEVER over-weight same-domain bridges** — bridges are cross-domain by design; same-domain is hygiene's job
- **NEVER propose > 5 candidates** — cognitive load cap
- **NEVER fabricate hypothesis** — 机械字符 match (无 semantic) → mark "low-confidence: surface 字符 match, 请人判断 substantive"
- **NEVER 跨 instinct + Card 混 promote** — if instinct cluster detected, surface to `/vault-evolve` Phase 5.b instead
- **ALWAYS bidirectional symmetry** — link is two-way; if candidate is archived, only update anchor
- **ALWAYS include hypothesis line** per bridge

### Bridge Mode failure modes

| Symptom | Fix |
|---|---|
| Anchor Card 无 Mechanism / Application | "anchor 缺 Mechanism — semantic match 信号不足；先补 Mechanism 再 invoke" |
| 0 cross-domain candidates | "本 Card 没找到 latent bridges. Possibly standalone." |
| >10 candidates | Threshold raise, keep top 5 |
| Same hypothesis already proposed (and rejected last time) | Skip — surface "上次已 propose / reject" |
| Anchor is an instinct, not a Card | Still works — but weight 略调 (instincts 跨域 bridge less rich than Cards) |
| User wants batch mode (5 anchors) | Loop Phase 1-6 per anchor; consolidate output |

---

## Stale Mode (`--mode=stale`)

Focused lifecycle pass on `_inbox/` + `status:draft` past TTL. Useful between full hygiene runs when only lifecycle review is needed (e.g., quarterly _inbox sweep).

### Stale Phase 1 — Glob targets

```bash
find "02 Cards/_inbox/" -name "C*.md" -mtime +14
find "02 Cards/" -name "C*.md" | xargs grep -l "status: draft" | xargs -I{} bash -c 'stat -c "%Y %n" "{}"'
```

### Stale Phase 2 — Classify

| Condition | Severity | Action |
|---|---|---|
| In `_inbox/` > 14d | 🟡 | Propose domain promotion OR archive |
| `status: draft` > 30d AND has Evidence / Mechanism / Application | 🟡 | Propose promote to `live` |
| `status: draft` > 30d AND body < 50 words | 🟡 | Propose archive (never matured) |
| `status: live` but 0 inbound links AND > 60d | 🟢 | Surface as standalone (acceptable for hub-less insights) |

### Stale Phase 3 — Propose per-cluster

Use same "approve all / some / skip" picker pattern as hygiene Phase 5.

### Stale Phase 4 — Apply + Log

Same as hygiene Phase 6-7. Append lint event line to today's daily under `## Lint`.

### Stale Mode hard rules

- **Never archive without user approval** — even past TTL
- **Never silently demote `live` → `archived`** — requires appended `## Update YYYY-MM-DD` block with reason
- **Default lint-exempt cards skip** — frontmatter `lint-exempt: true` honored

---

## Hard Rules

- **Never silently mutate a Card's claim, headline, or quoted blockquote.** Those are the user's voice.
- **Never auto-archive a `live` Card.** Suggest, never execute.
- **Never delete a Card.** Archive (`status: archived`) is the deepest demotion.
- **Never modify Card frontmatter `created:` field.** Permanent provenance stamp.
- **Always show patches before writing.** No silent fix sweeps.
- **Always log the lint event to the daily note.** A lint that doesn't appear in the ledger didn't happen.
- **Never lint outside **`02 Cards/`**.** Action / Time / Wiki have their own conventions; this skill is Card-scoped.

---

## Severity Calibration

| Symbol | Meaning | Action |
|---|---|---|
| 🔴 Critical | Breaks the graph (missing required field, broken link) | Fix in this run |
| 🟡 Warning | Degrades quality but graph still functional | Propose fix; user decides |
| 🟢 Suggestion | Optimization / observation | Log; no auto-fix |

A lint with 0 critical / 0 warnings / N suggestions is a healthy graph. Don't chase 0/0/0 — some suggestions are accepted entropy (e.g., a hub Card with 8 inbound links).

---

## Failure Modes

| Symptom | Fix |
|---|---|
| Lint produces 100+ findings on first run | Healthy — initial graph debt. Triage by severity, fix 🔴 only this pass, schedule a second pass next week for 🟡. |
| Same warning persists across 3 lint runs | User has consciously declined to fix. Stop surfacing it; add to a "won't fix" list in **`02 Cards/(C) README.md`**. |
| Linter wants to demote a Card user disagrees with | User wins. Add `lint-exempt: true` to Card frontmatter; future lints skip it. |
| Broken outbound link to a renamed Card | Surface the rename; user confirms; propagate the new wikilink across all referencing Cards in one Edit batch. |
| Concept-suggestion noise | Concepts appearing in <3 Cards aren't suggested. Threshold tunable in this skill. |

---

## Integration with Other Skills

| Trigger | Hand-off |
|---|---|
| Lint reveals workstream-worthy gap | **Propose** Action file (per `[[09 Rules/action.md]]` policy) — never auto-spawn |
| Lint reveals task-worthy followup | `/task-capture` (≤ 3 new tasks per write) |
| Lint reveals OKR-altering insight | Surface for next `/okr` Mode B check-in |
| Lint at end-of-cycle (W26) | Chain into `/biweekly-report` final pass + 12-week review |
| Lint reveals an Ingest backlog (Cards in `_inbox/` >14d that look domain-ready) | Suggest `/source-ingest` re-run on stale `_inbox/` items, OR direct promote |

---

## Cadence Recommendation

| Cadence | Trigger | Scope |
|---|---|---|
| **Monthly** | 1st of month OR >5 new Cards since last lint | Full scan, all checks |
| **End-of-cycle (W26)** | Quarter-close ritual | Full scan + status reconciliation + concept-suggestion review |
| **Ad-hoc** | After a `/source-ingest` burst (5+ Cards in one session) | Quick: critical only, defer warnings to next monthly |
| **Annual** | Year-end | Full pass + headline drift review (the hardest check) |

`/weekly-update` should *not* call this skill automatically — different tempos. Weekly is project status; lint is graph entropy. Bundling dilutes both.
