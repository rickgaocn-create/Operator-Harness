$ErrorActionPreference = 'Continue'
$log = "$env:USERPROFILE\.afk-code-claude2\daemon.log"
$node = 'C:\Program Files\nodejs\node.exe'
$shield = "$env:USERPROFILE\.afk-code-claude2\shield.mjs"
$entry = "$env:USERPROFILE\.afk-code-claude2\node_modules\afk-code\dist\cli\index.js"

# Convert Windows paths to file:// URLs for --import (Node ESM requires URL form on Windows)
$shieldUrl = 'file:///' + ($shield -replace '\\', '/')

# Backoff schedule (seconds) for restart attempts; settles at 30s after first 4 tries.
$backoffs = @(1, 5, 15, 30)
$attempt = 0

"`n[{0}] launcher start (auto-restart loop enabled · shield={1})" -f (Get-Date -Format o), $shieldUrl |
  Out-File -FilePath $log -Append -Encoding utf8

while ($true) {
  "[{0}] daemon spawn attempt #{1}" -f (Get-Date -Format o), ($attempt + 1) |
    Out-File -FilePath $log -Append -Encoding utf8

  & $node --import $shieldUrl $entry discord *>> $log
  $exitCode = $LASTEXITCODE

  "[{0}] daemon exited code={1} — restarting after backoff" -f (Get-Date -Format o), $exitCode |
    Out-File -FilePath $log -Append -Encoding utf8

  $delay = if ($attempt -lt $backoffs.Length) { $backoffs[$attempt] } else { 30 }
  Start-Sleep -Seconds $delay
  $attempt++
}
