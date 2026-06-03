# run_emit.ps1 — invoke Claude Code in autonomous mode to run /daily-emit
# Called by Windows Task `RG-daily-emit` daily at 08:00.
# Manual run:
#   powershell -ExecutionPolicy Bypass -File "<vault>\.claude\skills\daily-emit\scripts\run_emit.ps1"

$ErrorActionPreference = 'Stop'

$vaultRoot = '{{VAULT_ROOT}}'
$claudeExe = '{{USER_HOME}}\.local\bin\claude.exe'
$logDir    = "$vaultRoot\04 Notes\vault-evolve"
$today     = (Get-Date).ToString('yyyy-MM-dd')
$timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
$errorLog  = "$logDir\_emit-errors-$today.log"

# Pre-flight
if (-not (Test-Path $claudeExe)) {
    "[$timestamp] ERROR: claude CLI not found at $claudeExe" | Add-Content -Path $errorLog
    exit 1
}
if (-not (Test-Path $vaultRoot)) {
    "[$timestamp] ERROR: vault root not found at $vaultRoot" | Add-Content -Path $errorLog
    exit 1
}

Set-Location $vaultRoot

# Invoke /daily-emit autonomously
$prompt = "Execute the /daily-emit skill in autonomous mode for today ($today). Read tomorrow-seed file (_tomorrow-seed-$today.md), check idempotency (don't overwrite user-edited daily note), write today's daily note per [[09 Rules/time.md]] template + seed content. Log run to _emit-log.md. No interactive prompts."

try {
    & $claudeExe --print --dangerously-skip-permissions $prompt 2>&1 | Tee-Object -FilePath $errorLog -Append
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        "[$timestamp] WARNING: claude exited with code $exitCode" | Add-Content -Path $errorLog
    }
} catch {
    "[$timestamp] EXCEPTION: $_" | Add-Content -Path $errorLog
    exit 1
}

# Pruning
Get-ChildItem -Path $logDir -Filter "_emit-errors-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 30 |
    Remove-Item -Force -ErrorAction SilentlyContinue
