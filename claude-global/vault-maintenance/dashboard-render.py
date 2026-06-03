"""
Vault Observability Dashboard Renderer
========================================
Reads _metrics-log.md historical entries, emits:
  - _dashboard.md      : visual status + sparklines + alerts
  - _alerts.md         : current week's threshold breaches + suggested actions
  - Updates _action-loop.md with new alerts (append) + decays old ones

Pure Python, zero LLM cost. Run weekly via /vault-evolve Phase 5.d
or standalone: python dashboard-render.py
"""
from __future__ import annotations
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional

VAULT = Path(r"{{VAULT_ROOT}}")
EVOLVE_DIR = VAULT / "04 Notes" / "vault-evolve"
METRICS_LOG = EVOLVE_DIR / "_metrics-log.md"
DASHBOARD = EVOLVE_DIR / "_dashboard.md"
ALERTS = EVOLVE_DIR / "_alerts.md"
ACTION_LOOP = EVOLVE_DIR / "_action-loop.md"

# Sparkline blocks (8 levels)
SPARK = "▁▂▃▄▅▆▇█"

# Metric definitions: name → (parser_regex, healthy_band_check, action_message)
# healthy_band_check: lambda value -> "green" | "yellow" | "red"
METRIC_DEFS = {
    "auto_card_archive_rate": {
        "label": "auto-Card archive rate",
        "section": "System Health",
        "unit": "%",
        "lower_is_better": True,
        "green_threshold": 20,
        "yellow_threshold": 30,
        "action_on_red": "tighten /day-digest Phase 5.5 confidence gate +0.02",
    },
    "orphan_card_pct": {
        "label": "orphan card %",
        "section": "System Health",
        "unit": "%",
        "lower_is_better": True,
        "green_threshold": 15,
        "yellow_threshold": 25,
        "action_on_red": "run /card-lint --mode=bridge on top-N orphans",
    },
    "stale_draft_pct": {
        "label": "stale draft %",
        "section": "System Health",
        "unit": "%",
        "lower_is_better": True,
        "green_threshold": 30,
        "yellow_threshold": 50,
        "action_on_red": "run /card-lint --mode=stale",
    },
    "inbox_aging_days": {
        "label": "_inbox/ aging (days)",
        "section": "System Health",
        "unit": "d",
        "lower_is_better": True,
        "green_threshold": 7,
        "yellow_threshold": 14,
        "action_on_red": "batch promote or archive _inbox/ files",
    },
    "broken_wikilinks": {
        "label": "broken wikilinks",
        "section": "System Health",
        "unit": "",
        "lower_is_better": True,
        "green_threshold": 0,
        "yellow_threshold": 5,
        "action_on_red": "run /card-lint hygiene urgent",
    },
    "memory_md_lines": {
        "label": "MEMORY.md lines",
        "section": "System Health",
        "unit": "",
        "lower_is_better": True,
        "green_threshold": 180,
        "yellow_threshold": 200,
        "action_on_red": "prune MEMORY.md per its own rule",
    },
    "draft_acceptance_rate": {
        "label": "draft acceptance rate",
        "section": "Output Quality",
        "unit": "%",
        "lower_is_better": False,
        "green_threshold": 70,
        "yellow_threshold": 50,
        "action_on_red": "review register-calibration / source-quality",
    },
    "critique_convergence_passes": {
        "label": "critique convergence passes",
        "section": "Output Quality",
        "unit": "",
        "lower_is_better": True,
        "green_threshold": 2,
        "yellow_threshold": 3,
        "action_on_red": "investigate me.md frameworks (upstream draft quality issue)",
    },
    "morning_bootstrap_rating": {
        "label": "morning bootstrap (1-5)",
        "section": "Personal Leverage",
        "unit": "",
        "lower_is_better": False,
        "green_threshold": 4,
        "yellow_threshold": 3,
        "action_on_red": "/daily-emit logic review (3 consecutive days < 3)",
    },
    "eod_chew_rating": {
        "label": "EOD chew (1-5)",
        "section": "Personal Leverage",
        "unit": "",
        "lower_is_better": False,
        "green_threshold": 4,
        "yellow_threshold": 3,
        "action_on_red": "/day-digest Phase 4 framing review",
    },
    "wiki_first_hit_rate": {
        "label": "wiki first-hit rate",
        "section": "Cognitive Offload",
        "unit": "%",
        "lower_is_better": False,
        "green_threshold": 80,
        "yellow_threshold": 60,
        "action_on_red": "wiki dedup pass + aliases pass",
    },
    "chain_anchor_rename_count": {
        "label": "chain-anchor renames",
        "section": "Cognitive Offload",
        "unit": "",
        "lower_is_better": True,
        "green_threshold": 0,
        "yellow_threshold": 0,
        "action_on_red": "MEMORY rule violation per 09 Rules/action.md — investigate",
    },
}


def parse_log() -> list[dict]:
    """Parse _metrics-log.md into list of weekly entries (newest first)."""
    if not METRICS_LOG.exists():
        return []
    text = METRICS_LOG.read_text(encoding="utf-8")
    entries = []
    # Each entry begins with `## YYYY-MM-DD` heading
    blocks = re.split(r"^## (\d{4}-\d{2}-\d{2})", text, flags=re.MULTILINE)[1:]
    for i in range(0, len(blocks), 2):
        if i + 1 >= len(blocks):
            break
        date_str = blocks[i].strip()
        body = blocks[i + 1]
        entry = {"date": date_str, "metrics": {}}
        for key in METRIC_DEFS:
            label = METRIC_DEFS[key]["label"]
            # match patterns like "label: 23%" or "label = 23" or "| label | 23 |"
            patterns = [
                rf"{re.escape(label)}\s*[:=|]\s*([\d.]+)",
                rf"\|\s*{re.escape(label)}\s*\|\s*([\d.]+)",
            ]
            for pat in patterns:
                m = re.search(pat, body, re.IGNORECASE)
                if m:
                    entry["metrics"][key] = float(m.group(1))
                    break
        entries.append(entry)
    return sorted(entries, key=lambda x: x["date"], reverse=True)


def status_of(value: float, defn: dict) -> str:
    """Return 'green' | 'yellow' | 'red'."""
    g, y = defn["green_threshold"], defn["yellow_threshold"]
    if defn["lower_is_better"]:
        if value <= g:
            return "green"
        if value <= y:
            return "yellow"
        return "red"
    else:
        if value >= g:
            return "green"
        if value >= y:
            return "yellow"
        return "red"


def emoji(status: str) -> str:
    return {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(status, "⚪")


def sparkline(values: list[float], defn: dict) -> str:
    """Map a series to 8-level sparkline. Most recent on right."""
    if not values:
        return "—"
    lo, hi = min(values), max(values)
    if hi == lo:
        return SPARK[3] * len(values)
    out = []
    for v in values:
        # Normalize to 0-7 index
        norm = (v - lo) / (hi - lo)
        out.append(SPARK[min(7, int(norm * 7.99))])
    return "".join(out)


def trend_arrow(values: list[float], defn: dict) -> str:
    """↑ ↓ → based on last vs first."""
    if len(values) < 2:
        return ""
    delta = values[0] - values[-1]  # values are newest-first
    if abs(delta) < 0.001:
        return "→"
    improving = (delta < 0) if defn["lower_is_better"] else (delta > 0)
    return "↗ ✓" if improving else "↘ !"


def render_dashboard(entries: list[dict]) -> str:
    if not entries:
        return f"""---
type: vault-evolve-dashboard
auto-generated: true
last-rendered: {date.today()}
biz-eval: skip
---

# Vault Dashboard

⚠️ `_metrics-log.md` 还没数据 —— 先让 `/vault-evolve` Phase 5.c 跑一周积累 baseline。
"""

    latest = entries[0]
    history_4w = entries[:4]  # last 4 weeks (newest first)

    md = [
        "---",
        "type: vault-evolve-dashboard",
        "auto-generated: true",
        f"last-rendered: {date.today()}",
        f"last-data-point: {latest['date']}",
        "biz-eval: skip",
        "render-source: ~/.claude/vault-maintenance/dashboard-render.py",
        "---",
        "",
        "# 📊 Vault Observability Dashboard",
        "",
        f"> 最新数据 **{latest['date']}** · 渲染于 **{date.today()}** · 自动生成（vault-evolve Phase 5.d 调用 dashboard-render.py）· **不要手动编辑**",
        "",
        "## 🚦 当周状态板",
        "",
    ]

    # Group by section
    by_section = defaultdict(list)
    for key, defn in METRIC_DEFS.items():
        if key in latest["metrics"]:
            by_section[defn["section"]].append(key)

    alerts_list = []
    for section in ["System Health", "Output Quality", "Personal Leverage", "Cognitive Offload"]:
        keys = by_section.get(section, [])
        if not keys:
            continue
        md.append(f"### {section}")
        md.append("")
        md.append("| Metric | Current | Status | Trend (4w) | Spark |")
        md.append("|---|---|---|---|---|")
        for key in keys:
            defn = METRIC_DEFS[key]
            val = latest["metrics"][key]
            status = status_of(val, defn)
            unit = defn["unit"]
            series = [e["metrics"][key] for e in history_4w if key in e["metrics"]]
            spark = sparkline(list(reversed(series)), defn)  # oldest left, newest right
            arrow = trend_arrow(series, defn)
            md.append(f"| {defn['label']} | {val:g}{unit} | {emoji(status)} {status} | {arrow} | `{spark}` |")
            if status == "red":
                alerts_list.append((defn["label"], val, unit, defn["action_on_red"]))
        md.append("")

    md.append("---")
    md.append("")
    md.append("## 🚨 当周 alerts（红色阈值突破）")
    md.append("")
    if alerts_list:
        md.append("| Metric | 当前值 | 建议动作 |")
        md.append("|---|---|---|")
        for label, val, unit, action in alerts_list:
            md.append(f"| {label} | {val:g}{unit} | {action} |")
    else:
        md.append("✅ 当周无红色 alert。系统在 healthy 区间。")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## 📈 历史数据点")
    md.append("")
    md.append(f"近 4 周 emit log：")
    for e in history_4w:
        n_metrics = len(e["metrics"])
        md.append(f"- **{e['date']}** · {n_metrics} 项指标 emit")
    md.append("")
    md.append(f"完整历史见 [[_metrics-log]]")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## 🧹 Vanity check")
    md.append("")
    md.append("> Metric 在最近 4 周内**没有变化**且**没有触发 action** → 候选 prune（季度 review 时移除）。")
    md.append("")

    vanity_candidates = []
    for key, defn in METRIC_DEFS.items():
        series = [e["metrics"].get(key) for e in history_4w if key in e["metrics"]]
        series = [s for s in series if s is not None]
        if len(series) >= 3:
            if max(series) - min(series) < 0.01:
                vanity_candidates.append(defn["label"])

    if vanity_candidates:
        md.append("**4 周静止的指标**（候选 prune）：")
        for v in vanity_candidates:
            md.append(f"- {v}")
    else:
        md.append("✅ 所有指标在近 4 周有变化 —— 无 vanity 候选。")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## 🧪 Regression test status")
    md.append("")
    md.append("> Golden prompt suite 跑结果。月度 1 号 emit。")
    md.append("")
    md.append("（待 regression-test-runner.py 接入后填充）")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## 🎯 Action loop")
    md.append("")
    md.append(f"详 [[_action-loop]] — 每个 alert 是否被采纳 + 7d 内是否真改变了行为。")
    md.append("")

    return "\n".join(md)


def render_alerts(entries: list[dict]) -> str:
    if not entries:
        return ""
    latest = entries[0]
    alerts = []
    for key, defn in METRIC_DEFS.items():
        if key not in latest["metrics"]:
            continue
        val = latest["metrics"][key]
        status = status_of(val, defn)
        if status == "red":
            alerts.append({
                "key": key,
                "label": defn["label"],
                "value": val,
                "unit": defn["unit"],
                "action": defn["action_on_red"],
                "date": latest["date"],
            })

    md = [
        "---",
        "type: vault-evolve-alerts",
        f"render-date: {date.today()}",
        f"data-date: {latest['date']}",
        "biz-eval: skip",
        "---",
        "",
        "# 🚨 Vault Alerts",
        "",
        f"基于 {latest['date']} 的 metrics emit。"
    ]
    if not alerts:
        md.append("")
        md.append("✅ 当周无红色 alert。")
    else:
        md.append("")
        md.append(f"**{len(alerts)} 项红色 alert** —— 按 action 紧迫度排：")
        md.append("")
        for a in alerts:
            md.append(f"## {a['label']}")
            md.append("")
            md.append(f"- **当前值**: {a['value']:g}{a['unit']}")
            md.append(f"- **建议动作**: {a['action']}")
            md.append(f"- **首次触发**: {a['date']}")
            md.append(f"- **当前状态**: 🔴 待行动")
            md.append("")
    return "\n".join(md)


def append_to_action_loop(entries: list[dict]):
    """Append today's alerts to _action-loop.md (idempotent)."""
    if not entries:
        return
    latest = entries[0]
    today_str = date.today().isoformat()

    # Existing content
    if ACTION_LOOP.exists():
        existing = ACTION_LOOP.read_text(encoding="utf-8")
    else:
        existing = """---
type: vault-evolve-action-loop
purpose: "每个 alert 触发后, 用户行动留痕 (7d 跟踪窗口). Auto-appended by dashboard-render.py."
biz-eval: skip
---

# 🎯 Action Loop · Alert → 行动 → 结果

> 反 vanity 核心：metric 闪红 → 这里记一行 → 7d 后如果没动 → metric 被标 dormant → 30d dormant 自动进 vanity-candidate 列表。

| 日期 | Metric | 触发值 | 建议动作 | 用户已采纳? | 7d 后结果 | 状态 |
|---|---|---|---|---|---|---|
"""

    # Check if this date already has entries (idempotency)
    if today_str in existing:
        return  # already appended for today

    new_rows = []
    for key, defn in METRIC_DEFS.items():
        if key not in latest["metrics"]:
            continue
        val = latest["metrics"][key]
        status = status_of(val, defn)
        if status == "red":
            new_rows.append(
                f"| {today_str} | {defn['label']} | {val:g}{defn['unit']} | {defn['action_on_red']} | (待填) | (7d 后填) | 🔴 待行动 |"
            )

    if new_rows:
        ACTION_LOOP.write_text(existing.rstrip() + "\n" + "\n".join(new_rows) + "\n", encoding="utf-8")


def main():
    entries = parse_log()
    DASHBOARD.write_text(render_dashboard(entries), encoding="utf-8")
    ALERTS.write_text(render_alerts(entries), encoding="utf-8")
    append_to_action_loop(entries)
    print(f"dashboard rendered: {DASHBOARD}")
    print(f"alerts rendered: {ALERTS}")
    print(f"action loop updated: {ACTION_LOOP}")
    print(f"data points parsed: {len(entries)}")


if __name__ == "__main__":
    sys.exit(main())
