# Security & Sanitization

This repository is a **scrubbed** snapshot of a personal operator harness. It was built by copying the live system and then removing every secret and as much personal/proprietary content as practical. This document records exactly what was done so you can trust it — and where residual risk remains.

## What was REMOVED entirely (never copied / deleted)

- **Credentials & tokens:** `~/.claude/.credentials.json` (Anthropic OAuth), all Discord bot tokens (`*.env`), all Feishu `access.json` / `feishu-access.json`, WeChat/WeFlow tokens, the dashboard pairing QR (`auth-qr.png`), and every `.env`/`.env.bak`.
- **Personal vault content:** all numbered content folders (`00 Raw`, `01 Wiki`, `02 Cards` content, `03 Projects`, `04 Notes`, `06 Tasks`, `10 Action`), the `About Me/` folder (ID/passport/banking), embeddings (`.smart-env/`), session history (`.claudian/`), and all `_state` / `.daily-ingest-queue` runtime data.
- **Machine state:** logs, PIDs, `*.lastuuid`, caches, `node_modules`, `.venv`, `__pycache__`, `dist` build outputs (afk-code), and the personal `settings.local.json` allowlist (a minimal example ships instead).

## What was REDACTED in place (replaced with placeholders)

A scrubber rewrote all text files, replacing secrets, PII, and machine-specific values with `{{PLACEHOLDER}}` tokens. The identity files `me.md` and `MEMORY.md` were replaced with **fill-in skeletons** (their real content — bio, incident log — was personal and is gone). `priority_chats.json` was replaced with an illustrative example.

### Placeholder legend

**Machine values** — the installer (`bootstrap.ps1`) substitutes these automatically:

| Placeholder | Meaning |
|---|---|
| `{{VAULT_ROOT}}` | Absolute path to your Obsidian vault |
| `{{USER_HOME}}` | Your home dir (e.g. `C:\Users\you`) |
| `{{PYTHON_EXE}}` | Absolute path to your Python interpreter |
| `{{TASK_USER}}` | `DOMAIN\user` that scheduled tasks run as |
| `{{HOSTNAME}}` | Machine name |

**Your secrets / config** — you fill these in yourself (NOT auto-filled):

| Placeholder | Meaning |
|---|---|
| `{{FEISHU_APP_ID}}` | Your Feishu/Lark app ID (`cli_…`) |
| `{{FEISHU_OPEN_ID}}` / `{{FEISHU_CHAT_ID}}` / `{{FEISHU_MSG_ID}}` / `{{FEISHU_GROUP_ID}}` | Feishu identifiers |
| `{{WECHAT_ID}}` / `{{CALENDAR_ID}}` / `{{PHONE}}` / `{{UUID}}` | Personal identifiers |

**Personal identity / content** — rewrite in your own words:

| Placeholder | Meaning |
|---|---|
| `{{USER_NAME}}` | You |
| `{{ORG_A}}` … `{{ORG_G}}` | Organizations (employers, partners, vendors) |
| `{{PROJECT_A}}` / `{{PROJECT_B}}` / `{{PROJECT_C}}` / `{{FUND}}` | Projects / funds |
| `{{PERSON}}` / `{{PERSON_1}}` … `{{PERSON_8}}` | Other people |

## Verification

A multi-pass scan confirmed **zero** occurrences of: Anthropic keys (`sk-ant-`), GitHub PATs (`github_pat_`/`ghp_`), Slack tokens (`xox[bp]-`), Feishu app IDs (`cli_…`), Feishu open/chat/msg IDs (`ou_`/`oc_`/`om_`), WeChat IDs (`wxid_`), calendar IDs, the original username/hostname, absolute machine paths, and the known set of personal/company proper nouns.

## ⚠️ Residual risk — read before making this PUBLIC

This repo is intended to be kept **private**. The automated scrub caught all *structured* secrets and the *known* set of names/orgs, but **narrative example content** inside some skill specs and rule docs (e.g. `09 Rules/message-tone.md`, `meeting-note` references, trip templates) may still contain incidental internal context or a colleague name that wasn't on the known list. Before flipping this repository to public, do a manual pass over the files that contain `{{PERSON}}` / `{{ORG_*}}` placeholders and skim the `09 Rules/` and `vault/.claude/skills/` docs for anything organization-specific.

**If you ever committed a real secret by mistake:** rotate it immediately (a git rewrite is not enough — assume it's compromised).
