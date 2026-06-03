# Register 3 weekly maintenance tasks in Windows Task Scheduler.
# Run this script ONCE as Administrator (or current user, since tasks run as current user by default).
# Idempotent: deletes existing same-name tasks before creating.

$ErrorActionPreference = "Stop"
$ScriptDir = "{{USER_HOME}}\.claude\vault-maintenance"
$Python = (Get-Command python).Source

$Tasks = @(
  @{
    Name = "RG-vault-inbox-decay"
    Script = "$ScriptDir\inbox-decay.py"
    DayOfWeek = "Sunday"
    Time = "21:00"
    Description = "Tag overdue (>14 day) Inbox.md / Tasks.md items as #stale and emit report under 04 Notes/auto-reports/"
  },
  @{
    Name = "RG-vault-cards-archive"
    Script = "$ScriptDir\cards-archive.py"
    DayOfWeek = "Sunday"
    Time = "22:00"
    Description = "Archive cards older than 90 days with no incoming wikilinks to 02 Cards/_archive/"
  },
  @{
    Name = "RG-vault-weekly-metabolism"
    Script = "$ScriptDir\weekly-metabolism.py"
    DayOfWeek = "Friday"
    Time = "18:00"
    Description = "Tasks Kanban health + cards spawned + daily note coverage metrics for past 7 days"
  }
)

foreach ($t in $Tasks) {
  Write-Host "=== $($t.Name) ==="

  # Delete existing (no-op if absent)
  try { Unregister-ScheduledTask -TaskName $t.Name -Confirm:$false -ErrorAction Stop } catch { }

  # Build action: python <script>
  $Action = New-ScheduledTaskAction -Execute $Python -Argument "`"$($t.Script)`""

  # Build trigger: weekly on specified day at specified time
  $Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $t.DayOfWeek -At $t.Time

  # Build settings: run if on AC, allow on-demand, time limit 30min
  $Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

  # Register under current user, run only when logged in
  $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

  Register-ScheduledTask `
    -TaskName $t.Name `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description $t.Description | Out-Null

  Write-Host "  Registered: $($t.Name) — $($t.DayOfWeek) $($t.Time)"
}

Write-Host ""
Write-Host "=== Verification ==="
foreach ($t in $Tasks) {
  $info = Get-ScheduledTaskInfo -TaskName $t.Name
  Write-Host "$($t.Name): NextRunTime = $($info.NextRunTime)"
}

Write-Host ""
Write-Host "Done. To run manually for testing: Start-ScheduledTask -TaskName <name>"
Write-Host "To remove: schtasks /Delete /TN <name> /F"
