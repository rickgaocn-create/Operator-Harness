"""
ChartSpark dashboard updater
=============================
Reads all 04 Notes/vault-evolve/metrics/{date}.md emits, generates Chart.js JSON,
inserts as ```chartspark blocks into _dashboard.md between auto-chart markers.

Pure Python, no LLM cost. Run after each /vault-evolve Phase 5.c emit.

Usage: python chartspark-update.py
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from datetime import date

VAULT = Path(r"{{VAULT_ROOT}}")
EVOLVE_DIR = VAULT / "04 Notes" / "vault-evolve"
METRICS_DIR = EVOLVE_DIR / "metrics"
DASHBOARD = EVOLVE_DIR / "_dashboard.md"

BEGIN_MARK = "<!-- BEGIN AUTO-CHARTS -->"
END_MARK = "<!-- END AUTO-CHARTS -->"


def parse_frontmatter(text: str) -> dict:
    """Lightweight YAML frontmatter parser (handles flat key: value)."""
    m = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    in_list = None
    for raw in m.group(1).split("\n"):
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):  # list item under prev key
            if in_list is not None:
                fm[in_list].append(line[4:].strip().strip('"'))
            continue
        if ":" not in line:
            continue
        in_list = None
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if not val:
            # Could be start of a list
            fm[key] = []
            in_list = key
            continue
        if val.lower() in ("null", "none", "~"):
            fm[key] = None
        elif val.startswith('"') and val.endswith('"'):
            fm[key] = val[1:-1]
        else:
            try:
                fm[key] = int(val)
            except ValueError:
                try:
                    fm[key] = float(val)
                except ValueError:
                    fm[key] = val
    return fm


def load_emits() -> list[dict]:
    if not METRICS_DIR.exists():
        return []
    emits = []
    for f in sorted(METRICS_DIR.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            if fm.get("emit-date"):
                emits.append(fm)
        except Exception as e:
            print(f"skip {f.name}: {e}")
    # Sort by emit-date ascending (oldest left in chart)
    emits.sort(key=lambda e: str(e.get("emit-date", "")))
    return emits


def chart_block(title: str, chart_type: str, labels: list, datasets: list,
                y_min: float | None = None, y_max: float | None = None) -> str:
    cfg = {
        "type": chart_type,
        "data": {"labels": labels, "datasets": datasets},
        "options": {
            "responsive": True,
            "plugins": {
                "title": {"display": True, "text": title, "font": {"size": 14}},
                "legend": {"position": "bottom"}
            }
        }
    }
    if y_min is not None or y_max is not None:
        cfg["options"]["scales"] = {"y": {}}
        if y_min is not None:
            cfg["options"]["scales"]["y"]["min"] = y_min
        if y_max is not None:
            cfg["options"]["scales"]["y"]["max"] = y_max
    return "```chartspark\n" + json.dumps(cfg, indent=2, ensure_ascii=False) + "\n```"


def get(e, k, default=None):
    """Get metric value; null in frontmatter → None in python → skip in chart."""
    v = e.get(k)
    return v if v is not None else default


def make_dataset(label: str, emits: list, key: str, default=None) -> dict:
    return {
        "label": label,
        "data": [get(e, key, default) for e in emits],
        "spanGaps": True,  # connect over null gaps
        "tension": 0.3,
    }


def render_all_charts(emits: list[dict]) -> str:
    if len(emits) == 0:
        return f"📌 还没有 emit 数据。让 `/vault-evolve` Phase 5.c 跑一次后重跑此脚本。"
    if len(emits) == 1:
        labels = [str(emits[0].get("emit-date"))]
        e = emits[0]
        # Single-point summary instead of charts
        return (
            f"📌 只有 1 个数据点（**{labels[0]}**）— 单点无法画趋势图。"
            f"当周快照：\n\n"
            f"- MEMORY.md lines: **{e.get('memory-md-lines')}**\n"
            f"- Cards spawned: **{e.get('cards-spawned')}**\n"
            f"- Instincts captured: **{e.get('instincts-captured')}**\n"
            f"- vault-evolve runs: **{e.get('vault-evolve-runs')}**\n\n"
            f"等下次 emit 累积 ≥ 2 个数据点后，重跑此脚本就出 Chart.js 趋势图。"
        )

    labels = [str(e["emit-date"]) for e in emits]

    # Chart 1: System Health (lower = better)
    c1 = chart_block(
        "📉 System Health Trend · 越低越好",
        "line", labels,
        [
            make_dataset("MEMORY.md lines", emits, "memory-md-lines"),
            make_dataset("stale draft %", emits, "stale-draft-pct"),
            make_dataset("_inbox/ aging (d)", emits, "inbox-aging-days"),
            make_dataset("broken wikilinks", emits, "broken-wikilinks"),
        ],
    )

    # Chart 2: Activity Volume
    c2 = chart_block(
        "📊 Activity Volume per Week",
        "bar", labels,
        [
            make_dataset("Cards spawned", emits, "cards-spawned", 0),
            make_dataset("Instincts captured", emits, "instincts-captured", 0),
            make_dataset("/source-ingest", emits, "source-ingest-runs", 0),
            make_dataset("/day-digest", emits, "day-digest-runs", 0),
            make_dataset("/vault-evolve", emits, "vault-evolve-runs", 0),
        ],
    )

    # Chart 3: Personal Leverage (1-5 ratings)
    c3 = chart_block(
        "⭐ Personal Leverage Ratings (1-5)",
        "line", labels,
        [
            make_dataset("Morning bootstrap", emits, "morning-bootstrap-rating"),
            make_dataset("EOD chew", emits, "eod-chew-rating"),
        ],
        y_min=0, y_max=5,
    )

    # Chart 4: Output Quality (%)
    c4 = chart_block(
        "📈 Output Quality · 越高越好 (%)",
        "line", labels,
        [
            make_dataset("Draft acceptance %", emits, "draft-acceptance-rate"),
            make_dataset("Meeting share rate %", emits, "meeting-note-shareability"),
            make_dataset("Biweekly KR-mapping %", emits, "biweekly-kr-mapping"),
            make_dataset("Trip context recall %", emits, "trip-context-recall"),
            make_dataset("Carry-forward %", emits, "carry-forward-propagation"),
        ],
        y_min=0, y_max=100,
    )

    return f"""
### 📉 System Health (lower = better)

{c1}

### 📊 Activity Volume

{c2}

### ⭐ Personal Leverage Ratings

{c3}

### 📈 Output Quality (%)

{c4}

*Generated by `~/.claude/vault-maintenance/chartspark-update.py` from {len(emits)} emit data points · last update {date.today().isoformat()}.*
"""


def update_dashboard(charts_md: str):
    text = DASHBOARD.read_text(encoding="utf-8")
    if BEGIN_MARK not in text or END_MARK not in text:
        print(f"ERROR: markers not found in {DASHBOARD}")
        print(f"  Add this block somewhere in _dashboard.md:")
        print(f"    {BEGIN_MARK}")
        print(f"    placeholder")
        print(f"    {END_MARK}")
        return False

    pattern = re.escape(BEGIN_MARK) + r"\n.*?\n" + re.escape(END_MARK)
    replacement = BEGIN_MARK + "\n" + charts_md.strip() + "\n" + END_MARK
    new_text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    DASHBOARD.write_text(new_text, encoding="utf-8")
    return True


def main():
    emits = load_emits()
    print(f"Loaded {len(emits)} emit(s) from {METRICS_DIR}")
    if emits:
        first = emits[0].get("emit-date")
        last = emits[-1].get("emit-date")
        print(f"  range: {first} → {last}")
    charts = render_all_charts(emits)
    if update_dashboard(charts):
        print(f"OK Dashboard updated: {DASHBOARD}")
    else:
        print(f"FAIL Dashboard markers missing -- see above for fix")


if __name__ == "__main__":
    main()
