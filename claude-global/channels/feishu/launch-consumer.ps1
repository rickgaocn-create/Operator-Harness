$ErrorActionPreference = 'Continue'

# Feishu event-consumer daemon launcher.
# Runs `lark-cli event consume im.message.receive_v1 --as bot` 24/7, writing each
# inbound event to ~/.claude/channels/feishu/queue/events/<id>.json. The Feishu MCP
# plugin (in any fs-claude session) drains and deletes those files. Decouples
# inbound delivery from Claude session lifetime so messages sent while no
# session is up get processed on next launch.

$root      = "$env:USERPROFILE\.claude\channels\feishu"
$queueDir  = Join-Path $root 'queue'
$eventsDir = Join-Path $queueDir 'events'
$log       = Join-Path $root 'consumer-daemon.log'
$pidFile   = Join-Path $root 'consumer-daemon.pid'

# lark-cli wrapper. Hardcode to npm global so the schtask doesn't depend on
# whatever PATH the daemon process inherits at logon.
$larkCli = "$env:APPDATA\npm\lark-cli.cmd"
if (-not (Test-Path $larkCli)) {
  "[{0}] FATAL: lark-cli not found at {1}" -f (Get-Date -Format o), $larkCli |
    Out-File -FilePath $log -Append -Encoding utf8
  exit 1
}

# Ensure queue dirs exist.
New-Item -ItemType Directory -Force -Path $queueDir  | Out-Null
New-Item -ItemType Directory -Force -Path $eventsDir | Out-Null

# lark-cli --output-dir requires a relative path; we cd into $queueDir and pass
# 'events' so files land in $eventsDir.
Set-Location $queueDir

$profile = $env:FEISHU_LARK_PROFILE
if ([string]::IsNullOrEmpty($profile)) { $profile = 'business-morty' }
# Profile 'business-morty' MUST bind to app {{FEISHU_APP_ID}} (the COMPANY "Business Morty"
# bot, tenant 2cb5e0f5340d575d; {{USER_NAME}}'s open_id there = {{FEISHU_OPEN_ID}}).
# 2026-05-27 incident: a `config bind --source hermes` repointed this profile to Hermes's own
# app {{FEISHU_APP_ID}} ("Morty") by mistake, so the listener consumed the wrong app and
# inbound DMs silently vanished. Verify with: lark-cli --profile business-morty auth status
# --verify  → bot appName must read "Business Morty". Do NOT rebind via --source hermes.

$backoffs = @(1, 5, 15, 30)
$attempt  = 0

"`n[{0}] consumer launcher start (profile={1}, queue={2})" -f (Get-Date -Format o), $profile, $eventsDir |
  Out-File -FilePath $log -Append -Encoding utf8

$PID | Out-File -FilePath $pidFile -Encoding ascii

while ($true) {
  "[{0}] spawn attempt #{1}: lark-cli --profile {2} event consume im.message.receive_v1 --as bot --output-dir events" -f (Get-Date -Format o), ($attempt + 1), $profile |
    Out-File -FilePath $log -Append -Encoding utf8

  # No --quiet: keep the SDK's ready/connected/error lines in the log. They are the only
  # signal that the long-connection actually attached to Feishu (the 2026-05-27 wrong-app
  # incident was hard to diagnose precisely because --quiet had hidden them).
  & $larkCli --profile $profile event consume im.message.receive_v1 --as bot --output-dir events *>> $log
  $exitCode = $LASTEXITCODE

  "[{0}] consumer exited code={1}" -f (Get-Date -Format o), $exitCode |
    Out-File -FilePath $log -Append -Encoding utf8

  $delay = if ($attempt -lt $backoffs.Length) { $backoffs[$attempt] } else { 30 }
  Start-Sleep -Seconds $delay
  $attempt++
}
