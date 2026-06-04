#!/usr/bin/env bash
# Fired by the launchd WatchPaths agent com.operator-harness.RG-watcher-clippings whenever the
# clippings / card-inbox dirs change (event-driven, not polling). Drops a signal the SessionStart /
# UserPromptSubmit hooks drain, so the next session processes the new captures. The launchd-native
# replacement for the Windows FileSystemWatcher.
set -euo pipefail
VAULT_ROOT="${OPERATOR_VAULT_ROOT:-{{VAULT_ROOT}}}"
VAULT_ROOT="${VAULT_ROOT/#\~/$HOME}"
PENDING="$VAULT_ROOT/.claude/_pending"
mkdir -p "$PENDING"
ts="$(date '+%Y%m%d-%H%M%S')"
sig="$PENDING/${ts}-capture-process.signal"
{
  echo "skill: capture-process"
  echo "reason: clippings/card-inbox changed (launchd WatchPaths)"
  echo "at: $(date '+%F %T')"
} >"$sig"
# optional native nudge
command -v osascript >/dev/null 2>&1 && \
  osascript -e 'display notification "new capture to process" with title "Harness"' >/dev/null 2>&1 || true
