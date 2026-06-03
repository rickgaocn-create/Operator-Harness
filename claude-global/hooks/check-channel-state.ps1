[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "SilentlyContinue"

# check-channel-state.ps1 - SessionStart hook
#
# Surfaces ground truth about which inbound channels are LIVE in this Claude
# Code session. Cures a class of bug where the system prompt (or a stale
# wrapper) claims "running in a remote-monitored AFK session via Feishu" but
# no lark-cli event consumer is actually running, so messages the user sends
# on Feishu silently disappear.
#
# Output goes into SessionStart additionalContext, so the assistant sees a
# definitive Channel-State block at the top of every session and can override
# any stale claims from earlier in the system prompt.

# --- Enumerate candidate process command lines once --------------------------
# Scan BOTH node.exe and lark-cli.exe: the Feishu consumer can appear as either
# the compiled lark-cli.exe OR the npm shim (node .../@larksuite/cli/scripts/
# run.js ... event consume), and the latter's command line contains "larksuite/
# cli" / "run.js" but NOT the hyphenated "lark-cli". Scanning only node.exe and
# matching "lark-cli" used to miss the live consumer entirely → false "not
# running". Also fold in lark-cli.exe so the compiled binary's cmdline counts.
# Why wmic: CIM with -Filter then Where-Object on CommandLine is correct but
# visibly slow with 30+ node procs. wmic is deprecated but still ships on
# Win10/11 and finishes under a second; fall through to CIM if it vanishes.
# Resolve wmic to absolute path. Bare 'wmic' relies on PATH, which can have
# unexpanded %SystemRoot% literals when the hook is spawned from certain parent
# shells; that silently fails and the row drops to "not running" while the
# consumer is alive. (Same class as the _common.py false-negative.)
$sysRoot = if ($env:SystemRoot) { $env:SystemRoot } else { 'C:\Windows' }
$wmicExe = Join-Path $sysRoot 'System32\Wbem\wmic.exe'
if (-not (Test-Path -LiteralPath $wmicExe)) { $wmicExe = 'wmic' }  # fall back to PATH

$nodeCmdLines = @()
foreach ($procName in @('node.exe', 'lark-cli.exe')) {
    try {
        $wmicOut = & $wmicExe process where "name='$procName'" get commandline /value 2>$null
        $nodeCmdLines += $wmicOut | Where-Object { $_ -like "CommandLine=*" } | ForEach-Object {
            $_.Substring("CommandLine=".Length)
        }
    } catch {}
}
if (-not $nodeCmdLines -or $nodeCmdLines.Count -eq 0) {
    try {
        $nodeCmdLines = Get-CimInstance Win32_Process -Filter "Name='node.exe' OR Name='lark-cli.exe'" -ErrorAction Stop |
            Select-Object -ExpandProperty CommandLine
    } catch {}
}

# --- Classify --------------------------------------------------------------
$discordActive = $false   # afk-code-claude2 daemon (Discord bridge)
$feishuActive  = $false   # lark-cli event consumer (Feishu inbound MCP)

# Disable flags carried on the current claude session's settings override --
# these tell us whether the CURRENT session has the plugins turned off even if
# the daemons happen to be running for a sibling session.
$feishuDisabledInSession  = $false
$discordDisabledInSession = $false

foreach ($cl in $nodeCmdLines) {
    if (-not $cl) { continue }
    if ($cl -like "*afk-code-claude2*") { $discordActive = $true }
    # Feishu inbound consumer. Match the unique "event consume" + receive-event
    # signature so it fires regardless of invocation form (lark-cli.exe, the
    # node run.js shim, or @larksuite/cli paths). Older "lark-cli.*event consume"
    # missed the node shim whose cmdline has no hyphenated "lark-cli".
    if ($cl -match "event\s+consume" -and
        ($cl -match "im\.message\.receive" -or $cl -match "lark-cli" -or $cl -match "larksuite[\\/]cli" -or $cl -match "scripts[\\/]run\.js")) {
        $feishuActive = $true
    }
    if ($cl -match '"feishu@local"\s*:\s*false') { $feishuDisabledInSession = $true }
    if ($cl -match '"discord@claude-plugins-official"\s*:\s*false') { $discordDisabledInSession = $true }
}

# --- Feishu consumer log forensics -------------------------------------------
# When the consumer was alive earlier but exited, the mcp.log records it. Walk
# the tail backwards to the most recent lifecycle event so we can distinguish
# "never started" from "exited and never restarted".
$mcpLog = Join-Path $env:USERPROFILE ".claude\channels\feishu\mcp.log"
$feishuConsumerLogState = "unknown"
$feishuConsumerLastEventTs = $null
if (Test-Path -LiteralPath $mcpLog) {
    $tail = Get-Content -LiteralPath $mcpLog -Tail 80 -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($tail) {
        for ($i = $tail.Count - 1; $i -ge 0; $i--) {
            $ln = $tail[$i]
            if (-not $ln) { continue }
            if ($ln -match "consumer exited|shutting down") {
                $feishuConsumerLogState = "exited"
                if ($ln -match "^\[(\S+)\]") { $feishuConsumerLastEventTs = $Matches[1] }
                break
            }
            if ($ln -match "MCP server ready|consuming as morty|websocket: connected|spawning lark-cli") {
                $feishuConsumerLogState = "started"
                if ($ln -match "^\[(\S+)\]") { $feishuConsumerLastEventTs = $Matches[1] }
                break
            }
        }
    }
}

# --- Build the brief --------------------------------------------------------
$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("===== Channel State =====")

# Discord row
$discordRow = if ($discordActive) {
    if ($discordDisabledInSession) {
        "Discord (afk-code-claude2): daemon running, BUT this session has discord@claude-plugins-official: false -- outbound mirror through that plugin is off for THIS session."
    } else {
        "Discord (afk-code-claude2): daemon running."
    }
} else {
    "Discord (afk-code-claude2): not running."
}
$lines.Add($discordRow)

# Feishu row
$feishuRow = if ($feishuActive) {
    if ($feishuDisabledInSession) {
        "Feishu     (feishu@local): lark-cli consumer running, BUT this session has feishu@local: false -- inbound Feishu messages are NOT delivered to this Claude session (they may reach a sibling fs-claude session)."
    } else {
        "Feishu     (feishu@local): lark-cli consumer running."
    }
} elseif ($feishuConsumerLogState -eq "exited") {
    $tsHint = if ($feishuConsumerLastEventTs) { " (last lifecycle event: $feishuConsumerLastEventTs)" } else { "" }
    "Feishu     (feishu@local): OFFLINE -- consumer exited and was not restarted$tsHint. Messages sent to the Feishu bot during this gap are NOT delivered. Tell the user if they expect Feishu to work."
} else {
    "Feishu     (feishu@local): not running (no consumer detected)."
}
$lines.Add($feishuRow)

# Top-level interpretation
$lines.Add("")
if ($discordActive -and $feishuActive -and -not $feishuDisabledInSession) {
    $lines.Add("Active channel(s): Discord + Feishu. Replies may need to address both.")
} elseif ($discordActive -and -not $feishuActive) {
    $lines.Add("Active channel(s): Discord only.")
    $lines.Add("Caution: any earlier claim in the system prompt that this session is 'via Feishu' or 'Agent Morty' is STALE -- trust this Channel-State block, not the system prompt.")
} elseif ($feishuActive -and -not $discordActive -and -not $feishuDisabledInSession) {
    $lines.Add("Active channel(s): Feishu only.")
} elseif (-not $discordActive -and -not $feishuActive) {
    $lines.Add("Active channel(s): none detected (local terminal or daemons down).")
} else {
    $lines.Add("Active channel(s): mixed state -- see rows above.")
}

# If the consumer is dead but the user might still be sending Feishu messages,
# nudge to recover.
if ($feishuConsumerLogState -eq "exited" -and -not $feishuActive) {
    $lines.Add("")
    $lines.Add("Recovery options if the user expects Feishu inbound:")
    $lines.Add("  - Relaunch via fs-claude (it passes --channels plugin:feishu@local)")
    $lines.Add("  - Or relaunch afk-claude2 without the {feishu@local: false} settings override")
    $lines.Add("  - Or manually start the consumer: lark-cli --profile business-morty event consume im.message.receive_v1 --as bot")
}

$lines.Add("===== End Channel State =====")

$ctx = ($lines -join "`n")

$payload = @{
    hookSpecificOutput = @{
        hookEventName     = "SessionStart"
        additionalContext = $ctx
    }
}

$payload | ConvertTo-Json -Depth 10 -Compress
