# Interactive Report · Design System

Cinematic editorial palette. Crystallized from EPIC Summit v0.2 (2026-05-15).

## Color Palette

```css
:root {
  /* Hero / dark sections */
  --midnight: #0a1729;
  --midnight-2: #142847;
  --midnight-3: #1e3a5f;

  /* Primary accent — warm gold, draws eye to load-bearing content */
  --amber: #f59e0b;
  --amber-light: #fbbf24;
  --amber-glow: rgba(245, 158, 11, 0.15);

  /* Secondary — UE/engineering blue */
  --cobalt: #2563eb;
  --cobalt-deep: #1e40af;
  --cobalt-light: #60a5fa;

  /* Tertiary — for green-zone status / positive outcomes */
  --teal: #0d9488;

  /* Quaternary — for期权 / outlier / asymmetric items */
  --magenta: #be185d;

  /* Body / light section bg */
  --cream: #faf7f0;
  --paper: #ffffff;
  --paper-2: #f9f7f1;

  /* Text */
  --charcoal: #0f172a;
  --text: #1e293b;
  --muted: #64748b;
  --faint: #94a3b8;

  /* Borders */
  --border: #e2e8f0;
  --border-strong: #cbd5e1;

  /* NDA / danger */
  --nda-bg: #fef2f2;
  --nda-border: #fecaca;
  --nda-text: #991b1b;

  /* Status semantics */
  --success: #059669;
  --warn: #d97706;
  --danger: #dc2626;
}
```

## Typography Stack

```css
:root {
  --mono: ui-monospace, "SF Mono", "Cascadia Mono", "Roboto Mono", Menlo, monospace;
  --serif: "Source Han Serif SC", "Noto Serif CJK SC", Georgia, "Times New Roman", serif;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", sans-serif;
}
```

**Usage**:
- `--sans` — body text, headers, UI elements (default)
- `--serif` — hero accent words (italic), pull-quotes ("keeping the artist at the center"), big stat numbers in hero
- `--mono` — section numbers (§ 1 · AGENDA), date markers, code blocks, axis labels in SVG charts

## Type Scale

```css
h1 { font-size: clamp(36px, 5vw, 56px); line-height: 1.1; font-weight: 800; letter-spacing: -0.025em; }
h2 { font-size: clamp(28px, 3.5vw, 38px); line-height: 1.2; font-weight: 700; letter-spacing: -0.015em; }
h3 { font-size: 20px; line-height: 1.35; font-weight: 700; }
h4 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; color: var(--muted); }
.lead { font-size: 17px; color: var(--muted); line-height: 1.7; max-width: 760px; }
.section-num { font-family: var(--mono); font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; }
body { font-size: 16px; line-height: 1.65; }
```

## Spacing Scale

- Section vertical padding: `80px 32px` (60px on mobile)
- Card padding: `22px`
- Card gap: `18px`
- Card grid `minmax(290px, 1fr)`
- Hero padding: `100px 48px 60px` (60px 24px 40px on mobile)
- Component margin: `24px 0` between vizs/cards
- Border-radius: `8-12px` for cards, `999px` for pills, `6px` for SVG boxes

## Layout

```css
main { max-width: 1280px; margin: 0 auto; }
.section-inner { max-width: 1180px; margin: 0 auto; }
.card-grid { grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 18px; }
.studio-trio { grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 20px; }
.asks-grid { grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 18px; }
```

## Section Dark/Light Alternation

Default rhythm for 11-section document:
```
Cover (dark) → §1 light → §2 light → §3 dark → §4 light → §5 light → §6 dark → §7 light → §8 light → §9 dark → §10 light
```

The dark sections function as "movie poster" interludes — they're typically the highest-conviction strategic frames (industry validation / decision gates / timeline).

## Responsive Breakpoints

- **>720px**: full grid, side-by-side comparisons
- **<720px**: single-column stack, tables stack, heatmap reflows to 1-col, hero stats single row

## Print-Friendly Required Rules

```css
@media print {
  nav.top { display: none; }
  section { page-break-inside: avoid; padding: 24px 0; border: none; background: white !important; color: var(--text) !important; }
  section.dark { background: white !important; color: var(--text) !important; }
  section.dark h2, section.dark h3, section.dark p { color: var(--text) !important; }
  .hero { background: white !important; color: var(--text) !important; border: 2px solid var(--midnight); }
  /* ... */
}
```

## Accessibility

- Sufficient contrast on dark sections (rgba(255,255,255,0.92) text on midnight bg = 11+ ratio)
- All `<img>` tags need `alt` attribute
- Sticky nav `aria-current="page"` on active section (TODO: add to template)
- SVG visualizations include `<text>` labels (not just visual encoding)

## What Earned its Keep in v0.2

- Alternating dark/light gives rhythm + draws attention to load-bearing sections
- Big hero stat numbers anchor the read with "the punchline before the proof"
- Amber as primary accent reads "premium" + "Hollywood theatrical" — fits Animation Summit content theme
- Cobalt as secondary signals "engineering / spec / data"
- Magenta exclusively for asymmetric / option-like items (丁 MCP) — readers learn the color = "uncertain but high-stakes"
- Generous whitespace + serif italic accents in hero — "magazine cover" feel, signals craft

## What to Avoid

- Multiple accent colors competing (>3 strong accents in same section)
- Pure-text-on-dark sections (always pair text with visual element)
- Body copy in serif (only hero quotes / accents)
- Saturated color backgrounds for body sections (cream/paper only — color = accent, not surface)
