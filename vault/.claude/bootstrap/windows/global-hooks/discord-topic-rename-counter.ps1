# UserPromptSubmit hook (generalized for ALL AFK sessions).
# Counts user inputs per Claude session and, every Nth input, injects a
# reminder telling Claude to (1) resolve THIS session's Discord channel via
# content-matching and (2) rename it to match the current conversation topic.
#
# It does NOT hardcode any session/channel ids: the afk-code session id is a
# random 8-char value unrelated to Claude's UUID, the daemon persists no
# session->channel map, and channel names collide -- so the channel is resolved
# at rename time by matching transcript text (see resolve-channel.ps1).
$ErrorActionPreference = 'SilentlyContinue'

$EVERY    = 10
$DIR      = '{{USER_HOME}}\.afk-code-claude2'
$RESOLVER = "$DIR\resolve-channel.ps1"
$RENAMER  = "$DIR\rename-channel.ps1"

$raw = [Console]::In.ReadToEnd()
try { $j = $raw | ConvertFrom-Json } catch { exit 0 }

$sid = "$($j.session_id)"
$tp  = "$($j.transcript_path)"
$cwd = "$($j.cwd)"
if ([string]::IsNullOrWhiteSpace($sid)) { exit 0 }

# per-session counter
$safeSid = ($sid -replace '[^a-zA-Z0-9\-]', '_')
$counter = "$DIR\rename-counter-$safeSid.txt"
$n = 0
if (Test-Path $counter) { try { $n = [int]((Get-Content $counter -Raw).Trim()) } catch { $n = 0 } }
$n++
Set-Content -Path $counter -Value $n -Encoding ascii

if ($n % $EVERY -ne 0) { exit 0 }

Write-Output @"
[auto-channel-rename] User input #$n in this session ($EVERY-input cadence reached).
GOAL: rename this AFK Discord channel to reflect the CURRENT conversation topic.
STEPS (run exactly, in order):
  1) Resolve this session's channel id (cached after first run):
       powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$RESOLVER" -TranscriptPath "$tp" -Cwd "$cwd"
     If it prints an empty line / nonzero exit, this is NOT an AFK-bridged session -> do nothing, say nothing.
  2) If it printed a channel id <CID>, pick a concise kebab-case topic (prefix 'afk-', <=90 chars) summarizing what we are working on NOW, then:
       powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$RENAMER" -ChannelId <CID> -Name "afk-<topic>"
Note: Discord rate-limits renames to ~2 per 10 min; if it returns a rate-limit error, skip silently. After a successful rename, add only a one-line note and continue the user's request.
"@
exit 0
