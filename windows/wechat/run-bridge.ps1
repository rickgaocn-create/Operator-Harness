# run-bridge.ps1 — launch the native WeChat reader bridge (WeFlow replacement) on Windows.
# Used by the wechat-bridge scheduled task (runtime/scheduled-tasks/). Sets the token the harness
# already expects (WEFLOW_TOKEN default) so ingest.py / wechat_schedule_capture.py work unchanged.
#
# Cutover: ensure 微信 (Weixin.exe) is running, STOP WeFlow.exe, then enable the bridge task.
# The bridge reads the SQLCipher key from Weixin.exe's memory; 微信 must be open.

$ErrorActionPreference = 'Continue'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Local config (gitignored): sets $env:WECHAT_BRIDGE_TOKEN (must match WEFLOW_TOKEN the harness
# sends) and, if WeChat data is on another drive, $env:WECHAT_FILES_ROOT. Copy config.example.ps1
# to config.ps1 and fill it in. See README.md "Run".
if (Test-Path "$dir\config.ps1") { . "$dir\config.ps1" }

$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = '{{PYTHON_EXE}}' }

& $py (Join-Path $dir 'wechat_bridge.py') --port 5031 --host 127.0.0.1
