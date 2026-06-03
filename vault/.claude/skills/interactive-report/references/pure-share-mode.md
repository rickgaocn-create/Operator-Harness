# Interactive Report · Pure-Share Mode

When the artifact is a **share / FYI document** (not a decision-grade ask), 21 specific preferences differ from default decision-grade mode. Crystallized from EPIC Summit Interactive v0.4 → v0.7 iteration ({{USER_NAME}}: *"这个报告就是分享性质的"* · *"great job with the interactive footnotes"*).

## When to use Pure-Share Mode

- Source is a 会议纪要分享, 行业观察, 团队 update, 出差汇报 with no decisions in flight
- Audience is **team / peers / 工作室** — not 诸葛 / 董事会 / external counterparty
- The user explicitly says "纯分享 · 无决策请示" / "不需要决策" / "这是分享性质的"
- The source MD has no `## Decision Asks` / `## 决策请示` / `## 行动项` section
- The user has dropped `致 X` framing language

## Default = Decision-Grade

Pure-share is the **opt-in mode**. Default behavior assumes decision-grade (asks + gates + timeline + asks). If unclear, ask Phase 0 question 3 explicitly:

> 这是 (a) decision-grade（含 4 个 Q1-Q4 决策请示 + 决策门 + Gantt 时间轴）OR (b) pure-share（仅分享 · 无决策请示 · 无时间轴）?

---

## 21 Pure-Share Preferences

### 1. Drop decision sections entirely

**Do NOT include** in pure-share mode:
- §决策门 / Decision Gates (unified decision tree SVG)
- §决策请示 / Decision Asks (Q1-Q4 ask cards)
- §时间轴 / Timeline (Gantt chart with milestones)
- 致 X 框架 (any audience-specific salutation)

**Why**: pure-share has no decisions in flight. These sections turn the artifact into something it isn't — invite mis-reading as "do something" when intent is "be aware of."

### 2. No directive language in 概要

**Bad (decision-grade)**:
> 建议启动两条独立并行：① 引擎迁移评估 ② AI 工作流接入路径升级

**Good (pure-share)**:
> 两个值得团队持续关注的方向：① 引擎成熟度 ② AI 工作流双轨架构

**Why**: pure-share 概要 describes observations, not recommendations. Verb tense shifts from imperative ("建议启动") to declarative ("值得关注").

### 3. AI-disclaimer banner mandatory on any quantified analysis

**Required block** at top of any 量化 / 测算 / sensitivity / cost-value section:

```html
<div class="ai-disclaimer">
  🤖 AI 自动分析 · LLM-Generated Estimates
  本节所有数字均为 AI 基于会议纪要 + 行业公开数据自动估算 · 未经财务 / 业务侧人工复核
  仅作分享时的"如果"型直觉参考 · 任何商业 / 预算决策前必须重新人工校准基准假设
</div>
```

**Why**: pure-share artifacts get re-shared. Readers downstream may not know the numbers are LLM estimates. The badge propagates the provenance with the artifact, prevents quoting these numbers as facts.

### 4. Equal visual weight across same-tier items

**Don't elevate** "strategic" rows/cards at the cost of others — unless there is a true outlier with unambiguous business case.

**Example case from v0.5**:
- Agenda timetable: Juan 2nd + Miles 2nd are the most strategically dense sessions (5.8 路线图 / AI 路线图). Decision-grade mode would mark them with ⭐ + amber bg.
- Pure-share mode: every row gets the same treatment. The TIME label + speaker + session name is the data. The reader decides what matters.

**Exception — when emphasis IS valid**: a single load-bearing item that the entire artifact pivots around (e.g., MCP card in §4 of EPIC Summit — even pure-share keeps that one elevated because the conversation literally depends on it).

**Why**: pure-share is "here's what happened · you decide what matters." Pre-weighting the read steers the reader toward the author's conclusions — that's decision-grade behavior.

### 5. Visualization integrity > visual punch

If a chart's math is correct but it visually reads as "off" / cramped / misaligned — **the chart is wrong for this data, drop it**. Don't bandaid with elevation / glow / shadows.

**Example case from v0.5**:
- Time ribbon (5-hour linear axis with bars proportional to session duration): mathematically perfect but visually the narrow bars (Juan 2 at 8% width / Miles at 7% width) read as squashed against the right edge.
- Fix attempts (elevation, gradients, ▼ markers, glow) all made it WORSE by adding optical noise.
- Final fix: **drop the ribbon entirely**, replace with a clean timetable list. Each row gets equal vertical space regardless of session duration.

**Why**: pure-share favors legibility over cleverness. A boring table that's instantly readable beats a beautiful chart that requires squinting.

### 6. Image placement aesthetic-driven, not slot-filling

Posters / photos / event imagery must **earn their position** via one of:
- **Content-semantic match** — a stage photo of Juan goes in §4 (Juan's session content), not §1
- **Cinematic edge** — full-bleed banner with overlay caption, magazine-spread style, not a floated thumbnail
- **End-positioned appendix** — when content already tells the story, the official poster / agenda image lives in a final §Appendix Photo section as supporting record

**Anti-pattern**: dropping an image in the middle of §1 because "we need something visual there."

**Why**: pure-share is reader-led. Images that don't reinforce the section they're in distract from it.

### 7. Drop sections that don't earn their keep

If source MD explicitly marks a section "不录入报告" / "FYI only" / "internal only" → **remove from HTML render entirely**, don't even include as a minimized appendix.

**Why**: pure-share artifacts often get forwarded. Every section visible should serve the read; everything else is leak risk.

### 8. Fixed grids for fixed counts

When count is exact + known, use **fixed-column grid**, not responsive auto-fit:
- 4 cards → `grid-template-columns: repeat(2, 1fr)` (forced 2×2 square)
- 6 cards → either fixed 2×3 OR 3×2; pick based on card height
- Variable count → auto-fit acceptable

```css
.card-grid.quad { grid-template-columns: repeat(2, 1fr); }
.card-grid.sextet { grid-template-columns: repeat(3, 1fr); }
@media (max-width: 720px) {
  .card-grid.quad, .card-grid.sextet { grid-template-columns: 1fr; }
}
```

**Why**: auto-fit can render the same 4 cards as 1×4 / 2×2 / 4×1 depending on viewport — destroys the "set of 4" gestalt. Fixed grids preserve the count's signal.

### 9. Modern labels over traditional Chinese enumeration

Replace `甲乙丙丁戊己` → `A B C D E F` for議题 labels, decision branches, table rows, viz bubbles, etc.

**Why**: 甲乙丙 reads as "rustic / official document" feel. ABCDEF reads as "modern internal share." {{USER_NAME}}: *"这个太土了"*.

**Exception**: keep 甲乙丙丁 if the source artifact uses it for legal / contract reasons. Otherwise default to ABCDEF.

### 10. No NDA banner when source removes NDA framing

If source MD strips NDA flags from a session's content (e.g., a closed-door 路线图预览 becomes publicly-shareable after release) → **HTML render must follow**. Don't carry over banner styling, red "INTERNAL" tags, or collapsed nda-content blocks from prior revisions.

**Why**: pure-share readers don't know the artifact's revision history. A red NDA banner on content the team explicitly released would mis-signal.

### 11. Move heavy media to end

Official agenda images / event posters / large reference shots → move to **final §Appendix section** when the body content already tells the story.

**Anti-pattern (v0.3)**: agenda 长图 embedded inside §1 above the time ribbon → users scroll past it.
**Better (v0.4+)**: official agenda 长图 in §Appendix at the very end → readers who want the source can scroll there.

### 12. Title + framing explicitly "share"

**Title pattern**: `<Event Name> · 会议纪要分享` / `<Event> · 团队分享` / `<Event> · 行业观察`

**Hero meta**: `INTERNAL · 团队分享 / 会议纪要分享 / 行业观察 · YYYY-MM-DD`

**Hero subtitle should include**: a phrase like `纯分享，无决策请示` (rendered in amber-light callout) so readers immediately see the framing.

**Why**: the framing primes the read mode. Without it, a reader trained on decision-grade memos defaults to "what's the ask" mental mode and is confused when no ask appears.

### 13. Phone-first hero typography — accent line shrinks independently

Chinese subtitle phrases below the main h1 will inherit the h1 `font-size` clamp by default. On phone widths a long subtitle (`会议纪要分享 · 行业兑现度 + AI 工作流前瞻`) wraps or overflows. Override with an independent clamp:

```css
.hero h1 .accent {
  font-size: clamp(18px, 2.6vw, 28px);
  display: block;
  margin-top: 10px;
  line-height: 1.3;
  letter-spacing: 0;
}
```

**Why**: AFK phone-first review is the primary check (tunnel → phone screenshot). If the hero subtitle line overflows or breaks badly, the first impression is broken before any content. {{USER_NAME}}: *"字体很大一行站不下请缩小"*.

**How to apply**: any block where a long localized phrase sits below an h1. Mentally check at 375-414px viewport width (iPhone) before sync.

### 14. 概要 as labeled bullets, not prose paragraph

Decision-grade 概要s run as 3-sentence prose. Pure-share 概要 works better as **3-4 labeled bullets**: mono left-rail key (兑现度 / 关注方向 ① / 关注方向 ② / 最激进信号) + 1-line value on the right.

```css
.hero-bluf ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.hero-bluf li { display: grid; grid-template-columns: 92px 1fr; gap: 14px; align-items: baseline; }
.hero-bluf li .bluf-key { font-family: var(--mono); font-size: 11px; color: var(--amber); letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }
@media (max-width: 720px) {
  .hero-bluf li { grid-template-columns: 1fr; gap: 2px; }
}
```

**Why**: Prose 概要s hide structure inside punctuation. Bullets surface "there are exactly N things to know" + let the eye scan keys first. On phone, prose wraps make the read feel longer; labeled bullets present as a checklist. {{USER_NAME}}: *"概要可以分成bullet更清晰"*.

**How to apply**: drop on mobile by stacking key above value (not squeezing). Keep keys to 4-7 chars in mono caps for visual rhythm.

### 15. Atmospheric images get small + uncaptioned treatment

When an image is included for **vibe / 氛围 / 现场记录**, not informational showcase:

- Max-width ~480px (NOT full-bleed)
- Centered (`margin: 20px auto`)
- Rounded corners + soft shadow
- Single short mono caption (e.g., "现场 · 氛围记录") or no caption
- **Drop the gradient-overlay block** that lists who / what / when / title — that's an informational-image pattern, not atmospheric

**Why**: A full-bleed gradient-overlay banner with 3 lines of metadata reads as "important showcase," primes the reader to study the image. When the image is just mood, that primes wrong. {{USER_NAME}}: *"我只是想作为一个氛围美术展示并不是想真正展示"*.

**Anti-pattern**: building one universal `.stage-banner` component and using it for both informational AND atmospheric purposes. Two different intents = two different treatments.

### 16. Load-bearing insight blocks deserve cinematic hero treatment

When a finding is **the** point of a section (e.g., compounding/multiplier effects, 复利叠加, structural insight that the whole analysis builds toward), don't render it as a left-border callout. Build a cinematic hero:

- Dark gradient background (midnight → deeper midnight)
- Top accent stripe in amber gradient (`::before` pseudo-element, 3px high, fading at edges)
- Layered stack of contributing factors (one row per layer · mono tag + label + dim sublabel · amber-tinted background)
- `＋` separators between layers (mono, dim amber)
- Centered radial-glow payoff stat in big serif italic (40-56px clamp)
- Subtitle explaining the math ("乘性叠加 · 不是 1+1+1+1 = 4，而是 ×0.5 × ×0.6 × ×0.5 × ×0.7")
- Coupling footer with chain icon (⛓) explaining ordering / dependencies

**Why**: An impact statement at the bottom of a quantitative section reading as a small callout undersells the conclusion. Pure-share readers' eyes pause on visual weight — give weight to the actual signal (the multiplier outcome), not to the chart that produced it. {{USER_NAME}}: *"应该做好视觉让它增强印象"*.

**Pattern**: `.compounding-hero` block — see EPIC Summit v0.6 §8.3 for working example.

### 17. Subordinate sensitivity / indicator charts when they aren't load-bearing

A sensitivity tornado / variance chart is *indicator data*, not conclusion data. Show the 3-scenario summary inline (worst / basis / best as compact colored chips with PoC-multiple footnote); tuck the full SVG chart inside a `<details>` expandable.

```html
<h3 style="opacity: 0.85;">8.2 量化测算</h3>
<p style="font-size: 13px;">基准 ¥720K = ¥500/h × 120 × 3 × 4h. 三档情形：</p>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; max-width: 640px;">
  <!-- 最差 ¥162K · 基准 ¥720K · 最佳 ¥1.9M as bordered chips -->
</div>

<details>
  <summary>展开 · 三变量敏感性 tornado 图</summary>
  <div class="viz" style="max-width: 640px; opacity: 0.85;">...full SVG...</div>
</details>
```

**Why**: {{USER_NAME}}: *"是一个指标性的东西，不用那么大，也不是很看得懂"*. Big-but-illegible charts force readers to choose between scrolling past or studying. A 3-chip summary delivers the actionable takeaway in 2 seconds; the chart stays available for those who want the variable-swing breakdown.

**Visual signaling**: dim the section h3 (`opacity: 0.85`) to telegraph "this is supplementary, not the headline." Keep the load-bearing insight (preference 16) at full contrast right after.

### 18. Audit value tables for personal-vs-team rows

Pure-share value/impact tables should pass an audit before render: **is this value to the team or to me personally?** If the row only matters to the author (personal NDA channel, individual relationships, personal future option, individual BD pipeline), remove it. Don't fold it into "long-tail / 中长期" — just drop the row.

**Trigger phrases that indicate a personal-value row**:
- "持续 NDA 预览 / demo / MegaGrants"
- "长期 access" / "长期 NDA 通路"
- "个人 BD 价值" / "我的长期生态位"
- "未来 X 时可申请"（when X is author-specific opportunity, not team)

**Why**: {{USER_NAME}}: *"EPIC关系这里 持续 NDA 预览 / demo / MegaGrants不是很有团队的意义，是我的个人意义，对于分享没有很大价值所以删除"*. Personal value rows mixed into team tables (a) inflate the team's apparent surface area, (b) hint at strategy the team can't act on, and (c) blur ownership of follow-up.

**How to apply**: when source MD has a value-mechanism table, scan each row's 受益方 column. If 受益方 reads as the author alone → drop from pure-share render. Same row may legitimately exist in author's private dashboard, just not on the shared artifact. Also remove the corresponding quadrant-chart bubble if one exists.

**Precedent**: EPIC Summit v0.5 had `F · EPIC 关系` row in §8.1 + §8.4 + a quadrant bubble. v0.6 removed all three after audit (matched "long-tail / 个人价值" trigger).

### 19. Chinese audience → localize prose + retain technical English with tooltips

When the audience is a general Chinese reader (动画团队 / 团队分享 / 行业观察 / 非 AI 工程师群体), default to **Chinese-localized prose with selective English-with-tooltips** rather than mixed CN/EN code-switching.

**Three-tier strategy** (matches what {{USER_NAME}} ratified in v0.7):

| Tier | Rule | Examples |
|---|---|---|
| **Tier A · Localize inline** | Term has a clean Chinese equivalent that doesn't lose precision → replace English entirely | "cinematic" → "影视镜头", "pipeline" → "制作管线", "agentic" → "AI 代理式", "diffusion model" → "扩散模型", "Storyboard / Layout / Animation / Lighting" → "分镜 / 场景布局 / 动画 / 灯光" |
| **Tier B · English + tooltip on first mention** | Term is a proper noun / API / branded tech that should stay in English for searchability, but reader needs the gloss | "MetaHuman", "Niagara", "Composure", "Matrix Awakens", "USD（Universal Scene Description）" |
| **Tier C · Acronym + Chinese expansion + tooltip** | Common technical acronyms that the reader genuinely doesn't know | "MCP（模型上下文协议）", "PoC（概念验证）", "UEFN", "MegaGrants", "LOD" |

**Anti-patterns to delete**:
- "cinematic 管线" / "agentic 工作流" / "diffusion 模型" — mixed CN/EN within a noun phrase reads as untranslated draft
- "AI agent" / "MCP server" / "MCP 协议" repeated dozens of times — first mention has tooltip, subsequent mentions should use localized Chinese ("AI 代理 / MCP 服务端")
- "production / final-look / overlapping / re-render / context / scene / hero shot / sandbox" — English seasoning words in Chinese prose. All have natural Chinese equivalents.

**Why**: {{USER_NAME}}: *"there is too much English And phrases that are hard to understand such as MCP that are very AI specific. The audience will be a general audience that is Chinese and needs footnotes to understand certain language"*. Code-switching prose makes the reader stop on every English fragment to translate — kills flow. Pure-Chinese prose with strategic English-with-tooltips lets the reader stay in their native language while preserving access to the precise English term when they want it.

### 20. Interactive tooltip + § 术语注释 glossary (the dual-layer footnote)

**Implementation pattern** ({{USER_NAME}} ratified in v0.7 — *"great job with the interactive footnotes"*):

```html
<!-- inline: dotted-underlined Chinese term with superscript number + tap/hover popup -->
<span class="term" tabindex="0">MCP<sup>⑨</sup>
  <span class="def">
    <strong>MCP = Model Context Protocol（模型上下文协议）</strong> · Anthropic 2024 年提出的开放标准，
    让 AI 助手能直接操作其他软件。可理解为"AI 与软件之间的通用接口"。
  </span>
</span>

<!-- glossary section at end · § 术语注释 -->
<section id="glossary">
  <div class="section-num">§ N · 术语注释 · GLOSSARY</div>
  <div class="glossary">
    <div class="glossary-item">
      <div class="glossary-term">⑨ MCP<span class="cn">Model Context Protocol · 模型上下文协议</span></div>
      <div class="glossary-def">Anthropic 2024 年提出的开放标准...（完整版本）</div>
    </div>
  </div>
</section>
```

**Required CSS** (full block in `design-system.md` should pick this up):
- `.term` — dotted-amber underline + relative positioning + `cursor: help` + `outline: none`
- `.term .def` — absolute-positioned popup, dark background, 280px wide, opacity transition
- `.term:hover .def`, `.term:focus .def`, `.term:focus-within .def` — show
- `tabindex="0"` on `.term` makes it focusable, which is what enables phone tap-to-show
- Mobile: `.def { width: 240px; font-size: 12px }` @ ≤720px

**Dual-layer logic — both layers required**:
1. **Inline tooltip** — for the reader scrolling the body; doesn't require breaking flow
2. **§ 术语注释 glossary at end** — for the reader who: (a) prints to PDF (tooltips invisible), (b) exports to PNG (tooltips invisible), (c) wants to skim all terms at once, (d) forwards the artifact downstream where the recipient may not know to tap

If you only build the inline tooltips you fail use cases (a)-(d). If you only build the glossary section you fail flow-state reading. Both layers complement.

**First-occurrence rule**: tooltip on first appearance only. Subsequent uses of the same term render plain (no underline, no superscript) — context is already established.

**Numbering**: Chinese circled digits (①②③…⑩⑪⑫…⑳㉑㉒㉓㉔). Cleaner than `[1]` or `(1)` in Chinese typography. Numbering is shared between inline tooltip and glossary so reader can cross-reference.

**Why**: covers both rich-render (interactive HTML) AND static-render (PNG export, WeChat forward, PDF print) without compromise. {{USER_NAME}}'s v0.7 PNG export shows the glossary as a full section in the image — readers who only get the static image still see every term explained.

### 21. Version label includes "中文本地化版" tag for localized variants

When a report has been localized for Chinese audience following preferences 19-20, **mark it in the title + hero meta**:

- Title: `<Event Name> · 会议纪要分享 · v0.7 中文本地化版`
- Hero meta: `EPIC GAMES · 会议纪要分享 · YYYY-MM-DD · v0.7 中文本地化版`
- Footer: `Generated by Claude · YYYY-MM-DD · v0.7 (中文本地化版 · N 术语注释) · ...`

**Why**: pure-share artifacts get forwarded. The label tells downstream readers (a) this is the localized variant — there may be an English original; (b) it includes structured glossary support — they can scroll to §术语注释; (c) the version number gives the artifact a verifiable identity for "did you see the latest one?" conversations.

**When to skip the tag**: if the source MD is already Chinese-native and the report has no English-with-tooltips at all (no Tier B/C terms), don't tag. The label is for artifacts that consciously chose Chinese-first over CN/EN mixed.

---

## Pure-Share Section Sequence (8 sections vs decision-grade 11)

| § | Pure-Share | Decision-Grade |
|---|---|---|
| 1 | Cover (with 纯分享 badge) | Cover (with 致 X) |
| 2 | Agenda + Speakers (combined timetable) | Agenda time ribbon · Speaker heatmap |
| 3 | N 项目组综合印象 (2×2 if =4, 2×3 if =6) | 5 takeaways |
| 4 | Industry / Validation block | Industry / Validation block |
| 5 | Roadmap / Content body | Roadmap (with NDA banner if applicable) |
| 6 | Major Moment / Spotlight (e.g., Matrix demo) | 6 implications + quadrant matrix |
| 7 | N 潜在价值 (quadrant matrix optional) | **决策门** (unified decision tree) |
| — | — | §8 价值评估 (sensitivity tornado) |
| — | — | §9 决策请示 (Q1-Q4 asks) |
| — | — | §10 时间轴 (Gantt) |
| 8 | 量化分析 (with AI-disclaimer banner) | (§8 with no banner) |
| 9 | Appendix · 官方议程长图 / 源材料 (optional) | §11 Appendix · refs + NDA disclaimer |

Pure-share = 7-9 sections · decision-grade = 10-11 sections.

---

## Worked Example

**EPIC Summit Interactive v0.5** = pure-share gold standard.

Path: `<vault>/03 Projects/{{PROJECT_A}}/09 Reports/(C) EPIC Summit Interactive-2026-05-15.html`

**Sections in v0.5**:
1. Cover · hero + 概要 + poster + logo strip · 纯分享 framing
2. 议程与发言人 · single integrated timetable (11 rows, time + dot + title + speaker + coverage tag)
3. 4 项目组综合印象 · forced 2×2 quad grid
4. 行业兑现度 · 三家好莱坞工作室 (radar + pipeline SVG)
5. UE 5.8 + AI 工作流 · feature grid + MCP spotlight card + AI workflow SVG + Juan stage photo banner
6. Matrix demo · time acceleration chart + 10-step workflow table + use cases
7. 6 对{{PROJECT_A}}的潜在价值 · quadrant matrix + 6 cards
8. 量化分析 · 🤖 AI 自动分析 banner + value mechanism + sensitivity tornado + compounding callout
9. Appendix · 官方议程长图

**Removed in pure-share mode (vs v0.2 decision-grade)**:
- §决策门 / Decision Gates
- §决策请示 / 4 Asks Q1-Q4
- §时间轴 / Gantt timeline
- Speaker × dimension heatmap (BD/技术影响/战略路线图/长期价值)
- Decision-grade 概要 wording ("建议启动")

**Visual moves earned its keep**:
- Timetable replacing ribbon — clean read
- 2×2 quad grid for §3 — preserves "set of 4" gestalt
- AI-disclaimer banner on §8 — provenance propagates
- Juan stage photo as §4 banner — content-semantic placement
- Official poster in hero — earns position via "this is what we attended"
- Agenda long-image in §Appendix — supporting record without clogging body

---

## Anti-Patterns to Avoid

- ❌ Mixing decision asks into a pure-share artifact ("just one quick question for you")
- ❌ Carrying over Q1-Q4 asks card grid even after removing the section header
- ❌ Time-bound milestones ("5/29 立项 / 6/15 评估通过") in a doc with no decision asks → these create implicit commitments
- ❌ Auto-fit grids on exact-count card sets → layout becomes brittle
- ❌ Decorative SVG charts with no signal density → just text/table the data
- ❌ NDA red banners on content that's been declassified by the source MD
- ❌ "战略级 · 必须押注" / "强力推进信号" / "立即推进" language → reads as recommendation
- ❌ Footer that names individual decision-makers ("致 X + 工作室引擎评估组 + 动画团队")

---

*Pure-share isn't "less serious" — it's a different contract with the reader. The contract is: I show you what happened, you decide what to do.*
