@{{USER_HOME}}/Developer/browser-harness/SKILL.md

## AskUserQuestion → text-mode rendering (Discord/AFK visibility)

The `AskUserQuestion` tool renders a clickable picker in the local Claude Code UI but does NOT mirror into the Discord channel. When the user is AFK on Discord, that picker is invisible — they cannot see or answer the question, and the session stalls.

**Rule:** Do not call the `AskUserQuestion` tool for this user. Instead, output the question and its options as plain text in your normal response, then wait for the user's next message. Use this format exactly so the user can answer with just a number:

> ❓ **<one-line question>**
>
> 1. **<option label 1>** — <one-line description>
> 2. **<option label 2>** — <one-line description>
> 3. **<option label 3>** — <one-line description>
> *(Reply with the number, the label, or free text.)*

Constraints:
- Apply ONLY where you would have invoked `AskUserQuestion`. All other tool calls behave normally — this is not a "mirror everything to Discord" rule.
- Keep the question on one line, descriptions concise; the whole picker should fit in one Discord message.
- If you would have offered "Other (specify)" in `AskUserQuestion`, include the same option in the numbered list.
- After the user replies, parse their number/label and proceed as if it were an `AskUserQuestion` answer. Don't reinterpret a bare "1" as a stray keystroke when a text-mode picker is pending.

## Feishu reply formatting (rich posts + native bullets)

Always reply to {{USER_NAME}} on Feishu with **rich formatting**, never plain text or flattened markdown. The reply tool's send paths are NOT interchangeable — pick by what you need rendered:

- **Native bullet/numbered lists → the `md` tag inside a raw `content` post.** This is the ONLY path that renders real Feishu bullets:
  `reply(content={zh_cn:{title?, content:[[{tag:"md", text:"intro\n- a\n- b\n\n1. one\n2. two"}]]}})`.
  The plugin forwards row tags verbatim to Feishu, so the `md` tag renders true markdown (round bullets, `**bold**`, `` `mono` ``, `[t](url)`). One `md` element holds a whole multi-line block.
- **Do NOT use the `markdown` reply *param* for lists.** It pre-flattens `- item` into a **literal "- " text row** (a dash, not a Feishu bullet). It's fine for headers/bold-only replies, wrong whenever {{USER_NAME}} wants rendered bullets.
- **Never hand-type `·`/`•`/`-`/`1.` prefixes as plain text** in `content` rows — that's the pseudo-bullet anti-pattern. Use the `md` tag.

**cmd-metachar trap:** the send shells through `lark-cli.cmd` unquoted, so literal `& | < >` in message text break it. Use fullwidth ＆｜＜＞ or `/`、`；`. Quotes, ()%^*@#=$, backticks, CJK punctuation, emoji are safe.

Deep technical reference (post-JSON shape, emotion tags, reactions, the 2026-06-03 regression that produced this rule): auto-memory `feedback-feishu-rich-format`.
