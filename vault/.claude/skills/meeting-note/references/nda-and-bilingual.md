---
type: reference
parent-skill: meeting-note
loads-when: "deep-mode meeting includes NDA / 禁拍 content OR mixed CN/EN content needs governance"
created: 2026-05-21
---

# Deep Mode · NDA Handling + 中英混用 Governance

> Load when meeting contains NDA-marked content (vendor roadmap preview, preview release, 未公开战略) OR when CN/EN mixing needs explicit translation discipline.

## ⛔ NDA / 禁拍 内容标记约定

当任何环节属于「禁拍照 / 不外发 / 闭门」内容（典型：vendor 路线图预览 / preview release / 未公开产品方向）：

1. **章节级标记** — 子章节 heading 后缀 `（**部分 NDA**）` 或 `（**完全 NDA**）`
2. **frontmatter 字段** — 加 `nda-sections: [§2.6, §2.7]` 明示哪些段需 redact
3. **§ 风险与不确定 一段单列** — 标 "NDA 边界：[列具体段] 仅工作室内部决策层；转发前与 [对方对接人] 确认释放边界"
4. **biz-eval 输出同样需要 redact** — `/biz` chain 时把 NDA 段 abstract 为「[基于 NDA 路线图 hint，[结论摘要不含可识别细节]]」
5. **对外 report v1 路径** — Action Items 中明示 "去除 NDA 段后发 [上级]"

**典型 NDA 场景**：产品路线图预览、未发布版本 release notes、竞品内部数据、合作方未官宣战略方向、报价分档（vendor specific commercial floor）。

---

## ⛔ 中英混用偏好（降低 mixing，特别在表格 + 框架词）

**Default：内部呈报材料（meeting note + biz eval）应以中文为主。** AI 系统自动产出时常落入中英过度混用的 trap —— 表格列名 / 框架标签 / decision gates 用英文显得"专业"，实际对中文读者认知摩擦更大。

### 必须翻译为中文的（默认）

| 英文（避免）| 中文（首选）|
|---|---|
| Value Mechanism Decomposition | 价值机制拆解 |
| Beneficiary | 受益方 |
| Magnitude | 量级 |
| Defensive / Offensive / Option | 防御性 / 进攻性 / 战略期权 |
| Compounding Effects | 复利叠加效应 |
| Stack-or-nothing | 同进同退耦合 |
| Base / Worst / Best case | 基准 / 最差 / 最佳情形 |
| Sensitivity 分析 | 敏感性分析 |
| GO/NO-GO 闸 / Gate | 推进 / 否决 闸 / 决策门 |
| Pipeline | 管线 |
| Vendor | 供应商 |
| License | 授权 |
| Mitigation | 缓解措施 |
| Next Action | 下一步行动 |
| 概要 | 概要（保留即可，行业通用） |

### 可以保留英文的（专有 / 技术 / 行业通用）

- **产品 / 引擎名**：Unreal Engine / 虚幻引擎、UEFN、MetaHuman、MCP、USD、Lumen、Niagara、Blueprint、Sequencer、MegaLights、Mocopi
- **工种 / 流程**：Layout、cinematic、mocap、PoC、agent、diffusion 模型
- **公司名**：Epic / Sony Pictures Imageworks / AGBO / Blur / Anthropic（不强译）
- **框架短语**：概要、MECE、SCORARO、agentic、ROI
- **NPV / IRR / KPI / OKR / MoU 等通用金融 / 管理缩写**

### 判断规则

> "**如果一个中文读者第一眼能 1 秒内理解的英文术语 → 保留**；
> 否则 → 翻译为中文"。
>
> "表格列名 / 框架标签 / decision gates → **强制中文化**（这些是认知摩擦最高的位置）。"

### Anti-pattern

- ❌ 表格列名「Beneficiary / Magnitude / Timeline」并列出现
- ❌ "GO/NO-GO 闸" 出现在 概要 段（应：推进 / 否决 闸）
- ❌ "stack-or-nothing" 不加中文翻译就用
- ❌ "Lessons learned" / "deep dive" / "pain points" 这种本来就有完美中文（教训 / 深挖 / 痛点）的也用英文
