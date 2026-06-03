---
category: work
name: interactive-report
description: Convert a finished Markdown business artifact into a self-contained interactive HTML report. Use for leadership-forwardable versions of /biz, deep meeting notes, biweekly reports, or internal briefings.
model: claude-opus-4-7
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch
companion-rules:
  - "[[09 Rules/file-types.md]]"
  - "[[09 Rules/message-tone.md]]"
created: 2026-05-15
created-by: claude
source:
  - https://thariqs.github.io/html-effectiveness/
  - https://simonwillison.net/2026/May/8/unreasonable-effectiveness-of-html/
audit-trace: "2026-05-15 EPIC Summit Interactive HTML v0.1→v0.2 build session · {{USER_NAME}} approved 'this level of direction' · pattern crystallized as reusable skill"
---
# Skill: Interactive Report (MD → cinematic HTML for human consumption)

Convert an MD-source vault artifact into a **self-contained interactive HTML report** designed for human readers who would otherwise skim a wall of MD. Cinematic editorial aesthetic, 6-9 inline SVG visualizations, zero CDN deps, print + mobile friendly.

> **Why this skill exists** — Per Thariq Shihipar's "Unreasonable Effectiveness of HTML" (2026-05-08): *"Markdown is a report; HTML is an interface. Reports are for reading. Interfaces are for continuing the work."* The bottleneck isn't Claude reading — it's humans reading Claude's output. For high-stakes forwardable artifacts (诸葛/board/team), HTML render meaningfully changes whether the work gets engaged with.
>
> **Pattern origin** — 2026-05-15 EPIC Summit Interactive HTML v0.2. Reference exemplar at `<vault>/03 Projects/{{PROJECT_A}}/09 Reports/(C) EPIC Summit Interactive-2026-05-15.html`.

> **Contract reference** — Output respects [[09 Rules/file-types.md]] § (C)-prefix for AI-generated files. Voice register for the document body follows the source MD (typically Register B — formal third-person) per [[09 Rules/message-tone.md]].

## When to Use

- `/interactive-report` or "render to HTML" explicit trigger
- Source MD will be forwarded to 诸葛 / 董事会 / 工作室决策层 / 跨部门
- Source MD is a binding-deliverable that 诸葛 or upline is likely to skim
- Multi-section document with values/comparisons/decisions worth visualizing
- Companion to one of these source skills (chain after):
  - `/biz` (business evaluation) — `--render=html` flag
  - `/meeting-note --deep` — when forward to leadership
  - `/periodic-report --biweekly` — OKR-bucketed visualization
  - `/to-internal-briefing` — 1-page 内部汇报 made interactive
  - `/day-digest` — when the 4 chew sections need a dashboard form (rare)

**Don't use for:**
- Source MD < 200 lines or with no structured data — overkill, the MD is fine
- Active drafting / iteration on the source itself — finish the MD first, render after
- WeChat / 邮件 message drafts — those are Register A, wrong audience for interactive HTML
- Cards / instincts / daily notes — these are vault-internal, MD is correct format
- Anything with high-confidence NDA content where leakage risk > forward value

## How It Works

### Phase 0 — Resolve source + audience + scope + **mode**

Ask plain text (NOT AskUserQuestion — Discord rendering):

1. **Source MD path** — wikilink or **`03 Projects/.../*.md`** path. Default = most recently created `(C) *.md` in `09 Reports/` or `Pitches/`
2. **Audience** — (a) internal forward to 诸葛 / board (b) team-educational (动画团队 / 工作室) (c) sandbox / workflow validation
3. **🔑 Mode** (this is the most important question) — (a) **decision-grade** (含决策请示 Q1-Q4 + 决策门 + Gantt 时间轴 + 致 X 框架) OR (b) **pure-share** (纯分享 · 无决策请示 · 无时间轴 · 见 [**`references/pure-share-mode.md`**](references/pure-share-mode.md))
4. **🌐 Language register** (NEW · v0.7 · ratified by {{USER_NAME}} on EPIC Summit) — (a) **CN-first localized** (Chinese audience: 动画团队 / 团队分享 / 工作室 / 行业观察 — full Chinese prose + Tier B/C English-with-tooltips + § 术语注释 glossary · see prefs 19-21 in [**`references/pure-share-mode.md`**](references/pure-share-mode.md)) OR (b) **CN/EN mixed** (technical peer audience comfortable with code-switching) OR (c) **EN-only** (international audience). *Pure-share + Chinese team audience → (a) is the default — {{USER_NAME}}: "the audience will be a general audience that is Chinese and needs footnotes".*
5. **Format** — (a) scrollable single-page hybrid [recommended] (b) slide-deck-style (c) dashboard
6. **NDA detail level** — (a) include NDA section content with red banner + collapsed-by-default (b) **minimum** — exclude detail, show only "NDA path exists, content available in-person" placeholder (c) two builds. *Pure-share mode default: minimum, unless source MD keeps NDA framing.*
7. **Image richness** — (a) minimal (logos + 1-2 hero) (b) **rich** (10-15 images: studio stills + posters + logos) (c) pure SVG (zero external images)
8. **Static export** (NEW · v0.7) — produce a full-page PNG screenshot alongside the HTML? (a) **yes, both** [recommended for forwardable artifacts — phone WeChat scenarios benefit from a single image] (b) HTML only. *Static PNG inherits the dual-layer footnote signal because § 术语注释 glossary is in the body.*
9. **Output path** — default `<source-project>/09 Reports/(C) <source-stem> Interactive-<YYYY-MM-DD>.html` (+ `.png` sibling if static export)

**Mode is the single most important Phase 0 choice** — it determines whether to include §决策门 / §决策请示 / §时间轴 sections AND how to frame the 概要 / hero / language throughout. Read **`references/pure-share-mode.md`** before drafting if user picked (b).

If user says "go with recommended": pure-share Chinese team audience (most {{USER_NAME}} scenarios) → **(b) pure-share · (a) CN-first localized · (a) scrollable hybrid · (b) minimum NDA · (b) rich images · (a) HTML + PNG · default path**.

**Heuristic for auto-detecting pure-share mode** (if user doesn't explicitly say):
- Source MD has no `## 决策请示` / `## Decision Asks` / `## 行动项` section
- Source MD frontmatter has no `audience: 诸葛` / decision-maker
- Source MD title contains `分享` / `观察` / `update`
- The artifact section "Appendix" is marked "不录入" / "FYI only"
- User has explicitly removed 致 X framing language

**Heuristic for auto-detecting CN-first localized mode** (Phase 0 Q4):
- Audience is 动画团队 / 工作室 / 团队分享 / 跨次元沙龙观众 etc. (any Chinese team noun without explicit international peers)
- Source MD is Chinese-written but contains substantial English technical vocabulary (MCP / agentic / cinematic / pipeline / etc.)
- Source MD mentions WeChat / 朋友圈 / 微信群 as a forwarding channel
- Default `--render=html` invocations from Chinese-language source MDs

If any 2 of the above are true → assume (a) CN-first localized.

### Phase 1 — Read all source artifacts

Parallel reads:
- Source MD (full)
- Companion files referenced in source MD frontmatter (e.g., parent meeting note for a /biz output, OKR file for biweekly report, project CLAUDE.md)
- EPIC / counterparty wiki entries if referenced
- Daily note for that date if relevant context

**Do NOT summarize from memory** — actually read. Per [[I260515-day-digest-must-grep-kanban-tomorrow-before-sign-off]] discipline.

### Phase 2 — IA proposal (sign-off required before build)

Propose 8-11 sections matching the source MD's structure. Standard archetype (adapt to source):

1. **Cover / 概要** — hero with dark cinematic bg, 4-5 big stat callouts, 概要 callout, logo strip
2. **现场速览 / Context** — time ribbon (if event-based) OR scope card (if document-based) + relevance heatmap (if multi-actor)
3. **N 项目组综合印象 (Register C)** — card grid with implications per card
4. **行业兑现度 / Comparative validation** — studio trio OR comparison block + **radar chart** + paradigm shift SVG
5. **Roadmap / Key content** — feature grid + NDA banner if applicable + workflow SVG
6. **N 个具体含义** — **quadrant matrix** (投入 × 价值) + card grid detail
7. **决策门 / Decision gates** — unified decision tree SVG
8. **价值评估 / Value analysis** — value mechanism table + **sensitivity tornado** + complexity callout
9. **致诸葛 / Decision asks** — Q1-Q4 ask-card grid with {{USER_NAME}}-recommends
10. **时间线** — **Gantt timeline** with date axis, parallel tracks, diamond gates
11. **附录** — vault refs, public sources, NDA disclaimer

**Surface to user:**
- Proposed IA (sections + which SVG visualizations per section)
- Visual gap analysis (which images need fetching from where)
- 3-5 grill questions if scope ambiguous

**Wait for sign-off before Phase 3.**

### Phase 3 — Asset gathering (parallel WebFetch if needed)

If image richness = rich (b):
- WebFetch Wikipedia commons for: studio logos, case posters, key people headshots
- WebFetch official sources (Epic, vendor sites) for: product screenshots, feature stills
- Construct Wikipedia thumb URLs: **`https://upload.wikimedia.org/wikipedia/commons/thumb/X/XX/Y.svg/SIZEpx-Y.svg.png`**
- Verify URLs return 200 before embedding

If image richness = minimal (a):
- Logos only (Wikipedia commons URLs are stable + free to hot-link)

If image richness = pure SVG (c):
- Skip all external image fetching, use inline SVG for everything

**Always have alt-text** for `<img>` tags. Browser renders alt-text if URL 404s. Graceful degrade.

### Phase 4 — Draft v0.1 HTML

Use the canonical template at `<vault>/.claude/skills/interactive-report/references/canonical-template.html` as starting point. Replace placeholders with source content. Embed SVG visualizations from **`references/svg-library.md`**.

**Key build patterns:**
- Single self-contained HTML file (no CDN, no build step)
- CSS variables for the cinematic palette (see **`references/design-system.md`**)
- Alternating dark/light sections (cover dark · light · light · **dark** · light · light · **dark** · light · light · **dark** · light)
- Section anchors + sticky top nav + scroll-spy JS
- 演示模式 button (top-right) toggles `.present-mode` body class
- Print-friendly CSS (`@media print` resets dark sections, keeps content)
- Mobile-responsive (<720px breakpoint)

**Required SVG visualizations** (pick by source content):
| Source has | Add visualization |
|---|---|
| Event with agenda + speakers | Time ribbon (NDA-banded) + speaker heatmap |
| Multi-entity comparison (≥3 actors with multiple dimensions) | Radar / spider chart |
| Multiple proposals with cost + value dimensions | Quadrant matrix (bubble chart) |
| Multiple decision gates / phased actions | Unified decision tree (gold diamond gates) |
| Quantified estimate with sensitivity variables | Tornado chart (centered on basis, ± variable swings) |
| Time-sequenced milestones (across multiple tracks) | Gantt timeline (date axis, parallel tracks) |
| Process / pipeline before vs after | Side-by-side pipeline comparison SVG |
| Multi-step workflow with mixed actors (human vs AI) | Workflow SVG with color-coded steps |

### Phase 5 — Iterate with user

Save initial draft to vault path. If user has tunnel active (per `interaction-skills` or session context), sync to `/tmp/<artifact>/index.html`. Else just announce path.

Solicit feedback on:
- IA flow + section order
- Color palette / typography intensity
- Specific visualizations — too many / too few / wrong type
- Length — collapse sections if 诸葛 audience prefers shorter

Iterate with Edit (not Write) for surgical updates.

### Phase 6 — Ship + cross-link

After user accepts:

1. **Update source MD frontmatter** — add `interactive-html: "[[(C) <stem> Interactive-<date>]]"` field for back-link
2. **Update related artifacts** — if source has a wiki entry (counterparty / project), add the HTML link to wiki's 关联文档 section
3. **Append to daily note** § Ingests — log line: `[HH:MM] interactive-report rendered: <source> → <HTML path>`
4. **Optional tunnel** — if user asks "let me check on phone", spin Python http.server + cloudflared quick tunnel (see **`references/tunnel-runbook.md`**)
5. **Optional /biz auto-chain** — if source was a meeting note and biz-eval doesn't exist yet, propose `/biz` next

### Phase 7 — Confirm

> "已落档 [[(C) <stem> Interactive-<date>.html]] · 6-9 SVG visualizations · {N} sections · {KB} bytes · {N} external images. 视频/演示模式 button 在右上角. 打开 in 浏览器 OR `/share-to-phone` 启动 tunnel."

## Hard Rules

1. **NEVER skip Phase 2 IA sign-off** — building without scope agreement = waste of effort + user can't course-correct mid-build
2. **NEVER use AskUserQuestion** — Discord rendering issue per user CLAUDE.md. Plain text questions only.
3. **NEVER embed NDA content without explicit authorization** in Phase 0. Default = minimum (option b). Banner all NDA sections with red border + "INTERNAL — 不外发"
4. **NEVER skip print-friendly CSS** — 诸葛 audience may print + read on paper; dark sections must convert to white-bg with dark text via `@media print`
5. **NEVER embed CDN JS / CSS dependencies** — fully self-contained file. Inline everything. Hot-linked images via `<img src="...">` is OK (graceful degrade).
6. **NEVER fabricate quantified numbers** that aren't in the source MD. Reuse source MD's basis values (¥720K, etc.) verbatim. Cite source-MD assumptions block when shown.
7. **NEVER produce HTML > 200KB** — bigger means too much content, time to split. Compress aggressively (inline SVG paths simplified, redundant CSS removed).
8. **NEVER include hot-linked images from unstable sources** — Wikipedia commons + Epic CDN + Anthropic CDN OK; vendor-specific URLs that 404 in 6 months not OK.
9. **NEVER skip the 演示模式 toggle button** — it's the deck-mode affordance {{USER_NAME}} uses on phone + projector.
10. **ALWAYS reference Thariq footer credit** — `inspired by Thariq Shihipar · Unreasonable Effectiveness of HTML`
11. **ALWAYS Mobile-responsive** — breakpoint <720px; tables stack; heatmaps reflow; SVG `viewBox` makes them scale
12. **ALWAYS provide source-MD provenance** in HTML footer — `Source: <vault-path-of-source-MD>`. Permits audit.
13. **ALWAYS surface visual gaps** in Phase 2 before fetching — don't WebFetch 15 image URLs without showing user the candidate list first

## Failure Modes

| Symptom | Fix |
|---|---|
| Source MD < 200 lines | Tell user: "Source too thin for interactive treatment; HTML overhead > value. Recommend send MD as-is OR expand source first." |
| User can't decide audience in Phase 0 | Default to (a) internal forward 诸葛 — most common case. Confirm. |
| WebFetch fails on 1-2 image sources | Use Wikipedia commons fallback OR convert to inline SVG illustration. Don't block on a single failed image. |
| Source has NDA content but user wants public-shareable | Two-build path: build NDA-stripped version first, then NDA-included version if explicitly authorized after release-边界 confirmation. |
| User asks "can I check on phone" | Spin tunnel per **`references/tunnel-runbook.md`**. Confirm Python + cloudflared available; install cloudflared via winget if missing. |
| Source MD uses `${variable}` placeholders that weren't resolved | Halt, surface unresolved variables to user — never ship HTML with placeholder leakage |
| SVG visualization needed but content doesn't fit any of 8 standard types | Author custom inline SVG per source spec. Add to **`references/svg-library.md`** for future reuse. |
| User wants to update HTML after source MD changed | Re-run skill. Diff vs prior HTML (Glob for prior `(C) * Interactive-*.html` for same source). Surface delta. |
| Hot-linked image 404s at view time | Browser auto-renders alt-text. Acceptable graceful degrade. If critical, swap to inline SVG. |
| Print rendering breaks (dark sections still dark) | Verify `@media print` block exists + overrides `section.dark` to white-bg. Test with Ctrl+P preview before ship. |

## Output Locations + Naming

| Source MD type | Output HTML path |
|---|---|
| **`03 Projects/<proj>/Pitches/(C) <name> 业务评估 <date>.md**` | `**03 Projects/<proj>/09 Reports/(C) <name> Interactive-<date>.html`** |
| **`03 Projects/<proj>/04 会议纪要/<name>.md**` | `**03 Projects/<proj>/09 Reports/(C) <stem> Interactive-<date>.html`** |
| **`03 Projects/<proj>/09 Reports/(C) <name> v1 致诸葛-<date>.md**` | `**03 Projects/<proj>/09 Reports/(C) <name> Interactive-<date>.html`** |
| **`04 Notes/vault-evolve/<date>.md**` (digest output) | `**04 Notes/vault-evolve/(C) Dashboard-<date>.html`** |
| Cross-project / other | **`04 Notes/Interactive Reports/(C) <name>-<date>.html`** |

Always `(C)` prefix per [[09 Rules/file-types.md]] § AI-generated.

## Cross-skill Chain

| Trigger | Hand-off |
|---|---|
| `/biz` output saved + audience = 诸葛/board | Propose `/interactive-report --source=<biz-eval>` next |
| `/meeting-note --deep` saved + forward target = 诸葛/board | Propose `/interactive-report --source=<meeting-note>` |
| `/periodic-report --biweekly` saved | Propose `/interactive-report` for the PMO 双周报 |
| `/to-internal-briefing` saved | Propose `/interactive-report` for the 1-page brief |
| User asks "let me check on phone" | Spin tunnel via **`references/tunnel-runbook.md`** |
| HTML rendered + audience = 诸葛 + 诸葛 hasn't read in 24h | Surface ping reminder in next /day-digest |

## References

All in `<vault>/.claude/skills/interactive-report/references/`:

- `design-system.md` — full color palette / typography / spacing / responsive breakpoints
- `svg-library.md` — annotated SVG snippets for 8 visualization types
- `section-archetypes.md` — semantic patterns per section type · 3 sequencing patterns (default/compact/audit) + pure-share variant
- **`pure-share-mode.md`** — 12 specific preferences when artifact is share-grade (not decision-grade) · MUST read when Phase 0 mode = (b)
- `tunnel-runbook.md` — Python http.server + cloudflared quick tunnel for phone-access workflow
- `exemplars.md` — pointer list to highest-quality past renders · v0.2 (decision-grade) + v0.5 (pure-share) gold standards

## Lineage

- **Pattern origin** — Thariq Shihipar (Anthropic Claude Code team) · ["Using Claude Code: The Unreasonable Effectiveness of HTML"](https://simonwillison.net/2026/May/8/unreasonable-effectiveness-of-html/) · examples at [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/)
- **Crystallization moment** — 2026-05-15 EPIC Summit Interactive HTML v0.1 (functional) → v0.2 (cinematic editorial + 7 SVG visualizations). {{USER_NAME}}: *"I like this level of direction. Can you package it into a skill for the future."*
- **Exemplar** — [[03 Projects/{{PROJECT_A}}/09 Reports/(C) EPIC Summit Interactive-2026-05-15]]

---

*HTML for output, MD for source-of-truth. The layer separation {{USER_NAME}} + Thariq both arrived at independently — Markdown is your knowledge base format; HTML is what crosses the boundary out to a human reader of Claude's work.*
