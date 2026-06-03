# Resolve which Discord channel belongs to a Claude session, by matching the
# session's own transcript text against the afk-* channels' recent messages.
# Result is cached per-transcript so resolution only happens once per session.
#
# Usage: resolve-channel.ps1 -TranscriptPath <path> [-Force]
# Prints the channel id on success (empty + nonzero exit if none found).
param(
  [Parameter(Mandatory = $true)][string]$TranscriptPath,
  [string]$Cwd = '',
  [string]$GuildId = '1494160621367853320',
  [int]$MaxCandidates = 20,
  [switch]$Force
)
$ErrorActionPreference = 'Stop'
$envFile   = '{{USER_HOME}}\.afk-code-claude2\discord.env'
$cacheFile = '{{USER_HOME}}\.afk-code-claude2\session-channel-map.json'
$tok = ((Get-Content $envFile) | Where-Object { $_ -match '^DISCORD_BOT_TOKEN=' }) -replace '^DISCORD_BOT_TOKEN=', ''
$H = @{ Authorization = "Bot $tok"; 'User-Agent' = 'DiscordBot (afk-code, 1.0)' }

# --- cache ---
$cache = @{}
if (Test-Path $cacheFile) {
  try { (Get-Content $cacheFile -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $cache[$_.Name] = $_.Value } } catch {}
}
$key = $TranscriptPath.ToLower()
if (-not $Force -and $cache.ContainsKey($key) -and $cache[$key]) { Write-Output $cache[$key]; exit 0 }

if (-not (Test-Path $TranscriptPath)) { Write-Output ''; exit 1 }

# --- build distinctive markers from recent assistant messages ---
$assist = New-Object System.Collections.Generic.List[string]
foreach ($line in [System.IO.File]::ReadLines($TranscriptPath)) {
  if (-not $line.Trim()) { continue }
  try { $o = $line | ConvertFrom-Json } catch { continue }
  if ($o.type -eq 'assistant' -and $o.message -and $o.message.content) {
    $txt = ''
    foreach ($b in $o.message.content) { if ($b.type -eq 'text' -and $b.text) { $txt += $b.text } }
    if ($txt) { $assist.Add($txt) }
  }
}
# drop the most recent assistant message (current, possibly not yet mirrored)
if ($assist.Count -gt 1) { $assist.RemoveAt($assist.Count - 1) }

$markers = New-Object System.Collections.Generic.List[string]
for ($i = $assist.Count - 1; $i -ge 0 -and $markers.Count -lt 4; $i--) {
  $t = ($assist[$i] -replace '\s+', ' ').Trim()
  if ($t.Length -ge 50) { $markers.Add($t.Substring(0, [Math]::Min(80, $t.Length))) }
}
if ($markers.Count -eq 0) { Write-Output ''; exit 1 }

# --- candidate channels: live afk-* text channels ---
$chans = Invoke-RestMethod -Uri "https://discord.com/api/v10/guilds/$GuildId/channels" -Headers $H
$live = @($chans | Where-Object { $_.type -eq 0 -and $_.name -like 'afk-*' -and $_.name -notmatch '-archived-' })
$descById = { ([string]$_.id).PadLeft(20, '0') }

# Build the scan order. With -Cwd, prefer channels whose name still matches the
# daemon's cwd-derived base (afk-<sanitized cwd>, split on '/' only -> on Windows
# the whole backslash path) -- a fresh session's channel is named that way, so it
# hits immediately and non-bridged cwds (zero name matches) exit after 1 API call.
# Renamed channels no longer match the base, so the rest are scanned as fallback.
$ordered = @($live | Sort-Object $descById -Descending)
if ($Cwd) {
  $folder = (($Cwd -split '/') | Where-Object { $_ } | Select-Object -Last 1)
  $base = 'afk-' + (($folder.ToLower() -replace '[^a-z0-9\-_ ]', '' -replace '\s+', '-' -replace '-+', '-').Trim('-'))
  if ($base.Length -gt 94) { $base = $base.Substring(0, 94) }
  $matched = @($live | Where-Object { $_.name -eq $base -or $_.name -like "$base-*" })
  if ($matched.Count -eq 0) { Write-Output ''; exit 2 }   # genuine non-AFK cwd: cheap exit
  $matchedIds = $matched | ForEach-Object { $_.id }
  $rest = @($live | Where-Object { $matchedIds -notcontains $_.id })
  $ordered = @($matched | Sort-Object $descById -Descending) + @($rest | Sort-Object $descById -Descending)
}

$cands = $ordered | Select-Object -First $MaxCandidates
foreach ($c in $cands) {
  try { $msgs = Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/$($c.id)/messages?limit=50" -Headers $H }
  catch { continue }
  $blob = ($msgs | ForEach-Object { ($_.content -replace '\s+', ' ') }) -join "`n"
  foreach ($m in $markers) {
    if ($blob.IndexOf($m, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
      $cache[$key] = $c.id
      ($cache | ConvertTo-Json) | Set-Content -Path $cacheFile -Encoding utf8
      Write-Output $c.id
      exit 0
    }
  }
}
Write-Output ''
exit 2
