---
type: vault-evolve-dashboard
auto-generated: hybrid
data-source: "04 Notes/vault-evolve/metrics/*.md (live via Dataview)"
biz-eval: skip
note: 此页 99% 是 Dataview 实时查询。改 metrics 后**自动**更新，无需手动 re-render。
---

# 📊 Vault Observability Dashboard

> 数据实时查 `04 Notes/vault-evolve/metrics/*.md`（每周 emit 一份）。
> 编辑 / 浏览：用 Obsidian **Reading mode** 查看渲染效果。

---

## 🚦 当周状态板

> Dataview 自动查最新 emit + 对照 thresholds 着色。

```dataviewjs
const dir = '"04 Notes/vault-evolve/metrics"';
const pages = dv.pages(dir).sort(p => p["emit-date"], "desc");

if (!pages.length) {
  dv.paragraph("⚠️ 还没有 emit 数据。让 `/vault-evolve` Phase 5.c 跑一次。");
} else {
  const latest = pages[0];

  const defs = {
    "auto-card-archive-rate":     {label:"auto-Card archive %",     section:"System Health",    lower:true,  green:20, yellow:30, unit:"%"},
    "orphan-card-pct":            {label:"orphan card %",            section:"System Health",    lower:true,  green:15, yellow:25, unit:"%"},
    "stale-draft-pct":            {label:"stale draft %",            section:"System Health",    lower:true,  green:30, yellow:50, unit:"%"},
    "inbox-aging-days":           {label:"_inbox/ aging (d)",        section:"System Health",    lower:true,  green:7,  yellow:14, unit:"d"},
    "broken-wikilinks":           {label:"broken wikilinks",         section:"System Health",    lower:true,  green:0,  yellow:5,  unit:""},
    "memory-md-lines":            {label:"MEMORY.md lines",          section:"System Health",    lower:true,  green:180, yellow:200, unit:""},
    "draft-acceptance-rate":      {label:"draft acceptance %",       section:"Output Quality",   lower:false, green:70, yellow:50, unit:"%"},
    "critique-convergence-passes":{label:"critique passes (avg)",    section:"Output Quality",   lower:true,  green:2,  yellow:3,  unit:""},
    "biweekly-kr-mapping":        {label:"biweekly KR-mapping %",    section:"Output Quality",   lower:false, green:80, yellow:60, unit:"%"},
    "meeting-note-shareability":  {label:"meeting share rate %",     section:"Output Quality",   lower:false, green:70, yellow:50, unit:"%"},
    "morning-bootstrap-rating":   {label:"morning rating (1-5)",     section:"Personal Leverage",lower:false, green:4,  yellow:3,  unit:""},
    "trip-context-recall":        {label:"trip context recall %",    section:"Personal Leverage",lower:false, green:100,yellow:80, unit:"%"},
    "eod-chew-rating":            {label:"EOD chew rating (1-5)",    section:"Personal Leverage",lower:false, green:4,  yellow:3,  unit:""},
    "wiki-first-hit-rate":        {label:"wiki first-hit %",         section:"Cognitive Offload",lower:false, green:80, yellow:60, unit:"%"},
    "carry-forward-propagation":  {label:"carry-forward %",          section:"Cognitive Offload",lower:false, green:100,yellow:80, unit:"%"},
    "chain-anchor-rename-count":  {label:"chain-anchor renames",     section:"Cognitive Offload",lower:true,  green:0,  yellow:0,  unit:""},
  };

  function status(val, d) {
    if (val == null) return "⚪ n/a";
    if (d.lower) {
      if (val <= d.green) return "🟢";
      if (val <= d.yellow) return "🟡";
      return "🔴";
    } else {
      if (val >= d.green) return "🟢";
      if (val >= d.yellow) return "🟡";
      return "🔴";
    }
  }

  const sections = ["System Health", "Output Quality", "Personal Leverage", "Cognitive Offload"];
  for (const section of sections) {
    dv.header(3, section);
    const rows = [];
    for (const [key, d] of Object.entries(defs)) {
      if (d.section !== section) continue;
      const val = latest[key];
      const display = val == null ? "n/a" : `${val}${d.unit}`;
      rows.push([d.label, display, status(val, d)]);
    }
    dv.table(["Metric", "Current", "Status"], rows);
  }
}
```

---

## 📈 4 周趋势（sparkline）

> 每个 metric 的近 4 个 emit 趋势。Unicode sparkline，从左（旧）到右（最新）。

```dataviewjs
const dir = '"04 Notes/vault-evolve/metrics"';
const pages = dv.pages(dir).sort(p => p["emit-date"], "desc");
const recent4 = pages.slice(0, 4);

if (recent4.length < 2) {
  dv.paragraph(`📌 当前 emit 数：${recent4.length}。需 ≥ 2 个才能画趋势。下次 emit 后会自动出 sparkline。`);
} else {
  const SPARK = "▁▂▃▄▅▆▇█";
  const metrics = [
    "memory-md-lines","stale-draft-pct","meeting-note-shareability",
    "trip-context-recall","carry-forward-propagation",
    "skills-invoked","cards-spawned","cards-archived","instincts-captured",
    "source-ingest-runs","day-digest-runs","vault-evolve-runs"
  ];
  const rows = [];
  for (const m of metrics) {
    const series = recent4.map(p => p[m]).filter(v => v !== null && v !== undefined);
    if (series.length < 2) { rows.push([m, "—", "—"]); continue; }
    const ordered = series.slice().reverse();
    const lo = Math.min(...ordered);
    const hi = Math.max(...ordered);
    let spark = "";
    if (hi === lo) {
      spark = SPARK[3].repeat(ordered.length);
    } else {
      for (const v of ordered) {
        const norm = (v - lo) / (hi - lo);
        spark += SPARK[Math.min(7, Math.floor(norm * 7.99))];
      }
    }
    const delta = ordered[ordered.length - 1] - ordered[0];
    const arrow = Math.abs(delta) < 0.001 ? "→" : (delta > 0 ? "↗" : "↘");
    rows.push([m, "`" + spark + "`", `${arrow} ${ordered[0]} → ${ordered[ordered.length - 1]}`]);
  }
  dv.table(["Metric", "Sparkline (oldest → newest)", "Delta"], rows);
}
```

---

## 📊 趋势图表（ChartSpark / Chart.js）

> 由 `~/.claude/vault-maintenance/chartspark-update.py` 周期性 regenerate（每次 emit 后跑一次或 vault-evolve Phase 5.d 自动跑）。**不要手动编辑标记段内容** —— 改了会被覆盖。

<!-- BEGIN AUTO-CHARTS -->
📌 只有 1 个数据点（**2026-05-15**）— 单点无法画趋势图。当周快照：

- MEMORY.md lines: **204**
- Cards spawned: **6**
- Instincts captured: **5**
- vault-evolve runs: **4**

等下次 emit 累积 ≥ 2 个数据点后，重跑此脚本就出 Chart.js 趋势图。
<!-- END AUTO-CHARTS -->

---

## 🚨 当周红色 alerts

> 自动从最新 emit 提取所有红色阈值突破。

```dataviewjs
const dir = '"04 Notes/vault-evolve/metrics"';
const pages = dv.pages(dir).sort(p => p["emit-date"], "desc");

if (!pages.length) {
  dv.paragraph("⚠️ 无数据.");
} else {
  const latest = pages[0];
  if (latest.alerts && latest.alerts.length > 0) {
    dv.list(latest.alerts.map(a => "🔴 " + a));
  } else {
    dv.paragraph("✅ 当周无红色 alert。");
  }
}
```

详细 alerts + 建议动作见 [[_alerts]].

---

## 🎯 Action loop tracker

> 每个 alert 触发 → 这里记一行 → 7d 后看是否真行动了。

```dataview
TABLE WITHOUT ID
  file.link AS "Alert",
  triggered AS "触发日期",
  metric AS "Metric",
  action AS "建议动作",
  status AS "状态"
FROM "04 Notes/vault-evolve/alerts"
WHERE status != "resolved"
SORT triggered DESC
LIMIT 20
```

> 👆 当前为空属正常 —— 等 vault-evolve emit 累积后会自动 surface。
> 详细见 [[_action-loop]].

---

## 🧹 Vanity check

> 任何 metric **4 周内值无变化** + **没触发过 action** → 候选 prune（季度 review 移除）。

```dataviewjs
const dir = '"04 Notes/vault-evolve/metrics"';
const pages = dv.pages(dir).sort(p => p["emit-date"], "desc");
const recent4 = pages.slice(0, 4);

if (recent4.length < 4) {
  dv.paragraph(`📌 累积 ${recent4.length}/4 周数据。需 ≥ 4 周才能 vanity-check。`);
} else {
  const metrics = ["auto-card-archive-rate","orphan-card-pct","stale-draft-pct","inbox-aging-days","broken-wikilinks","memory-md-lines","draft-acceptance-rate","critique-convergence-passes","biweekly-kr-mapping","meeting-note-shareability","morning-bootstrap-rating","trip-context-recall","eod-chew-rating","wiki-first-hit-rate","carry-forward-propagation","chain-anchor-rename-count"];
  const vanity = [];
  for (const m of metrics) {
    const series = recent4.map(p => p[m]).filter(v => v !== null && v !== undefined);
    if (series.length < 3) continue;
    if (Math.max(...series) - Math.min(...series) < 0.01) {
      vanity.push(m);
    }
  }
  if (vanity.length === 0) {
    dv.paragraph("✅ 所有 metrics 在近 4 周有变化 — 无 vanity 候选。");
  } else {
    dv.paragraph(`**${vanity.length} 个 4-周静止 metrics** 候选 prune：`);
    dv.list(vanity);
  }
}
```

---

## 🧪 Regression test status

> Golden prompts 上次跑结果。

```dataview
TABLE WITHOUT ID
  file.link AS "Test",
  "last-run" AS "上次运行",
  "last-verdict" AS "结果"
FROM "04 Notes/vault-evolve/tests/golden"
WHERE test-id
SORT "test-id" ASC
```

> 当前为 baseline 期 —— last-run = null. 等月度第 1 个工作日 vault-evolve Phase 5.e 跑一遍。

---

## 📅 历史 emit 索引

```dataview
TABLE WITHOUT ID
  file.link AS "Emit",
  "emit-date" AS "日期",
  "window-days" AS "窗口 (d)",
  length(alerts) AS "Alert 数"
FROM "04 Notes/vault-evolve/metrics"
SORT emit-date DESC
```

---

## 🔧 维护节奏

| 项 | 频率 | 触发 |
|---|---|---|
| 新 emit 写入 metrics/ | 每周 | `/vault-evolve` Phase 5.c (autonomous Sunday EOD) |
| 此 dashboard 内容 | **实时** | Obsidian Reading mode 渲染 Dataview |
| Alert escalation | 每周 | `/vault-evolve` Phase 5.d |
| Regression test | 每月 1st workday | `/vault-evolve` Phase 5.e |
| Vanity prune review | 每季度 1st workday | `/vault-evolve` Phase 5.f |

## 相关文件

- 数据源：`04 Notes/vault-evolve/metrics/*.md`（每周一个新文件）
- Schema 定义：[[_metrics]]
- 历史 narrative：[[_metrics-log]]
- Alerts 详情：[[_alerts]]
- Action loop：[[_action-loop]]
- Regression tests：[[tests/README|tests folder]]

---

> 💡 **打开姿势**：Obsidian → 此文件 → `Ctrl+E` 切到 **Reading mode** 看 Dataview 渲染。Edit mode 看的是 raw query 源代码。
