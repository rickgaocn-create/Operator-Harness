# setup_schedule.ps1 — register `{{USER_NAME}}-daily-emit` as daily 08:00 Windows Task
# Idempotent.
#
# Install:
#   powershell -ExecutionPolicy Bypass -File ".claude\skills\daily-emit\scripts\setup_schedule.ps1"
#
# Uninstall:
#   Unregister-ScheduledTask -TaskName '{{USER_NAME}}-daily-emit' -Confirm:$false

$ErrorActionPreference = 'Stop'

$taskName = '{{USER_NAME}}-daily-emit'
$script   = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\skills\daily-emit\scripts\run_emit.ps1'

if (-not (Test-Path $script)) { throw "Script not found at $script" }

$wrapper = "$env:USERPROFILE\.claude\skills\daily-emit\run_wrapper.cmd"
New-Item -ItemType Directory -Force -Path (Split-Path $wrapper) | Out-Null
@"
@echo off
powershell -ExecutionPolicy Bypass -NoProfile -File "$script"
"@ | Set-Content -Path $wrapper -Encoding ASCII

$action  = New-ScheduledTaskAction -Execute $wrapper
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00am
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20) `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 15)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Limited

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description 'Daily 08:00 — run /daily-emit skill in autonomous mode (read tomorrow-seed, write today daily note)' | Out-Null

Write-Host "Registered scheduled task: $taskName"
Write-Host "  next run: daily 08:00"
Write-Host "  wrapper:  $wrapper"
Write-Host "  log dir:  D:\Administrator\Documents\{{USER_NAME}}\04 Notes\vault-evolve\"
Write-Host ""
Write-Host "NOTE: existing '{{USER_NAME}}-daily-note-create' (09:00 scaffold) remains as fallback."
Write-Host "      08:00 emit creates daily note; 09:00 scaffold is idempotent (skip if exists)."
