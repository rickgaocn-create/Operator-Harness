---
layer: platform
paths:
  - "**/*.md"
pillar: Sensitivity · 敏感度护栏
binding: true
created: 2026-05-14
created-by: claude
---

# Sensitivity Guard · 敏感度护栏

> Binding rule for files with `sensitivity:` frontmatter. Mitigates Anthropic-cloud exposure risk by reducing unintentional Read of sensitive files.

## Levels

| Level | Examples | Read policy |
|---|---|---|
| `low` (default if unset) | normal vault content | No special handling |
| `medium-pii` | partner contact info, BD strategy with names | Allowed; mask phone/email when surfacing |
| `high-pii` | 身份证号 / 护照号 / 银行卡号 / 户籍住址 | **Display-mask sensitive fields** in any reply; log access |
| `max-pii` | 支付 PIN / passwords / cryptographic keys | **Never display in full** unless user explicitly asks for the literal value; log every access |

## Binding rules (Claude MUST follow)

1. **Don't proactively Read `high-pii` / `max-pii` files** unless the user explicitly names the file or the field is required to complete the user's stated task. Do not grep/glob across all vault for "sensitive content"; do not bring sensitive files into context for "completeness".

2. **When Reading is justified**, mask in reply by default:
   - High-PII fields: show last-4 only (`...0152` for card numbers, `1301...0614` for ID numbers)
   - Max-PII: show as `85**88` style or `[REDACTED]`. Provide full value only if user message contains an explicit phrase requesting the literal (`"give me the full PIN"`, `"show 完整 PIN"`, etc.)

3. **Log access** to **`04 Notes/sensitive-access-log.md`** after Reading any `high-pii` / `max-pii` file:
   - One line per access: `- YYYY-MM-DD HH:MM · <file relative path> · <trigger reason>`
   - Append-only; never edit prior entries

4. **Do not write sensitive content into auto-memory** (`~/.claude/projects/.../memory/`). The vault is canonical for these — auto-memory is for portable references only, not PII.

5. **Don't echo sensitive content in Bash output** when possible. Prefer Python with manual masking over `grep` that would expose values verbatim in tool results (which are kept in conversation history).

## Audit by user

{{USER_NAME}} can grep **`04 Notes/sensitive-access-log.md`** to see what was read when. If frequency / triggers don't match his memory of asks, he can investigate.

## Out of scope

This rule cannot:
- Prevent the data from traveling to Anthropic API once Read (the act of Read sends content as context)
- Enforce retention/deletion at Anthropic side
- Cover network egress from other tools (MCPs / Bash command output)

For those, see [[09 Rules/_archive/lane-isolation.md]] (if exists) and the longer-term plan in **`auto-memory/auto-doc-skills-update.md`** style routines.
