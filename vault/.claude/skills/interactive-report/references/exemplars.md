# Interactive Report · Exemplars

Quality baseline for the skill. When in doubt about "what should v0.x look like", open these.

## Gold standard

### EPIC Summit Interactive — 2026-05-15 v0.2

**Path**: `<vault>/03 Projects/{{PROJECT_A}}/09 Reports/(C) EPIC Summit Interactive-2026-05-15.html`

**Source MD**: **`04 会议纪要/【EPIC Games】Unreal Animation Summit-2026-05-14.md**` + companion `**01 Pitches/(C) EPIC Unreal Summit · 业务评估 2026-05-14.md`**

**Audience**: 诸葛 (郭子川) · 工作室引擎评估组 · 动画团队

**Stats**:
- 117 KB · 11 sections · 7 SVG visualizations · 11 hot-linked Wikipedia images
- Build time ~ 1 session (~2-3 hours of conversation)
- Reception: {{USER_NAME}} "very functional and similar to what I expected" (v0.1) → "I like this level of direction" (v0.2)

**Sections demonstrated**:
1. Cover (dark · cinematic hero · 5-stat strip · 概要 callout · filtered logo strip)
2. Agenda (time ribbon + speaker heatmap)
3. 5 Register C 印象 (card grid with implications)
4. **3 Studios (dark)** — trio block + radar chart + pipeline comparison SVG
5. UE 5.8 + AI (feature grid + NDA banner + AI workflow SVG + philosophy callout)
6. 6 Implications (quadrant matrix + card grid)
7. **Decision gates (dark)** — unified decision tree SVG
8. Value analysis (mechanism table + tornado chart + compounding callout + integrated table)
9. 4 Asks (Q1-Q4 cards with {{USER_NAME}}-recommend overlay)
10. **Timeline (dark)** — Gantt chart with 6 tracks + critical path band
11. Appendix (6-column grid: vault refs / wiki / OKR / public sources / community impls / NDA)

**Visual moves that earned their keep**:
- Alternating dark/light section rhythm
- Hero stats strip (¥720K basis value as a single big number anchors quantitative discussion)
- Filtered-to-white logo strip in hero (`filter: brightness(0) invert(1)`)
- Radar chart with custom polygon math (scores 6-10 mapped to pentagonal vertices)
- Quadrant matrix bubbles with `stroke-dasharray` for 期权 items (visual encoding of asymmetry)
- Decision tree with gold-gradient diamonds + path arrows
- Gantt with vertical "today" amber line + red critical path overlay band
- Tornado chart ranked top-to-bottom by sensitivity, with worst/basis/best scenario markers at bottom

**Iteration notes (v0.1 → v0.2)**:
- v0.1 used light cream + navy + blue + gold — "functional but conservative"
- v0.2 deep midnight + amber + cobalt + teal — "cinematic editorial"
- v0.2 added: speaker heatmap, radar, quadrant matrix, decision tree, sensitivity tornado, proper Gantt (the 6 new SVG vizs)
- v0.2 also restructured agenda from table → time ribbon (more visual, less listy)

## What to take from this exemplar

1. **Don't skimp on the hero** — it's the first 1.5s of the read. Stat strip + 概要 callout + logo strip = orienting the reader fast.
2. **Visualizations are not decoration** — each SVG should answer a specific question the source MD asks. If you can remove a viz and the meaning is preserved, remove it.
3. **Alternating dark/light gives rhythm** — readers fatigue on monotone backgrounds. Cinematic interludes (dark sections) at sections 3, 6, 9 = visual punctuation.
4. **Print-friendly is non-negotiable** — Ctrl+P should produce a clean white-bg version that 诸葛 can paper-read.
5. **Hot-linked images are OK** — Wikipedia commons URLs are stable + free + de-risk through alt-text graceful degrade.

## Gold standard #2 · Pure-Share Mode

### EPIC Summit Interactive — 2026-05-15 v0.7 中文本地化版 (pure-share + CN-localized, current)

**Path**: `<vault>/03 Projects/{{PROJECT_A}}/09 Reports/(C) EPIC Summit Interactive-2026-05-15.html`

**Mode**: pure-share (会议纪要分享 · 团队分享 · 无决策请示)

**Source MD**: same as v0.2, but {{USER_NAME}} edited the source MD between v0.3 and v0.4 to remove decision-grade framing (致诸葛 / Q1-Q4 asks / NDA banners) — the HTML render followed.

**Audience**: 动画团队 · 会议纪要分享 (no individual decision-maker named)

**Stats**: ~102 KB · 9 sections · 7 SVG visualizations · 3 hot-linked event images (poster + Juan stage + agenda long-image)

**Sections kept** (vs v0.2 decision-grade):
1. Cover (with 纯分享 badge in amber) — same hero structure but reframed
2. 议程与发言人 — single integrated **timetable** (11 rows, time + dot + title + speaker + coverage tag) replacing the previous time-ribbon + speaker-heatmap split
3. 4 项目组综合印象 — forced 2×2 `quad` grid (was 5 cards auto-fit in v0.2)
4. 行业兑现度 · 3 工作室 — radar + pipeline SVG kept
5. UE 5.8 + AI 工作流 — kept · MCP spotlight kept (single exception to "equal weight" rule because MCP IS the load-bearing signal)
6. Matrix demo dedicated section — kept
7. 6 对{{PROJECT_A}}的潜在价值 — kept · quadrant matrix kept
8. 量化分析 — kept WITH new 🤖 AI 自动分析 banner mandatory at top
9. Appendix · 官方议程长图 — official poster moved to end (was inline in §1 in v0.3)

**Sections dropped vs v0.2**:
- §决策门 · 统一决策树 (5-path SVG) — gone
- §4 决策请示 · Q1-Q4 ask card grid — gone
- §时间轴 · Gantt chart with 6 tracks — gone
- Speaker × dimension heatmap (技术影响 / BD / 战略路线图 / 长期价值) — folded into timetable; the 4 evaluation dimensions removed entirely
- "建议启动两条独立并行..." 概要 directive language — reframed as "两个值得团队持续关注的方向"
- "致诸葛 + 工作室引擎评估组" footer — replaced with "动画团队 · 会议纪要分享"
- 5/29 立项 / 6/15 评估 etc. time-bound milestones — gone (no decision asks → no implicit deadlines)
- 甲乙丙丁戊己 labels — modernized to A B C D E F throughout
- ⭐ 下半场 emphasis on Juan 2nd / Miles 2nd timetable rows — removed; all sessions equal weight

**Iteration moves that ratified the pattern**:
- v0.3 → v0.4: {{USER_NAME}} said `这个报告就是分享性质的` + listed specific drops (决策图 / 致诸葛 / 4 请示 / 时间轴) + the AI 自动分析 标语 add
- v0.4 → v0.5: ribbon visualization (mathematically correct) was visually rejected ("Juan 和 Miles 更偏了"); ultimately replaced with timetable list — taught the rule **"chart integrity > chart cleverness"**
- v0.5 trims: 4 综合印象 → 2×2 fixed grid · spotlight 下半场 highlighting removed · speaker heatmap removed
- v0.5 → v0.6 moves:
  - Hero subtitle `.accent` got an independent font-size clamp (`clamp(18px, 2.6vw, 28px)`) — Chinese accent inheriting h1's 32-56px was overflowing on phone (pref 13)
  - 概要 prose → 4 labeled bullets with mono left-rail keys (兑现度 / 关注方向 ① / 关注方向 ② / 最激进信号) — clearer scan on phone (pref 14)
  - Juan stage banner downgraded from full-bleed 3-line-caption-overlay → 480px centered atmospheric image with single "现场 · 氛围记录" mono caption (pref 15)
  - §8.3 复利叠加 promoted from left-border callout → cinematic dark hero block: amber-tagged 4-layer stack + radial-glow `1⁄5 – 1⁄10` payoff in serif italic (pref 16)
  - §8.2 sensitivity tornado demoted from full inline SVG → 3-card scenario strip with full chart tucked in `<details>` expandable (pref 17)
  - `F · EPIC 关系` row removed from §8.1 + §8.4 tables + quadrant chart — personal-value (NDA preview / demo / MegaGrants) doesn't belong on team-share artifacts (pref 18)
- v0.6 → v0.7 moves (latest gold standard — Chinese localization layer):
  - Full prose pass: every "cinematic / agentic / diffusion / pipeline / Storyboard / Layout / Animation / Lighting / production / final-look / re-render / sandbox" replaced with Chinese equivalent (pref 19 Tier A)
  - 21 inline `.term` tooltip widgets added on first occurrence of: MetaHuman / Niagara / Composure / Matrix Awakens / Skeletal Mesh / Direct Mesh Controls / Control Rig Physics / Animation Mixer / root motion / Crowd plugin / mass entity / LOD / USD / depth/normal/edge / gray box / MCP / Blueprint / PoC / UEFN / MegaGrants — dotted-amber underline + superscript Chinese circled digit + tap/hover popup with plain-language Chinese explanation (pref 20 inline layer)
  - § 9 · 术语注释 · GLOSSARY section added before appendix — 24 entries each with English term + Chinese name + 1-2 sentence explanation (pref 20 glossary layer)
  - Section labels localized: "§ 1 · AGENDA & SPEAKERS" → "§ 1 · 议程与发言人", §2 综合印象, §3 行业兑现度, §4 虚幻引擎 5.8 路线图 + AI 工作流, §6 对{{PROJECT_A}}的潜在价值, §8 量化分析, §9 术语注释, §10 附录
  - Hero stats English bits localized: "8 月 2026" → "2026 年 8 月", "15M 玩家" → "1500 万玩家", "AI Assistant" → "AI 助手", "Fortnite Darth Vader AI Sidekick" → "《堡垒之夜》达斯·维达 AI 伙伴"
  - Version + footer relabeled to "v0.7 中文本地化版 · 24 术语注释" (pref 21)
  - Static PNG export added (full-page screenshot via browser-harness): 968 × 24,354px, 6.8 MB, hosted at /report.png on tunnel — dual-layer footnote system means PNG still shows full glossary section, no information loss on forward

**What this exemplar teaches**:
1. Pure-share is a **distinct mode**, not "decision-grade lite" — different framing, different sections, different language register
2. Equal visual weight is a feature, not a bug — pure-share lets the reader's eye land where their own priorities draw it (one exception: load-bearing insight blocks deserve cinematic hero treatment per pref 16)
3. AI-disclaimer banner propagates with the artifact through forwards — non-negotiable on quantified content
4. Cleanliness beats cleverness — a structured table or 3-card strip can outperform a fancy SVG when the chart's reading is ambiguous
5. Image positioning is aesthetic-driven, not slot-filling — official poster moved to end because the body content already tells the story; atmospheric images get small uncaptioned treatment
6. Fixed grids for fixed counts (2×2 for exact-4) preserve the "set" gestalt that auto-fit destroys
7. **Phone-first layout check before "done"** — tunnel preview viewed on phone surfaces typography overflow + chart legibility issues that desktop hides
8. **Visual hierarchy serves the signal, not the analysis** — give visual weight to the *conclusion* (compounding payoff), subordinate the *method* (sensitivity tornado)
9. **Audit value tables for personal-vs-team rows** — rows that benefit only the author belong on a private dashboard, not on the team-share
10. **Chinese audience = Chinese-first prose + dual-layer footnotes** — inline tooltips for flow-state reading + § 术语注释 glossary for static export / forward / print. Both layers required, not either/or.
11. **Don't code-switch within noun phrases** — "cinematic 管线" reads as untranslated draft. Either fully localize ("影视镜头管线") or wrap in tooltip ("MetaHuman" with gloss). No middle ground.
12. **Export channels diversify the audience** — interactive HTML (tunnel link, phone tap), static PNG (WeChat forward), and the source MD (vault peers) all need to render the same signal. Build the report so the static export doesn't lose information.

**See also**: `pure-share-mode.md` for the 21 codified preferences.

---

## Future exemplars (to be filled)

When new interactive reports are built and approved by user, add entries here:

### [Project] [Subject] Interactive — [Date] v[N]
- Path: ...
- Mode: decision-grade / pure-share
- Source: ...
- Audience: ...
- Stats: ...
- What it teaches: ...
