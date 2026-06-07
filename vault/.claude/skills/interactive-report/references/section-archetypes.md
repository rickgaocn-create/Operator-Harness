# Interactive Report · Section Archetypes

11 canonical section patterns. Pick + remix per source MD's structure.

---

## §1. Cover / Hero

**Purpose**: orient reader · 概要 · "why am I reading this"

**Required elements**:
- Dark cinematic bg (linear-gradient: midnight → midnight-2 → midnight-3, with amber + cobalt radial accents)
- Hero meta (date · audience · INTERNAL flag · NDA disclaimer) in mono font, 0.55 opacity
- H1 title (CN main + EN accent in italic serif)
- Hero subtitle (≤2 lines · context)
- Hero stats strip (4-5 big numbers: speakers / studios / OKR touches / quantified value / decision count)
- Hero 概要 (≤6 lines · amber-glow border-left)
- Logo strip below (filtered to white via `filter: brightness(0) invert(1)`)

**Skip if**: source MD is < 500 words (too thin for a hero, just lead with §1).

---

## §2. Context / Agenda / Setup

**Purpose**: ground the rest of the document · time and actor map

**Element options** (pick based on source):
- **Event-based**: time ribbon (HTML CSS, NDA-banded) + speaker heatmap (grid)
- **Document-based**: scope/audience card grid (3-5 cards)
- **Decision-based**: stakeholder map (HTML grid) + timeline strip

**Always include**:
- Source-criticism callout if source contains AI-generated transcripts / 飞书 spaces / mixed reliability sources

---

## §3. Register C · Project-Team Impressions / Core Takeaways

**Purpose**: surface the project-team's first-person directional impressions (per [[09 Rules/message-tone.md]] Register C)

**Pattern**:
- N cards (typically 4-7)
- Each card: `label` (small mono) + `h3` headline (declarative claim) + `p` elaboration + `implication` block (border-top dashed, smaller text, "对 X 而言" framing)

**Voice**:
- "我看下来…" / "我觉得…" / "对{{PROJECT_A}}而言…" (项目组第一人称)
- NOT "X 由 A 与 B 构成…" (AI 框架式)

**Anti-pattern**: turning this section into framework-tabular analysis. Cards stay 项目组立场.

---

## §4. Industry Validation / Comparative Block

**Purpose**: hard external proof / comparative analysis

**Required**:
- **Studio/Actor trio block** — 2-4 entities side-by-side with logo + tagline + poster + bullet list + 1-line lesson
- **Radar chart** comparing entities on 5 dimensions (per `svg-library.md` § 3)
- **Paradigm shift SVG** (pipeline comparison or workflow) showing the conceptual frame

**Tone**: usually dark section (high-impact visual interlude)

---

## §5. Roadmap / Key Content / Feature Catalog

**Purpose**: substantive content - the "what they said" record

**Pattern**:
- Feature card grid (6-9 cards organized by category)
- NDA banner + collapsible NDA section (if applicable)
- Philosophical callout (italic serif on amber-light bg) for "load-bearing quote"
- Workflow SVG demo (per `svg-library.md` § 9)

---

## §6. Implications / Decisions Framing

**Purpose**: bridge from "what they said" to "what we should do"

**Required**:
- **Quadrant matrix** (per `svg-library.md` § 4) plotting 4-10 implications on (effort × value) axes with bubble sizes for magnitude
- Card grid below with implications detail (each card matches a quadrant position)

**Recommendation**: this section is usually the most important for {{PERSON}} — show effort vs value matrix front-and-center.

---

## §7. Decision Gates / Trigger Conditions

**Purpose**: bind each decision to specific value evidence — avoid "PoC ran but nobody pulls the trigger"

**Required**:
- **Unified decision tree SVG** (per `svg-library.md` § 5) — root "today" → branch into N tracks → gates → outcomes
- Detail strips below for each track (optional supplement)

**Tone**: typically dark section (strategic interlude #2)

---

## §8. Value Analysis (multi-dimensional)

**Purpose**: anti-naive ROI · honor structural variation in value types

**Required**:
- Value mechanism table (议题 / 价值产生机制 / 受益方 / 时间 / 性质 / 量级 with `<span class="magnitude">` pills)
- **Sensitivity tornado chart** (per `svg-library.md` § 6) for the highest-leverage quantified议题
- Compounding effects callout (amber border-left, listing叠加 scenarios)
- Investment vs value integrated table

**Critical**: always include the "数字均为粗估" disclaimer + show worst/basis/best scenarios.

---

## §9. Decision Asks (Q1-Q4)

**Purpose**: explicit asks of the audience · single-action each

**Pattern**:
- Ask card grid (3-5 cards typically)
- Each card: `q-label` (Q1 · 议题 X) + `q-title` + `p` context + `recommendation` block (with "{{USER_NAME}} 建议 →" auto-prefix via CSS pseudo)

**Critical**: each ask must be answerable in one of {accept / push back / defer / kill}. Otherwise it's not an ask, it's commentary.

---

## §10. Timeline / Gantt

**Purpose**: bind decisions to dates · show parallel work · highlight critical path

**Required**:
- **Gantt chart SVG** (per `svg-library.md` § 7) with date axis, parallel tracks, gates as diamonds, today marker, critical path band
- Detail milestone table below

**Tone**: typically dark section (strategic interlude #3)

---

## §11. Appendix

**Purpose**: provenance · references · NDA disclaimer

**Grid**:
- vault sources column
- related wiki column
- OKR / Action anchors column
- public sources column
- community implementations column (if relevant)
- NDA disclaimer column

**Footer below**: generated by / source MD path / Thariq credit / self-contained note

---

## Section Sequencing Patterns

**Default — Decision-Grade (10-11 sections)** — for full-stack 内部汇报 with asks:
```
Cover (dark · with 致 X framing) →
§1 Context →
§2 Register C N takeaways →
§3 Industry Validation (dark) →
§4 Roadmap (with NDA if applicable) →
§5 Implications →
§6 Decision Gates (dark) →
§7 Value (with AI disclaimer if quantified) →
§8 Asks Q1-Q4 →
§9 Timeline / Gantt (dark) →
§10 Appendix
```

**Pure-Share (7-9 sections)** — for 团队分享 / 行业观察 / 会议纪要分享 · no decisions in flight
```
Cover (dark · with 纯分享 badge · NO 致 X) →
§1 Context (integrated timetable + speakers if event) →
§2 N 综合印象 (fixed grid if exact count — 2×2 for =4) →
§3 Industry / Validation block (dark) →
§4 Roadmap / Content body (with major spotlight if any) →
§5 Major Moment / Standalone Section (dark · e.g., Matrix Demo) →
§6 N 潜在价值 (quadrant matrix · optional) →
§7 量化分析 (🤖 AI 自动分析 banner mandatory · no time-bound milestones) →
§8 Appendix · 源材料 / 官方图 (optional · supporting record)
```

⚠️ **Pure-share differences from decision-grade — see [pure-share-mode.md](pure-share-mode.md) for the 12 specific preferences**. Key drops: §决策门 / §决策请示 / §时间轴 / speaker × dimension heatmap. Key adds: 🤖 AI 自动分析 banner on quantified sections, equal-weight visual treatment, fixed grids for fixed counts.

**Compact (7 sections)** — for shorter biweekly / weekly:
```
Cover (dark) →
§1 OKR Buckets →
§2 What Moved →
§3 Risks + Gaps (dark) →
§4 下双周聚焦 →
§5 Asks →
§6 Appendix
```

**Audit (5 sections)** — for /sanity or /card-lint output:
```
Cover (dark) →
§1 Findings →
§2 Auto-applied →
§3 Propose-for-review (dark) →
§4 Manual flag →
§5 Telemetry / Refs
```

## When to Skip Sections

- Skip §3 Industry Validation if source is internal-only (no external comparison)
- Skip §6 Decision Gates if no decisions in flight (informational document)
- Skip §8 Asks if source is FYI not action-soliciting
- Skip §10 Timeline if all items are immediate / no future schedule
- Never skip §11 Appendix — provenance is non-negotiable for forwardable artifacts
