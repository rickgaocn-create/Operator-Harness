---
category: work
name: okr
description: Create or check in OKRs. Mode A drafts MECE-tested OKR trackers and auto-chains to /biz; Mode B handles weekly KISS reviews and end-cycle grading.
model: claude-opus-4-7
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
# Skill: OKR Creation & Monitoring

Translate "what matters this quarter" into a disciplined OKR set, then keep it alive through weekly check-ins until it ships or gets consciously killed. Covers both **authoring** (new OKRs) and **monitoring** (running OKRs to closure).

> Source canon: **`00 Raw/Clippings/OKR工作法.md`** — the "深度实战指南" summarized. This skill operationalizes that canon against vault conventions (`(C)` tracker format, per-project Kanban task model per [[09 Rules/tasks.md]], MECE, SCORARO).

## When to Use

**Mode A — Create OKRs:**
- "Set OKRs", "定OKR", "plan the quarter", "draft Q[n] goals"
- Start of new quarter / half (default cadence)
- Mid-quarter strategic reset (war-room, pivot, new mandate)
- New project spinning up → scaffolded OKR set for its first quarter

**Mode B — Monitor OKRs:**
- "OKR check-in", "复盘OKR", "update the tracker", "KISS review"
- Weekly / bi-weekly cadence against an existing Tracker
- End-of-quarter grading (score each KR 0.0–1.0, narrate the delta)
- Any time a KR's status would flip 🟢 → 🟡 → 🔴

**Don't invoke for:**
- Ad-hoc task capture → `/task-capture`
- Full weekly vault refresh → `/weekly-update` (which calls this skill's Mode B as a sub-phase)
- Drafting a single deal memo or strategic doc → freelance with SCORARO

---

## Core Principles (from OKR工作法 + vault)

1. **O is qualitative, KR is quantitative — never invert.** O answers "we will do *what*"; KR answers "how we'll *know*."
2. **Stretch, not safety.** Target achievement = **60–70%** means success. 100% across every KR means the KRs were sandbagged.
3. **Output over input.** "打 50 个电话" is input. "达成 5 个意向订单" is output. **Reject any KR phrased as activity.**
4. **Focus ceiling: ≤ 3 Os · ≤ 4 KRs per O.** More fractures the quarter — a forcing function. If 5 Os feel "critical," 2 of them aren't.
5. **No fluff verbs in KRs.** Ban standalone: 优化 / 加强 / 提升 / 改善 / 推动 / 探索. Require numerics, deltas, or named deliverables.
6. **MECE across one O's KR set.** KRs together must be sufficient to conclude "O achieved." No gaps, no double-counting.
7. **Alignment up and down.** Each O ties upward to a vault-level goal (root `CLAUDE.md` / `GOALS.md`) and downward to ≥1 tactical chain in `Inbox.md`.
8. **Decoupled from compensation.** OKRs can be ambitious *because* missing them is cheap. Keep bonus/review talk out of OKR drafting.
9. **Visible, not buried.** Living OKRs sit in the project-scoped Tracker, linked from root and project CLAUDE.md.
10. **Living document.** Mid-cycle adjustments are fine — but the change is logged in **变更日志**, never silent.

**Execution formula (from source):**
> 有效执行 = 清晰的目标 (O) × 量化的结果 (KR) × 持续的反馈 (Check-in)

If any factor is zero, the product is zero. A clear O with fuzzy KRs = zero. Great KRs with no check-in rhythm = zero.

---

## Mode A — Creation

### Phase A1: Scope & upstream alignment

Read before asking:
- Root `CLAUDE.md` → **My Goals & Current Progress** + **My Current Projects & Overviews**
- `GOALS.md` (if it exists)
- Target project's `CLAUDE.md` → Process, Current Status, any existing OKR block
- Prior quarter's `(C) Q[n-1] OKR Tracker.md` if it exists — what landed, what didn't, what carried over

Then open the interview:
> "Before we write Os — what's the **strategic arc** this quarter is serving? One sentence. The OKRs will be a MECE decomposition of that arc."

Capture the arc as a preamble at the top of the Tracker.

### Phase A2: Draft Objectives (qualitative, ≤ 3)

For each candidate O, test:

| Gate | Question | Fail condition |
|---|---|---|
| 质性 | Is this a direction, not a number? | Contains metrics → that's a KR |
| 跳一跳 | Would a competent team hit only 60–70%? | "Definitely achievable" → too soft |
| 战略杠杆 | If we hit this, does something material change? | Cosmetic / maintenance work → demote |
| 独立 | Meaningfully different from the others? | Overlap → merge or re-cut |

If >3 candidates survive, **force a cut.** Ask: "If we could only win one, which dies first?" Kill until ≤3.

### Phase A3: Draft Key Results (quantitative, ≤ 4 per O)

Run the **4-part test** on each KR:

1. **Output test** — Result, not activity?
   - ❌ "开展社交媒体矩阵化推广" (activity)
   - ✅ "获取 10 万名新关注用户且 CAC ≤ 15 元" (output with constraint)

2. **Number test** — Baseline, target, or binary completion state?
   - ❌ "优化详情页转化率"
   - ✅ "详情页转化率从 X% 提升至 Y%"
   - ✅ "签约日系动画供应商 ≥ 1 家" (binary count is fine)

3. **Deadline test** — Timeframe explicit?
   - Default: completes by quarter end
   - Milestone KRs: add mid-quarter date

4. **Causality test** — If all KRs hit, is O obviously achieved?
   - All KRs green but O still feels unfinished → KRs incomplete; add one
   - One KR could miss and O still be a win → that KR isn't load-bearing; demote or delete

**Fluff-verb blacklist (reject on sight):**

| Banned | Replace with |
|---|---|
| 优化 X | 将 X 从 A 降至 B / 提升至 B |
| 加强 / 提升 X (无数字) | 具体指标 + 目标值 |
| 推动 X | 交付 X / 签署 X / 上线 X |
| 探索 X | 识别 N 个 X / 完成 N 次 X 对标 |
| 梳理 X | 输出 X 文档 / 落地 X SOP |

### Phase A4: MECE audit

For each O's KR set:
- **Mutually exclusive?** Two KRs counting the same thing from different angles → merge.
- **Collectively exhaustive?** A critical angle uncovered → add a KR (or scope O down).

If an O has 4 KRs and the MECE check keeps failing → often the O is two Os stuck together. Split.

### Phase A5: Write the Tracker

**Path:** **`03 Projects/<project>/(C) Q[n] OKR Tracker.md`**
**Reference:** **`03 Projects/{{PROJECT_A}}/(C) Q2 OKR Tracker.md`** — copy structure, don't reinvent.

Required sections, in order:
1. **Frontmatter** — `tags`, `project`, `quarter`, `owner`, `created`, `updated`, `status`
2. **Title + period + milestone anchors + update cadence**
3. **📊 Dashboard (概要)** — one row per O: Objective · 进度 · 状态 · 关键风险
4. **O sections** — for each:
   - **战略假设** (1–2 sentences — why this O matters *this* quarter)
   - **KR sub-sections** — each a 7-field table (指标 / 状态 / 进度 / Owner / 截止 / 下一步 / 风险)
5. **🔄 周更节奏** — the weekly ritual (see Mode B)
6. **📝 变更日志** — dated append-only log
7. **🔗 关联文档** — upward links + sideways (Inbox, project CLAUDE.md)

**Status icons:** 🟢 按节奏推进 · 🟡 启动中 / 需加速 · 🔴 阻塞 · ✅ 已完成
**Progress bar:** `⬜⬜⬜⬜⬜` — each ⬛ = 20%, round to nearest 20%, plus percentage.

### Phase A6: Link downstream

After writing the Tracker:
1. Link in the project's CLAUDE.md (Current Status or new OKR line)
2. Optionally update root CLAUDE.md → My Current Projects → project's Next Milestone
3. **Don't auto-batch all "下一步" tasks into the project Kanban.** Surface one chain at a time per `/task-capture` (≤ 3 new tasks per write).

### Phase A7: Auto-Chain `/biz` (Mode A only) — ⚠️ HARD GATE (non-optional, non-deferrable)

> **2026-05-23 hardening:** This phase is now a hard gate — instruction-driven auto-chain proved unreliable in 6 prior events. See [[.claude/skills/meeting-note/references/deep-variants.md]] § Phase 7 for canonical pattern.

### MUST-DO operational steps (in this order, this session, before ending the turn)

1. **Read frontmatter check.** Look for `biz-eval: skip`. If present, announce skip + END.
2. **Announce** (one-line, plain-text): *"🔁 Auto-chaining /biz on [tracker-path] per CLAUDE.md auto-chain rule. Add `biz-eval: skip` to frontmatter to opt out for future evals."*
3. **INVOKE the /biz skill via the Skill tool RIGHT NOW.** Call `Skill(skill="biz", args="<tracker-path> --lens strategy,finance")`. Default lens override (OKR coherence is strategy + finance question; risk lens fires only when KR data signals exposure). Do NOT defer, do NOT ask, do NOT end your turn until you have made this tool call.
4. **After /biz returns**, patch the Tracker's frontmatter: `biz-eval: completed`, `biz-eval-doc: "[[...]]"`, `biz-eval-date: YYYY-MM-DD`.
5. **Run biz-doc-critic grader loop** (Outcomes pattern):
   - Invoke `biz-doc-critic` subagent with eval-file path + `iteration: 1`
   - If `revise`: fix named hard fails → re-invoke (max 3) → escalate at iteration 3

Eval surfaces O-level coherence, KR ambition calibration (跳一跳 sweet spot vs. sandbag), upstream/downstream alignment gaps, and resource adequacy questions the Tracker itself doesn't ask.

**Mode B (check-in) does NOT auto-chain `/biz`** — check-ins are routine status updates, not new artifacts. The `/biz` evaluation cadence for ongoing OKRs is end-of-quarter grading (Phase B5), invoked manually when the user is ready for the post-mortem pass.

---

## Mode B — Monitoring

### Check-in cadence

- **Default:** every Friday 15:00 (stated in Tracker 周更节奏)
- **High-velocity projects** ({{PROJECT_A}}-style launch crunch): weekly
- **Steady-state projects:** bi-weekly
- **End of quarter:** full grading pass (Phase B5)

### Phase B1: KISS structured review

For each KR, run the 4 KISS questions in sequence — tight check-in, not deep-dive:

| KISS | Prompt | Surfaces |
|---|---|---|
| **K**eep | 本周这个 KR 上什么动作有效？值得固化？ | Reinforcement → fold into SOP |
| **I**mprove | 哪个环节卡了 / 慢了？怎么改？ | Friction → next-step task |
| **S**tart | 需要尝试什么新方法 / 关系 / 杠杆？ | Hypothesis → explicit experiment |
| **S**top | 哪些动作 ROI 低，应该停掉？ | Cost-cut → deprecate cleanly |

**Discipline:** A KR with no K/I/S/S bullet this week means **no activity happened on it** — flag explicitly. Two consecutive silent weeks → re-evaluate whether it's still the right KR.

### Phase B2: Update Tracker fields

For each KR, in this order:
1. **进度** — numeric or ratio (`2 / 5`). Recompute the ⬛⬛⬜⬜⬜ bar.
2. **状态** — flip icon: on pace to hit target by 截止? 🟢 / 🟡 / 🔴 / ✅
3. **下一步** — rewrite to the *next* concrete checkpoint. Old "下一步" that's done → mention in 变更日志, not kept in the field.
4. **风险** — add/remove. If a risk materialized, move it to 变更日志 and note the mitigation.

**Roll-up:** recompute the O-level progress bar as a weighted average of its KRs (equal weight unless flagged otherwise).

### Phase B3: Append to 变更日志

One row per week, terse:

```
| 2026-05-01 | O1 KR1 进度 0/3 → 1/3（小鹏联动 MOU 达成）；O2 KR2 🟡→🔴（王鹤书记路径受阻） | 周五 check-in |
```

### Phase B4: Escalation rules

Some signals get surfaced upstream, not just logged:

- **Any KR 🔴 for 2+ weeks** → flag in reply, propose: (a) reschedule 截止, (b) rescope KR, (c) abandon and log why
- **Any O dashboard bar not moving for 3 weeks** → this O is dead weight; propose dropping or pivoting
- **Scope creep** ("just one more KR" mid-quarter) → push back; append to a "Q[n+1] carry-over" list instead
- **New commitment from check-in** → offer to write as a chain via `/task-capture` (≤ 3 new tasks per batch)

### Phase B5: End-of-quarter grading (last 2 weeks of Q)

Score each KR **0.0–1.0** — calibrated to the stretch principle:

| Score | Meaning |
|---|---|
| 1.0 | Target fully hit. If every KR scored 1.0, KRs were too soft — note it. |
| 0.7 | Sweet spot. "跳一跳够得着" — what ambitious OKRs should average to. |
| 0.4 | Meaningful progress, clear miss. Not failure — learn from it. |
| 0.0 | No progress / abandoned. Demands an explicit post-mortem. |

For each O, average its KR scores. Then narrate:
1. What landed and why
2. What missed and why (root cause, not "no time")
3. What carries into Q[n+1] — as a seeded carry-over list, not auto-copied

**Write-back:** Close the Tracker with an **"End of Quarter — Grading"** section (don't delete live data). Start a fresh `(C) Q[n+1] OKR Tracker.md` via Mode A with the carry-over list in hand.

---

## Integration with Other Skills

| Trigger | Hand-off |
|---|---|
| Check-in produces new commitments | `/task-capture` (≤ 3 per batch) |
| Weekly update references OKR status | `/weekly-update` calls Mode B as a sub-phase |
| Raw market signal affecting an O | Log to **`00 Raw/`** first; decide at next check-in whether it changes a KR |
| Strategic reframe surfaces | `/preserve` learnings to CLAUDE.md, then Mode A revisit on affected Os |
| End of session with OKR decisions | `/compress` into a session log referencing the Tracker |

---

## Hard Rules

- **`(C)` prefix on every Tracker file.** No exceptions.
- **Never silently delete or re-word a KR mid-quarter.** Mutate → log in 变更日志 with reason and date.
- **Never fabricate progress numbers.** If user doesn't know "how many signed" this week → `进度: ? / N · 待确认` and surface the gap.
- **Never exceed 3 Os / 4 KRs per O.** Push back once citing focus principle; if user insists, write it but flag dilution risk in dashboard.
- **Tracker is not a task list.** "下一步" fields are *pointers* to atomic tasks — execution happens in the project Kanban (**`03 Projects/<project>/Tasks.md`**).
- **Ask before editing a non-`(C)` OKR doc** (a user-authored OKR note).

---

## ⚠️ Anti-Patterns (spot and kill)

| Pattern | Why it's bad | Fix |
|---|---|---|
| KR = "完成 X 项目" | Project completion is binary activity, not result | Replace with the result the project was meant to produce |
| Same 截止 on every KR | Everything due on quarter's last day → no mid-quarter feedback | Stagger; ≥1 KR per O with mid-quarter milestone |
| O reads like a KR ("Q2 增长 20%") | O should describe a *direction*, not a number | "巩固增长引擎，打破流量天花板" — KRs quantify it |
| 探索 / 调研 / 梳理 KR with no output artifact | Verb masks lack of commitment | Require named deliverable (报告、SOP、名册、对标文档) |
| Tracker last updated >14 days ago | OKRs have died | Honest reset: rescue via check-in OR write "abandoned Q[n]" in 变更日志 + plan Q[n+1] clean |
| 100% KR hit rate celebrated | Sandbagged targets | Next quarter, raise ambition; note pattern in 变更日志 |

---

## Worked Mini-Example (electronic commerce)

Input: "本季度要把电商店铺做起来。"

**Bad (accepted as-is):**
> O: 做好电商业务
> KR1: 优化详情页 · KR2: 加强推广 · KR3: 提升复购

**Good (after running this skill):**
> **O：通过服务与体验升级，重塑店铺核心竞争力并提升销售额**
> - **KR1（流量转化）：** 通过详情页 A/B 测试，3 个月内将线上转化率从 2.1% 提升至 3.5%
> - **KR2（获客成本）：** 社交媒体矩阵化推广获取 10 万新关注用户，且 CAC ≤ 15 元
> - **KR3（留存复购）：** 建立会员分层运营体系，将 90 天复购率从 18% 提升至 28%

Every fluff verb removed, every KR has baseline + target + implicit deadline, three KRs together are MECE (acquisition · cost · retention).

---

## Confirm Pattern

**After Mode A:**
> Created **`03 Projects/<project>/(C) Q[n] OKR Tracker.md`** — [N] Os / [M] KRs. Quality gates passed: [list]. First check-in scheduled Friday [date]. Upstream links added. No tasks auto-written to Inbox — flag when you want the first chain decomposed.

**After Mode B:**
> Updated `(C) Q[n] OKR Tracker.md`: [n] KR progress fields, [m] status flips ([🟢→🟡] / [🟡→🔴]), [k] rows appended to 变更日志. [Any escalation flags]. [Any tasks queued for `/task-capture`].
