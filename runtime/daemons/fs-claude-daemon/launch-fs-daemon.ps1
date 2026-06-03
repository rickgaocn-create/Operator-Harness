$ErrorActionPreference = 'Continue'

# Feishu (Business Morty) daemon launcher — mirrors the afk-code-claude2 Discord
# daemon. Keeps a Claude Code session attached to the Feishu channel
# (plugin:feishu@local, queue-reader mode) alive 24/7 inside a ConPTY so it
# drains ~/.claude/channels/feishu/queue/events and auto-replies as the bot.
#
# Three layers of resilience, same as the Discord daemon:
#   1. shield.mjs       — swallows uncaught errors so the harness never dies
#   2. this restart loop — respawns the harness with backoff when Claude exits
#   3. (scheduled task RestartOnFailure + healthcheck task kick it if the whole
#      process tree dies)

$log    = "$env:USERPROFILE\.fs-claude-daemon\daemon.log"
$node   = 'C:\Program Files\nodejs\node.exe'
$shield = "$env:USERPROFILE\.fs-claude-daemon\shield.mjs"
$entry  = "$env:USERPROFILE\.fs-claude-daemon\fs-pty-harness.cjs"

# Convert Windows paths to file:// URLs for --import (Node ESM needs URL form on Windows)
$shieldUrl = 'file:///' + ($shield -replace '\\', '/')

# Backoff schedule (seconds); settles at 30s after the first 4 tries.
$backoffs = @(1, 5, 15, 30)
$attempt  = 0

"`n[{0}] fs-claude daemon launcher start (auto-restart loop · shield={1})" -f (Get-Date -Format o), $shieldUrl |
  Out-File -FilePath $log -Append -Encoding utf8

while ($true) {
  "[{0}] harness spawn attempt #{1}" -f (Get-Date -Format o), ($attempt + 1) |
    Out-File -FilePath $log -Append -Encoding utf8

  & $node --import $shieldUrl $entry *>> $log
  $exitCode = $LASTEXITCODE

  "[{0}] harness exited code={1} — restarting after backoff" -f (Get-Date -Format o), $exitCode |
    Out-File -FilePath $log -Append -Encoding utf8

  $delay = if ($attempt -lt $backoffs.Length) { $backoffs[$attempt] } else { 30 }
  Start-Sleep -Seconds $delay
  $attempt++
}
