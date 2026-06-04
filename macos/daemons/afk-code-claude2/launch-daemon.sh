#!/usr/bin/env bash
# macOS launcher for the afk-code Discord bridge (port of launch-daemon.ps1).
# Runs the afk-code CLI with exponential-backoff restart. Loaded by the launchd agent
# com.operator-harness.afk-code-claude2-daemon (RunAtLoad + KeepAlive), so launchd also
# restarts the whole launcher if it ever exits.
set -uo pipefail

HERE="$HOME/.afk-code-claude2"
ENV_FILE="$HERE/discord.env"
LOG="$HERE/daemon.log"
# afk-code install location: prefer a global bin, else the repo runtime copy
AFK_BIN="$(command -v afk-code || true)"
[[ -n "$AFK_BIN" ]] || AFK_BIN="node $HOME/Developer/afk-code/dist/cli/index.js"

# load tokens (DISCORD_BOT_TOKEN, DISCORD_USER_ID) from the gitignored env file
[[ -f "$ENV_FILE" ]] && set -a && . "$ENV_FILE" && set +a

if [[ -z "${DISCORD_BOT_TOKEN:-}" ]]; then
  echo "$(date '+%F %T') no DISCORD_BOT_TOKEN in $ENV_FILE — not starting" >>"$LOG"
  exit 0
fi

delays=(1 5 15 30)
i=0
while true; do
  echo "$(date '+%F %T') starting afk-code discord bridge" >>"$LOG"
  # shellcheck disable=SC2086
  $AFK_BIN discord >>"$LOG" 2>&1 || true
  d=${delays[$i]:-30}
  echo "$(date '+%F %T') bridge exited; restart in ${d}s" >>"$LOG"
  sleep "$d"
  (( i < ${#delays[@]}-1 )) && i=$((i+1))
done
