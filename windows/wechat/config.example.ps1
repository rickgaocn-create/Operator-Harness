# windows/wechat bridge — local config TEMPLATE.
# Copy to config.ps1 (gitignored) and fill in. run-bridge.ps1 dot-sources config.ps1.

# Bearer token the bridge requires; MUST match WEFLOW_TOKEN the harness sends.
# Generate: python -c "import secrets;print(secrets.token_hex(16))"
$env:WECHAT_BRIDGE_TOKEN = ''

# Only if WeChat data is NOT under %USERPROFILE%\Documents\xwechat_files:
#   WECHAT_FILES_ROOT — the xwechat_files dir (the <acct> subdir is auto-discovered), OR
#   WECHAT_DB_DIR     — the exact db_storage path (skips discovery).
# $env:WECHAT_FILES_ROOT = 'E:\path\to\xwechat_files'

# Optional: processes scanned for the SQLCipher key (default: Weixin.exe,WeFlow.exe)
# $env:WECHAT_KEY_PROCS = 'Weixin.exe,WeFlow.exe'
