# Renames a Discord channel via the afk-code bot token.
# Usage: rename-channel.ps1 -Name "afk-some-topic" [-ChannelId <id>]
param(
  [Parameter(Mandatory = $true)][string]$Name,
  [string]$ChannelId = '1509726896106242079'  # default: this AFK session's channel
)
$ErrorActionPreference = 'Stop'
$envFile = '{{USER_HOME}}\.afk-code-claude2\discord.env'
$tok = ((Get-Content $envFile) | Where-Object { $_ -match '^DISCORD_BOT_TOKEN=' }) -replace '^DISCORD_BOT_TOKEN=', ''
$H = @{ Authorization = "Bot $tok"; 'User-Agent' = 'DiscordBot (afk-code, 1.0)'; 'Content-Type' = 'application/json' }

# Discord channel-name rules: lowercase, no spaces, only a-z 0-9 - _
$safe = ($Name.ToLower() -replace '[^a-z0-9\-_\s]', '' -replace '\s+', '-' -replace '-+', '-').Trim('-')
if ($safe.Length -gt 95) { $safe = $safe.Substring(0, 95) }
if ([string]::IsNullOrWhiteSpace($safe)) { Write-Output 'ERR: empty name after sanitize'; exit 1 }

$body = @{ name = $safe } | ConvertTo-Json -Compress
try {
  $resp = Invoke-RestMethod -Uri "https://discord.com/api/v10/channels/$ChannelId" -Method Patch -Headers $H -Body $body
  Write-Output ("OK renamed -> #" + $resp.name)
}
catch {
  $r = $_.Exception.Response
  if ($r) {
    $sr = New-Object System.IO.StreamReader($r.GetResponseStream())
    Write-Output ("ERR: " + $sr.ReadToEnd())
  } else { Write-Output ("ERR: " + $_.Exception.Message) }
  exit 1
}
