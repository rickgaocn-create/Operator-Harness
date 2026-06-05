# Wrapper for the twice-weekly /harness-evolve --autonomous drain task.
# Invoked by Windows Task Scheduler (Mon + Thu 06:30). Mirrors vault-evolve-daily.ps1.
# Runs claude non-interactively with harness-evolve in autonomous (L2 drain) mode.
#
# /harness-evolve --autonomous is internally gated to 🟢-only (reversible, no-judgment):
# it drains `new -> distilled` clustering + `distilled -> promoted` on positive corrections,
# and DEFERS every corrective rule-promotion (🟡) and irreversible change (🔴) to the L2 report
# (04 Notes/vault-evolve/_l2-log.md) for {{USER_NAME}}'s in-session review. Bounded: <=3 changes/cycle,
# one subsystem, QA'd. Trust-earned ramp: twice-weekly to start; promote to daily only after
# a few clean L2 cycles (per 09 Rules/autonomous-routines.md).

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

# Vault root DISCOVERED from script location (global-hooks -> windows -> bootstrap -> .claude -> {{USER_NAME}}),
# not hardcoded, so the drain registers on any client (multi-client portability).
$vault = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")).Path
$logDir = "$vault\04 Notes\vault-evolve"
$schedulerLog = "$logDir\_l2-scheduler.log"
$lockFile = "$logDir\_l2-running.lock"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Idempotency: skip if a run is already in progress (e.g., an interactive /harness-evolve)
if (Test-Path $lockFile) {
    $lockAge = (Get-Date) - (Get-Item $lockFile).LastWriteTime
    if ($lockAge.TotalMinutes -lt 30) {
        "$timestamp SKIP: another L2 run in progress (lock age $($lockAge.TotalMinutes.ToString('F1')) min)" | Out-File -FilePath $schedulerLog -Append
        exit 0
    } else {
        Remove-Item $lockFile -Force
        "$timestamp Cleared stale L2 lock (age $($lockAge.TotalMinutes.ToString('F1')) min)" | Out-File -FilePath $schedulerLog -Append
    }
}

"$timestamp PID $PID" | Out-File -FilePath $lockFile
"$timestamp START harness-evolve --autonomous (L2 drain, green-tier only)" | Out-File -FilePath $schedulerLog -Append

try {
    Set-Location $vault

    # Find claude CLI (same discovery order as vault-evolve-daily.ps1)
    $claudeCmd = $null
    $candidates = @(
        "$env:USERPROFILE\AppData\Local\Programs\claude\claude.exe",
        "$env:APPDATA\npm\claude.cmd",
        "claude.cmd",
        "claude.exe",
        "claude"
    )
    foreach ($c in $candidates) {
        try {
            $resolved = Get-Command $c -ErrorAction Stop
            $claudeCmd = $resolved.Source
            break
        } catch {
            continue
        }
    }

    if (-not $claudeCmd) {
        "$timestamp ERROR: claude CLI not found in any candidate path. Check PATH or update this script." | Out-File -FilePath $schedulerLog -Append
        exit 1
    }

    "$timestamp Using claude at: $claudeCmd" | Out-File -FilePath $schedulerLog -Append

    # --print: non-interactive; --dangerously-skip-permissions: unattended tool use.
    # /harness-evolve --autonomous enforces its own tiered safety (green auto / yellow propose / red manual) + caps + QA.
    $output = & $claudeCmd --print --dangerously-skip-permissions "/harness-evolve --autonomous" 2>&1 | Out-String
    $exitCode = $LASTEXITCODE

    $outputTail = ($output -split "`n" | Select-Object -Last 30) -join "`n"
    "$timestamp END (exit $exitCode)`n--- output tail ---`n$outputTail`n--- end output ---" | Out-File -FilePath $schedulerLog -Append

} catch {
    "$timestamp EXCEPTION: $($_.Exception.Message)`n$($_.ScriptStackTrace)" | Out-File -FilePath $schedulerLog -Append
} finally {
    if (Test-Path $lockFile) {
        Remove-Item $lockFile -Force
    }
}
