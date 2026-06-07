[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

# inject-catchup-brief.ps1 - SessionStart hook
# Detects gap since last session + drains _pending/ signal queue + writes catch-up brief.

$vault = "D:\Administrator\Documents\{{USER_NAME}}"
$pendingDir = "$vault\.claude\_pending"
$stateDir = "$vault\.claude\_state"
$lastStartFile = "$stateDir\last-session-start.timestamp"
$now = Get-Date
$nowIso = $now.ToString("yyyy-MM-ddTHH:mm:ssK")

New-Item -ItemType Directory -Force -Path $pendingDir | Out-Null
New-Item -ItemType Directory -Force -Path $stateDir | Out-Null

# 1. Read previous session-start timestamp
$lastStart = $null
$gapHours = $null
if (Test-Path -LiteralPath $lastStartFile) {
    try {
        $lastStartStr = Get-Content -LiteralPath $lastStartFile -Raw -Encoding UTF8
        $lastStart = [DateTime]::Parse($lastStartStr.Trim())
        $gapHours = [Math]::Round(($now - $lastStart).TotalHours, 1)
    } catch {}
}

# 2. Write current timestamp
$nowIso | Set-Content -LiteralPath $lastStartFile -Encoding UTF8 -NoNewline

# 3. Drain _pending signals
$pendingSignals = @()
if (Test-Path -LiteralPath $pendingDir) {
    $signalFiles = Get-ChildItem -Path $pendingDir -Filter "*.signal" -File -ErrorAction SilentlyContinue | Sort-Object Name
    foreach ($sig in $signalFiles) {
        $content = ""
        try { $content = (Get-Content -LiteralPath $sig.FullName -Raw -Encoding UTF8).Trim() } catch {}
        $pendingSignals += [PSCustomObject]@{
            File = $sig.Name
            Created = $sig.CreationTime.ToString("yyyy-MM-dd HH:mm")
            Content = $content
        }
    }
}

# 3b. Scan judgment-queue (SessionEnd drains flagged judgment-moments here for batched extraction)
$judgmentQueueDir = "$stateDir\judgment-queue"
$judgmentFiles = @()
$judgmentCandidates = 0
if (Test-Path -LiteralPath $judgmentQueueDir) {
    $jf = Get-ChildItem -Path $judgmentQueueDir -Filter "*.json" -File -ErrorAction SilentlyContinue | Sort-Object Name
    foreach ($f in $jf) {
        $n = $null
        try {
            $obj = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
            $n = $obj.flagged
        } catch {}
        if ($null -ne $n) { $judgmentCandidates += [int]$n }
        $judgmentFiles += $f.Name
    }
}

# 3c. Distill state: status:new events ready to cluster (threshold 5) + proposals pending review
$DISTILL_THRESHOLD = 5
$correctionsFile = "$stateDir\corrections.jsonl"
$proposalsFile = "$stateDir\distill-proposals.jsonl"
$newEventCount = 0
$pendingProposals = 0
if (Test-Path -LiteralPath $correctionsFile) {
    try { $newEventCount = (Select-String -LiteralPath $correctionsFile -Pattern '"status":\s*"new"' -AllMatches).Count } catch {}
}
if (Test-Path -LiteralPath $proposalsFile) {
    try { $pendingProposals = (Select-String -LiteralPath $proposalsFile -Pattern '"status":\s*"pending-review"' -AllMatches).Count } catch {}
}

# 3d. Harness Dashboard capture inbox (NL utterances flagged 'ready' via the dashboard
# Route button; /capture-process is the consumer that routes them to tasks/cards/notes).
$captureFile = "$stateDir\dashboard\capture-inbox.jsonl"
$captureReady = 0
if (Test-Path -LiteralPath $captureFile) {
    try { $captureReady = (Select-String -LiteralPath $captureFile -Pattern '"status":\s*"ready"' -AllMatches).Count } catch {}
}

# 4. Latest daily note mtime
$dailyNoteDir = "$vault\04 Notes\daily notes"
$latestDaily = $null
$latestDailyHoursAgo = $null
if (Test-Path -LiteralPath $dailyNoteDir) {
    $latestFile = Get-ChildItem -Path $dailyNoteDir -Filter "*.md" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestFile) {
        $latestDaily = $latestFile.Name
        $latestDailyHoursAgo = [Math]::Round(($now - $latestFile.LastWriteTime).TotalHours, 1)
    }
}

# 5. Today's daily note state
$todayDate = $now.ToString("yyyy-MM-dd")
$todayDaily = "$dailyNoteDir\$todayDate.md"
$todayExists = Test-Path -LiteralPath $todayDaily
$todayChewed = $false
$todaySealed = $false
if ($todayExists) {
    try {
        $todayContent = Get-Content -LiteralPath $todayDaily -Raw -Encoding UTF8
        if ($todayContent -match "Shape of Today") { $todayChewed = $true }
        if ($todayContent -match "status:\s*closed") { $todaySealed = $true }
    } catch {}
}

# 6. Yesterday's daily note
$yesterdayDate = $now.AddDays(-1).ToString("yyyy-MM-dd")
$yesterdayDaily = "$dailyNoteDir\$yesterdayDate.md"
$yesterdayExists = Test-Path -LiteralPath $yesterdayDaily
$yesterdayChewed = $false
if ($yesterdayExists) {
    try {
        $yesterdayContent = Get-Content -LiteralPath $yesterdayDaily -Raw -Encoding UTF8
        if ($yesterdayContent -match "Shape of Today") { $yesterdayChewed = $true }
    } catch {}
}

# 7. Tomorrow-seed for today exists?
$seedFile = "$vault\04 Notes\vault-evolve\_tomorrow-seed-$todayDate.md"
$seedExists = Test-Path -LiteralPath $seedFile

# 7b. Harness pulse — consolidated liveness verdict ({{USER_NAME}}-tier7-harness-pulse, every 3h).
# Surface the single verdict here so harness health is visible at session start
# without running /harness-health. Channels are NOT re-shown — check-channel-state.ps1
# owns the live channel view (more current than this file); this surfaces the
# scheduler / cortex / queue / error-rate findings the pulse consolidates.
$pulseFile = "$stateDir\harness-pulse.json"
$pulseSeverity = $null
$pulseFindings = @()
$pulseAgeHours = $null
if (Test-Path -LiteralPath $pulseFile) {
    try {
        $pulse = Get-Content -LiteralPath $pulseFile -Raw -Encoding UTF8 | ConvertFrom-Json
        $pulseSeverity = $pulse.severity
        foreach ($f in $pulse.findings) { if ($f.msg) { $pulseFindings += [string]$f.msg } }
        if ($pulse.ts) { $pulseAgeHours = [Math]::Round(($now - [DateTime]::Parse([string]$pulse.ts)).TotalHours, 1) }
    } catch {}
}

# 8. Build brief - conclusion-first + terse. The computation above is unchanged;
# only the OUTPUT is trimmed: one status line + a do-list, detail via /status.
# (Lowers per-session overhead - the dump violated {{USER_NAME}}'s own conclusion-first rule.)
$brief = New-Object System.Collections.Generic.List[string]

# The conclusion: compute the do-list first.
$recs = @()
if (-not $yesterdayChewed -and $yesterdayExists -and ($null -eq $gapHours -or $gapHours -lt 48)) {
    $recs += "/day-digest --catchup --date $yesterdayDate (yesterday not chewed)"
}
if (-not $todayExists -and $seedExists) {
    $recs += "/daily-emit (today note missing, seed exists)"
} elseif (-not $todayExists) {
    $recs += "/daily-note (today note missing)"
}
if ($pendingSignals.Count -gt 0) {
    $recs += "process $($pendingSignals.Count) pending signal(s): $(( $pendingSignals | ForEach-Object { $_.File } ) -join ', ')"
}
if ($captureReady -gt 0) {
    $recs += "/capture-process ($captureReady dashboard capture(s) flagged ready -> tasks/cards/notes)"
}
if ($judgmentCandidates -gt 0) {
    $recs += "extract ~$judgmentCandidates judgment candidate(s) -> corrections.jsonl (dedup, then clear queue)"
}
if ($newEventCount -ge $DISTILL_THRESHOLD) {
    $recs += "distill due ($newEventCount new): judgment_distill.py --brief"
}
if ($pendingProposals -gt 0) {
    $recs += "review $pendingProposals distill proposal(s) (approve/reject)"
}

# One-line status (detail via /status).
$sevTag = if ($null -eq $pulseSeverity) { "no-verdict" } else { switch ($pulseSeverity) { "red" { "RED" } "yellow" { "yellow" } default { "green" } } }
$gapStr = if ($null -ne $gapHours) { "${gapHours}h" } else { "?" }
$todayTag = if (-not $todayExists) { "today-note MISSING" } elseif (-not $todaySealed) { "today open" } else { "today closed" }
$bits = @("pulse $sevTag", "gap $gapStr", "$($pendingSignals.Count) sig", "$captureReady cap", "$judgmentCandidates jdg", $todayTag)
$brief.Add("===== Harness brief ($nowIso) =====")
$brief.Add("> " + ($bits -join " | "))

# Pulse findings only when not green.
if ($pulseSeverity -eq "red" -or $pulseSeverity -eq "yellow") {
    foreach ($m in $pulseFindings) { $brief.Add("  ! $m") }
}
if ($null -ne $pulseAgeHours -and $pulseAgeHours -gt 4) {
    $brief.Add("  ! pulse verdict stale (${pulseAgeHours}h) - check {{USER_NAME}}-tier7-harness-pulse")
}

# The do-list, or nothing.
$brief.Add("")
if ($recs.Count -eq 0) {
    $brief.Add("OK - nothing pending, proceed.")
} else {
    $brief.Add("Do:")
    foreach ($r in $recs) { $brief.Add("  * $r") }
}

# Front door + detail pointers (one line).
$brief.Add("")
$brief.Add("Engage by intent: /operate routes (today | process this | make forwardable | think with me | check the machine). /status = full health.")
$brief.Add("===== End =====")

$ctx = ($brief -join "`n")

$payload = @{
    hookSpecificOutput = @{
        hookEventName     = "SessionStart"
        additionalContext = $ctx
    }
}

$payload | ConvertTo-Json -Depth 10 -Compress
