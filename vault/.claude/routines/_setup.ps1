# Tier 7 Phase 4 — Windows Task Scheduler registration for 4 autonomous routines.
# Idempotent: unregisters existing then re-registers. Run as Administrator if needed.
#
# All 3 routines start in DRY_RUN mode (notification-only) — see _common.is_dry_run().
# To promote eod-snapshot to write mode after 7-day dry-run, set DRY_RUN=0 in the task action.

$vault = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$resolver = Join-Path $vault ".harness\resolve_runtime.py"
$bootstrapPython = (Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source)
if (-not $bootstrapPython) {
    $bootstrapPython = (Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source)
}
if (-not $bootstrapPython) {
    throw "No Python launcher found on PATH; set HARNESS_PYTHON or install Python 3.10+."
}
$python = (& $bootstrapPython $resolver python).Trim()
if (-not $python) {
    throw "Runtime resolver did not return a Python executable."
}

$tasks = @(
    @{
        name = "RG-tier7-inbox-drift"
        script = "$vault\.claude\routines\inbox-drift.py"
        trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
        desc = "Hourly: alert if 06 Tasks/Inbox.md exceeds 20 open items"
    },
    @{
        name = "RG-tier7-pre-trip"
        script = "$vault\.claude\routines\pre-trip.py"
        trigger = New-ScheduledTaskTrigger -Daily -At "18:00"
        desc = "Daily 18:00: alert if any trip bundle has trip-date matching tomorrow"
    },
    @{
        name = "RG-tier7-eod-snapshot"
        script = "$vault\.claude\routines\eod-snapshot.py"
        trigger = New-ScheduledTaskTrigger -Daily -At "23:30"
        desc = "Daily 23:30: freeze Operon embed results into snapshot HTML comments (DRY_RUN default)"
    },
    @{
        name = "RG-tier7-harness-pulse"
        script = "$vault\.claude\routines\harness-pulse.py"
        trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 3) -RepetitionDuration (New-TimeSpan -Days 365)
        desc = "Every 3h: consolidated harness liveness verdict (channels/scheduler/cortex/queues); edge-triggered alert on worsening"
    },
    @{
        name = "RG-tier7-relation-gaps"
        script = "$vault\.claude\routines\relation-gaps.py"
        trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "22:00"
        desc = "Weekly Sun 22:00: detect under-connected 01 Wiki entries + missing relation links (DRY default); run /relation-map to wire"
    }
)

foreach ($t in $tasks) {
    if (Get-ScheduledTask -TaskName $t.name -ErrorAction SilentlyContinue) {
        Write-Host "Unregistering existing task: $($t.name)"
        Unregister-ScheduledTask -TaskName $t.name -Confirm:$false
    }

    $action = New-ScheduledTaskAction -Execute $python -Argument "`"$($t.script)`""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

    Register-ScheduledTask `
        -TaskName $t.name `
        -Action $action `
        -Trigger $t.trigger `
        -Settings $settings `
        -Description $t.desc `
        -User $env:USERNAME `
        -RunLevel Limited
    Write-Host "Registered: $($t.name)"
}

Write-Host "`nAll 5 routines registered. Check Windows Task Scheduler GUI to verify."
Write-Host "Audit log: $vault\.claude\_state\autonomous-log.jsonl"
Write-Host "`nTo promote eod-snapshot to write mode (after 7-day dry-run period):"
Write-Host "  Edit task RG-tier7-eod-snapshot -> Add 'DRY_RUN=0' env var to the action"
