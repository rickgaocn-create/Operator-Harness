---
layer: instance
type: instance-config
for-rule: "[[09 Rules/trip-application]]"
created: 2026-05-25
created-by: claude
---

# Instance config · Trip-application defaults ({{USER_NAME}})

> Concrete defaults the [[09 Rules/trip-application]] archetype consumes. A teammate swaps these for their own org's form, approver, and entity; the archetype (sections, fields, hard rules) is platform.

## xlsx申请表 baseline
- **Template:** `07 Attachments/差旅预定协助申请表 2026-05-14_上海_高培尧_v3.xlsx` (2 sheets: 申请表 + 差旅费支付明细表)
- **Output location:** `03 Projects/{{PROJECT_A}}/07 Attachments/` (or the active project's `07 Attachments/`)
- **No `(C)` prefix** — administrative form, not a Claude narrative.

## 邮件
- **Template:** [[(C) 差旅申请邮件模板]]
- **Recipient:** 梁艳琳（行政 · 木木）
- **Cc roster:** 直接上级 · 行政人事总监 · 财务 · CEO
- **Output location:** `03 Projects/{{PROJECT_A}}/03 行程计划/`

## 申请人 identity (pointers — don't inline PII)
- 高培尧 ({{USER_NAME}}) · {{ORG_C}}发行 · {{PROJECT_A}} — see [[About Me/identity-documents]] · [[About Me/employment]]
- **合同主体 (报销公司主体):** per MEMORY § Employment Entity — may ≠ project entity; never change without consulting it.
