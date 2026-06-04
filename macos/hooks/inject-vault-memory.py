#!/usr/bin/env python3
"""SessionStart hook (macOS/cross-platform port of inject-vault-memory.ps1).

Injects the ALWAYS-ON CORE (me.md + CLAUDE.md) for sessions launched OUTSIDE the vault.
Skips when cwd is inside the vault (Claudian @imports the core natively) or BH_NO_INJECT=1.
On any uncertainty, injects (safe default: never silently drop the core).
"""
import json, os, sys

VAULT = os.path.expanduser(os.environ.get("OPERATOR_VAULT_ROOT", "{{VAULT_ROOT}}"))


def _norm(p):
    return os.path.normcase(os.path.normpath(os.path.expanduser(p))).rstrip("/\\")


def main():
    if os.environ.get("BH_NO_INJECT") == "1":
        return 0
    # cwd-aware skip
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        if raw.strip():
            cwd = (json.loads(raw) or {}).get("cwd")
            if cwd:
                c, v = _norm(cwd), _norm(VAULT)
                if c == v or c.startswith(v + os.sep) or c.startswith(v + "/"):
                    return 0
    except Exception:
        pass  # fall through and inject

    files = [(os.path.join(VAULT, "me.md"), "Identity"),
             (os.path.join(VAULT, "CLAUDE.md"), "Operating instructions")]
    sections = []
    for path, _desc in files:
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    sections.append(f"===== Vault file: {path} =====\n\n{fh.read()}")
            except Exception as e:
                sections.append(f"===== Vault file: {path} (read error: {e}) =====")
        else:
            sections.append(f"===== Vault file: {path} (not found) =====")

    header = (
        f"The following files from the user's Obsidian vault ({VAULT}) are the ALWAYS-ON CORE — "
        "identity + operating instructions. Treat them as the permanent memory bank. Write durable "
        "behavioral feedback / preferences / identity into the vault (me.md / 09 Rules / Cards / "
        "MEMORY.md incident log), where the learn-loop governs it. The Claude Code auto-memory "
        "directory is for MACHINE-LOCAL ops/infra pointers only — never durable knowledge.\n\n"
        "ON-DEMAND — NOT loaded here. READ the file before the relevant op:\n"
        "  - MEMORY.md             — incident-driven hard rules — before any high-stakes / forwardable write\n"
        "  - vault-map.md          — folder routing, skills index — when navigating the vault\n"
        "  - 09 Rules/file-types.md — (C)-prefix, frontmatter, naming — before creating/renaming framework files\n"
        "  - 09 Rules/cards.md      — Card pillar — before any 02 Cards/ op\n"
        "  - 09 Rules/action.md     — Action pillar + chain anchors — before any 10 Action/ op\n"
        "  - 09 Rules/time.md       — Time pillar — before time-cascade ops\n"
        "  - 09 Rules/tasks.md      — Task Capture Protocol — before bulk task writes\n"
        "  - 09 Rules/raw-immutable.md — 00 Raw/ immutability — before 00 Raw/ or 01 Wiki ops\n\n"
        "Binding hierarchy when files disagree: 09 Rules/* -> project CLAUDE.md -> root CLAUDE.md -> "
        "MEMORY.md (index, not source of truth).\n\n"
        f"Skills: {VAULT}/.claude/skills/<name>/SKILL.md. Subagents: {VAULT}/.claude/agents/<name>.md.\n"
    )
    ctx = header + "\n" + "\n\n".join(sections)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": ctx}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
