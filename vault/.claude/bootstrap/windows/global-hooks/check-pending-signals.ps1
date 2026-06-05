[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

# check-pending-signals.ps1 — UserPromptSubmit hook
# Fires on every user message. If _pending/ has new signals since last check,
# inject as system reminder so Claude knows to handle them. Cheap — only runs
# if dir has files.

$vault = "D:\Administrator\Documents\{{USER_NAME}}"
$pendingDir = "$vault\.claude\_pending"
$stateDir = "$vault\.claude\_state"
$lastCheckFile = "$stateDir\last-pending-check.timestamp"

# Ensure state dir
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

# Quick exit if no pending dir
if (-not (Test-Path -LiteralPath $pendingDir)) {
    # No output → nothing injected
    exit 0
}

# Read last check timestamp
$lastCheck = $null
if (Test-Path -LiteralPath $lastCheckFile) {
    try {
        $lastCheck = [DateTime]::Parse((Get-Content -LiteralPath $lastCheckFile -Raw -Encoding UTF8).Trim())
    } catch {}
}

# Find signal files newer than last check
$newSignals = @()
$allSignals = Get-ChildItem -Path $pendingDir -Filter "*.signal" -File -ErrorAction SilentlyContinue
foreach ($sig in $allSignals) {
    if ($null -eq $lastCheck -or $sig.CreationTime -gt $lastCheck) {
        $content = ""
        try { $content = (Get-Content -LiteralPath $sig.FullName -Raw -Encoding UTF8).Trim() } catch {}
        $newSignals += [PSCustomObject]@{
            File = $sig.Name
            Created = $sig.CreationTime.ToString("HH:mm")
            Content = $content
            FullPath = $sig.FullName
        }
    }
}

# Update last-check timestamp
(Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK") | Set-Content -LiteralPath $lastCheckFile -Encoding UTF8 -NoNewline

# Only inject if there are new signals
if ($newSignals.Count -eq 0) {
    exit 0
}

# Build minimal injection (additionalContext via hookSpecificOutput)
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("===== Pending Automation Signals ($($newSignals.Count) new) =====")
foreach ($sig in $newSignals) {
    $lines.Add("  - [$($sig.Created)] $($sig.File)")
    if ($sig.Content) { $lines.Add("      $($sig.Content)") }
}
$lines.Add("")
$lines.Add("Action: handle these signals (invoke corresponding skills), then delete each signal file. Signal dir: $pendingDir")
$lines.Add("===== End Pending Signals =====")

$ctx = ($lines -join "`n")

$payload = @{
    hookSpecificOutput = @{
        hookEventName     = "UserPromptSubmit"
        additionalContext = $ctx
    }
}

$payload | ConvertTo-Json -Depth 10 -Compress
