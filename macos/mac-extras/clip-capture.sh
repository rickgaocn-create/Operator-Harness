#!/usr/bin/env bash
# mac-only: capture the current clipboard (pbpaste) into the vault's 00 Raw/Clippings inbox,
# the same inbox the Windows FileSystemWatcher feeds. Bind it to a macOS Shortcut, Raycast,
# or a Quick Action hotkey for one-keystroke capture from anywhere.
#
# Usage:  clip-capture.sh ["optional source label"]
set -euo pipefail

VAULT_ROOT="${OPERATOR_VAULT_ROOT:-{{VAULT_ROOT}}}"
VAULT_ROOT="${VAULT_ROOT/#\~/$HOME}"
INBOX="$VAULT_ROOT/00 Raw/Clippings"
mkdir -p "$INBOX"

command -v pbpaste >/dev/null 2>&1 || { echo "pbpaste not found (macOS only)"; exit 1; }
content="$(pbpaste)"
[[ -n "${content// /}" ]] || { echo "clipboard empty — nothing captured"; exit 0; }

label="${1:-clipboard}"
ts="$(date '+%Y-%m-%d-%H%M%S')"
out="$INBOX/(C) clip-$ts.md"
{
  echo "---"
  echo "type: clipping"
  echo "created-by: clip-capture"
  echo "created: $(date '+%Y-%m-%d')"
  echo "source: $label"
  echo "---"
  echo
  echo "$content"
} >"$out"

echo "captured -> $out"
# native confirmation banner if available
if command -v osascript >/dev/null 2>&1; then
  osascript -e "display notification \"$(basename "$out")\" with title \"Clipped to vault\"" >/dev/null 2>&1 || true
fi
