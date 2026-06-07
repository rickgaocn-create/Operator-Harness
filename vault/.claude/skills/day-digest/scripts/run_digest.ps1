# run_digest.ps1 — invoke Claude Code in autonomous mode to run /day-digest
# Called by Windows Task `{{USER_NAME}}-day-digest` daily at 23:00.
# Manual run:
#   powershell -ExecutionPolicy Bypass -File "<vault>\.claude\skills\day-digest\scripts\run_digest.ps1"

$ErrorActionPreference = 'Stop'

$vaultRoot = 'D:\Administrator\Documents\{{USER_NAME}}'
$claudeExe = '{{USER_HOME}}\.local\bin\claude.exe'
$logDir    = "$vaultRoot\04 Notes\vault-evolve"
$today     = (Get-Date).ToString('yyyy-MM-dd')
$timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
$runLog    = "$logDir\_digest-log.md"
$errorLog  = "$logDir\_digest-errors-$today.log"

# Pre-flight
if (-not (Test-Path $claudeExe)) {
    "[$timestamp] ERROR: claude CLI not found at $claudeExe" | Add-Content -Path $errorLog
    exit 1
}
if (-not (Test-Path $vaultRoot)) {
    "[$timestamp] ERROR: vault root not found at $vaultRoot" | Add-Content -Path $errorLog
    exit 1
}

# cd into vault (Claude Code skill discovery requires CWD = vault)
Set-Location $vaultRoot

# Invoke Claude Code with the /day-digest skill in autonomous mode
# --dangerously-skip-permissions: required for unattended execution (no tool approval prompts)
# --print: non-interactive single-shot mode (Claude executes prompt, prints result, exits)
$prompt = "Execute the /day-digest skill in autonomous mode for today ($today). Read all 14 data sources per [[09 Rules/digest-job.md]], write 4 AI-Chew sections to today's daily note, write tomorrow-seed file. Log run to _digest-log.md. No interactive prompts."

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

# Pruning: keep last 30 error logs (delete older)
Get-ChildItem -Path $logDir -Filter "_digest-errors-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 30 |
    Remove-Item -Force -ErrorAction SilentlyContinue
