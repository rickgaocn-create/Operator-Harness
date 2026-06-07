---
type: brand-style-analysis
project: {{PROJECT_A}}
derived-from: "[[99 Attachments/Files/产品介绍示意(2).pptx]]"
extracted-at: 2026-05-15
extracted-by: claude
status: v0.1 (从单一参考样本反推 · 后续可叠加更多样本精修)
---

# {{PROJECT_A}} PPT 品牌样式分析 v0.1

> **来源**：2026-05-15 新版《{{PROJECT_A}}》介绍书（[[99 Attachments/Files/产品介绍示意(2).pptx]]，21 张，企业微信 cache 抓取）
>
> **目的**：作为 `/wangyue-pitch-deck` skill 的样式 ground truth，反推 BD 提案 PPT 应有的品牌调性 + 结构 + 元素库。

---

## 一、画布与全局规格

| 项 | 值 |
|---|---|
| 比例 | **16:9** widescreen |
| 尺寸 | 13.333 × 7.5 inches（pt = 960 × 540）|
| 张数 | 21（典型 BD 提案区间 12-21 张）|
| 母版 | 1 个，含 11 个 layout |
| 主导元素 | 图片（21/21 张都有图） |
| 图表 / 表格 | 0（数据全部以图形式呈现）|

## 二、品牌字体（hierarchy 4 层）

| 层 | 字体 | 用途 | 出现频率 |
|---|---|---|---|
| **中文主体** | **玄度** | 大部分正文 + 副标 | 264 次（最高）|
| **中文标题** | **方正VDL LOGO黑 简 SemiBold** | 章节标题 / 强调 | 66 次 |
| **中文强调** | **方正VDL LOGO黑 简 ExtraBold** | 关键 hero 字 | 2 次（sparse, 高浓度）|
| **英文** | **Barlow SemiBold** | tagline + Latin labels | 34 次 |
| **fallback** | Arial | 极少（兼容用） | 3 次 |

**字号阶梯（pt）**：
- 72pt — hero display（如封底大字 · sparse）
- 44pt — 章节大标题
- 32pt — slide 标题
- **28pt — body emphasis（出现最多 · 142 次 · 主力字号）**
- 18pt — 副标题 / panel label
- 16pt — body text
- 14pt — 注释 / footnote
- 11pt — caption / tagline

## 三、品牌 tagline （**load-bearing**）

```
ONE / UNITY / RISK EVERYTHING
```

- **几乎每张内容页都有** —— 是{{PROJECT_A}} PPT 视觉识别度的核心
- 字体：Barlow SemiBold
- 字号：11pt（caption 级别，不抢戏）
- 位置：通常顶部或角落（具体位置因 layout 而异）

**任何 BD 输出必须保留此 tagline** —— 这是{{PROJECT_A}} PPT 跟其他二游 deck 一眼区分开的标记。

## 四、标题命名约定

**模式**：`[节] - [副标]`

| 示例 | 节 | 副标 |
|---|---|---|
| 产品预约进展 | 产品 | 预约进展 |
| 产品里程碑 - 上线时间2027年 | 产品里程碑 | 上线时间2027年 |
| 产品进展 - 核心卖点 | 产品进展 | 核心卖点 |
| 美术 - 中式写实都市 | 美术 | 中式写实都市 |
| 玩法-人灵玩法 | 玩法 | 人灵玩法 |
| 发行节点-广州{{ORG_G}}试玩会 | 发行节点 | 广州{{ORG_G}}试玩会 |

**节级关键词词典**（从样本提取，未来 BD 提案应在此列表内选 + 必要时扩展）：
- 产品 / 产品进展 / 产品里程碑
- 美术（包含子主题：写实角色 / 写实场景）
- 玩法（包含子主题：人灵玩法 / 人灵战斗）
- 发行节点（试玩会 / 漫展 / 测试）
- ⚠️ 破折号前后**统一带空格**（`美术 - 中式写实都市` 优于 `美术-中式写实都市`，但样本两种都有，**未来版本统一化**）

## 五、章节结构（21 张样本的 narrative arc）

```
封面 (1)
  ↓
数据页 (2)         ← KPI hero: 600万 / Tap 215万 / B站 101万
  ↓
时间线 (3)         ← 4 milestones: 6月{{ORG_G}}试玩 / 7月BW / 8-10月二测 / 2027年上线
  ↓
章节扉页 1 (4)     ← "产品进展 - 核心卖点 / 中式写实都市 / 美术"
  ↓
内容页 5-10        ← 美术深挖: 写实角色 + 材质 + 渲染 + 场景 + TOD
  ↓
章节切换 (11)      ← 回扣 + 衔接
  ↓
章节扉页 2 (12)    ← "玩法-人灵玩法"
  ↓
内容页 13-18       ← 月灵设计 + 循环式玩法 + 战斗
  ↓
节点页 19-20       ← 试玩会 + BW（含场地 / 花费 / 嘉宾 / 联动）
  ↓
封底 (21)          ← 大图 + 回应封面
```

**节奏规律**：
- 每 5-7 张一个章节边界
- 章节扉页后**先给上下文**，再展开细节
- 内容页采用「图主文辅」—— 大图占视觉主导，文字 1-2 段精炼说明
- 节点页（发行类）独立成块，含具体投入规模数据（500W / 800W）+ 嘉宾联动

## 六、9 种 slide 类型库

| 类型 | 元素 | 样本张 | BD 提案用法 |
|---|---|---|---|
| **封面** | 全屏图 + 极少文字 | 1 | 项目名 + 副标 + 项目方 |
| **数据页** | hero 大字 + break-down + 日期 | 2 | KPI 数据 / 用户规模 / 流水 |
| **时间线** | 4-5 列 milestone | 3 | 合作 / 项目 / 发行节奏 |
| **章节扉页** | 大章节名 + tagline + 可选大图 | 4, 12 | 提案章节分隔 |
| **内容（图重）** | 标题 + 1-3 主图 + caption | 5-10, 14-18 | 能力展示 / 案例 / 产品细节 |
| **对比** | 左右 panel + 标签 | 9 | 现实 vs 渲染 / 当前 vs 升级 / 我方 vs 竞品 |
| **特性矩阵** | 3-4 feature 并列 + 配图 | 16, 17 | 能力点 / 服务包 / 差异化 |
| **发行节点 / 事件** | 事件名 + 场地 + 投入规模 + 嘉宾 + 联动 | 19, 20 | BD 重大节点 / 试玩会 / 异业联动 |
| **封底** | 大图 + 联系方式 | 21 | 致谢 / 联系信息 |

## 七、图片策略（核心）

> {{PROJECT_A}} PPT 的**视觉主导是图**，文字是辅助。这是高品质二游 deck 的标志性做法。

**图片类别**：
- 概念原画（角色 / 场景）
- 建模渲染（in-engine + 后期合成）
- 实机截图（含 watermark）
- 现实采风 vs 场景对比（如「珠江新城」对比图）
- 玩家评价 / 媒体引言（引用形式）
- 嘉宾 / coser / 联动伙伴 logo 矩阵

**含义**：BD 提案的 PPT skill 输出 **必须有图占位 / 图调用机制** —— 纯文字 PPT 跟{{PROJECT_A}} brand 不对位。

## 八、对 `/wangyue-pitch-deck` skill 的设计要求

| 要求 | 来源 |
|---|---|
| 16:9 widescreen 强制 | § 一 |
| 字体优先级 4 层（玄度 / 方正VDL / Barlow / Arial） | § 二 |
| 字号阶梯按 28pt body / 32pt title / 44pt section title 系统 | § 二 |
| **每张内容页必带** `ONE / UNITY / RISK EVERYTHING` tagline | § 三 |
| 标题命名 `[节] - [副标]`，破折号带空格 | § 四 |
| 章节 narrative arc：封面→数据→时间线→章节扉页→内容→切换→新章节→节点→封底 | § 五 |
| 9 种 slide 类型库（cover / data / timeline / section-divider / content-image-heavy / comparison / feature-grid / distribution-event / closing） | § 六 |
| 图占位 / 图调用机制（不允许纯文字 slide） | § 七 |

## 九、深度分析增量（2026-05-15 二轮）

### 9.1 真正的品牌 accent 调色板（替换 v0.1 推测）

| 颜色 | 用途 | 频率 |
|---|---|---|
| **#FFD800（金黄）** | **主 accent** — title underline / 章节 hero / 事件 banner / feature 短线 | **52 fill instances（top）** |
| **#0045E0（深蓝）** | 辅 accent — 子类标签 chip（1.59 × 0.39in 蓝底白字） | 28 fills + 3 lines |
| **#FFFFFF** | 正文文字主色 | 84 font color instances |
| **#000000** | 细描边（dots / panel）+ 黄底黑字（高对比） | 5 lines + 2 fills |

### 9.2 Shape 类型分布（280 个 shape 全统计）

| 类型 | 数量 | 用途 |
|---|---|---|
| TEXT_BOX | 114 | 标题 + 正文 + caption |
| PICTURE | 86 | 图驱动 |
| AUTO_SHAPE | 60 | accent 装饰（rectangles / ovals / brace 等）|
| GROUP | 16 | 复合元素 |
| LINE | 4 | 分隔线 |

**AUTO_SHAPE 内部 geometry 分布**：
- **RECTANGLE × 138 主导** — 几乎所有 accent / banner / underline / panel 都是矩形
- OVAL × 4 — 仅 slide 3 时间线的 4 个 dot
- LEFT_BRACE × 3 — slide 14 装饰边框（稀有）
- ROUNDED_RECTANGLE × 1 — slide 15 装饰角块

### 9.3 Signature anchor positions（出现 ≥ 3 张 slide 的精确坐标）

| 元素 | 精确位置 + 尺寸 | 颜色 | 出现 slides |
|---|---|---|---|
| **Gold title underline** ⭐ | (0.72, 1.67) × (5.02, 0.21) | #FFD800 | **5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18（13 张）** |
| Footer text box | (0.59, 6.92) × (3.14, 0.34) | — | 2, 3, 4, 11, 14, 15（6 张）|
| Footer text box variant | (0.68, 6.92) × (3.14, 0.34) | — | 12, 13, 18（3 张）|

**判读**：gold title underline 在 (0.72, 1.67) 位置 × (5.02, 0.21) 尺寸的 #FFD800 矩形 = **{{PROJECT_A}} PPT 的视觉签名**，缺失即偏离品牌。

### 9.4 视觉原语库（8 种签名 shape pattern）

| pattern | shape | 尺寸 (in) | 颜色 | 用途 | 典型 slide |
|---|---|---|---|---|---|
| **Title underline** | Rectangle | 5.02 × 0.21 @ (0.72, 1.67) | #FFD800 | 标题下方签名 underline | 5-10, 12-18 |
| Blue label chip | Rectangle | 1.59 × 0.39 | #0045E0 | 子类标签 (黑/白字) | 5, 6, 7 |
| Gold event banner | Rectangle | 3.28-5.74 × 0.28-0.34 | #FFD800 | 节点页嘉宾 / 联动 callout (黑字) | 19, 20 |
| Timeline dot | Oval | 0.15 × 0.15 | #FFD800 / #000000 | 时间线 milestone marker | 3 |
| Section hero block | Rectangle | 5.15 × 3.77 | #FFD800 | 章节扉页大 hero（黑字 44pt） | 4 |
| Feature underline | Rectangle | 2.68 × 0.14 | #FFD800 | feature 卡片底部装饰短线 | 16, 17 |
| Left brace | LEFT_BRACE | 0.3 × 2.42 | (varies) | 装饰边框（稀有）| 14 |
| Data emphasis bar | Rectangle | 3.94 × 0.21 | #FFD800 | 数据 hero 页的次级分隔线 | 2 |

### 9.5 Position grid（标准 anchor）

```
canvas: 13.333 × 7.5 in (16:9)

[Tagline 右上]         (8.6, 0.30) → width 4.5 right-aligned
[Title 文本框]         (0.72, 0.85) → width 11.0, height 0.7 · 32pt 方正VDL SemiBold 白
[Title underline 金条] (0.72, 1.67) → 5.02 × 0.21 #FFD800   ⭐ 签名
[Content 开始]         top ≥ 2.30
[Content 结束]         top ≤ 6.90
[Footer area]          (0.59-0.68, 6.92) → width 3.14, height 0.34

节点页变体：title underline 左移到 left=0.13（slide 19/20）
```

### 9.6 .pptx 模板（v0.1 落档）

[[.claude/skills/wangyue-pitch-deck/templates/wangyue-master.pptx]] — 40KB，9 张 slide，每张对应一种 slide type，全部 accent shape + position 已 baked。

**slide index → type 映射**：
1. cover · 2. data_kpi · 3. timeline_milestones · 4. section_divider · 5. content_image_heavy · 6. content_comparison · 7. feature_grid · 8. distribution_event · 9. closing

未来 `/wangyue-pitch-deck` skill 跑生成时：clone 此模板 → 复制对应 type slide → 替换 `[XXX]` 占位为实际内容 → 输出。

**模板可重建**：`[[.claude/skills/wangyue-pitch-deck/templates/_build-template.py]]` 是模板的可执行 source，brand tokens 改动后跑一遍即可重新生成。

---

## 十、v0.2 后续扩展（剩余 unknown）

| 局限 | 如何补 |
|---|---|
| 主 logo 文件路径未拿到 | 用户给 logo 文件（PNG / SVG）+ 标准位置；模板里加一个 `[LOGO]` 占位 shape |
| 没有 chart / table 模板（样本无）| BD 提案常需 capability matching table / ROI matrix / Gantt timeline → v0.2 加 3-5 个 chart 模板 |
| 英文版字号比例未验证 | 用户给 1 份英文版样本对照 |
| 真实背景渐变 / 复杂图层未克隆 | 模板用 solid `#0A0A14`；如{{PROJECT_A}}品牌实际用渐变背景，需 user 给 1 个参考背景图片 |
| LEFT_BRACE 装饰使用规则不清 | 1 张样本 slide 用了，规则不强；v0.2 看新样本是否复用 |

---

## Provenance

- 样本采集：企业微信 cache `WXWork/.../2026-05/产品介绍示意(2).pptx`（2026-05-15 同步进入 vault 99 Attachments/Files）
- 分析工具：python-pptx + 手工 review
- 分析脚本：[[99 Attachments/Files/_pptx-analysis.json]]（raw 数据）

## 关联

- Skill 主体：[[.claude/skills/wangyue-pitch-deck/SKILL.md]]
- Brand tokens：[[.claude/skills/wangyue-pitch-deck/brand-tokens.json]]
