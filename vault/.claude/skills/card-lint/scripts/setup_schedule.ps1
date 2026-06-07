# setup_schedule.ps1 — register `{{USER_NAME}}-card-lint` as weekly Sunday 23:30 Windows Task
# Idempotent: re-running updates trigger/action.
#
# Install:
#   powershell -ExecutionPolicy Bypass -File ".claude\skills\card-lint\scripts\setup_schedule.ps1"
#
# Uninstall:
#   Unregister-ScheduledTask -TaskName '{{USER_NAME}}-card-lint' -Confirm:$false

$ErrorActionPreference = 'Stop'

$taskName = '{{USER_NAME}}-card-lint'
$script   = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\skills\card-lint\scripts\run_card_lint.ps1'

if (-not (Test-Path $script)) { throw "Script not found at $script" }

# Wrap in cmd so PowerShell args don't quote-bleed
$wrapper = "$env:USERPROFILE\.claude\skills\card-lint\run_wrapper.cmd"
New-Item -ItemType Directory -Force -Path (Split-Path $wrapper) | Out-Null
@"
@echo off
powershell -ExecutionPolicy Bypass -NoProfile -File "$script"
"@ | Set-Content -Path $wrapper -Encoding ASCII

$action  = New-ScheduledTaskAction -Execute $wrapper
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 11:30pm
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
    -Description 'Weekly Sunday 23:30 — run /card-lint --mode=hygiene autonomously (audit 02 Cards/ graph: orphans, stale, broken links, frontmatter drift)' | Out-Null

Write-Host "Registered scheduled task: $taskName"
Write-Host "  next run: weekly Sunday 23:30"
Write-Host "  wrapper:  $wrapper"
Write-Host "  log dir:  D:\Administrator\Documents\{{USER_NAME}}\04 Notes\vault-evolve\"
