#!/usr/bin/env python3
"""PreToolUse hook for Write/Edit — enforces CN-audience zero-English-residue rule.

Reads tool input JSON via stdin. If target path matches CN-audience patterns + content
has non-whitelist English in body → exit 2 (block tool, Claude sees stderr).
Otherwise → exit 0 (allow).

Escape hatches in frontmatter:
- `localize-cn: skip`  → skip check
- `audience: en`       → skip check
- `humanize: skip`     → does NOT skip CN check (different concern)
"""
from __future__ import annotations
import json, sys, re
from pathlib import Path

# Force UTF-8 on stdin/stdout/stderr (Windows default cp1252 breaks CN JSON)
for stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

# --- 1. Read tool input ---
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # malformed input, don't block

tool_name = data.get('tool_name', '')
if tool_name not in ('Write', 'Edit', 'NotebookEdit'):
    sys.exit(0)

tool_input = data.get('tool_input', {}) or {}
file_path = tool_input.get('file_path', '') or ''

# `content` = text to scan for residue. Write/NotebookEdit = full file; Edit = new_string (inserted text).
is_edit = not tool_input.get('content')
content = tool_input.get('content', '') or tool_input.get('new_string', '')
if not content:
    sys.exit(0)

# Opt-in frontmatter source: a Write carries it in `content`; an Edit's new_string does NOT, so
# read the TARGET FILE's frontmatter to decide opt-in (closes the Edit-path gap — 2026-05-25).
if is_edit:
    try:
        head = Path(file_path).read_text(encoding='utf-8', errors='replace')[:2000]
    except Exception:
        sys.exit(0)  # target unreadable (e.g. brand-new file via Edit) -> don't block
else:
    head = content[:2000]

# --- 2. Opt-in gate. Replaces the old broad path filter, which over-blocked at 52% on real
# files (daily notes, knowledge cards, vault-evolve system files all tripped it — measured
# 2026-05-25). Enforce ONLY on files that DECLARE they are CN-forwardable artifacts:
#   - `audience: cn` in frontmatter (explicit opt-in), OR
#   - a forwardable `type:` — meeting* / 会议* / internal-briefing / bd-update / market-intel /
#     periodic-report. Personal notes, cards, system files carry none of these → never checked.
# Escape hatches (audience: en/jp, localize-cn: skip) still win. ---
if 'localize-cn: skip' in head or 'audience: en' in head or 'audience: jp' in head:
    sys.exit(0)
m = re.search(r'^type:\s*(.+?)\s*$', head, re.MULTILINE)
ftype = (m.group(1).strip().strip('\'"').lower() if m else '')
FORWARDABLE = {'internal-briefing', 'bd-update', 'market-intel', 'periodic-report', 'biweekly'}
if not ('audience: cn' in head or ftype.startswith('meeting') or '会议' in ftype or ftype in FORWARDABLE):
    sys.exit(0)

# --- 4. Strip safe blocks (frontmatter, code, URLs, paths, wikilinks) ---
def strip_safe_blocks(text: str) -> str:
    # Strip frontmatter
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end > 0:
            text = text[end + 4:]
    # Strip code blocks (fenced + inline)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`\n]+`', '', text)
    # Strip URLs
    text = re.sub(r'https?://\S+', '', text)
    # Strip wikilinks
    text = re.sub(r'\[\[[^\]]+\]\]', '', text)
    # Strip markdown image and link refs
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    text = re.sub(r'\[[^\]]+\]\([^)]+\)', '', text)
    # Strip Windows file paths (D:\... etc.)
    text = re.sub(r'[A-Z]:[\\\/][\w\\\/\-\.一-鿿]+', '', text)
    # Strip unix paths (long paths starting with /)
    text = re.sub(r'(?<![\w])/(?:\w[\w\-\.]*[\\\/])+\w[\w\-\.]*', '', text)
    # Strip HTML comments (often vault staging markers)
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    # Strip filenames with extensions
    text = re.sub(r'\b[\w\-]+\.(?:md|py|json|cmd|ps1|sh|js|ts|yaml|yml|toml|html|css|cfg|conf|log|txt|csv|xlsx|pptx|docx|pdf)\b', '', text)
    return text

body = strip_safe_blocks(content)

# --- 4b. CN-artifact gate (WRITES only): the rule governs CN work-artifact BODIES, not
# English/mixed docs. For a full Write, only enforce when the body is predominantly Chinese
# (>=20% CJK) — an English design doc / CV is not a CN artifact. For an EDIT, the target file's
# frontmatter already established it's a CN-forwardable artifact, so a short English insertion IS
# residue regardless of its own CJK ratio — skip this gate. (verified 2026-05-25)
if not is_edit:
    cjk = len(re.findall(r'[一-鿿]', body))
    latin = len(re.findall(r'[A-Za-z]', body))
    if cjk + latin == 0 or cjk / (cjk + latin) < 0.20:
        sys.exit(0)

# --- 5. Residue DENYLIST — chat-residue English that has a CN equivalent. Source of truth:
# [[09 Rules/auto-chain-style.md]] § Localize-CN (categories 1-7). Keep roughly in sync; this
# fails SAFE — a term missing here = under-flag, never a false block on a brand / name / acronym.
# Flagging only KNOWN residue (not "all non-whitelist English") is what makes this gate safe to
# arm: brands (honor/oppo/steam), person names, tech acronyms (hdmi/udk) are never in this set. ---
RESIDUE = {
    "rick",  # 称谓: {{USER_NAME}} -> 高培尧 (signature/EN-doc exceptions handled by audience:en escape)
    "bluf", "attendees",
    "commit", "ship", "push", "carry", "anchor", "align", "escalate", "confirm", "ballpark",
    "deadline", "trigger", "baseline", "backfill", "handoff", "review", "spec", "lock", "sell",
    "framing", "deck", "leader", "owner", "host", "onboarding", "introducer", "supersede",
    "verify", "incomplete", "fuller", "benchmark", "narration",
    "brief", "quote", "metaphor", "session", "framework", "pattern", "dedup", "grind", "focus",
    "scope", "surface", "leverage", "momentum", "feedback", "agenda", "rubric", "takeaway",
    "caveat", "polish", "follow",
    "critical", "heavyweight", "lightweight", "pending", "blocked", "tbd",
    "carry-forward", "sign-off", "ad-hoc", "post-hoc", "must-fix", "close-out", "in-flight",
    "push-back", "hand-off", "sanity-check", "best-practice", "deep-dive",
}

# --- 6. Flag only English chunks that ARE in the residue denylist ---
english_chunks = re.findall(r'[A-Za-z]+(?:[-_][A-Za-z]+)*', body)
violations = []
seen_offenders = set()
for chunk in english_chunks:
    lc = chunk.lower()
    if lc in RESIDUE and lc not in seen_offenders:
        seen_offenders.add(lc)
        violations.append(chunk)

if not violations:
    sys.exit(0)

# --- 7. Build error message + block ---
unique = sorted(set(v.lower() for v in violations))
msg_lines = [
    f"🔴 CN-audience zero-English violation in: {file_path}",
    f"Found {len(unique)} CN-residue term(s) (English with a CN equivalent) in body:",
    f"  {', '.join(unique[:20])}{' ...' if len(unique) > 20 else ''}",
    "",
    "Per CLAUDE.md § Hard Fails, CN work artifact body must be monolingual.",
    "Fix options:",
    "  (1) Replace English with CN per .claude/skills/localize-cn/SKILL.md 50+ wordlist",
    "  (2) Add `localize-cn: skip` to frontmatter if intentional EN-mixing required",
    "  (3) Add `audience: en` or `audience: jp` to frontmatter if not CN audience",
    "  (4) Common: commit→承诺/锁定/应下, framing→定调, deck→方案材料, brief→简报, grind→累积, OK→可以/行",
    "",
    "Edit content + retry Write tool.",
]
print('\n'.join(msg_lines), file=sys.stderr)
sys.exit(2)
