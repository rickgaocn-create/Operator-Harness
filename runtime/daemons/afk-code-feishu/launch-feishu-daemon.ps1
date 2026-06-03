$ErrorActionPreference = 'Continue'
$log = "$env:USERPROFILE\.afk-code\feishu-daemon.log"
"`n[{0}] feishu launcher start" -f (Get-Date -Format o) | Out-File -FilePath $log -Append -Encoding utf8

# Separate pipe so the Feishu daemon coexists with the Discord daemon.
$env:AFK_DAEMON_SOCKET = '\\.\pipe\afk-code-feishu-daemon'

# Use the local Developer fork (which contains the feishu transport)
& "C:\Program Files\nodejs\node.exe" "{{USER_HOME}}\Developer\afk-code\dist\cli\index.js" feishu *>> $log
"[{0}] feishu launcher exit code={1}" -f (Get-Date -Format o), $LASTEXITCODE | Out-File -FilePath $log -Append -Encoding utf8
