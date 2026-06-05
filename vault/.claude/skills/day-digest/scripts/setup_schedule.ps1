# setup_schedule.ps1 — register `{{USER_NAME}}-day-digest` as daily 23:00 Windows Task
# Idempotent: re-running updates trigger/action.
#
# Install:
#   powershell -ExecutionPolicy Bypass -File ".claude\skills\day-digest\scripts\setup_schedule.ps1"
#
# Uninstall:
#   Unregister-ScheduledTask -TaskName '{{USER_NAME}}-day-digest' -Confirm:$false

$ErrorActionPreference = 'Stop'

$taskName = '{{USER_NAME}}-day-digest'
$script   = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\skills\day-digest\scripts\run_digest.ps1'

if (-not (Test-Path $script)) { throw "Script not found at $script" }

# Wrap in cmd so PowerShell args don't quote-bleed
$wrapper = "$env:USERPROFILE\.claude\skills\day-digest\run_wrapper.cmd"
New-Item -ItemType Directory -Force -Path (Split-Path $wrapper) | Out-Null
@"
@echo off
powershell -ExecutionPolicy Bypass -NoProfile -File "$script"
"@ | Set-Content -Path $wrapper -Encoding ASCII

$action  = New-ScheduledTaskAction -Execute $wrapper
$trigger = New-ScheduledTaskTrigger -Daily -At 11:00pm
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
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
    -Description 'Daily 23:00 — run /day-digest skill in autonomous mode (read 14 vault sources, write 4 chew sections + tomorrow-seed)' | Out-Null

Write-Host "Registered scheduled task: $taskName"
Write-Host "  next run: daily 23:00"
Write-Host "  wrapper:  $wrapper"
Write-Host "  log dir:  D:\Administrator\Documents\{{USER_NAME}}\04 Notes\vault-evolve\"
