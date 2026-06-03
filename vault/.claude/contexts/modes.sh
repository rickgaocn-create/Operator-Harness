# Claude Code context-mode launchers — the HARD (interactive) variant of the /mode skill.
# bash + zsh. The macOS-side counterpart to modes.ps1 (syncs via the vault).
#
# Appends a persona to the DEFAULT system prompt via --append-system-prompt
# (verified on Claude Code 2.1.150). NEVER --system-prompt (that REPLACES the default
# and would strip your CLAUDE.md + SessionStart vault load). A normal --append launch
# keeps hooks + CLAUDE.md (only --bare skips those).
#
# Activate: add to ~/.zshrc (or ~/.bashrc) —
#   source "$HOME/Documents/{{USER_NAME}}/.claude/contexts/modes.sh"   # adjust to your vault path
#
# Usage:  claude-bd | claude-research | claude-afk | claude-mode <name>

# Resolve this file's dir in both bash and zsh:
if [ -n "${BASH_SOURCE:-}" ]; then
  _ecc_ctx="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  _ecc_ctx="$(cd "$(dirname "${(%):-%x}")" && pwd)"
fi
export _ecc_ctx

claude-mode() {
  local mode="$1"; shift 2>/dev/null
  if [ -z "$mode" ]; then echo "usage: claude-mode <bd|research|afk> [claude args...]"; return 1; fi
  local f="$_ecc_ctx/$mode.md"
  if [ ! -f "$f" ]; then
    echo "context mode '$mode' not found. Available: $(ls "$_ecc_ctx"/*.md 2>/dev/null | xargs -n1 basename | sed 's/\.md$//' | grep -v '^_' | tr '\n' ' ')" >&2
    return 1
  fi
  claude --append-system-prompt "$(cat "$f")" "$@"
}

claude-bd()       { claude-mode bd "$@"; }
claude-research() { claude-mode research "$@"; }
claude-afk()      { claude-mode afk "$@"; }
