$ErrorActionPreference = 'Continue'
$log = "$env:USERPROFILE\.afk-code\daemon.log"
"`n[{0}] launcher start" -f (Get-Date -Format o) | Out-File -FilePath $log -Append -Encoding utf8
& "C:\Program Files\nodejs\npx.cmd" -y afk-code discord *>> $log
"[{0}] launcher exit code={1}" -f (Get-Date -Format o), $LASTEXITCODE | Out-File -FilePath $log -Append -Encoding utf8
