# setup_schedule.ps1 — register the daily 06:00 WeChat ingest as a Windows Scheduled Task.
# Idempotent: re-running updates the trigger/action; safe to run multiple times.
#
# Run:
#   powershell -ExecutionPolicy Bypass -File ".claude\skills\daily-wechat-ingest\scripts\setup_schedule.ps1"
#
# Uninstall:
#   Unregister-ScheduledTask -TaskName '{{USER_NAME}}-daily-wechat-ingest' -Confirm:$false

$ErrorActionPreference = 'Stop'

$taskName = '{{USER_NAME}}-daily-wechat-ingest'
$pythonExe = '{{USER_HOME}}\AppData\Local\Programs\Python\Python311\python.exe'
$script    = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\skills\daily-wechat-ingest\scripts\ingest.py'
$logDir    = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\.daily-ingest-queue\_logs'

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Prereqs
if (-not (Test-Path $pythonExe)) { throw "Python not found at $pythonExe" }
if (-not (Test-Path $script))    { throw "Script not found at $script" }

# Wrap python invocation so stdout/stderr lands in a date-stamped log
$wrapper = "$env:USERPROFILE\.claude\skills\daily-wechat-ingest\run_wrapper.cmd"
New-Item -ItemType Directory -Force -Path (Split-Path $wrapper) | Out-Null
@"
@echo off
setlocal
set LOG=$logDir\%date:~-4,4%%date:~-10,2%%date:~-7,2%-run.log
"$pythonExe" "$script" --days 1 >> "%LOG%" 2>&1
"@ | Set-Content -Path $wrapper -Encoding ASCII

$action  = New-ScheduledTaskAction -Execute $wrapper
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -RestartCount 1 -RestartInterval (New-TimeSpan -Minutes 30)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Limited

# Register (overwrite if exists)
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Daily WeChat ingest from priority work chats — pulls last 24h messages + media, appends to daily note + Inbox.' | Out-Null

Write-Host "Registered scheduled task: $taskName"
Write-Host "  next run: 06:00 daily"
Write-Host "  wrapper:  $wrapper"
Write-Host "  logs:     $logDir"
Write-Host ""
Write-Host "Verify:    Get-ScheduledTask -TaskName '$taskName' | Format-List"
Write-Host "Run now:   Start-ScheduledTask -TaskName '$taskName'"
Write-Host "Uninstall: Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
