#!/usr/bin/env bash
# macOS launcher for the Feishu inbound event consumer (port of launch-consumer.ps1).
# Runs `lark-cli event consume` in a restart loop, draining inbound IM messages to the
# queue the feishu@local plugin reads. Loaded by com.operator-harness.feishu-event-consumer-daemon.
set -uo pipefail

HERE="$HOME/.claude/channels/feishu"
LOG="$HERE/consumer-daemon.log"
PIDFILE="$HERE/consumer-daemon.pid"
PROFILE="${LARK_PROFILE:-business-morty}"
EVENT="${FEISHU_EVENT_KEY:-im.message.receive_v1}"
OUTDIR="$HERE/queue/events"
mkdir -p "$OUTDIR"
echo $$ >"$PIDFILE"

command -v lark-cli >/dev/null 2>&1 || { echo "$(date '+%F %T') lark-cli not found on PATH" >>"$LOG"; exit 0; }

delays=(1 5 15 30); i=0
while true; do
  echo "$(date '+%F %T') consuming $EVENT (profile=$PROFILE)" >>"$LOG"
  lark-cli --profile "$PROFILE" event consume "$EVENT" --as bot --output-dir "$OUTDIR" >>"$LOG" 2>&1 || true
  d=${delays[$i]:-30}
  echo "$(date '+%F %T') consumer exited; restart in ${d}s" >>"$LOG"
  sleep "$d"
  (( i < ${#delays[@]}-1 )) && i=$((i+1))
done
