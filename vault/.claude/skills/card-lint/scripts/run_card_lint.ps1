# run_card_lint.ps1 — invoke Claude Code in autonomous mode to run /card-lint
# Called by Windows Task `{{USER_NAME}}-card-lint` weekly on Sunday at 23:30.
# Manual run:
#   powershell -ExecutionPolicy Bypass -File "<vault>\.claude\skills\card-lint\scripts\run_card_lint.ps1"

$ErrorActionPreference = 'Stop'

$vaultRoot = 'D:\Administrator\Documents\{{USER_NAME}}'
$claudeExe = '{{USER_HOME}}\.local\bin\claude.exe'
$logDir    = "$vaultRoot\04 Notes\vault-evolve"
$today     = (Get-Date).ToString('yyyy-MM-dd')
$timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
$errorLog  = "$logDir\_card-lint-errors-$today.log"

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

# Invoke /card-lint --mode=hygiene autonomously (weekly cadence)
$prompt = "Execute the /card-lint skill in autonomous mode (--mode=hygiene) for today ($today). Audit 02 Cards/ graph per [[09 Rules/cards.md]] and skill SKILL.md: orphans / stale / broken wikilinks / frontmatter drift / missing cross-refs. Surface findings to _decisions.md if drift > threshold; otherwise log clean-pass to _card-lint-log.md. No interactive prompts."

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

# Pruning: keep last 30 error logs
Get-ChildItem -Path $logDir -Filter "_card-lint-errors-*.log" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 30 |
    Remove-Item -Force -ErrorAction SilentlyContinue
