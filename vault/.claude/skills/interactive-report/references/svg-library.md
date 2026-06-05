# Interactive Report · SVG Visualization Library

8 reusable visualization patterns. Crystallized from EPIC Summit v0.2.

Each pattern includes: **purpose** · **when to use** · **viewBox** · **structural skeleton** · **data shape it needs from source MD**.

For full working examples, see `<vault>/03 Projects/{{PROJECT_A}}/09 Reports/(C) EPIC Summit Interactive-2026-05-15.html` (gold-standard exemplar).

---

## 1. Time Ribbon (for event/agenda)

**When**: source has a time-ordered agenda with NDA / public segments mixed.

**Data needed**: array of `{start_minutes, end_minutes, label, type: public|nda|gap}`

**ViewBox**: variable (HTML div with absolute positioning, not SVG — uses CSS for the band itself + SVG markers if needed)

**Structural pattern**:
```html
<div class="time-ribbon">
  <!-- top markers -->
  <span class="time-marker" style="left: 0%;">13:30</span>
  <span class="time-marker" style="left: 16%;">14:50</span>
  ...
  <div class="time-ribbon-track">
    <div class="time-block public" style="left: 0%; width: 16%;">开场 · UEFN · Juan 1st</div>
    <div class="time-block gap" style="left: 16%; width: 4%;">茶歇</div>
    <div class="time-block public" style="left: 20%; width: 12.5%;">Sony · KPDH</div>
    <div class="time-block nda" style="left: 65%; width: 9%;">🔒 NDA · 5.8 路线图</div>
    ...
  </div>
  <div class="time-legend">...</div>
</div>
```

**Conversion math**: minutes-from-start / total-minutes × 100% = `left` percent. Use a fixed start (e.g., 13:30) and end (e.g., 21:30) for the ribbon, anchor positions relative.

**Color**: `.public`=cobalt, `.nda`=danger, `.gap`=faint-gray.

---

## 2. Speaker / Actor Heatmap

**When**: source has N actors (speakers/partners/competitors) × M dimensions to compare.

**Data needed**: per actor, score 0-3 per dimension (or NDA marker).

**ViewBox**: HTML CSS grid (not SVG — semantic + accessible)

**Structural pattern**:
```html
<div class="speaker-heatmap">
  <!-- header row -->
  <div class="heatmap-cell header"></div>
  <div class="heatmap-cell header">技术影响</div>
  <div class="heatmap-cell header">BD / 关系</div>
  <div class="heatmap-cell header">战略路线图</div>
  <div class="heatmap-cell header">长期价值</div>

  <!-- per-speaker row -->
  <div class="heatmap-cell speaker">Juan S. Gomez<div class="role">全球产品组</div></div>
  <div class="heatmap-cell score-3" data-axis="技术">极高</div>
  <div class="heatmap-cell score-2" data-axis="BD">中</div>
  <div class="heatmap-cell score-nda" data-axis="路线图">NDA</div>
  <div class="heatmap-cell score-3" data-axis="长期">极高</div>
  ...
</div>
```

**Score classes** (gradient blue):
- `score-0` — light gray, "—"
- `score-1` — pale blue (#dbeafe), "低"
- `score-2` — medium blue (#93c5fd), "中"
- `score-3` — strong blue (#3b82f6, white text), "极高"
- `score-nda` — red border + bg, "NDA"

**Responsive**: <720px collapses to single column with per-cell `data-axis` label.

---

## 3. Radar / Spider Chart (multi-actor comparison)

**When**: 2-4 actors × 5-7 dimensions, comparative profile.

**ViewBox**: `0 0 720 460` (wide enough for legend)

**Math**: for each axis at angle θ from top (clockwise), score 0-10 maps to radius 0-180. Coordinates from center (360, 230):
- angle 0° (top): `x = 0, y = -score*18`
- angle 72° (top-right): `x = sin(72°)*score*18, y = -cos(72°)*score*18 = 0.951*r, -0.309*r`
- angle 144° (bottom-right): `0.588*r, 0.809*r`
- angle 216° (bottom-left): `-0.588*r, 0.809*r`
- angle 288° (top-left): `-0.951*r, -0.309*r`

For score 10 (r=180): top=`(0,-180)` · TR=`(171,-56)` · BR=`(106,146)` · BL=`(-106,146)` · TL=`(-171,-56)`

**Structural pattern**:
```svg
<svg viewBox="0 0 720 460">
  <g transform="translate(360, 230)">
    <!-- concentric pentagons (grid lines for 2, 4, 6, 8, 10) -->
    <polygon points="0,-180 171,-56 106,146 -106,146 -171,-56" fill="none" stroke="rgba(255,255,255,0.12)"/>
    <polygon points="0,-144 137,-44 85,117 -85,117 -137,-44" fill="none" stroke="rgba(255,255,255,0.1)"/>
    ...

    <!-- axes -->
    <line x1="0" y1="0" x2="0" y2="-180" stroke="rgba(255,255,255,0.15)"/>
    ...

    <!-- axis labels -->
    <text x="0" y="-195" font-size="12" fill="rgba(255,255,255,0.7)" text-anchor="middle">Cinematic 品质</text>
    <text x="190" y="-50">管线成熟度</text>
    ...

    <!-- Actor 1 polygon (scores 9,9,7,9,6) -->
    <polygon points="0,-162 138,-45 67,93 -95,131 -103,-34" fill="rgba(245, 158, 11, 0.25)" stroke="rgb(245, 158, 11)" stroke-width="2"/>
    <!-- vertices as circles for visibility -->
    <circle cx="0" cy="-162" r="4" fill="rgb(245, 158, 11)"/>
    ...

    <!-- Actor 2, 3 with different colors -->
  </g>

  <!-- legend top-right -->
  <g transform="translate(540, 50)">
    <rect width="160" height="100" rx="6" fill="rgba(0,0,0,0.4)"/>
    <circle cx="14" cy="22" r="6" fill="rgb(245, 158, 11)"/>
    <text x="28" y="26" fill="white">Actor 1</text>
    ...
  </g>
</svg>
```

**Color assignment**: amber (1st/featured), cobalt (2nd), teal ({{ORG_B}}), magenta (4th).

---

## 4. Quadrant Matrix (cost vs value bubble chart)

**When**: 4-10 items plotted on (effort × value) axes, with bubble size = magnitude.

**ViewBox**: `0 0 800 480`

**Layout**: chart area 80-740 × 40-420. Center cross at (410, 230) splits into 4 quadrants:
- Top-left: high-value, low-effort — "立即推进"
- Top-right: high-value, high-effort — "战略大赌"
- Bottom-left: low-value, low-effort — "顺手做"
- Bottom-right: low-value, high-effort — "避开"

**Structural pattern**:
```svg
<svg viewBox="0 0 800 480">
  <!-- bg gradient -->
  <rect x="80" y="40" width="660" height="380" fill="url(#quad-bg)" rx="8"/>

  <!-- axis lines (dashed cross) -->
  <line x1="80" y1="230" x2="740" y2="230" stroke="#cbd5e1" stroke-dasharray="4,4"/>
  <line x1="410" y1="40" x2="410" y2="420" stroke="#cbd5e1" stroke-dasharray="4,4"/>

  <!-- quadrant labels (subtle) -->
  <text x="245" y="68" font-size="11" fill="#94a3b8" text-anchor="middle" font-weight="600">高价值 · 低投入 — 立即推进</text>
  <text x="575" y="68">高价值 · 高投入 — 战略大赌</text>
  ...

  <!-- axis labels + ticks -->
  <text x="80" y="446" font-family="ui-monospace" font-size="10" text-anchor="middle">¥0</text>
  <text x="245" y="446">¥30K</text>
  <text x="410" y="446">¥120K</text>
  <text x="575" y="446">¥300K+</text>
  <text x="410" y="468" font-size="12" text-anchor="middle" font-weight="700">投入成本 →</text>
  <text x="68" y="44" text-anchor="end" font-weight="700">↑ 战略价值</text>

  <!-- Bubbles (radius=magnitude*20, position based on effort/value coords) -->
  <g>
    <circle cx="600" cy="100" r="42" fill="rgba(245, 158, 11, 0.4)" stroke="#f59e0b" stroke-width="2"/>
    <text x="600" y="93" font-size="20" text-anchor="middle" font-weight="800">甲</text>
    <text x="600" y="111" font-size="11" text-anchor="middle">引擎迁移</text>
  </g>
  <g>
    <circle cx="250" cy="140" r="48" fill="rgba(13, 148, 136, 0.45)" stroke="#0d9488" stroke-width="3"/>
    <text x="250" y="135" font-size="22" text-anchor="middle" font-weight="800">乙</text>
    <text x="250" y="155">MetaHuman</text>
    <text x="250" y="168" font-size="10">★ 立即</text>
  </g>
  ...
  <!-- Dashed-border bubble for option/期权 items -->
  <circle cx="115" cy="130" r="38" fill="rgba(190, 24, 93, 0.3)" stroke="#be185d" stroke-width="2" stroke-dasharray="6,3"/>

  <!-- annotations -->
  <text x="295" y="135" font-family="ui-monospace" font-size="10" fill="#0d9488" font-weight="600">← 最高 ROI</text>
</svg>
```

**Color**: by recommendation strength — teal = recommended立即, amber = strategic-bet, magenta-dashed = option, cobalt = standard.

---

## 5. Unified Decision Tree

**When**: 3-7 parallel decision tracks each with 1-4 gates ending in outcomes.

**ViewBox**: `0 0 900 620`

**Structural pattern**:
```svg
<svg viewBox="0 0 900 620">
  <defs>
    <radialGradient id="diamond-gold">
      <stop offset="0%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#d97706"/>
    </radialGradient>
    <marker id="tree-arr" markerWidth="8" markerHeight="8" refX="7" refY="2.5" orient="auto">
      <polygon points="0 0, 8 2.5, 0 5" fill="rgba(255,255,255,0.5)"/>
    </marker>
  </defs>

  <!-- Root node -->
  <g transform="translate(380, 20)">
    <rect width="140" height="46" rx="8" fill="rgba(245, 158, 11, 0.25)" stroke="#f59e0b" stroke-width="2"/>
    <text x="70" y="22" font-family="ui-monospace" font-size="10" fill="#fbbf24" text-anchor="middle" font-weight="700">2026-05-15</text>
    <text x="70" y="38" font-size="13" text-anchor="middle" font-weight="700" fill="white">今天 · 起点</text>
  </g>

  <!-- Branch lines from root to track headers (5 tracks) -->
  <path d="M 450,66 L 100,120" stroke="rgba(255,255,255,0.3)" fill="none"/>
  <path d="M 450,66 L 280,120" stroke="rgba(255,255,255,0.3)" fill="none"/>
  ...

  <!-- Track header (5 across) -->
  <g transform="translate(30, 120)">
    <rect width="140" height="42" rx="8" fill="rgba(13, 148, 136, 0.25)" stroke="#0d9488" stroke-width="2"/>
    <text x="70" y="20" text-anchor="middle" fill="white" font-weight="700">议题乙</text>
    <text x="70" y="34" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.7)">MetaHuman ★</text>
  </g>
  ...

  <!-- Gate diamonds (gold) - sized 100x60 -->
  <g transform="translate(50, 200)">
    <polygon points="50,0 100,30 50,60 0,30" fill="url(#diamond-gold)" stroke="#fbbf24" stroke-width="2"/>
    <text x="50" y="28" font-family="ui-monospace" font-size="9" text-anchor="middle" font-weight="700" fill="#0f172a">5/29 前</text>
    <text x="50" y="40" font-size="9" text-anchor="middle" font-weight="600" fill="#0f172a">PoC 立项</text>
  </g>

  <!-- Outcome leaf nodes (green rectangles) -->
  <g transform="translate(30, 380)">
    <rect width="140" height="50" rx="6" fill="rgba(16, 185, 129, 0.25)" stroke="#10b981" stroke-width="2"/>
    <text x="70" y="22" font-size="11" text-anchor="middle" font-weight="700" fill="white">通过 → 二测接入</text>
    <text x="70" y="40" font-size="9" text-anchor="middle" fill="rgba(255,255,255,0.7)">≥ 50% 时间节省</text>
  </g>

  <!-- Dashed paths for期权 / observation tracks -->
  <line x1="620" y1="162" x2="620" y2="200" stroke="rgba(255,255,255,0.3)" stroke-dasharray="4,3" marker-end="url(#tree-arr)"/>

  <!-- Legend at bottom -->
  <g transform="translate(20, 570)">
    <polygon points="0,8 16,16 0,24 -16,16" fill="url(#diamond-gold)" transform="translate(16,0)"/>
    <text x="42" y="22" font-size="11" fill="rgba(255,255,255,0.7)">决策门</text>
    ...
  </g>
</svg>
```

**Color**: gold diamond = decision gate; teal rect = recommended path; green rect = milestone; magenta dashed = option/observation; gray = killed.

---

## 6. Sensitivity Tornado Chart

**When**: quantified estimate with 3-6 variables, each with low/high swing.

**ViewBox**: `0 0 800 340`

**Layout**: center line at x=400 represents basis value. Bars extend left (downside) and right (upside) by variable's swing. Ranked by sensitivity (largest swing on top).

**Math**: scale each variable's swing relative to total displayable range. If max swing is ±¥360K and chart width = 520 (260 each side), then ¥360K = 260px, ¥288K ≈ 208px, etc.

**Structural pattern**:
```svg
<svg viewBox="0 0 800 340">
  <!-- center axis (basis value) -->
  <line x1="400" y1="40" x2="400" y2="310" stroke="#64748b" stroke-width="2"/>
  <text x="400" y="26" font-family="ui-monospace" font-size="11" text-anchor="middle" font-weight="700">¥720K (基准)</text>

  <!-- ticks below -->
  <text x="140" y="328" font-family="ui-monospace" font-size="10" text-anchor="middle">¥360K</text>
  <text x="270" y="328">¥540K</text>
  <text x="400" y="328">¥720K</text>
  <text x="530" y="328">¥900K</text>
  <text x="660" y="328">¥1.08M</text>

  <!-- Variable 1 (most sensitive, top): 镜头数 ±¥360K -->
  <g transform="translate(0, 60)">
    <text x="20" y="22" font-size="13" font-weight="700">镜头数</text>
    <text x="20" y="38" font-size="11" fill="#64748b">60 ↔ 180</text>
    <rect x="140" y="10" width="260" height="32" rx="4" fill="#fee2e2" stroke="#dc2626"/>
    <text x="270" y="32" font-family="ui-monospace" font-size="11" fill="#991b1b" text-anchor="middle" font-weight="700">−¥360K</text>
    <rect x="400" y="10" width="260" height="32" rx="4" fill="#d1fae5" stroke="#059669"/>
    <text x="530" y="32" font-family="ui-monospace" font-size="11" fill="#065f46" text-anchor="middle" font-weight="700">+¥360K</text>
    <text x="700" y="32" font-size="11" font-weight="700">最敏感 ⓘ</text>
  </g>
  <!-- Variable 2, 3 below, ranked by swing size -->
  ...

  <!-- Three scenarios at bottom: worst / basis / best -->
  <g transform="translate(0, 270)">
    <line x1="140" y1="10" x2="140" y2="30" stroke="#dc2626" stroke-width="3"/>
    <text x="140" y="46" font-family="ui-monospace" font-size="10" fill="#991b1b" text-anchor="middle" font-weight="700">¥162K</text>
    <text x="140" y="60" font-size="10" fill="#991b1b" text-anchor="middle">最差</text>
    ...
  </g>
</svg>
```

**Color**: red bar = downside, green bar = upside, intensity matches sensitivity rank.

---

## 7. Gantt Timeline

**When**: multi-track schedule with milestones + duration bars.

**ViewBox**: `0 0 940 540` (wide for date axis + tracks)

**Layout**:
- Date axis at top (x=160 to x=900) — left side labels
- Track labels right-aligned at x=150
- Bars positioned by date (linear mapping)
- Diamond markers for decision gates (gold)
- "Today" marker as vertical line in amber

**Date-to-x conversion**: `x = 160 + (date_offset_days / total_days) * 740`. For 5/15 → 9/30 (138 days):
- 5/15 → 160
- 5/22 → 197
- 5/29 → 234
- 6/15 → 251... actually compute properly: (7 / 138) * 740 = 37.5

Simpler manual mapping when dates are unevenly spaced — just place by visual proportion (5/15 = 160, 5/22 = 230, 5/29 = 300, 6/15 = 400, 6/30 = 500, 7/15 = 600, 8/1 = 700, 8/30 = 800, 9/30 = 900).

**Structural pattern**:
```svg
<svg viewBox="0 0 940 540">
  <!-- Date axis + vertical gridlines -->
  <line x1="160" y1="40" x2="900" y2="40" stroke="rgba(255,255,255,0.3)"/>
  <text x="160" y="28" font-family="ui-monospace" font-size="11" text-anchor="middle">5/15</text>
  <line x1="160" y1="40" x2="160" y2="500" stroke="rgba(255,255,255,0.08)" stroke-dasharray="2,3"/>
  ...

  <!-- TRACK: 戊 (top, fastest action) -->
  <text x="150" y="76" text-anchor="end" font-weight="700" fill="white">戊 · AI 评估</text>
  <text x="150" y="90" text-anchor="end" font-size="10" fill="rgba(255,255,255,0.5)">3 维度评估卡</text>
  <rect x="160" y="64" width="740" height="22" rx="4" fill="rgba(13, 148, 136, 0.35)" stroke="#0d9488"/>
  <polygon points="225,75 235,67 235,83" fill="#fbbf24"/>
  <text x="240" y="78" font-family="ui-monospace" font-size="10" fill="white">5/22 入卡</text>

  <!-- TRACK: 乙 (PoC + 接入) -->
  <text x="150" y="124" text-anchor="end" font-weight="700" fill="white">乙 · MetaHuman</text>
  <polygon points="290,123 300,115 300,131" fill="#fbbf24"/>
  <text x="295" y="125" font-family="ui-monospace" font-size="9" fill="white">5/29</text>
  <rect x="300" y="116" width="100" height="20" rx="4" fill="rgba(245, 158, 11, 0.45)" stroke="#f59e0b"/>
  <text x="350" y="130" font-size="10" text-anchor="middle" font-weight="600" fill="white">PoC 1 周</text>
  <rect x="405" y="116" width="490" height="20" rx="4" fill="rgba(13, 148, 136, 0.35)" stroke="#0d9488"/>
  ...

  <!-- "Today" marker (full-height amber line) -->
  <line x1="160" y1="40" x2="160" y2="500" stroke="#fbbf24" stroke-width="2"/>
  <text x="160" y="478" font-family="ui-monospace" font-size="10" fill="#fbbf24" text-anchor="middle" font-weight="700">今天</text>

  <!-- Critical path overlay band -->
  <rect x="290" y="356" width="220" height="14" rx="2" fill="rgba(220, 38, 38, 0.4)" stroke="#dc2626"/>
  <text x="400" y="367" font-size="10" text-anchor="middle" font-weight="700" fill="white">关键路径 5/29 → 6/30</text>

  <!-- Legend -->
  <g transform="translate(20, 420)">
    <polygon points="14,28 24,20 24,36" fill="#fbbf24"/>
    <text x="34" y="32" font-size="11" fill="rgba(255,255,255,0.8)">决策门</text>
    ...
  </g>
</svg>
```

**Color**: bar fill = recommended track color (teal / amber / cobalt / magenta-dashed), gold diamond = gate, red overlay = critical path.

---

## 8. Pipeline Comparison (before vs after)

**When**: workflow paradigm shift — old vs new.

**ViewBox**: `0 0 900 340`

**Structure**: two horizontal rows of boxes. Old (top) in red-toned, new (bottom) in green-toned.

```svg
<svg viewBox="0 0 900 340">
  <defs>
    <marker id="arr-red" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#dc2626"/>
    </marker>
  </defs>

  <!-- Title 1 (old) -->
  <text x="20" y="36" font-family="ui-monospace" font-size="13" fill="rgba(255,255,255,0.55)" font-weight="700">传统 CG 管线 · 串行 · 月级周期</text>

  <!-- Old row: chain of red boxes with arrows -->
  <g transform="translate(20, 56)">
    <rect x="0" y="0" width="115" height="42" rx="6" fill="rgba(220, 38, 38, 0.18)" stroke="#dc2626"/>
    <text x="57" y="26" font-size="12" fill="white" text-anchor="middle" font-weight="600">Script</text>
    ...
    <path d="M 115,21 L 130,21" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arr-red)"/>
    ...
  </g>
  <text x="20" y="130" font-size="11" fill="rgba(252, 165, 165, 0.85)" font-style="italic">导演 review 在最后 · 返工成本极高</text>

  <!-- divider -->
  <line x1="20" y1="160" x2="880" y2="160" stroke="rgba(255,255,255,0.15)" stroke-dasharray="4,4"/>

  <!-- Title 2 (new) -->
  <text x="20" y="190" font-family="ui-monospace" font-size="13" fill="rgba(255,255,255,0.55)" font-weight="700">UE 5 管线 · 并行 + overlapping · 周/天级</text>

  <!-- New: single long bar showing "all parallel" -->
  <g transform="translate(20, 210)">
    <rect x="0" y="0" width="860" height="42" rx="6" fill="rgba(13, 148, 136, 0.25)" stroke="#0d9488" stroke-width="1.5"/>
    <text x="430" y="26" font-size="13" fill="white" text-anchor="middle" font-weight="700">所有步骤并行 + overlapping</text>
  </g>

  <!-- New: parallel sub-boxes showing the steps that overlap -->
  <g transform="translate(20, 262)">
    <rect x="0" y="0" width="210" height="42" rx="6" fill="rgba(255,255,255,0.08)" stroke="#0d9488"/>
    <text x="105" y="20" font-size="11" fill="rgba(255,255,255,0.85)" text-anchor="middle">Layout</text>
    <text x="105" y="34" font-size="10" fill="rgba(13, 148, 136, 0.95)" text-anchor="middle" font-weight="600">≈ final look</text>
    ...
  </g>
  <text x="20" y="325" font-size="11" fill="rgba(110, 231, 183, 0.95)" font-style="italic">决策前置 · 返工率结构性下降</text>
</svg>
```

**Color**: red-tone = old/painful, teal/green = new/improved.

---

## 9. Workflow / Process Diagram (multi-step with mixed actors)

**When**: 5-10 step process with color-coded "who/what" per step (human vs AI vs system).

**ViewBox**: `0 0 900 380`

**Structure**: boxes arranged in 2 rows. Box color encodes actor type. Arrows between boxes.

```svg
<svg viewBox="0 0 900 380">
  <defs>
    <marker id="arr2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#2563eb"/>
    </marker>
  </defs>

  <!-- Step 1 (UE/human - blue) -->
  <g transform="translate(20, 20)">
    <rect width="190" height="84" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
    <text x="95" y="26" font-family="ui-monospace" font-size="10" fill="#1e40af" text-anchor="middle" font-weight="700">STEP 1</text>
    <text x="95" y="48" font-size="14" fill="#0f172a" text-anchor="middle" font-weight="700">Reference 图像</text>
    <text x="95" y="66" font-size="11" fill="#64748b" text-anchor="middle">"hospital interior"</text>
    <text x="95" y="78" font-size="11" fill="#64748b" text-anchor="middle">艺术家定方向</text>
  </g>

  <!-- Arrow to step 2 -->
  <path d="M 210,62 L 240,62" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arr2)"/>

  <!-- Step 4 (AI - amber) -->
  <g transform="translate(686, 20)">
    <rect width="190" height="84" rx="10" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
    <text x="95" y="26" font-family="ui-monospace" font-size="10" fill="#92400e" text-anchor="middle" font-weight="700">STEP 4 · AI</text>
    <text x="95" y="48" font-size="14" font-weight="700" text-anchor="middle">AI 风格帧</text>
    ...
  </g>

  <!-- L-shaped arrow wrapping to row 2 -->
  <path d="M 780,104 L 780,150 L 116,150 L 116,200" stroke="#2563eb" stroke-width="1.5" fill="none" marker-end="url(#arr2)"/>

  <!-- Final outcome (green) -->
  <g transform="translate(686, 200)">
    <rect width="190" height="84" rx="10" fill="#d1fae5" stroke="#059669" stroke-width="2"/>
    <text x="95" y="26" font-family="ui-monospace" font-size="10" fill="#065f46" text-anchor="middle" font-weight="700">最终</text>
    <text x="95" y="48" font-size="14" fill="#065f46" text-anchor="middle" font-weight="700">Production-grade</text>
    ...
  </g>

  <!-- Legend below -->
  <g transform="translate(20, 310)">
    <rect x="0" y="0" width="20" height="20" rx="4" fill="#dbeafe" stroke="#2563eb"/>
    <text x="30" y="14" font-size="12">UE / 艺术家工作</text>
    <rect x="160" y="0" width="20" height="20" rx="4" fill="#fef3c7" stroke="#d97706"/>
    <text x="190" y="14">AI 加速</text>
    <rect x="280" y="0" width="20" height="20" rx="4" fill="#d1fae5" stroke="#059669"/>
    <text x="310" y="14">production-grade 输出</text>
  </g>
</svg>
```

**Color**: blue=human/UE, amber=AI, green=final output, dark=system, gray=transition.

---

## Composability Rules

- **One viz per concept** — don't combine radar + Gantt + quadrant in same SVG. Separate viz containers per visualization.
- **viewBox always set** — for proper scaling on mobile + retina. Width 100% via CSS.
- **Legends are mandatory** when color encodes information (heatmap, radar, decision tree, Gantt).
- **Use `<text>` labels not just visual encoding** — accessibility + SVG-to-image conversion.
- **Mono font for axis labels + dates + numbers**; sans font for prose labels.
- **Annotation arrows OK** but use sparingly (1-2 per viz max).

## When to Roll Custom

If the source content doesn't fit any of these 9 patterns, author custom inline SVG. Then **add it back to this library** as a new pattern with: purpose / when to use / data shape / structural skeleton.
