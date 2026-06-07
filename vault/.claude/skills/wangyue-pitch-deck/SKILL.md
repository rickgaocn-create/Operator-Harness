---
category: work
name: wangyue-pitch-deck
description: Generate Wangyue-branded PowerPoint decks from approved source material. Use for BD pitches, internal reports, or investor-facing Wangyue presentations.
model: claude-opus-4-7
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Skill: {{PROJECT_A}}品牌 PPT 生成器

> 把任意 BD 提案 / 报告 / 评估 markdown，转成符合{{PROJECT_A}}品牌调性的 .pptx 文件。
>
> **底座**：Anthropic 官方 `pptx` skill（user-global · 已装 2026-05-14）。
> **包装层**：{{PROJECT_A}}品牌 tokens + 9 种 slide 类型库 + 章节 narrative arc。

## 何时触发

- 「做一份{{PROJECT_A}} deck / {{PROJECT_A}} PPT」
- 「把 (C) XXX v0.1.md 做成 PPT」
- 「生成对外 / partner-facing / 对内 / 致{{PERSON}} 等 PPT」
- 显式 `/wangyue-pitch-deck` 或 `/{{PROJECT_A}} pitch`

**不触发**：HTML 演示 / 网页 slides / 通用非{{PROJECT_A}} PPT —— 那些走 Anthropic 原生 `/pptx`。

## 何时**不**用

- 学术 / 论文 / 数据分析 deck（用 `/pptx` 原生）
- 跨项目 / 个人 / {{ORG_B}} 项目的 PPT（建另一个 skill `/{{ORG_B}}-inc-pitch-deck`）
- 单页 onepager（用 `/design`）
- 海报 / KV 视觉物料（用 `/design`）

---

## 流程

### Phase 1: Read 源材料

读用户指定的源 markdown（pitch / 评估 / 报告）。优先来源：
- **`03 Projects/{{PROJECT_A}}/Pitches/(C) *.md`**
- **`03 Projects/{{PROJECT_A}}/09 Reports/(C) *.md`**
- **`03 Projects/{{PROJECT_A}}/04 会议纪要/*.md`**（如要 cinematic-style 后续 follow-up deck）

如未指定 → 列最近修改的 3-5 个候选，让用户选。

### Phase 2: 询问参数（≤ 4 个 ask）

```
1. 受众场景: (a) 对外 partner-facing / (b) 内部 cc {{PERSON}} / (c) 投资人 / (d) 高规格 vendor
2. 张数目标: 12-15 (lean) / 16-21 (standard) / 22-30 (深度 deck)
3. 语言: 中文 / 中英 / 英文 (后两个对应英文 spec — 字号微调)
4. 重点章节 (可多选): 数据进展 / 产品 / 美术 / 玩法 / BD 商务 / 发行节点 / 价值评估
```

每个都有 default（受众=对外 / 张数=16-21 / 语言=中文 / 重点=自动从源材料推断），用户可省略以接受 default。

### Phase 3: 章节 narrative arc 生成

按 [[brand-tokens.json]] § section_structure 的 default arc，结合源材料内容选择子集：

```
封面 → 数据/进展 → 时间线 → 章节扉页 → 内容(N) → 切换 → 新章节扉页 → 内容(N) → 节点 → 封底
```

提案类（如 (C) 雷电模拟器 - 6月线下+软文响应方案）的 arc 调整：
- 封面 → 我方 BD 立场（数据页）→ 对方提议 timeline → 章节扉页（我方分析）→ 决策点 4 张 → 章节扉页（价值评估）→ 能力匹配 + 时间线 + ROI → 节点 / 边界 → 封底

让用户确认 arc 后再生成（避免做完再返工）。

### Phase 4: Clone template + 应用品牌 tokens

**正确流程（template-first）**：
1. **不** 从空白生成 —— 而是 clone 现成模板：[[.claude/skills/wangyue-pitch-deck/templates/wangyue-master.pptx]]
2. 模板含 9 张 slide，每张 = 一种 slide type 的视觉原语（gold underline / blue chips / timeline dots / tagline 全已就位）
3. 对每张要生成的 slide：复制模板对应 type 的 slide → 替换占位文本 `[XXX]` 为真内容 → 替换占位图片 panel 为真图（或保留占位让用户后填）

**slide type → 模板 slide index 映射**（见 `brand-tokens.json § template_file`）：

| 你想做的 slide | 用模板第几张 |
|---|---|
| 封面 | 1 (cover) |
| 数据 hero (e.g., 600万预约) | 2 (data_kpi) |
| 时间线 / milestone | 3 (timeline_milestones) |
| 章节扉页 | 4 (section_divider) |
| 内容（图重 + 蓝色标签）| 5 (content_image_heavy) |
| 对比（左右 / 上下）| 6 (content_comparison) |
| 3 列特性矩阵 | 7 (feature_grid) |
| 发行节点 / 事件 | 8 (distribution_event) |
| 封底 | 9 (closing) |

**Python-pptx 实现示例**（伪代码）：
```python
from pptx import Presentation
import copy
from lxml import etree

TPL = Presentation(".claude/skills/wangyue-pitch-deck/templates/wangyue-master.pptx")
OUT = Presentation(".claude/skills/wangyue-pitch-deck/templates/wangyue-master.pptx")

# 删除 OUT 里除第 1 张外的 slides（保留 cover 起步）
# 然后按 plan 一张一张复制模板对应 type 的 slide 进 OUT

def copy_slide_from_template(out_prs, tpl_slide):
    # 用底层 XML 操作复制 slide（python-pptx 没有原生 copy_slide API，需 monkey-patch lxml）
    blank_layout = out_prs.slide_layouts[6]
    new_slide = out_prs.slides.add_slide(blank_layout)
    for shape in tpl_slide.shapes:
        new_el = copy.deepcopy(shape.element)
        new_slide.shapes._spTree.insert_element_before(new_el, 'p:extLst')
    return new_slide

# 然后 grep + replace 占位:
def replace_placeholder(slide, marker, new_text):
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if marker in run.text:
                        run.text = run.text.replace(marker, new_text)
```

**品牌 tokens 已 encoded 在模板里**（fonts / sizes / colors / positions / tagline），所以 phase 4 不需要再"注入"这些 — 直接 clone + 改字即可。

### Phase 4b: 完整 brand tokens 参考

如需手工对照（不 clone 模板, 完全自建 slide）：

```python
# 画布
CANVAS = (Inches(13.333), Inches(7.5))  # 16:9

# 字体栈
FONTS = {
  "cn_body": "玄度",
  "cn_head": "方正VDL LOGO黑 简 SemiBold",
  "cn_heavy": "方正VDL LOGO黑 简 ExtraBold",
  "latin": "Barlow SemiBold",
  "fallback_latin": "Arial",
}

# 字号阶梯 (pt)
SIZES = {
  "hero_display": 72, "section_title": 44, "slide_title": 32,
  "body_emphasis": 28, "subtitle": 18, "body": 16,
  "footnote": 14, "caption": 11,
}

# 品牌色
COLORS = {
  "gold": "#FFD800",       # 主 accent — title underline 等
  "blue": "#0045E0",       # 辅 accent — 标签 chip
  "white": "#FFFFFF",      # 正文文字
  "black": "#000000",      # 黄底黑字 (高对比) + 细描边
  "dark_bg": "#0A0A14",    # 默认深色背景
}

# 签名 anchor
TITLE_UNDERLINE = (Inches(0.72), Inches(1.67), Inches(5.02), Inches(0.21))
TAGLINE = "ONE / UNITY / RISK EVERYTHING"
TAGLINE_POS = (Inches(8.6), Inches(0.30), Inches(4.5), Inches(0.3))  # right-aligned
```

**永远先尝试 clone 模板**，只在用户明确说"要个特殊新 slide type"时才走 phase 4b 自建。

### Phase 5: 图片占位策略

{{PROJECT_A}} PPT 是图驱动的。对每张内容 slide：

1. **优先用源材料里已有的图**（如 .md 内 `![[]]` embed 的截图 / 概念图）
2. **次优**：在 vault 内 grep 相关项目图片（`07 Attachments/` · `99 Attachments/Files/`）
3. **未命中**：插入占位图 + 在 slide 注释里写「TODO: 替换为 X 实机截图」让用户后填
4. **绝不**：用 stock photo / AI 生成"凑数图" —— {{PROJECT_A}}品牌不允许

### Phase 6: 输出 + 落档

| 受众 | 输出路径 |
|---|---|
| 对外 partner-facing | **`03 Projects/{{PROJECT_A}}/Pitches/(C) [pitch-name] · {{PROJECT_A}}版 v[X].pptx`** |
| 内部 cc {{PERSON}} | **`03 Projects/{{PROJECT_A}}/09 Reports/(C) [report-name] v[X].pptx`** |
| 投资人 | **`03 Projects/{{PROJECT_A}}/Pitches/(C) [investor-name] 介绍 v[X].pptx`** |

生成完后：
1. 在源 markdown frontmatter 加 `deck-output: "[[(C) ... .pptx]]"`
2. 打印 confirm 给用户：路径 + 张数 + 已用 / 未用的 slide 类型
3. 提示用户在 PowerPoint / WPS 打开做最后人工 polish（**永远不假设 skill 输出即终稿**）

### Phase 7: Auto-chain（可选）

如源 markdown 是新的（无对应 `/biz` 评估），可选 chain `/biz`。但**不强制** —— PPT 是分发工具，不是分析工具。

---

## Hard Rules

1. **永远 16:9** —— {{PROJECT_A}}品牌画布。4:3 拒绝。
2. **每张内容 slide 必带 tagline** `ONE / UNITY / RISK EVERYTHING`。漏一张视为 brand 违规。
3. **标题命名 `[节] - [副标]`** —— 破折号前后带空格（统一化 `美术 - 中式写实都市` 而非 `美术-中式写实都市`）。
4. **图驱动** —— 任何纯文字 slide 都是 anti-pattern。最少 1 张主图占视觉主导。
5. **字体降级链** —— 没装玄度 → 思源黑体；没装方正VDL → 思源黑体 Bold；没装 Barlow → Inter SemiBold。Arial 是最后 fallback。
6. **永远不在 skill 内部假设终稿** —— 输出 confirm 时明示「请在 PowerPoint / WPS 内人工 polish 视觉调性细节」。
7. **不引入非{{PROJECT_A}}配色** —— 配色暂保留 white-on-dark 主调，v0.2 扩 brand 调色板后才解锁多色。

---

## Anti-Patterns

- ❌ 4:3 画布（行业标准 + {{PROJECT_A}}样本都是 16:9）
- ❌ 纯文字 bullet list slide（违反图驱动原则）
- ❌ 用 Microsoft 默认字体（Calibri / SimSun）—— 没装玄度也要 fallback 到思源
- ❌ 漏 tagline 或自定义改字（如改成「Wangyue / {{PROJECT_A}} / Risk」—— 偏离 brand）
- ❌ 数据用文本写（如「累计预约 600 万」用 16pt body 字号）—— 应用 hero_display 72pt 或 section_title 44pt
- ❌ AI 生成图占位 — {{PROJECT_A}}品牌不接受
- ❌ Slogan 在英文场合译为「One Unity Risk」—— 保留原文不译
- ❌ 输出 v1 就 cc {{PERSON}} —— 永远 v0.1 内部 review 后再 v1.0 外发

---

## 当前 v0.1 局限（你需要知道）

- 背景渐变 / 色块的具体色值还在反推 —— 输出默认偏 white-on-dark 高对比，需用户在 PPT 内手动 polish 配色
- Logo 文件路径未配置 —— v0.2 加入
- 不支持图表 / 表格 自动生成（样本里都是图，没有 chart） —— v0.2 加 5-6 个 BD 常用 chart 模板（capability matching / ROI matrix / timeline gantt）

**实操建议**：先跑一次试试，看哪部分 polish 工作量大，那部分就是 v0.2 优先 backlog。

---

## 参考

- 样式分析全文：[[.claude/skills/wangyue-pitch-deck/references/style-analysis-2026-05-15]]
- 品牌 tokens：[[.claude/skills/wangyue-pitch-deck/brand-tokens.json]]
- 原始样本：[[99 Attachments/Files/产品介绍示意(2).pptx]]（21 张新版《{{PROJECT_A}}》介绍书 · 2026-05-15）
- 底座 skill：Anthropic 官方 `pptx`（user-global · `~/.claude/skills/pptx/`）
- 关联：[[(C) 12 - 动画管线深度 · 实时与离线工作流]] § 二游 stylized 章节
