---
category: meta
name: vault-evolve
description: Run the daily self-evolution routine: audit structure, telemetry, drift, and proposals. Safe changes may auto-apply; risky changes go to review.
model: claude-opus-4-7
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Skill: Vault Evolve (`/vault-evolve`)

The daily self-evolving routine. Observes what the user actually does with the vault, detects drift between intent and behavior, applies safe corrections automatically, surfaces structural decisions for review, and accumulates accepted/rejected patterns into a ledger the `vault-manager` subagent reads to improve over time.

> **First principle:** evolution is pattern compression from your judgments, not random mutation. Every change the system makes traces to either (a) a safe deterministic rule, or (b) a pattern observed 3+ times in your prior dispositions.

---

## Operating modes

| Mode | Trigger | Behavior |
|---|---|---|
| **Interactive** | User types `/vault-evolve` | Process phases live; surface 🟡 items one by one; wait for user dispositions; apply approved items. |
| **Autonomous** | `/vault-evolve --autonomous` (scheduled task) | Process phases silently; auto-apply 🟢 items; defer all 🟡 items to written report; never block on user input. |
| **Catch-up** | Last run >24h ago (any mode) | Process accumulated gap. Treat the gap as one telemetry window, not multiple daily runs. Don't produce N missed reports. |

Detect mode via:
1. `--autonomous` argument → autonomous
2. No argument → interactive
3. If today's report already exists AND mode is autonomous → exit gracefully (idempotency)

---

## Safety tiers (load-bearing — read every phase against this)

| Tier | What | Authority |
|---|---|---|
| 🟢 **Safe** | Description trigger ADDITIONS (never removals), frontmatter completion on framework files (`created-by: claude`), dead wikilink comment-out, rolling log appends, MEMORY.md hierarchy pointer refreshes | Auto-apply in both modes |
| 🟡 **Review** | Subagent system prompt edits, auto-chain rule additions, skill merge proposals, skill retire candidates, MEMORY.md incident additions, **`09 Rules/**` patches, body rewrites of any `**.claude/skills/<name>/SKILL.md`** beyond frontmatter | Propose-only; user dispositions via `vault-manager: execute` next session |
| 🔴 **Manual** | Skill deletion, subagent deletion, user-authored content edits (Cards prose body, project files, meeting notes, contracts, deal artifacts), any operation on **`06 Tasks/**`, `**.obsidian/**`, `**00 Raw/`** immutable subfolders, `chain-anchor` renames | NEVER auto. Surface with extra warning + manual path |

When in doubt → propose, not auto.

---

## Phase 0: Pre-flight

**Router-surface safe cleanup:** shortening skill frontmatter descriptions is safe only when routing intent is preserved and the edit touches `description:` only. Removing mojibake-like text from a frontmatter description is also safe. Body rewrites remain review-only. Never normalize plugin-fed syntax (`{{operonId}}`, `{{status}}`, `{{datetimeStart}}`, `chain-anchor`, Dataview/Operon fences, Obsidian links/tags/callouts/task checkboxes) by guesswork.

```bash
# Resolve dates
today=$(date +%Y-%m-%d)
yesterday=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)
report_dir="04 Notes/vault-evolve"
today_report="$report_dir/${today}.md"
log_file="$report_dir/_log.md"
ledger="$report_dir/_decisions.md"
```

Ensure **`04 Notes/vault-evolve/`** exists. Read `_log.md` to find last-run date — defines the telemetry window.

**Idempotency check:** If `$today_report` exists AND mode is `--autonomous` AND its `last-updated:` frontmatter is <2h old, exit with: *"Today's report already current (last run HH:MM). Skipping."*

---

## Phase 1: Telemetry intake

Gather signals from the gap between last run and now.

### Sources

| Source | What to extract | How |
|---|---|---|
| **Recent session logs** | **`04 Notes/Session Logs/*.md`** since last run | Glob by mtime; read `## Decisions Made`, `## Files Touched`, `## Pending Tasks` |
| **Daily notes since last run** | **`04 Notes/daily notes/*.md`** | Read frontmatter `cards-spawned`, `actions-touched`, `people-touched`; scan `## Ingests`, `## Lint`, `## Sanity` sections |
| **File mtime delta** | All `*.md` modified since last run | `find . -name "*.md" -newer "$last_run_marker"` |
| **Decision ledger** | `_decisions.md` recent entries | Read pending dispositions from yesterday's report; check if user added inline `[accepted]` / `[rejected]` markers |
| **Wikilink graph delta** | New `[[wikilink]]` patterns since last run | Grep recent files; compare against prior-run snapshot if available |
| **Engine learn-loop surfaces** (2026-05-23) | `.claude/_state/corrections.jsonl` (`status:new` → promotion candidates), `.claude/_state/grader-verdicts.jsonl` (first-try pass-rate, iteration trend), `.claude/_state/promotion-predictions.jsonl` (due prediction verdicts) | Read counts + recent entries; `new` corrections become Phase 4 promotion proposals; due predictions become Phase 4 verdict-review items |
| **Obsidian runtime sensor** (2026-05-28) | `.claude/_state/obsidian-runtime.json` | If present, read as Obsidian API observability: active file, workspace leaves, plugin list, metadata-cache counts. Missing/stale snapshot is a 🟡 observability degradation only; never treat Obsidian-closed as routine failure. |
| **Harness pulse** (2026-05-26) | `.claude/_state/harness-pulse.json` (current verdict) + `.claude/_state/autonomous-log.jsonl` `routine:"harness-pulse"` entries since last run | Current severity + findings; trend = how many pulses were yellow/red and which finding `code`s recur across the window. The `harness-pulse` Tier-7 routine pushes incidents in real time; vault-evolve consumes the *accumulation* for chronic patterns. |

### Extract

- **Skills invoked:** count per skill (heuristic — search session logs + daily notes for `/skill-name` mentions)
- **Subagents called:** count per subagent (search for `vault-researcher:` / `vault-manager:` / etc.)
- **Files touched per pillar:** counts in **`02 Cards/**`, `**04 Notes/**`, `**10 Action/**`, `**03 Projects/`**
- **New cards / archived workstreams / closed tasks:** counts
- **Cross-skill chains observed:** e.g., `/meeting-note-deep` → `/biz` (auto-chain firing as designed) vs. user manually invoking `/biz` separately (auto-chain miss)
- **Harness-pulse trend:** over the window, count green/yellow/red pulses and which finding codes recurred (e.g. `feishu-down` in 6 of 8 pulses). Persistent findings feed Phase 2 as 🟡; one-off transients are informational only.

Build a `telemetry` block — terse, scannable, no prose.

> **Judgment-graph backlog-mining (occasional, not per-run):** the `09 Rules/_judgment/` graph is fed mainly by interactive corrections, which trickle. To bootstrap/refresh it from the existing corpus, run `python .claude/_eval-fixtures/judgment_harvest.py --json` (scripted, 0-token). Three tiers: `logic` (meta Cards + instincts + corrections), `prior` (domain belief Cards), `domain` (daily-note work-logs — real BD/deal judgment; use `--tier domain` to focus the distill there and balance the graph's meta-heaviness). A batched model distill clusters the output into `mined-proposals.jsonl` (pending-review) → human approves → encode to nodes. Run when a batch of new Cards/notes has accrued, not every cycle. See `_eval-fixtures/README.md` § Judgment-loop tools.

---

## Phase 2: Standard audit (delegate to existing infrastructure)

Don't reinvent. Chain to existing audit operations:

1. **vault-manager subagent `audit` operation** — orphan cards, dead wikilinks, misplaced files, **root-level strays** (per `09 Rules/file-types.md` § Root-Level Discipline — files at a major folder root that violate the allow-list), stale Action files, frontmatter rot. Read-only delegation; capture findings into the report. Strays always surface as 🟡 propose-only (never auto-moved) — destination is judgment-heavy, user picks.
2. **`/sanity`-equivalent inline scan** for items vault-manager doesn't cover: legacy path drift in `04 Notes/`, `Inbox.md` overdue clusters (read-only — `06 Tasks/` is read-only here too), CLAUDE.md / MEMORY.md / GOALS.md line counts.
3. **`/card-lint`-equivalent scan** if >5 cards added since last run.
4. **MCP health + provenance audit (added 2026-05-21):**
   - `mcporter list` — surface any 🔴 (offline / HTTP error) or 🟡 (auth-needed) servers since last run
   - `npm outdated -g 2>/dev/null | grep -E '@playwright/mcp|smart-connections|firecrawl|chrome-devtools-mcp'` — if any pinned community MCP has a new version, surface as 🟡 with the diff between installed and latest. Don't auto-upgrade; force a conscious decision (supply-chain risk per Card [[C260521-mcp-observability-via-mcporter]])
   - Cross-check installed MCPs against vendor-signed list: Anthropic / Microsoft / Sentry / Linear / Cloudflare. Community-maintained → flag for periodic security review.

5. **Engine-feedback checks (2026-05-23 — delegate to the standalone tools; never inline their logic):**
   - `python .claude/_eval-fixtures/foundational-lint.py` + `verify-load.py` — always-loaded drift + load-reliability. **Skip if today's `/sanity` already ran them** (it does by default).
   - `python .claude/_eval-fixtures/judgment-registry.py` — refresh the judgment manifest; surface any *new* contradiction-review candidate as 🟡.
   - `python .claude/_eval-fixtures/promotion_predictions.py` — validate the promotion-prediction state surface; any due prediction with `verdict: null` becomes a 🟡 review item, not an auto-failure.

6. **Harness-pulse chronic-pattern check (2026-05-26):** from the window's `harness-pulse` verdicts (Phase 1), a finding `code` present in ≥50% of pulses is **chronic** — surface as 🟡 with the recurrence count (e.g. recurring `scheduler-stalled` → a Tier-7 task keeps dying; recurring `corrections-stuck` → judgment promotions are stalled; recurring `vault-evolve-missing` → *this* routine isn't firing). A single transient pulse is informational only — never propose on one-off noise. Division of labor: the pulse already pushed any RED incident in real time; vault-evolve's job is the *pattern*, not the incident.

Tag every finding with a tier (🔴 / 🟡 / 🟢).

**Skip if already-fresh:** if a `/sanity` report from today exists at **`04 Notes/sanity-reports/`**, reference it instead of re-running.

---

## Phase 3: Skill usage analysis

Run `python .claude/_eval-fixtures/skill_surface_lint.py` before proposing description refinements. Treat failures as skill hygiene drift: active descriptions must stay at or below 300 characters, avoid mojibake-like text, and preserve the plugin-syntax protection contract in `09 Rules/harness-surfaces.md`.

For each skill in **`<vault>/.claude/skills/<name>/SKILL.md`**:

### A. Last-invocation heuristic

Grep recent session logs + daily notes for `/<skill-name>` mentions. If never seen since last run, increment days-since-use.

| Days since use | Tier |
|---|---|
| ≤7 | 🟢 healthy |
| 8–30 | 🟢 informational |
| 31–60 | 🟡 propose review (is this still relevant?) |
| 61+ | 🟡 propose retire candidate |

### B. Description trigger drift

Compare the skill's `description:` frontmatter trigger phrases against the user's actual vocabulary in recent sessions:

- For each invocation observed, what phrase did the user use? (Pull from session logs.)
- Was that phrase already in the `description:` field?
- If a phrase appears 3+ times and is NOT in the description → propose adding it (🟢 — additions only).

### C. Overlap detection

For pairs of skills, compute trigger phrase overlap. If two skills share >40% of their meaningful trigger phrases → propose merge or namespace clarification (🟡).

### D. Auto-chain miss

If skill X is supposed to auto-chain to skill Y (per CLAUDE.md § Skill Auto-Chain Rules) but observations show user manually invoked Y after X → flag auto-chain not firing. Possible causes: description weak, intent ambiguous, hook missing. Propose investigation (🟡).

---

## Phase 4: Subagent learning loop (the evolution mechanic)

This phase is what makes the system "self-evolving" rather than just a daily audit.

### Read the decision ledger

**`04 Notes/vault-evolve/_decisions.md`** — append-only log of past proposals + user dispositions. Format:

```markdown
## YYYY-MM-DD

### Proposal · <type>
**Target:** <file or subagent>
**Reason:** <observation that triggered it>
**Proposed change:** <specifics>
**Safety:** 🟢/🟡/🔴
**Outcome:** Applied | [accepted] | [rejected — reason: …] | [pending]
```

**Engine corrections feed this loop (2026-05-23):** unpromoted entries (`status:new`) in `.claude/_state/corrections.jsonl` are promotion candidates — file each as a `Proposal · rule-promotion` (new correction → hard rule / Card / rubric line). This is the learn arrow closing: a captured edit becomes encoded judgment. Falling unpromoted-backlog + falling grader failure-rate (per `grader-verdicts.jsonl`) = the gates compounding.

**Promotion prediction review (decision observability, 2026-05-28):** every approved rule/rubric/example promotion from `corrections.jsonl` must append a row to `.claude/_state/promotion-predictions.jsonl`. The row states the trigger class, forbidden behavior, expected behavior, replayability, and review horizon. During Phase 4, review any row whose `eval_after.by` has elapsed or whose `min_occurrences` has clearly been met. Allowed verdicts:

- `passed` — the trigger recurred and the promoted rule prevented the failure.
- `failed` — the trigger recurred and the same failure class returned.
- `unobserved` — review date arrived but the trigger did not recur.
- `inconclusive` — evidence was mixed or too noisy.

A `failed` verdict re-enters the correction/distill loop as `kind: rule-failed-retest`; the next proposal must sharpen the rule, tighten the trigger, move the rule to a better layer, or retire it. Three failures touching the same area become a 🟡 structural review item.

### Pattern compression

For each **proposal type** (e.g., "vault-manager audit confidence-tier separation"), count:
- N_accept = proposals of this type accepted by user
- N_reject = proposals of this type rejected
- N_total = N_accept + N_reject + N_pending

| Threshold | Action |
|---|---|
| N_accept ≥ 3 AND N_reject = 0 | Propose **encode as default** — update vault-manager system prompt to apply this pattern preemptively (🟡 — needs final user confirm before encoding) |
| N_reject ≥ 3 AND N_accept = 0 | Propose **suppress future proposals** of this type — add to vault-manager's "accepted entropy" list. Stop surfacing (🟡 — needs final user confirm). |
| Mixed (some accept, some reject) | Pattern is context-dependent; surface the cases with their context. No encoding yet. |
| N_total < 3 | Insufficient signal. Continue collecting. |

### vault-manager system prompt update format

When a pattern crosses the encode threshold, the proposed update to **`<vault>/.claude/agents/vault-manager.md`** follows this format:

```markdown
## Learned defaults (auto-appended by /vault-evolve, dated YYYY-MM-DD)

- Per pattern observed N times: <encoded rule>
  - Origin: ledger entries dated [date1, date2, date3]
  - Reversal: if this default produces unwanted behavior, remove this line.
```

This keeps learned defaults **separable** from hand-authored system prompt — easy to audit, easy to roll back.

---

## Phase 5: Cross-pillar pattern detection

Beyond skills/subagents, observe vault-wide patterns:

| Pattern | Detection | Proposal |
|---|---|---|
| User types task list inline (no `/task-capture`) 3+ times | Grep daily notes for unsynced `- [ ]` lines outside **`06 Tasks/`** | 🟡 Propose `/task-capture` nudge in `/resume` |
| Card cites archived Action file 3+ times | Cross-check **`02 Cards/**` ↔ `**10 Action/_archive/`** | 🟡 Propose Card-update SOP after archiving Actions |
| Same 3+ Cards orphaned for >14 days | vault-manager audit output | 🟡 Propose `/card-lint` orphan-link pass |
| CLAUDE.md line count drifting up | `wc -l` weekly | 🟡 Propose `/preserve` Phase 2 auto-archive |
| MEMORY.md at 200-line cap with adds pending | Line count | 🟡 Propose pruning candidates (terse 1-line entries to fold) |
| New skill added but not in `Skills I Use Daily.md` | Glob **`.claude/skills/*/SKILL.md`** vs index | 🟢 Auto-add row to index |
| Skill description has no `--<flag>` variants but skill body documents them | Description vs body text mismatch | 🟢 Append flag triggers to description |
| **Instinct cluster (N≥3 same domain + similar trigger/action)** | Glob **`02 Cards/instincts/I*.md`**，parse frontmatter `domain:` + `trigger:` + `action:`，group by domain，within-domain fuzzy-match trigger/action keywords | 🟡 Propose promotion path (Card / 09 Rule / Skill) — see Phase 5.b below |
| **Instinct confidence stuck at 0.5 for >60d** | Frontmatter `confidence: 0.5` + `created:` >60d ago | 🟡 Propose 升 live (re-validate) or 降 archived (没复现) — user pick |
| **Instinct `status: clustered` but `promoted-to: null`** | Frontmatter inconsistency | 🟡 Surface — cluster proposed but never executed; ask user follow up |

---

## Phase 5.b: Instinct Cluster Detection (2026-05-14 加入)

> 借自 homunculus 的 "evolution from instincts cluster" 概念。详 [[09 Rules/instincts.md]]。

### Process

1. **Glob `02 Cards/instincts/I*.md`** (excludes README)
2. **Parse frontmatter** for each: `domain`, `trigger`, `action`, `confidence`, `status`, `created`
3. **Filter** to status ∈ {draft, live}（已 clustered/promoted/archived 跳过）
4. **Group by `domain`**
5. **Within domain，fuzzy-match trigger + action keywords**：
   - 取每个 instinct 的 trigger + action 内容
   - 提取 nouns + verbs（停用词去掉：when / 的 / a / the / 时 / etc.）
   - 计算每对 instinct 的 keyword overlap ratio
   - ≥40% overlap 算"相似"
6. **检测 cluster**: 同 domain 内 3+ 相似 instincts → 形成 cluster
7. **Cluster proposal**: 对每个 cluster surface 1 个🟡 proposal:

```
## Instinct cluster · {domain} · {cluster headline}

涉及 instincts:
- [[I260514-...]]
- [[I260515-...]]
- [[I260516-...]]

**共同主题**: {synthesized common trigger-action}

**Propose promotion path**:
A. 提升为 Card — 已 synthesized 出 mechanism + application → 写 `02 Cards/{domain}/C{date}-{slug}.md`
B. 提升为 09 Rule — 已 enforce-able → 写 `09 Rules/{topic}.md` 或 patch 现有 rule
C. 提升为 Skill — 已 workflow-able → 调用 `/skill-new` (Phase 0 含相关 instincts as reference)
D. 暂不 promote — 维持 instinct cluster 状态再观察

**Disposition**: `[pending]`
```

8. **Once user picks (A/B/C/D)** in disposition:
   - A → guide creation of Card; patch all instincts `promoted-to: "[[C...]]"` + `status: promoted`
   - B → guide creation of Rule; patch instincts `promoted-to: "[[09 Rules/...]]"` + `status: promoted`
   - C → invoke `/skill-new` Phase 0 with cluster instincts pre-loaded as masters reference
   - D → patch instincts `status: clustered`（不 promote 但 mark 已识别）

### Heuristic for "similarity"

不强求精确 NLP — 简单 keyword overlap 已经足够 surface 候选 cluster。用户在 disposition 阶段会校准。

如果 fuzzy-match 过于 noisy（false positive 多），fall back 到更严格：必须 domain 相同 AND ≥1 keyword 完全相同。

---

## Phase 5.c: Metrics Emit (2026-05-14 加入)

> Per [[04 Notes/vault-evolve/_metrics.md]] schema. Emits weekly (default Sunday EOD) or on-demand. Skip if last metrics emit was < 6 days ago (autonomous mode) unless on-demand.

### Process

1. **Determine cadence**: is this run a "weekly metrics" run? Check `_metrics-log.md` last entry. If ≥ 6d ago OR explicit user prompt → emit. Otherwise skip.

2. **Compute all 5 metric sections + stretch** per `_metrics.md` schema:
   - **System Health**: auto-Card archive rate, orphan %, stale draft %, `_inbox/` aging, broken wikilinks, MEMORY.md line count
   - **Output Quality**: draft acceptance rate, biweekly KR-mapping, meeting note shareability
   - **Personal Leverage**: morning bootstrap rating (from daily note frontmatter), trip context recall, EOD chew rating, AFK draft acceptance
   - **Cognitive Offload**: MEMORY.md hit rate, wiki-grep first-hit, carry-forward propagation, chain-anchor invariance
   - **System Activity**: skills invoked, Cards spawned/archived, instincts captured, source-ingest/day-digest/vault-evolve runs
   - **Stretch · Portability**: non-vault-specific skill ratio, rule layer abstraction, subagent transferability, install footprint

3. **Write emit data** as frontmatter-only file at **`04 Notes/vault-evolve/metrics/{YYYY-MM-DD}.md`** (the Dataview source; one file per emit). ALSO append narrative summary to `_metrics-log.md` for historical readability. Frontmatter must include every metric key the dashboard expects (`memory-md-lines`, `stale-draft-pct`, `cards-spawned`, etc.) — use `null` for not-yet-measurable rather than omitting the key, so DataviewJS can show `n/a` instead of breaking.

4. **For each metric crossing action threshold** → file 🟡 proposal in the dated report (Phase 6). Example: orphan card % > 25% → propose "run `/card-lint --mode=bridge` on top-N orphans".

5. **Read manual ratings** from yesterday's daily note `daily-rating:` frontmatter field (added 2026-05-14 by `/daily-note` Phase 7 close mode). Aggregate into weekly average for Personal Leverage rows.

6. **Regenerate ChartSpark charts** in `_dashboard.md`. The Dataview live sections (status board, sparkline, alerts, action loop, vanity, regression) auto-refresh on read, but ChartSpark Chart.js blocks are static — they must be regenerated by:
   ```bash
   python {{USER_HOME}}\.claude\vault-maintenance\chartspark-update.py
   ```
   The script reads all **`metrics/*.md`** emits, generates 4 Chart.js JSON blocks (System Health line / Activity bar / Personal Leverage line / Output Quality line), and writes them between the `<!-- BEGIN AUTO-CHARTS -->` / `<!-- END AUTO-CHARTS -->` markers in `_dashboard.md`. Idempotent — safe to rerun. With 1 emit it writes a snapshot placeholder; with ≥ 2 emits it writes actual charts. **Never hand-edit content between those markers** — it gets overwritten on next run.

### Skip condition

If the user has not yet adopted the `daily-rating:` frontmatter field (first 7 days after rollout) → emit metrics with "n/a" placeholder for Personal Leverage rows; do not file a threshold proposal until baseline is established.

---

## Phase 6: Evolution report

Single dated report at **`04 Notes/vault-evolve/{YYYY-MM-DD}.md`**. Template:

```markdown
---
type: vault-evolve-report
date: YYYY-MM-DD
mode: autonomous | interactive
last-updated: YYYY-MM-DD HH:MM:SS
window-start: YYYY-MM-DD (last run)
auto-applied: N
proposed: M
status: pending-review | reviewed | applied
---

# Vault-Evolve · YYYY-MM-DD

> Daily audit + evolution pass. Window: [start] → [today]. Auto-applied N · Proposed M · Manual review K.

## 概要 — top decisions to make

[1-3 highest-leverage 🟡 items the user should disposition this session. Skip section if 0 🟡 items.]

---

## Auto-applied (🟢 — N items)

| Target | Change | Reason |
|---|---|---|
| `.claude/skills/biz/SKILL.md` | Description: appended trigger "评估这个" | Observed 5 invocations matching this phrase in last window |
| ... |

---

## Propose for review (🟡 — M items)

### M.1 · <Title>
**Target:** <file or subagent>
**Current state:** <quote or excerpt>
**Proposed change:** <specific edit>
**Reason:** <observation count + pattern>
**Safety note:** <what could go wrong>
**Disposition:** `[pending]` — to apply, reply `vault-manager: execute evolve-M.1`

[repeat per proposal]

---

## Manual review (🔴 — K items, if any)

[Items requiring deeper review — deletions, body rewrites, structural changes. Each surfaces with explicit warning.]

---

## Telemetry summary

| Metric | This window | Prior window | Delta |
|---|---|---|---|
| Skills invoked (unique) | N | M | +/- |
| Subagent calls | N | M | +/- |
| New Cards | N | M | +/- |
| Workstreams archived | N | M | +/- |
| Tasks captured | N | M | +/- |

**Most-used skill this window:** `/skill-X` (N invocations)
**Least-used / retire candidate:** `/skill-Y` (last seen: D days ago)

---

## Audit findings (delegated)

[Compact summary of vault-manager audit + sanity-equivalent + card-lint findings. Severity-tagged.]

---

## Learning loop status

[Patterns crossing thresholds this run. What got proposed for encoding / suppression.]

---

## Next run

- Scheduled: tomorrow 06:00 (Windows Task Scheduler)
- Manual rerun: `/vault-evolve` anytime
- Decision ledger: [[_decisions]]
- Rolling log: [[_log]]
```

---

## Phase 7: Tiered apply

### 🟢 Auto-apply (both modes)

Use `Edit` for each safe change. After each, append to `_decisions.md`:

```markdown
### Proposal · <type> · auto-applied YYYY-MM-DD
**Target:** <file>
**Change:** <specifics>
**Reason:** <obs>
**Safety:** 🟢
**Outcome:** Applied
```

Hard rule: **never auto-apply if the file's mtime is within 5 minutes** (likely user is editing — defer to next run).

### 🟡 Propose-only

Write to report. Don't edit. User dispositions next session via `vault-manager: execute evolve-<id>`. The vault-manager subagent reads the report, processes the approved IDs as a batch via its EXECUTE phase, and appends outcomes to `_decisions.md`.

### 🔴 Manual

Surface in report with explicit warning. No execute keyword applies — user must take action manually with full context.

---

## Phase 8: Decision ledger update

Before exit, scan yesterday's (or the prior) report for inline dispositions the user added (e.g., user opened the report file in Obsidian, added `[accepted]` / `[rejected — reason: ...]` next to specific proposals).

For each dispositioned proposal:
1. Update the corresponding entry in `_decisions.md` with the outcome
2. If `[accepted]` — propose execution via vault-manager (next phase)
3. If `[rejected with reason]` — capture the reason; this informs Phase 4's pattern compression

---

## Phase 9: Log + confirm

Append a single line to **`04 Notes/vault-evolve/_log.md`**:

```markdown
| YYYY-MM-DD HH:MM | autonomous | window: 1d | 🟢 applied: N | 🟡 proposed: M | 🔴 manual: K | report: [[YYYY-MM-DD]] |
```

### Interactive mode confirm

```
Vault-evolve complete · YYYY-MM-DD
🟢 N auto-applied · 🟡 M proposed · 🔴 K manual

Top decision: <概要 item 1>

Full report: [[04 Notes/vault-evolve/YYYY-MM-DD]]
Decision ledger: [[04 Notes/vault-evolve/_decisions]]

Want to disposition 🟡 items now (M items, ~3min)? Or defer to your next session?
```

### Autonomous mode

Silent — no chat output. Report file is the entire interface. Scheduler log captures exit status.

---

## Hard rules

- **Tier discipline.** Every change traces to a tier. 🟢 auto, 🟡 propose, 🔴 manual. No exceptions.
- **Mtime guard.** Don't auto-apply to files modified in last 5 minutes (active user editing).
- **Idempotency.** Running twice on the same day produces no new changes — only updates the timestamp.
- **Never edit user-authored prose.** Card bodies, project docs, meeting notes, contracts, deal artifacts. Frontmatter-only on framework files; never body without `🟡` propose first.
- **Decision ledger is append-only.** Never rewrite history. If a learned default needs reversal, add a new entry stating the reversal — don't delete the original.
- **vault-manager system prompt updates are append-only.** Learned defaults go in a dedicated section appended by /vault-evolve. Never touch hand-authored sections.
- **Batch ceiling: 50 auto-applied changes per run.** Larger → split across days. Limits blast radius.
- **No edits to:** **`06 Tasks/**`, `**.obsidian/**`, `**00 Raw/`** immutable subfolders, `chain-anchor` fields in Action files (immutable per `[[09 Rules/action.md]]`).
- **Autonomous mode never asks questions.** All decisions deferred to the written report.
- **Report file is the single source of truth.** If the report says auto-applied N items, those N items got `_decisions.md` entries. If not, something failed — surface the gap in next run.

---

## Failure modes

| Symptom | Fix |
|---|---|
| Phase 1 finds zero telemetry (last run very recent, or user inactive) | Run a thin audit-only pass; skip pattern detection for this window. |
| `_decisions.md` doesn't exist on first run | Create it with header frontmatter; treat first run as baseline (no pattern compression possible). |
| User edited yesterday's report with conflicting dispositions (e.g., `[accepted]` AND `[rejected]` on same item) | Surface in next report's "Anomalies"; do not apply. |
| Pattern threshold crossed (N_accept ≥ 3) but pattern would conflict with hand-authored system prompt | Don't auto-encode. Surface as 🟡 with the conflict noted. |
| Skill description refinement would create description >500 words | Skip the addition; surface as 🟡 — needs human-curated condensation. |
| Two skills' descriptions become identical after refinements | Detect at end of Phase 7; surface as 🟡 merge candidate. |
| Scheduler task fails (network, Claude CLI not in PATH, etc.) | Wrapper script catches + logs to `_scheduler.log`; next interactive run detects the gap and processes catch-up. |
| User runs `/vault-evolve` interactively while autonomous run is in progress | Detect via lockfile `_running.lock`; show progress and merge results. |

---

## Integration with other skills + subagents

| Trigger | Hand-off |
|---|---|
| Phase 5.c emits new metrics | Run `chartspark-update.py` (step 6) so `_dashboard.md` Chart.js stays in sync with `metrics/` |
| Audit reveals stale Action files | Delegate to `vault-manager: propose-archive` |
| Audit reveals dead wikilinks | Delegate to `vault-manager: repair-wikilinks` |
| Card-lint findings need action | Surface in 🟡 with link to `/card-lint` for next session |
| MEMORY.md needs pruning | Surface in 🟡 — never auto-edit MEMORY.md per its own rule |
| Skill retire approved by user | Execute via `vault-manager: execute evolve-<id>` (moves SKILL.md folder to `_archive/`, removes row from `Skills I Use Daily.md`) |
| Subagent prompt update approved | Edit **`<vault>/.claude/agents/<name>.md**` in the "Learned defaults" section (canonical home; the `08 Agents/` mirror is retired — do not recreate it) |
| New cross-chain pattern detected | Propose in 🟡; if approved, encode in CLAUDE.md § Skill Auto-Chain Rules |

---

## Lineage / why this exists

Per [[02 Cards/meta/C260511-vault-skills-converted-to-real-claude-code-skills]], the vault is now an operating system rather than three half-connected systems. An OS that doesn't observe its own behavior degrades. This skill is the daily observation + correction loop. It complements:

- `/sanity` — drift detection (broader vault-wide audit, weekly cadence)
- `/card-lint` — Card graph health (monthly cadence)
- `harness-pulse` (Tier-7 routine) — real-time liveness reflex (every 3h), pushes incidents immediately; this skill consumes its accumulated verdicts to surface *chronic* patterns the reflex only ever saw as one-offs
- `vault-manager` subagent — on-demand structural ops with two-phase safety
- This skill — daily routine that observes USAGE patterns, not just structural drift, and accumulates learnings the vault-manager reads to improve over time

The "self-evolving" promise rests on three constraints:
1. Pattern compression from user judgments (not random mutation)
2. Tiered safety (auto only for additive, never-removes operations)
3. Append-only ledger (every change is auditable + reversible)

Without all three, "self-evolution" becomes "self-mutation" — which is what makes most agentic-loop experiments fail.
