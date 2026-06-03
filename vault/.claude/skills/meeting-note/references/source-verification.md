---
type: reference
parent-skill: meeting-note
loads-when: "source includes AI-generated transcript (智能纪要 / 妙记 / 飞书 AI / OCR'd PDF) OR meeting has official agenda (multi-speaker summit)"
also-used-by: meeting-summary
created: 2026-05-21
---

# Source Verification · AI Transcripts + Official Agenda Cross-Reference

> Load when deep-mode Phase 1 detects AI-transcripts or multi-speaker meetings with published agendas.

## ⛔ Source Verification (AI-generated transcripts involved)

When sources include **智能纪要 / 妙记 / 飞书 AI 纪要 / OCR'd PDF / auto-minutes** of any kind:

1. **Read the source's own disclaimer** — most AI-generated minutes carry a "可能不准确，请谨慎甄别" notice. That notice must propagate forward; flag it in the meeting note's frontmatter (`source_warnings: [ai-generated-may-have-errors]`).
2. **Cross-verify model names, product names, and key numbers against ≥2 sources.** AI transcription commonly mishears proper nouns (e.g., "SeedDance" → "CDS" / "C-Dance"; "FORCE 大会" → "force大会"; vendor specifics → mangled English). User's hand-written notes + vendor PPT are the cross-check.
3. **If a term appears in only ONE source and looks unusual**, flag for user verification before treating as canonical: *"AI 纪要中出现 'X'，PPT/手记中未见 — 请确认是否为 'Y' 的转录错误。"*
4. **Numbers from AI transcripts**: cross-check arithmetic where possible (e.g., "周期 1 周 → 5 小时" appears in both 智能纪要 and user notes → trust; "8 模态" only in transcript → flag).
5. **⛔ 人名误识是最高频问题** — AI 转录 routinely 把外籍发言人名字识别成完全不存在的人（典型：Juan Gomez → "Wang Owen"；Thierry Labelle → "Ted Tieri"；Ryan McNeely → "Ryan"；Miles Perkins → "Mars"；Adams Holmes → "Adam"）。**人名必须以官方议程为准**，AI 转录名只作 fallback。

---

## Official Agenda Cross-Reference（多发言人会议必做）

若有任何形式的 **官方议程**（活动长图 / PDF / 群内分享 / 官网链接 / 会议邀请函）：

1. **以官方议程为人名 / 主题 / 时段的唯一可信源** — AI 转录里的人名几乎必有误识，议程是 ground truth
2. **建立 transcript ↔ agenda 映射** — 在 frontmatter `notes:` 字段记录所有校正：`Adams Holmes ← "Adam"；Miles Perkins ← "Mars"；AGBO ← "Aggo Studios"` 等
3. **议程图入档** — 引用议程图原文件（e.g. `[[00 Raw/Wechat/YYYY-MM-DD|官方议程长图]]`）作为 `sources` 字段第二条
4. **议程未覆盖的部分明示** — 录音始末时段 vs 议程时段对照表，标出哪些段未录到（茶歇 / Happy Hour / NDA 禁拍段）
5. **当议程 vs 转录冲突时** — 议程赢；但要在 `notes:` 写一行 "议程 vs 转录冲突项：…" 留审计
