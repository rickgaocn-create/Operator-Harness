# Mirrors the latest assistant text response to the active Feishu chat.
# Fires on Stop. No-op unless: (a) the prompting user message came from Feishu,
# and (b) the assistant did NOT already call mcp__plugin_feishu_feishu__reply
# this turn (avoids double-send).

$ErrorActionPreference = 'SilentlyContinue'

$stateDir = Join-Path $env:USERPROFILE '.claude\channels\feishu'
$debugLog = Join-Path $stateDir 'mirror.log'
function Log($msg) {
    try {
        New-Item -ItemType Directory -Force -Path $stateDir | Out-Null
        Add-Content -LiteralPath $debugLog -Value "[$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss.fffZ')] $msg" -Encoding utf8
    } catch {}
}

# Force UTF-8 input decoding. Claude Code sends hook stdin as UTF-8 JSON,
# but PS 5.1's [Console]::In uses the console's input encoding (cp936 on
# zh-CN Windows) — which mojibakes any em-dash / CJK / · in the stdin path
# strings (none today, but safer to be explicit) and definitely mojibakes
# the same in the transcript content we read below.
try {
    [Console]::InputEncoding = [Text.UTF8Encoding]::new($false)
    $stdin = [Console]::In.ReadToEnd()
    $hookInput = $stdin | ConvertFrom-Json
} catch {
    Log "could not parse hook stdin: $_"
    exit 0
}

$transcript_path = $hookInput.transcript_path
$session_id = $hookInput.session_id
if (-not $transcript_path -or -not (Test-Path -LiteralPath $transcript_path)) {
    Log "no transcript_path or file missing: $transcript_path"
    exit 0
}

# Get-Content without -Encoding uses the system codepage (cp936 on zh-CN
# Windows), which mojibakes UTF-8 transcript content. Force UTF-8.
$lines = Get-Content -LiteralPath $transcript_path -Encoding UTF8
if (-not $lines) { exit 0 }

# Walk backwards to find: (a) consecutive assistant text blocks from the end,
# (b) whether any of those assistant turns used the Feishu reply tool,
# (c) the user message that prompted this assistant turn (skipping tool_results).
$assistantTexts = @()
$replyCalls = 0
$promptingUserContent = $null
$lastAssistantUuid = $null

for ($i = $lines.Count - 1; $i -ge 0; $i--) {
    $line = $lines[$i]
    if (-not $line) { continue }
    try { $msg = $line | ConvertFrom-Json } catch { continue }

    if ($msg.type -eq 'assistant') {
        if (-not $lastAssistantUuid) { $lastAssistantUuid = $msg.uuid }
        $content = $msg.message.content
        if ($content -is [array]) {
            $localTexts = @()
            foreach ($block in $content) {
                if ($block.type -eq 'text' -and $block.text) {
                    $localTexts += $block.text
                }
                elseif ($block.type -eq 'tool_use' -and $block.name -eq 'mcp__plugin_feishu_feishu__reply') {
                    $replyCalls++
                }
            }
            if ($localTexts.Count -gt 0) {
                $assistantTexts = ,(($localTexts -join "`n")) + $assistantTexts
            }
        }
    }
    elseif ($msg.type -eq 'user') {
        $content = $msg.message.content
        $isToolResult = $false
        $userText = ''
        if ($content -is [string]) {
            $userText = $content
        } elseif ($content -is [array]) {
            foreach ($block in $content) {
                if ($block.type -eq 'tool_result') { $isToolResult = $true; break }
                if ($block.type -eq 'text' -and $block.text) { $userText += $block.text }
            }
        }
        if (-not $isToolResult) {
            $promptingUserContent = $userText
            break
        }
    }
}

if (-not $promptingUserContent) {
    Log "no prompting user message found"
    exit 0
}

# Q1c: skip mirror if assistant called reply() this turn — avoids double-send.
if ($replyCalls -gt 0) {
    Log "skipped: assistant called reply() $replyCalls time(s) this turn"
    exit 0
}

# Detect active Feishu chat from the prompting user message.
$rx = '<channel\s+source="[^"]*feishu[^"]*"\s+chat_id="(oc_[^"]+)"'
$m = [regex]::Match($promptingUserContent, $rx)
if ($m.Success) {
    $chat_id = $m.Groups[1].Value
} else {
    # Fallback for afk-code feishu sessions: those don't inject a <channel> tag
    # (input arrives via PTY pipe, not the MCP plugin), but the wrapper's
    # --append-system-prompt contains the marker below. Pull chat_id from feishu.env.
    $isAfkFeishu = $false
    foreach ($line in $lines) {
        if ($line -and $line.Contains('AFK session via Feishu')) { $isAfkFeishu = $true; break }
    }
    if (-not $isAfkFeishu) {
        Log "no feishu channel tag in prompting message"
        exit 0
    }

    # Avoid duplicates: if the afk-code bridge is actively watching THIS transcript,
    # the daemon is already mirroring — skip. Compare its last claimed JSONL to ours.
    $bridgeLog = $null
    foreach ($p in @(
        "$env:USERPROFILE\AppData\Local\Temp\feishu-bridge.log",
        "$env:USERPROFILE\AppData\Local\Programs\Git\tmp\feishu-bridge.log",
        '/tmp/feishu-bridge.log',
        'C:\tmp\feishu-bridge.log'
    )) {
        if ($p -and (Test-Path -LiteralPath $p)) { $bridgeLog = $p; break }
    }
    $bridgeWatchingUs = $false
    if ($bridgeLog -and (Test-Path -LiteralPath $bridgeLog)) {
        $myFileName = [System.IO.Path]::GetFileName($transcript_path)
        $logTail = Get-Content -LiteralPath $bridgeLog -Tail 100 -ErrorAction SilentlyContinue
        for ($j = $logTail.Count - 1; $j -ge 0; $j--) {
            $ln = $logTail[$j]
            if ($ln -match 'Found (new|modified) JSONL.*?([0-9a-f-]{36}\.jsonl)' -or $ln -match 'Watching:.*?([0-9a-f-]{36}\.jsonl)') {
                $watchedName = $Matches[$Matches.Count - 1]
                if ($watchedName -eq $myFileName) { $bridgeWatchingUs = $true }
                break
            }
        }
    }
    if ($bridgeWatchingUs) {
        Log "skipped: afk-code bridge is watching our transcript ($myFileName)"
        exit 0
    }

    $envPath = Join-Path $env:USERPROFILE '.afk-code\feishu.env'
    if (-not (Test-Path -LiteralPath $envPath)) {
        Log "afk-feishu session but no feishu.env at $envPath"
        exit 0
    }
    $envContent = Get-Content -LiteralPath $envPath -Raw
    $em = [regex]::Match($envContent, '(?m)^FEISHU_CHAT_ID=(oc_\S+)')
    if (-not $em.Success) {
        Log "afk-feishu session but FEISHU_CHAT_ID missing from feishu.env"
        exit 0
    }
    $chat_id = $em.Groups[1].Value
    Log "afk-feishu fallback: using chat_id=$chat_id from feishu.env"
}

$assistantText = ($assistantTexts -join "`n`n").Trim()
if (-not $assistantText) {
    Log "no assistant text to mirror"
    exit 0
}

# Dedupe per session — never mirror the same assistant uuid twice.
$stateFile = Join-Path $stateDir "mirror-$session_id.lastuuid"
$prevUuid = $null
if (Test-Path -LiteralPath $stateFile) {
    $prevUuid = (Get-Content -LiteralPath $stateFile -Raw).Trim()
}
if ($prevUuid -eq $lastAssistantUuid) {
    Log "already mirrored uuid=$lastAssistantUuid"
    exit 0
}

# Chunk on paragraph/line boundaries — Feishu drops long messages.
$CHUNK = 1500
$chunks = @()
$rest = $assistantText
while ($rest.Length -gt $CHUNK) {
    $cut = $CHUNK
    $idx = $rest.LastIndexOf("`n`n", $CHUNK)
    if ($idx -gt ($CHUNK / 2)) {
        $cut = $idx
    } else {
        $idx2 = $rest.LastIndexOf("`n", $CHUNK)
        if ($idx2 -gt ($CHUNK / 2)) { $cut = $idx2 }
    }
    $chunks += $rest.Substring(0, $cut)
    $rest = $rest.Substring($cut).TrimStart("`n")
}
if ($rest) { $chunks += $rest }

# Send each chunk via lark-cli using `post` msg_type — one row per line.
# Reason: Feishu's `text` msg_type strips/truncates embedded newlines visually,
# making multi-line mirror output unreadable. `post` with rows preserves line
# breaks. Mirrors the same fix applied in the feishu plugin's sendText().
#
# Delivery path: write JSON payload to a UTF-8 temp file, then invoke
# `bash -c "lark-cli ... --content \"$(cat 'tmpfile')\" --msg-type post"` via
# ProcessStartInfo. Why this layered approach:
#   - PS 5.1's `&` call operator silently strips embedded `"` from native args.
#   - `cmd /c "lark-cli ... --content \"...\""` works for simple JSON but
#     cmd.exe re-tokenizes on internal `"` when the payload contains backticks,
#     asterisks, or large CJK strings — produces "positional arguments not
#     supported" errors from lark-cli.
#   - Git Bash's `$(cat 'file')` command substitution makes the JSON content
#     opaque to the shell parser — no quoting at the shell level, only at the
#     filesystem level (which is byte-clean).
# UTF-8 encoding on the temp file is critical: stdin of PS 5.1 hooks comes in
# at the console encoding (cp936 on zh-CN Windows), so CJK in $contentJson
# went through one decode/encode round already; UTF8Encoding(false) writes
# without BOM so `cat` produces clean UTF-8 bytes.
$LARK_PROFILE = if ($env:LARK_PROFILE) { $env:LARK_PROFILE } else { 'morty' }
$BASH_EXE = 'C:\Program Files\Git\bin\bash.exe'
$sent = 0
foreach ($c in $chunks) {
    $tmpFile = $null
    try {
        $lines = $c -split "`r`n|`n"
        $rows = @()
        foreach ($line in $lines) {
            if ($line.Length -eq 0) {
                $rows += ,@(@{ tag = 'text'; text = ' ' })
            } else {
                $rows += ,@(@{ tag = 'text'; text = $line })
            }
        }
        $contentJson = (@{ zh_cn = @{ content = $rows } } | ConvertTo-Json -Depth 6 -Compress)

        $tmpFile = Join-Path $env:TEMP "feishu-mirror-$([guid]::NewGuid()).json"
        [IO.File]::WriteAllText($tmpFile, $contentJson, [Text.UTF8Encoding]::new($false))
        $bashTmpPath = $tmpFile -replace '\\', '/'

        $bashCmd = "lark-cli --profile $LARK_PROFILE im +messages-send --as bot --chat-id $chat_id --content `"`$(cat '$bashTmpPath')`" --msg-type post"
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $BASH_EXE
        $psi.Arguments = '-c "' + ($bashCmd -replace '"', '\"') + '"'
        $psi.UseShellExecute = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.CreateNoWindow = $true
        $p = [System.Diagnostics.Process]::Start($psi)
        $p.WaitForExit()
        $exit = $p.ExitCode
        if ($exit -eq 0) {
            $sent++
        } else {
            $errOut = $p.StandardError.ReadToEnd()
            $stdOut = $p.StandardOutput.ReadToEnd()
            Log "lark-cli failed exit=$exit for chat=$chat_id chunk-len=$($c.Length) stderr=$errOut stdout=$stdOut"
        }
    } catch {
        Log "bash/lark-cli threw: $_"
    } finally {
        if ($tmpFile -and (Test-Path -LiteralPath $tmpFile)) {
            Remove-Item -LiteralPath $tmpFile -Force -ErrorAction SilentlyContinue
        }
    }
}

if ($sent -gt 0) {
    Set-Content -LiteralPath $stateFile -Value $lastAssistantUuid -Encoding utf8
    Log "mirrored uuid=$lastAssistantUuid chat=$chat_id chunks=$sent total-len=$($assistantText.Length)"
}
exit 0
