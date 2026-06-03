$ErrorActionPreference = 'Continue'

# Feishu event-consumer daemon launcher — PERSONAL tenant (sibling of launch-consumer.ps1).
# Runs `lark-cli --profile morty-personal event consume im.message.receive_v1 --as bot` 24/7,
# writing inbound events to the SAME queue dir as the corporate consumer
# (~/.claude/channels/feishu/queue/events/). Both consumers share one queue; the MCP plugin's
# reader drains them in mtime order and dedups by event_id. Tenant_key + app_id in each event
# payload let the plugin route replies to the matching profile (option B: unified dual-tenant
# dispatch). Personal app: {{FEISHU_APP_ID}} ("Agent Morty"). Personal open_id for {{USER_NAME}}:
# {{FEISHU_OPEN_ID}}.

$root      = "$env:USERPROFILE\.claude\channels\feishu"
$queueDir  = Join-Path $root 'queue'
$eventsDir = Join-Path $queueDir 'events'
$log       = Join-Path $root 'consumer-personal-daemon.log'
$pidFile   = Join-Path $root 'consumer-personal-daemon.pid'

# lark-cli wrapper. Hardcode to npm global so the schtask doesn't depend on
# whatever PATH the daemon process inherits at logon.
$larkCli = "$env:APPDATA\npm\lark-cli.cmd"
if (-not (Test-Path $larkCli)) {
  "[{0}] FATAL: lark-cli not found at {1}" -f (Get-Date -Format o), $larkCli |
    Out-File -FilePath $log -Append -Encoding utf8
  exit 1
}

# Ensure queue dirs exist (shared with the corporate launcher).
New-Item -ItemType Directory -Force -Path $queueDir  | Out-Null
New-Item -ItemType Directory -Force -Path $eventsDir | Out-Null

# lark-cli --output-dir requires a relative path; we cd into $queueDir and pass
# 'events' so files land in $eventsDir.
Set-Location $queueDir

$profile = $env:FEISHU_LARK_PROFILE_PERSONAL
if ([string]::IsNullOrEmpty($profile)) { $profile = 'morty-personal' }
# Profile 'morty-personal' MUST bind to app {{FEISHU_APP_ID}} (PERSONAL "Agent Morty" bot,
# personal tenant). Verify with: lark-cli --profile morty-personal auth status --verify  →
# bot appName must read "Agent Morty". If the keychain entry `appsecret:{{FEISHU_APP_ID}}`
# is wiped (e.g. by a `config init --force-init` for a different app reusing this profile name),
# restore via: printf '%s' <secret> | lark-cli config init --name morty-personal
# --app-id {{FEISHU_APP_ID}} --app-secret-stdin --force-init.

$backoffs = @(1, 5, 15, 30)
$attempt  = 0

"`n[{0}] consumer launcher start (profile={1}, queue={2})" -f (Get-Date -Format o), $profile, $eventsDir |
  Out-File -FilePath $log -Append -Encoding utf8

$PID | Out-File -FilePath $pidFile -Encoding ascii

while ($true) {
  "[{0}] spawn attempt #{1}: lark-cli --profile {2} event consume im.message.receive_v1 --as bot --output-dir events" -f (Get-Date -Format o), ($attempt + 1), $profile |
    Out-File -FilePath $log -Append -Encoding utf8

  # No --quiet: keep the SDK's ready/connected/error lines in the log. The connect line is
  # the only signal the long-connection actually attached to Feishu (lesson from the
  # 2026-05-27 wrong-app incident on the corporate side).
  & $larkCli --profile $profile event consume im.message.receive_v1 --as bot --output-dir events *>> $log
  $exitCode = $LASTEXITCODE

  "[{0}] consumer exited code={1}" -f (Get-Date -Format o), $exitCode |
    Out-File -FilePath $log -Append -Encoding utf8

  $delay = if ($attempt -lt $backoffs.Length) { $backoffs[$attempt] } else { 30 }
  Start-Sleep -Seconds $delay
  $attempt++
}
