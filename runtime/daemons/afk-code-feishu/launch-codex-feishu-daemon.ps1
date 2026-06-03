$ErrorActionPreference = 'Continue'
$log = "$env:USERPROFILE\.afk-code\codex-feishu-daemon.log"
"`n[{0}] codex-feishu launcher start" -f (Get-Date -Format o) | Out-File -FilePath $log -Append -Encoding utf8

# Keep the Codex Feishu messaging path on the current Open Morty bot.
$env:AFK_DAEMON_SOCKET = '\\.\pipe\codex-afk-feishu-daemon'
$env:AFK_DAEMON_TOKEN = 'codex-afk-feishu-session-v1'
$env:AFK_FEISHU_CONFIG_FILE = "$env:USERPROFILE\.afk-code\codex-feishu.env"
$env:FEISHU_LARK_PROFILE = 'codex-afk-feishu'
$env:AFK_FEISHU_START_COMMAND = 'feishu-codex'

& "C:\Program Files\nodejs\node.exe" "{{USER_HOME}}\Developer\afk-code\dist\cli\index.js" feishu *>> $log
"[{0}] codex-feishu launcher exit code={1}" -f (Get-Date -Format o), $LASTEXITCODE | Out-File -FilePath $log -Append -Encoding utf8
