# Wrapper for the daily /vault-evolve scheduled task.
# Invoked by Windows Task Scheduler at 06:00 daily.
# Runs claude non-interactively with the vault-evolve skill in autonomous mode.

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

$vault = "D:\Administrator\Documents\{{USER_NAME}}"
$logDir = "$vault\04 Notes\vault-evolve"
$schedulerLog = "$logDir\_scheduler.log"
$lockFile = "$logDir\_running.lock"

# Ensure log dir exists
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Idempotency: skip if a run is already in progress (e.g., interactive run)
if (Test-Path $lockFile) {
    $lockAge = (Get-Date) - (Get-Item $lockFile).LastWriteTime
    if ($lockAge.TotalMinutes -lt 30) {
        "$timestamp SKIP: another run in progress (lock age $($lockAge.TotalMinutes.ToString('F1')) min)" | Out-File -FilePath $schedulerLog -Append
        exit 0
    } else {
        # Stale lock — likely a crashed prior run. Clear it.
        Remove-Item $lockFile -Force
        "$timestamp Cleared stale lock (age $($lockAge.TotalMinutes.ToString('F1')) min)" | Out-File -FilePath $schedulerLog -Append
    }
}

# Create lock
"$timestamp PID $PID" | Out-File -FilePath $lockFile

"$timestamp START vault-evolve daily (autonomous)" | Out-File -FilePath $schedulerLog -Append

try {
    Set-Location $vault

    # Find claude CLI. It's typically at one of:
    #   $env:USERPROFILE\AppData\Local\Programs\claude\claude.exe
    #   $env:APPDATA\npm\claude.cmd
    #   anywhere in $env:Path
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

    # Run claude non-interactively.
    # --print: non-interactive mode, prints final output and exits
    # --dangerously-skip-permissions: allows tool use without per-tool prompts (required for unattended scheduled runs)
    # The /vault-evolve skill enforces its own tiered safety internally (Balanced mode — 🟢 auto, 🟡 propose, 🔴 manual)
    $output = & $claudeCmd --print --dangerously-skip-permissions "/vault-evolve --autonomous" 2>&1 | Out-String
    $exitCode = $LASTEXITCODE

    # Append a truncated tail of the output for debugging (full output goes to the report file)
    $outputTail = ($output -split "`n" | Select-Object -Last 30) -join "`n"
    "$timestamp END (exit $exitCode)`n--- output tail ---`n$outputTail`n--- end output ---" | Out-File -FilePath $schedulerLog -Append

} catch {
    "$timestamp EXCEPTION: $($_.Exception.Message)`n$($_.ScriptStackTrace)" | Out-File -FilePath $schedulerLog -Append
} finally {
    # Always release lock
    if (Test-Path $lockFile) {
        Remove-Item $lockFile -Force
    }
}
