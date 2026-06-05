---
layer: mixed
paths:
  - "03 Projects/**/*.md"
  - "04 Notes/**/*.md"
  - "10 Action/12 Active/CV-*.{md,html}"
  - "**/*pitch*.{md,html}"
scope: cross-cutting (style layer)
applies-to-skills:
  - "[[.claude/skills/localize-cn/SKILL.md]]"
  - "[[.claude/skills/humanize/SKILL.md]]"
  - "[[.claude/skills/pragmatic/SKILL.md]]"
origin: 2026-05-21 Phase 3.2.c restructure — extracted static rule tables from each style-layer SKILL.md to slim them below the 200-line skim threshold; resolves M.11 (CLAUDE.md +60% growth from inline auto-chain rule blocks)
created-by: claude
created: 2026-05-21
---

# Auto-Chain Style Rules · 风格层规则汇总

> **Why this is a 09 Rules file, not three SKILL.md inline blocks:** the wordlists, pattern catalogues, and numbered rule sets are STATIC reference data, not dispatch logic. SKILL.md files load every session (cold-path token cost); rule files load on-demand when the SKILL.md says "see § X". Keeping the 5-category wordlist / 29-pattern check / 13-rule set out of SKILL.md drops each below the 200-line skim threshold without losing content.

## Order when multiple chains apply

Canonical in [[CLAUDE.md]] § Skill Auto-Chain Rules; restated here for completeness:

| Combination | Order |
|---|---|
| Business + CN-audience | `/biz` → `/localize-cn` |
| Creative writing + CN-audience | `/humanize` → `/localize-cn` |
| Project-internal CN meeting note | `/biz` → `/localize-cn` → `/pragmatic` |
| Project-internal briefing (CN, no biz lens) | `/localize-cn` → `/pragmatic` |
| Project-internal CN with creative element | `/humanize` → `/localize-cn` → `/pragmatic` |
| **Work report 语义类 (周报 / 双周报 / status update / 工作汇报 — 任何载体)** | `/localize-cn` → `/pragmatic` （强制，载体无关）|
| Pure creative writing (non-CN) | `/humanize` only |

### Semantic-class auto-trigger（语义类强制触发，载体无关）

> **加入触发原因（2026-05-28 incident）：** cn-guard 现按 **path + frontmatter** 触发；DM / Feishu message / Discord message / 邮件草稿 等"非文件"载体绕过守护。**语义类触发**补这个盲区——不看路径，只看请求语义。

**触发关键词**（同义即触发，不限中英）：
- 中文："产出周报 / 双周报 / 工作报告 / 工作汇报 / 周总结 / 双周总结 / status update / status 同步 / 进度汇报"
- 英文："weekly report / biweekly report / status update / work summary / weekly recap"
- 派生："过去 N 天 / 这周 / 本双周 / 这个月" + "做个汇报 / 总结 / report"

**触发动作**：在 ✋ 任何 surface（文件 / Feishu reply / Discord reply / 邮件正文 / 飞书文档 / 妙享文档 / interactive-report HTML）输出前，全文过一遍 `/localize-cn`（按本文件 § Localize-CN 1-7 节残留词表过滤）+ `/pragmatic`（按本文件 § Pragmatic 规则 4 删装饰 + 规则 5 短句 ≤30 字 + 规则 6 去名字化 section header + 规则 8 删 editorial parentheticals）。

**自检 EN 残留 watchlist**（高频 chat-residue，输出前 grep / 读一遍替换）：
backlog（积压）· framing（定调 / 叙事）· partition（切分）· bolt-on（嵌入段）· UX（用户体验）· starving（空转 / 0 投入）· sourcing（标的搜寻）· dormant（停滞 / 沉寂）· mandate（接手任务 / 委派）· fallback（备选 / 兜底）· closeout（收尾）· handoff（交接）· re-date（重排日期 / 改期）· spec（规格）· benchmark（参考基准）· AM-first（上午第一件事）· cliff（集中节点）· build day（自建日）· last-ditch（最后一搏）· dormant track（停滞条线）· workstream（工作线）· deal-structuring（谈判结构 / 交易拆解）。

**白名单 vs 黑名单按 audience 切（2026-05-28 加 · push-back 实测）**：

| 标识 | self / vault 内部 | 项目内 PMO（{{PERSON}} / 小K 已知 chain） | **公司其他成员（{{PERSON_1}} / 财务 / 法务 / 外部）** |
|---|---|---|---|
| Chain-anchor 内部代号（`京差0522` / `厦差0525` / `渠道争取`） | ✅ 保留 | ✅ 保留 | ❌ **删** — 换成业务描述（"北京行" / "厦门差旅" / "渠道资源争取工作线"）|
| Action / Task file ID（`T260526-channel-resource-push` / `T260527-feishu-ai-enablement`）| ✅ 保留 | ⚠️ 可换 wikilink 别名 | ❌ **删** — 换成工作线名（"渠道争取" / "飞书 AI 提效"）|
| Card ID（`C260527-prioritize-channels-by-share-not-reach`）| ✅ 保留 | ⚠️ 提取卡片要点 | ❌ **删** — 直接复述要点|
| Operon Task GUID（7 字符如 `xp9rk2v` / `h1z5w2k` / `nwd576e`）| ✅ 保留 | ❌ **删** | ❌ **删** — 内部 join key，纯噪声|
| Instinct ID（`I260525-heads-down-build-day-starves-unblock-by-message-items`）| ✅ 保留 | ❌ **删** | ❌ **删** — 元方法论，不属业务汇报|
| OKR 顶层代号（`O1` / `O2` / `O3`）| ✅ 保留 | ✅ 保留 | ⚠️ 视读者 — 入 OKR 体系成员可留，外部 / 财务 / 法务删 |
| KR 子代号（`O1.KR1` / `O1.KR2` / `O1.KR3`）| ✅ 保留 | ✅ 保留 | ❌ **删** — 描述本身（"端午试玩会" / "渠道资源"）已够|
| 内部黑话（"悬崖" / "starving" / "AM-first 机械动作" / "instinct 实测"）| ✅ 保留 | ⚠️ 删 | ❌ **删** — 换中性描述（"关键节点" / "长期空转" / "上午先处理收尾"）|
| 产品 / 平台名（TapTap / B 站 / 4399 / Wegame / Steam / Google Play / iOS / AppStore / 火山引擎）| ✅ | ✅ | ✅ — 行业通用|
| 版本号（`v1` / `v2` / CBT1 / CBT2）| ✅ | ✅ | ✅ — 行业通用|

**Driver**：2026-05-28 周报 v2 给{{PERSON_1}} audience 时仍保留 `T260526-channel-resource-push` 等代号被 push-back —「考虑到受众是我公司其他成员类似百洋」。

**为什么强制载体无关**：path-based guard 只保护文件落盘，但项目内沟通有大量 Feishu DM / 群消息形式的"轻文档"，audience 仍是{{PERSON}} / {{PERSON_1}} / 内部 PMO — 同等正式度要求。语义类触发把守护从"文件类"延伸到"任何 report 类输出"。

---

### Forwardable 文档默认格式增强（2026-05-28 加）

work-report 类输出落到飞书云文档 / 妙享 / interactive-report HTML 时，<b>不要只靠 Markdown 原生元素</b>，主动用富 block 提升可读性。

| 场景 | 用 |
|---|---|
| 时间窗 + 一句话现状 / 重大风险 / 重点结论 / 下周关注 | `<callout>` 高亮框，颜色按语义（blue 信息 / green 推进 / yellow 提醒 / red 风险 / orange 重点 / purple 待办）|
| 渠道 / 标的 / 项目状态对照（≥4 行同结构） | `<table>` 表格，表头 `light-gray` 背景|
| 关键数字、人名、节点日期 | `<b>` 加粗（不用装饰 emoji 替代）|
| 章节层级 | `<h1>` 一级、`<h2>` 二级；不超 3 层 |
| 编号列表 | `<ol><li seq="auto">` 自动编号 |
| 并列对比（A 方案 vs B 方案 / 现状 vs 目标） | `<grid>` 双栏 |

**反例**：把整篇周报塞成纯 `<p>` 段落 + 行内 emoji。重点会埋掉。

**判断准则**：「读者一眼能不能找到风险 / 待办 / 关键数字」。找不到就用 callout 框 + 加粗 + 表格切出来。

**Front gate (all major forwardable outputs):** `/best-of-n` runs FIRST — N full-pipeline candidates → `biz-doc-critic` selects/merges — *before* any finish-chain order above. Canonical: [[CLAUDE.md]] § Skill Auto-Chain Rules § Enforcement; mechanics [[.claude/skills/best-of-n/SKILL.md]].

---

# § Localize-CN · 中文残留校验规则表

> **Loaded by:** **`[[.claude/skills/localize-cn/SKILL.md]]`** Phase 2 (scan + propose).

## 1. 称谓（最高优先级）

- ❌ {{USER_NAME}} → ✅ **高培尧**（per MEMORY.md `feedback_cn-monolingual-and-name`）
- ❌ "{{USER_NAME}} own" → ✅ "高培尧 负责"
- 例外：邮件签名 / 名片标识 / 英文专属档案（如 CV-EN）— 保留

## 2. 章节标题 / Section Headers

> **标准（{{USER_NAME}} 2026-06-02）**：结论先行段一律标 **概要**（纯英文文档用 **Overview**）。**永不使用「BLUF」字样** — 逻辑（结论/现状→问题→动作先行）保留，仅弃用该 jargon 标签。

| 英文 | 中文 |
|---|---|
| Overview / Executive Summary | **概要**（结论先行；亦可视语境用 **核心结论**） |
| Action Items | **待办** / **下一步** |
| Decision Made | **关键决议** |
| Raw Notes | **原始记录** / **备注** |
| Attendees | **与会人员** |
| Context | **背景** |
| Next Steps | **后续步骤** |
| Key Points | **要点** |
| Carry-forward | **沿用 / 待续** |

## 3. 英文动词残留（chat-residue 主源）

| 英文 | 中文 |
|---|---|
| commit | 承诺 / 锁定 |
| ship | 交付 / 发出 |
| push | 推进 / 推动 |
| carry | 沿用 / 累计 |
| anchor | 锚点 / 基准 |
| align | 对齐 |
| escalate | 升级 / 上报 |
| confirm | 确认 |
| ballpark | 区间估算 / 大致量级 |
| commit signal | 承诺信号 |
| soft asset | 软资产 / 关系资产 |
| deadline | 截止 |
| trigger | 触发 |
| baseline | 基线 |
| backfill | 补填 |
| handoff | 交接 |
| pull / push back | 推回 / 推回 |
| follow up | 跟进 |
| review | 评审 / 复盘 |
| spec | 规格说明 / 细则 |
| lock | 锁定 |
| sell | 讲得通 / 推得动 |
| framing | 定调 / 定位 |
| deck | 方案 / 方案材料 |
| leader / ld | 负责人 / 组长 |
| owner | 负责 / 责任方 |
| host | 主持 / 召集 |
| head | 负责人 / 头 |
| deep dive | 深度对接 / 深聊 |
| onboarding | 新手引导 / 入职 |
| introducer | 引子 / 导入 |
| supersede | 替代 / 取代 |
| sign-off | 正式签批 / 签批 |
| verify | 核实 / 验证 |
| incomplete | 不全 / 不完整 |
| fuller | 补全 / 更全 |
| benchmark | 对标 / 基准 |
| best practice | 最佳实践 |
| sub-speaker | 子讲者 / 二线发言 |
| narration | 叙述 / 描述 |
| design (作动词 / 名词) | 设计 |
| BD 对接 | 商务对接 |
| ML 路线 | 男性向二次元路线 |

## 4. body 内长尾 code-switch 词

| 英文 | 中文 |
|---|---|
| brief（作名词）| 简报 / 简要 |
| brief（作动词）| 简要说明 / 通气 |
| quote / key quote | 引用 / 关键引用 |
| metaphor | 隐喻 / 意象 |
| case / case study | 案例 / 案例研究 |
| session | 场次 / 时段 |
| framework | 框架 |
| trigger（作名词）| 触发 / 触发点 |
| pattern | 模式 / 范式 |
| dedup | 去重 |
| grind（游戏黑话）| 累积 / 反复刷 |
| boss（游戏术语）| 首领（严肃文档）/ boss（游戏圈内）|
| coser（二次元术语）| 扮演者（严肃）/ coser（圈内可保留）|
| focus | 重点 / 聚焦 |
| scope | 范围 / 边界 |
| surface | 表面 / 浮现 |
| leverage | 杠杆 / 撬动 |
| momentum | 势头 / 动能 |
| feedback（body 中名词）| 反馈 / 评价（section header 保留）|
| agenda | 议程 |
| baseline | 基线 |
| ad-hoc | 临时 |
| sanity check | 合理性核验 / 验真 |
| rubric | 评分准则 / 评判标准 |
| takeaway | 收获 / 要点 |
| caveat | 附注 / 限制 |
| polish | 打磨 / 精修 |
| push back | 推回 / 反驳 |
| hand off | 交接 |
| post-hoc | 事后 |
| pre-write | 写前 / 写时 |
| run-time | 运行时 |

**B 站术语类** — inline 保留可：BW / PV / coser / UP 主 / OTT / MAU / VT。句法仍 CN。
**行业 acronym 保留**：BD / KOL / IP / SDK / API / MCP / PMO 等接受。

## 5. 英文 jargon / 程度副词

| 英文 | 中文 |
|---|---|
| OK | 好 / 行 / 可以 |
| critical | 关键 |
| heavyweight | 重型 / 复杂 |
| lightweight | 轻 / 简易 |
| ad-hoc | 临时 |
| in-flight | 进行中 |
| open loop | 未决 |
| close-out / close the loop | 收尾 / 闭环 |
| escalation path | 上报路径 |
| commit window | 承诺窗口 |

## 6. 时间 / 数字 / 进度

| 英文 | 中文 |
|---|---|
| Q2 | Q2（保留，业务术语） |
| Week 20 / W20 | W20 或 第 20 周（视读者偏好） |
| TBD | 待定 |
| EOD | 下班前 / 当日截止 |

## 7. 状态 / 优先级

| 英文 | 中文 |
|---|---|
| in progress | 进行中 |
| pending | 待办 |
| blocked | 阻塞 |
| 🔴 must-fix | 🔴 必须修正（或直接用 emoji + 中文标签）|

## 白名单（保留，不要翻译）

- **专有名词与品牌：** TapTap · B 站 / Bilibili · {{PROJECT_A}} · 心动 · 诗悦 · {{ORG_C}} · ByteDance / 字节跳动 · Nuverse · HoYoverse / 米哈游 · SEGA · 任天堂 · Anthropic · OpenAI · Google · Apple
- **AI / 技术产品名：** Claude · Claude Code · GPT · Opus · Sonnet · Haiku · OpenClaw / 小龙虾 · Hermes-Agent · Obsidian · Notion · Cursor · MCP
- **版本号 / 测试节点：** v1 / v0.2 / CBT1 / CBT2 / OBT · A-tier / S 级 · P0 / P1 / P2
- **文件路径、命令行、代码块、URL** — 全部保留
- **标准缩写：** IP · KOL · KOC · BD · PMO · CEO · COO · ROI · LTV · DAU / MAU · SaaS · API · UI / UX · SOP · KR / OKR · NDA · ROFR · LOI · MOU · SDK · PC / iOS / Android
- **业务术语：** IPO · M&A · FO · JGC · JBR · DD · MBA · PE / VC · IC
- **文化 / 行业语：** ACG · GBA · NDS · BW · CJ

---

# § Humanize · AI 痕迹清除规则表

> **Loaded by:** **`[[.claude/skills/humanize/SKILL.md]]`** Phase 2 (pattern scan).
> **Source:** [blader/humanizer](https://github.com/blader/humanizer) (English) + [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) (Chinese).

## Content Issues (6)
1. **Significance inflation** — "pivotal moment", "intimate / deepest / most ambitious of its kind" → specific facts. Drop superlatives unless verifiable.
2. **Name-dropping** — "cited in NYT, BBC, FT" → actual quote or concrete reference; or cut.
3. **Vague -ing analyses** — "symbolizing, reflecting, showcasing, demonstrating" → state directly with source.
4. **Promotional language** — "world-grade", "breathtaking", "transformative", "game-changing" → neutral descriptors.
5. **Vague attribution** — "experts believe", "many argue" → name source or drop.
6. **Formulaic challenges** — "despite challenges, continues to thrive" → cut.

## Language Tells (6)
7. **Telltale vocabulary** — `actually`, `additionally`, `testament`, `landscape`, `realm`, `tapestry`, `paramount`, `pivotal`, `crucial`, `endeavor`, `delve`, `navigate`, `harness` (v), `leverage` (v), `unlock`, `unleash`, `bolster`, `cultivate`, `embark`, `seamlessly`, `meticulously`, `robust` (adj), `intricate`, `nuanced` — cut or replace with plain word.
8. **Copula avoidance** — "serves as", "features", "boasts", "represents" → prefer plain "is" / "has".
9. **Negative parallelisms** — "It's not just X, it's Y" / "Not only ... but also" → state second point directly.
10. **Rule of three** — artificial three-item lists ("A, B, and C") where only one/two are real → use natural quantities.
11. **Synonym cycling** — repeating same referent with different words ("protagonist, main character, central figure") in sequence → reuse the same word.
12. **False ranges** — "from X to Y" lists that aren't actually a range ("from the Big Bang to dark matter") → direct list.

## Style Markers (6)
13. **Em-dash overuse** ⚠️ **HIGH PRIORITY** (caught CV 2026-05-19 user feedback) — single loudest AI tell in modern English prose. **≤ 1 em-dash per ~300 words of body text**; never two em-dashes in same sentence. Substitution table:
    - Mid-sentence aside `X — Y — Z` → commas (`X, Y, Z`) or parentheses (`X (Y) Z`)
    - Em-dash before clarification → colon (`X — meaning Y` → `X: Y`)
    - Em-dash before contrast → semicolon or period (`X — but Y` → `X; but Y` or `X. But Y.`)
    - Em-dash for emphasis at end → drop dash, end sentence (`X — and that's the point` → `X. That's the point.`)
    - KEEP em-dashes for: date ranges (`Apr 2017 — Aug 2019`), citation separators in pull-quotes, stat-block key/val separators
    - After pass: count remaining em-dashes per 200-word window; if >1, another pass
14. **Excessive boldface** — bolding routine terms → reserve bold for proper nouns + the 4-5 most-anchored facts.
15. **Inline headers** — **`Header.`** or **`Header:`** pattern at sentence start → convert to prose or section header.
16. **Title Case headings** — ALL-CAPS / Title Case where lowercase would do → lowercase, unless real heading.
17. **Emojis and curly quotes** — remove emojis from formal artifacts; convert " " to standard quotes.
18. **Hyphenated pairs** — "cross-functional", "data-driven", "well-rounded" → drop hyphens where natural, OR use simpler word.

## CN AI 套话 — 中文专属 AI 痕迹 (2026-05-20 加 · 沪差0519 残留诊断触发)

中文 AI 写作有一套"高密度套话词"，看似专业但实际是 AI 训练偏差。**严格替换**：

| ❌ AI 套话 | ✅ 自然中文 |
|---|---|
| 深度对接 | 深聊 / 进一步对接 / 实质对接 |
| 全方位 / 全维度 | 各方面 / 多角度（看场景）|
| 一体化 / 一站式 | 整合 / 一并 / 一同（具体说明）|
| 闭环 / 形成闭环 | 完整 / 跑通 / 收尾（具体动作）|
| 赋能 / 全面赋能 | 帮助 / 支持 / 加持 |
| 抓手 | 切入点 / 着力点 |
| 拉齐 / 拉通 | 对齐 / 同步 |
| 颗粒度 | 粒度 / 细化程度 |
| 价值闭环 | 价值流转 / 价值链路 |
| 链路 | 路径 / 流程（除非真讲 chain）|
| 体感 | 实感 / 感受 |
| 沉淀 | 积累 / 留存 |
| 复盘 | 回顾 / 总结 |
| 抓机会 / 抢占心智 | 找机会 / 占领认知 |
| 顶层设计 | 整体规划 / 总体框架 |
| 战略级 / 战略性 | 战略 / 关键 |
| 拳头产品 / 战略级产品 | 主力产品 / 关键产品 |
| 拥抱 + 名词 | 接受 / 采纳 |
| 加速 + 名词 | 推进 / 提速 |
| 形成势能 / 蓄能 | 积累势头 / 准备力量 |
| 头部 / 头部企业 | 行业领先 / 第一梯队 |
| 范式 / 范式转移 | 模式 / 模式转变 |
| 长期主义 | 长期投入 / 坚持 |
| 卡位 / 占位 | 抢位 / 抢占 |
| 心智占领 | 占领认知 |
| 价值主张 | 卖点 / 核心价值 |
| 用户心智 | 用户认知 |
| 全链路 | 全流程 / 完整流程 |
| 内核 / 底层逻辑 | 核心 / 基本逻辑 |
| 落地 + 名词 | 实施 / 执行（除非"落地试玩会"等具体表达）|
| 持续 + 动词 + 名词 | 一直 + 动词（"持续推进"→"一直推进"或更精准词）|
| 多维度 | 多方面 / 多角度 |
| 痛点 | 问题 / 难点 |
| 风口 | 机会 / 时机 |
| 思维方式 / 心智模型 | 思路 / 想法 |
| 高维 / 降维 | 上层 / 下沉（除非真讲技术）|
| 元能力 / 元 + 名词 | 基础能力（不要装 meta-X）|
| 二次曲线 / 第二增长曲线 | 新增长点（不要装专业）|

**判断准则：** 这条短语在你{{PERSON_1}} / {{PERSON}} / 何宗寰 实际说话中会自然出现吗？如果不会，就是 AI 套话，必须替换。

## Tone Red Flags (7)
19. **Chatbot artifacts** — "I hope this helps!", "Let me know if...", "Feel free to..." → delete.
20. **Cutoff disclaimers** — "while details are limited", "as of my last update" → delete.
21. **Persuasive tropes** — "at its core, what matters is", "the truth is" → cut.
22. **Signposting** — "Let's dive in", "Here's what you need to know", "First, let me explain..." → cut.
23. **Hedging overload** — "could potentially possibly" → reduce to one hedge ("may" or "might").
24. **Generic conclusions** — "the future looks bright", "the possibilities are endless" → replace with specifics or cut.
25. **False humility** — "I'm just sharing my thoughts", "for what it's worth" → cut.
26. **Brag-as-modesty** — "I won't mention X (but here's X)" pattern → commit or cut entirely.
27. **Inflation by metaphor** — "this is the seed that grew into a forest" → drop or direct claim.
28. **Triplet rhythm in closes** — "concise, focused, and impactful" three-word adjective stacks → pick one.
29. **Self-citation as authority** — "as I've argued elsewhere" → cite or cut.

---

# § Pragmatic · 对话式记录风格（{{PERSON}}风格）规则集

> **Loaded by:** **`[[.claude/skills/pragmatic/SKILL.md]]`** Phase 3 (apply rules).

## 规则 1：二元分类用「正向 / 没那么正向」

```
✗ 不用: 优点 / 缺点 · strengths / weaknesses · 机会 / 风险 · 强项 / 弱项 · 利好 / 利空
✓ 用: 正向的 / 没那么正向的
```

「没那么正向」= face-saving 措辞，比「负向 / 缺点」温和，给对方留台阶。

## 规则 2：每条直接陈述 takeaway，无 editorial 解读

```
✗ 不要加: 
  · "版本质量背书已给"   (editorial 总结)
  · "这是核心推进点"     (emphasis)
  · "评级动态化通路被打开"  (抽象转译)
  · "进入到游戏设计层级对话" (语境补充)
  · "(参 [[TapTap]] § 当前{{PROJECT_A}}分级 A 级)" (引用追加)

✓ 听众假设 = 项目内人，不需要 explanation 层
```

## 规则 3：保留对方原话的感觉

```
✗ 不商务化翻译:
  「希望实际来玩包体」→ ❌「完成度待提升，期望深度试玩」
  「翻天覆地」→ ❌「质量取得显著改进」
  「想看一起做大」→ ❌「拟联合策划资源池放大」

✓ 用对方说的方式说
✓ 必要时可以直接保留口语「觉得」「了解了」「就是」「还是有点」
```

## 规则 4：拿掉所有装饰物

删除：emoji 标签（🅐🅑🅒 / 🔴🟢🟡 / 🔥）· bold ** **（除非真需要强调结构性差异）· italic * * · em-dash —（用句号/逗号/顿号代替）· 括号注（如 `(说话人 5, 推测 黄岩松)`）· wikilinks `[[]]` · 编号+横线分隔（`1. text — context`）

保留：阿拉伯数字编号（1. 2. 3.）· 中文句末标点（。, 、）· 必要时简要 parenthesis 注释（极简）

## 规则 5：中文句末标点 + 完整动词短语 + 单条 ≤30 字

每条独立成行 · 完整「主语+动词+宾语」（不堆叠）· 单条不超 30 字 · 句号/逗号收尾，不破折号补充。

例：
- ✓ "觉得产品翻天覆地，不是同一个游戏"（16 字）
- ✓ "对游戏框架了解了，认为有潜力"（14 字）
- ✗ "对游戏的框架了解后觉得有潜力 — 进入到游戏设计层级对话（问改造机制、对比塞尔达零件焊接、问 boss 机制）"（60+ 字）

## 规则 6：去名字化 section header + todo 主语

```
✗ section header 绑 specific person + title:
  · 「商务总监{{PERSON_4}}」· 「高培尧 负责」· 「{{PROJECT_A}}主创 负责（高培尧转达）」· 「TapTap 负责（仅记录）」

✓ section header 用职能 / 侧:
  · 「商务」· 「商务侧」· 「{{PROJECT_A}}侧」· 「TapTap侧」
```

todo 行同理：

```
✗ "回{{PERSON_4}}发布会节点（与{{PERSON}}+主创对齐...）"
✓ "发布会节点（与{{PERSON}}对齐...）"
```

为什么：项目内 doc 的 ownership 已经 implicit（谁写谁负责）。Section header 绑 specific person + title 让 doc 像私人 report 而不是 institutional record。具体名字保留在 inline 引用，header 与 todo header 用职能 / 侧。

## 规则 7：信息层 vs 决议层 — 项目内 briefing 用信息词汇

```
✗ 「关键决议」「锁定承诺」「确认对方承诺」「回暖」「锁定」
✓ 「关键信息」「核心反馈」「场内结论」「较好」
```

近义对照：

```
反馈回暖（情绪化判断）       → 反馈较好（中性观察）
对{{PROJECT_A}}新版本反馈（具体引用） → 对{{PROJECT_A}}的进步（抽象化）
一起做大一些（放大野心）     → 一起做好（适度）
```

为什么：项目内 briefing 是 informational layer，不是 decision-locking layer。对方在会议上说的话不应被 codify 成 commitment — 留余地。

## 规则 8：删 editorial parentheticals + 角色补充注

```
✗ 「{{PERSON_4}}（商务总监 / 召集人）」  →  ✓ 「{{PERSON_4}}」
✗ 「{{PROJECT_A}}主创 负责（高培尧转达）」 →  ✓ 「{{PROJECT_A}}侧」
✗ 「TapTap 负责（仅记录）」     →  ✓ 「TapTap侧」
✗ 「（出身长安幻想云上盛歌+蔚蓝星球 · 待确认姓名）」 → 删整段
```

判断准则：「（...）」 里如果是 AI 给读者的 helpful context，不是被引用对象原话，就删。

## 规则 9：核心结论 / 概要 排序 = 现状 → 问题 → 动作

```
✗ 现状好 → todo 列表 → "另外还有 3 个问题"
✓ 现状好 → 待关注 3 块 → todo 列表
```

后续动作里包含「回应这 3 块」，必须先说出这 3 块是什么读者才能读懂动作。

{{PERSON}}风格 概要 三段顺序：

```
1. 一句话现状（好 / 不好 / 分类）
2. 待关注 / 待回应的内容
3. 本周 / 短期 todo
```

## 规则 10：shareable 版剪掉 staging artifacts

项目内 vault 版可保留 staging（AI 转录校正字段表 · 跨场可复用基线 · 软项 / 个人社交 agenda · 报送字段 / 抄送对象）。但 push 到飞书 / 群 / PMO 可见版要剪掉。

判断准则：「这条对 audience 有 actionable value，还是只对我自己有 staging value？」后者 → vault 留，shareable 版剪。

配合 frontmatter：
```yaml
pragmatic-passed: 2026-05-19            # vault 版（保留 staging）
pragmatic-shareable-passed: 2026-05-19  # 剪过的 shareable 版
```

## 规则 11：不重复 概要 的 facts — 不开 recap section

```
✗ 不要写: 「关键信息」「核心要点」「会议要点」「主要结论」 类 recap section，
   把 概要 + § 各方反馈的 facts 再总结一遍

✓ 概要 一次。§ 各方反馈一次。§ 待办一次。不三遍。
```

若有「程序性安排」类信息（招募配额 / 试玩会到场 / 素材截止等非反馈项），拆进对应 owner 段（§ 商务 / § {{PROJECT_A}}侧）的尾部，不另开 recap section。

## 规则 12：游戏 / 产品反馈三元分类（不是二元）

```
✗ 二元：「正向 / 没那么正向」 (单纯 sentiment binary)
✓ 三元：「肯定 / 顾虑 / 建议」
```

BD 会议纪要中，对方对产品的反馈一般含三种性质：
- **肯定**：对方明确认可、表扬、定性正面（「翻天覆地」「质量提升显著」）
- **顾虑**：对方指出的问题点、风险、不足（「角色不对称执着太强」）
- **建议**：对方给的具体改进路径 / 行动 / 参考案例（「需后期写实材质压一压」「参一环做法挂蓝链」）

混在二元里建议会被顾虑吃掉，丢失对方提供的 actionable value。三元能让待办列表直接从「建议」列拉出。

## 规则 13：游戏反馈按主题切，非游戏反馈按功能切

```
✓ 游戏反馈按业务主题切:
  - 玩法 · 角色 / 美术 · 战斗 · 内容 / 剧情 · 风格 / 节奏 · 画面 / 融合度 · 宣发 / 评级 · 数据信号 · 商业化结构

✓ 非游戏反馈按功能切:
  - 商业化结构对接 · 协作意向与节点 · 测试期合作建议
```

游戏反馈按主题让读者看「他们对产品某个层面的整体印象」（编辑 + 运营 + 商业化对玩法都说了什么混在一起看）。按功能切会 burying 跨线共识。非游戏反馈按功能切才合理 — inherently belong to specific functional buckets。

锚点：[[feedback-bd-meeting-note-spec]] memory 中的默认 spec。

## Deal-debrief 模式（deal / 路演内容的覆盖规则）

> **何时启用**：纪要主体是 BD / deal 推进（评级、商业模型、资源、名额、金额、竞品对标、组织关系），而非产品反馈时。多 counterparty 路演速报是典型。内嵌的产品反馈块（如某编辑评价）仍按规则 1/12/13 走三元。
>
> 默认 13 条是按"接收产品反馈"提炼的，直接套在 deal 内容上会删掉价值。本模式覆盖其中 5 条：

**覆盖规则 2 / 7 / 8（不删 insider 判断）**：保留说话人 / 我方自己的**简短判断与口头按语** —「重点推进问题不大，但离持续维护评级侧关系」「搪塞过去了」「尹有信心」这类。删的是 AI 给读者补的解释层，不是内部人自己的判断。判准：**谁说的** —— 内部人的判断留，AI 的注解删。

**覆盖规则 5（不强拆 deal 事实簇）**：一连串"条款＋数字"允许成簇成行，不强切 ≤30 字、不强求完整主谓宾。"50+20，可做到至少30万，尹有信心"整条保留，拆开反而丢上下文。

**覆盖规则 1 / 12（deal 内容不做情绪分类）**：deal 推进按**事项**列，不套「正向 / 没那么正向」「肯定 / 顾虑 / 建议」。只有内嵌的产品反馈块才用三元。

**新增 — 逐字保留以下硬信息**（不可商务化、不可抽象、不可省）：
- 数字：金额、名额、占比、日活 / 月活等。
- 商业模型缩写：CPA / CPS / CPR 等。
- 评级与口头评价："原先 B，现比蓝色星原好"。
- 竞品对标："联想第一，小黑盒第二，高于顺网"、"如何跑赢异环"。
- 组织 / 关系情报："评级组和尹彧超群不是一个组"、"缺口在持续维护评级侧关系"。

**结构（每个 counterparty 一段）**：
```
{counterparty}
评级 / 关系：现状 + 口头评价 + 关系缺口。
可推进：逐条事项（数字、模型、资源原样）。
商业结构：模式 / 分成 / 路径（如有）。
竞品位置：对标口径（如有）。
风险：一行（如有）。
```
内嵌产品反馈单列小块，用三元（肯定 / 顾虑 / 建议）。完整 spec：[[feedback-meeting-spec-roadshow-debrief]]。

---

## 风格对照表（pragmatic vs 报告式）

| 维度 | 报告式总结 | 对话式记录（pragmatic）|
|---|---|---|
| 读者假设 | 需要 onboarding | 已知项目背景 |
| 每条结构 | takeaway + context | 仅 takeaway |
| 信息密度 | 中 | 高 |
| 语气距离 | 保持专业距离 | 短，像直接对话 |
| 原话保留 | 商务化翻译 | 保留对方原话感 |
| 分类 | 多维标签 | 二元 / 三元简单 |
| Editorial 层 | 有解读 / 引申 | 无 |
| 装饰物 | bold / emoji / em-dash | 全部删除 |
| 单条字数 | 不限 | ≤ 30 字 |
| 适用 | 外部 senior / IC / 董事会 | 项目内 PMO / 主创 / 团队 |
