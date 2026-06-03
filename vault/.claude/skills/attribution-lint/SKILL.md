---
category: work
name: attribution-lint
description: Check cross-source summaries for party-attribution discipline. Use /attribution-lint on meeting-summary, bd-update, or market-intel docs before forwarding.
model: claude-sonnet-4-6
allowed-tools: Read, Edit, Glob, Grep, Bash
companion-rules:
  - "[[09 Rules/attribution-discipline.md]]"
created-by: claude
created: 2026-05-21
---

# Skill: Attribution Lint

Verify every `**[party]**：` cell in a cross-source summary doc traces to source. Run before forwarding to leadership; run in bulk to audit historical docs.

→ Canonical rule: [[09 Rules/attribution-discipline.md]]

---

## Modes

| Invocation | Mode |
|---|---|
| `/attribution-lint <file>` | **Single file** — verify one doc |
| `/attribution-lint --sweep` OR `/attribution-audit` | **Bulk** — scan all `type: meeting-summary` / `bd-update` / `market-intel` docs in vault |
| `/attribution-lint --fix <file>` | **Auto-fix** — flag violations + propose patches; user confirms each |

---

## Single-file workflow

### Step 1: Read frontmatter

Required fields:
- `type` ∈ { `meeting-summary`, `bd-update`, `market-intel`, `briefing`, ... } (see [[09 Rules/attribution-discipline.md]] § 1)
- `source_anchors:` list (per § 4 of the rule)

If missing → fail immediately:
> ❌ 文档缺 `source_anchors:` frontmatter 字段。[[09 Rules/attribution-discipline.md]] § 4 要求 cross-source 汇总文档强制提供 provenance。

### Step 2: Extract every party-prefixed cell

Grep pattern (multiline-aware):
```
^\s*[•\-\*]?\s*\*\*([^\*]+)\*\*\s*[：:]\s*(.+)$
```

Or in markdown tables, scan cell contents for the same pattern.

For each match → record `(prefix, claim, line_number)`.

### Step 3: Classify prefix

- **Counterparty prefix** (e.g., `TapTap`, `B 站`, `荣耀`, `EPIC`, vendor / partner / company names) → requires `source_anchors` entry with `quote:` + `source:`
- **Approved synthesis prefix** (per [[09 Rules/attribution-discipline.md]] § 3):
  - `我方判断`
  - `项目组观察`
  - `我方推断` (含变体 `我方推断（基于 XXX）`)
  - `我方自陈`
  - `我方` (compatible with `我方判断` family)
  - Approved prefix → must have `synthesis_from:` entry in `source_anchors`, OR be self-evident (我方 own statement)

If prefix matches neither → **violation type 1: unknown prefix** (e.g., `主创`, `编辑`, `KOL` — these should be canonicalized).

### Step 4: Verify source-anchor coverage

For each counterparty-prefixed cell:
- Look in `source_anchors` for `cell:` that matches this cell's logical location (best-effort string match on 主题/列名/前缀)
- Verify `quote:` field exists and is non-empty
- Verify `source:` field exists and points to a real wikilink (Glob check)

For each approved-synthesis-prefixed cell:
- Look in `source_anchors` for `cell:` match
- Verify `synthesis_from:` exists with ≥1 signal listed
- If `synthesis_from:` lists only 1 signal AND prefix is `我方推断` → OK; if only 1 signal AND prefix is `我方判断` → warning (judgment usually rests on multiple signals)

If no `source_anchors` match found → **violation type 2: orphan cell**.

### Step 5: Report

```
=== Attribution Lint Report ===
File: <path>
Total party-prefixed cells: N
Anchored: X
Approved synthesis (provenanced): Y
Violations: Z

--- Violations ---
[L42] **TapTap**：都市部分可玩的东西还是少
  Type: orphan cell (no source_anchors match)
  Verdict: ⛔ FABRICATION RISK
  Suggested fix: 改前缀为 **我方判断**：+ 添加 source_anchors 条目 synthesis_from:[...]

[L67] **主创**：...
  Type: unknown prefix
  Verdict: ⚠️ canonicalize
  Suggested fix: 改为 **我方-研发** 或 **我方-主创** 之一

--- Summary ---
PASS: 0 / FAIL: 2
```

Exit code 0 if PASS, 1 if any FAIL.

### Step 6: Stamp passed docs

If lint passes (0 violations):
- Add HTML comment at file bottom: `<!-- attribution-lint: passed YYYY-MM-DDTHH:MM ISO_TIMESTAMP -->`
- Move on

---

## Quote-grounding gate (hard, deterministic — closes Anti-Pattern 5)

Step 4 confirms a counterparty cell *has* a `source_anchors` entry; it does NOT confirm the quoted text actually appears in the source. Close that gap on every single-file lint by running the deterministic grounding gate:

```bash
python .claude/_eval-fixtures/behavioral/attribution_gate.py \
  --artifact "<file>" --sources "<each cited source meeting note>" --log
```

- Each `⛔ FABRICATION RISK` line = a sentence-length 「quote」 attributed to a counterparty that is NOT found in any source. Treat as a HARD violation (same severity as an orphan cell) → surface + route to [[09 Rules/attribution-discipline.md]] § 8 Recovery.
- `--log` records the run to `_state/gate-verdicts.jsonl` (feeds the promotion tracker below). Always pass it on real docs.
- **Scope (honest):** catches verbatim-quote fabrication (the 2026-05-19 class). Does NOT catch paraphrased-claim fabrication (a counterparty prefix carrying a synthesized *position* without quote marks) — that still needs human + `source_anchors` judgment. Short 「…」 (< ~12 normed chars: titles / slogans) are intentionally exempt.

## Promotion criterion (manual step → PostToolUse auto-hook)

The gate runs as a MANUAL step today. Promote it to an automatic PostToolUse hook (auto-gate every `type: meeting-summary` / `bd-update` save) ONLY when all three hold — check with `attribution_gate.py --status`:

1. **Volume** — ≥ 15 real summary docs gated (logged).
2. **Precision** — false-positive rate < 10% across logged flags (disposition each: real fabrication vs false alarm).
3. **Recall** — the `recall-test-fabrication.md` fixture still returns FAIL.

Anti-forget: (a) every `--log` run prints the docs-gated count and announces TARGET REACHED at 15; (b) a dated backstop reminder. **When promoted:** wire `attribution_gate.py` into `.claude/settings*.json` PostToolUse for the relevant `type`s, and change this heading to `## Promotion criterion — PROMOTED YYYY-MM-DD`.

---

## Sweep mode

```bash
/attribution-audit
```

1. `Glob` vault for `*.md` files where frontmatter contains `type: meeting-summary` OR `type: bd-update` OR `type: market-intel`
   - Use `Grep` with pattern `^type: (meeting-summary|bd-update|market-intel|briefing)$` `glob: "**/*.md"`
2. For each matching file, run Single-file workflow (Steps 1-5)
3. Aggregate report:

```
=== Attribution Sweep Report ===
Scanned: N files
Passed: X
Failed: Y (listed below)
Skipped (no `source_anchors`): Z

--- Failures ---
[[file1]] — 3 violations (orphan cells: L42, L67, L91)
[[file2]] — 1 violation (unknown prefix: L33)

--- Skipped (need `source_anchors` retrofit) ---
[[file3]]
[[file4]]
```

User decides which to fix manually.

---

## Auto-fix mode

`/attribution-lint --fix <file>`:

For each violation:
1. Show the violation line
2. Propose specific patch (e.g., 改前缀 + 新增 `source_anchors` 条目)
3. Wait for user confirm
4. Apply patch via Edit
5. Re-run lint until 0 violations

Never auto-fix without confirmation — user judgment required on whether a cell should be reclassified vs deleted vs left as fabrication-flagged-for-followup.

---

## Anti-Patterns

- ❌ Skipping lint on `audience: 上级` docs — these are the highest-stakes use case
- ❌ Adding HTML stamp `<!-- attribution-lint: passed -->` without actually running the lint
- ❌ Treating `source_anchors` as optional even when `type: meeting-summary` — it's required by [[09 Rules/attribution-discipline.md]] § 4
- ❌ Using `--fix` non-interactively — every patch needs user confirmation
- ❌ Auto-generating `source_anchors` retrofit from existing cells without verifying against source — that's how fabrications get *blessed*, not caught
