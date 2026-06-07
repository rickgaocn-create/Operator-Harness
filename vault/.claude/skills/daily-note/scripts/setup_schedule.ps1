# setup_schedule.ps1 — register the daily-note creator as a weekday 09:00 task.
# Idempotent: re-running updates the trigger/action; safe to run multiple times.
#
# Run:
#   powershell -ExecutionPolicy Bypass -File ".claude\skills\daily-note\scripts\setup_schedule.ps1"
#
# Uninstall:
#   Unregister-ScheduledTask -TaskName '{{USER_NAME}}-daily-note-create' -Confirm:$false

$ErrorActionPreference = 'Stop'

$taskName  = '{{USER_NAME}}-daily-note-create'
$pythonExe = '{{USER_HOME}}\AppData\Local\Programs\Python\Python311\python.exe'
$script    = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\skills\daily-note\scripts\create_today.py'
$logDir    = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\.daily-ingest-queue\_logs'

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if (-not (Test-Path $pythonExe)) { throw "Python not found at $pythonExe" }
if (-not (Test-Path $script))    { throw "Script not found at $script" }

# Wrapper so stdout/stderr lands in a date-stamped log
$wrapper = "$env:USERPROFILE\.claude\skills\daily-note\run_wrapper.cmd"
New-Item -ItemType Directory -Force -Path (Split-Path $wrapper) | Out-Null
@"
@echo off
setlocal
set LOG=$logDir\%date:~-4,4%%date:~-10,2%%date:~-7,2%-daily-note.log
"$pythonExe" "$script" >> "%LOG%" 2>&1
"@ | Set-Content -Path $wrapper -Encoding ASCII

$action  = New-ScheduledTaskAction -Execute $wrapper
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 9:00am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -RestartCount 1 -RestartInterval (New-TimeSpan -Minutes 15)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Limited

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Weekday 09:00 — create today daily note scaffold if missing. Idempotent.' | Out-Null

Write-Host "Registered scheduled task: $taskName"
Write-Host "  next run: weekdays 09:00 (Mon-Fri)"
Write-Host "  wrapper:  $wrapper"
Write-Host "  logs:     $logDir"
