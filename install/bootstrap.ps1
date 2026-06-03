#requires -Version 5.1
<#
.SYNOPSIS
  Install the operator harness onto this machine: copy the vault framework and the
  ~/.claude machinery into place, substitute machine-specific placeholders, and
  (optionally) register the scheduled tasks and daemon launchers.

.DESCRIPTION
  Reads install\config.json (see config.example.json), resolves machine values
  (auto-detecting any left null), then:
    1. copies ./vault/*          -> <vaultRoot>
    2. copies ./claude-global/*  -> <userHome>\.claude
    3. rewrites {{VAULT_ROOT}} / {{USER_HOME}} / {{PYTHON_EXE}} / {{TASK_USER}} /
       {{HOSTNAME}} in all copied text files
    4. optional: registers runtime\scheduled-tasks\*.xml (placeholders substituted)
    5. optional: copies runtime\daemons launchers into home dirs

  It does NOT fill in your secrets or personal identity placeholders
  ({{FEISHU_*}}, {{USER_NAME}}, {{ORG_*}}, ...). Do that by hand after install
  (see INSTALL.md / SECURITY.md).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install\bootstrap.ps1 -ConfigPath install\config.json
#>
[CmdletBinding()]
param(
  [string]$ConfigPath = "$PSScriptRoot\config.json",
  [switch]$Force,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Info($m){ Write-Host "[*] $m" -ForegroundColor Cyan }
function Ok($m){ Write-Host "[+] $m" -ForegroundColor Green }
function Warn($m){ Write-Host "[!] $m" -ForegroundColor Yellow }

# ---- 1. config ----
if (-not (Test-Path $ConfigPath)) {
  throw "Config not found: $ConfigPath  (copy config.example.json -> config.json and edit it)"
}
$cfg = Get-Content $ConfigPath -Raw | ConvertFrom-Json

$vaultRoot = $cfg.vaultRoot
if ([string]::IsNullOrWhiteSpace($vaultRoot)) { throw "config.vaultRoot is required" }
$userHome  = if ($cfg.userHome)  { $cfg.userHome }  else { $env:USERPROFILE }
$pythonExe = if ($cfg.pythonExe) { $cfg.pythonExe } else { (Get-Command python -ErrorAction SilentlyContinue).Source }
if ([string]::IsNullOrWhiteSpace($pythonExe)) { Warn "Python not found on PATH; set config.pythonExe. Hooks that call Python will fail until you do." }
$taskUser  = if ($cfg.taskUser)  { $cfg.taskUser }  else { "$env:USERDOMAIN\$env:USERNAME" }
$hostName  = if ($cfg.hostname)  { $cfg.hostname }  else { $env:COMPUTERNAME }

$claudeHome = Join-Path $userHome '.claude'

Info "vaultRoot  = $vaultRoot"
Info "userHome   = $userHome   (-> $claudeHome)"
Info "pythonExe  = $pythonExe"
Info "taskUser   = $taskUser"
Info "hostname   = $hostName"
if ($DryRun) { Warn "DRY RUN — no files will be written." }

$map = @{
  '{{VAULT_ROOT}}' = $vaultRoot
  '{{USER_HOME}}'  = $userHome
  '{{PYTHON_EXE}}' = $pythonExe
  '{{TASK_USER}}'  = $taskUser
  '{{HOSTNAME}}'   = $hostName
}

$TextExt = '.md','.py','.ps1','.cmd','.mjs','.cjs','.ts','.js','.json','.toml','.xml','.txt','.sh','.base','.tmpl','.npmrc'

function Substitute-Tree($root) {
  Get-ChildItem -Path $root -Recurse -File | Where-Object { $TextExt -contains $_.Extension.ToLower() } | ForEach-Object {
    $p = $_.FullName
    try {
      $raw = [System.IO.File]::ReadAllText($p)
      $new = $raw
      foreach ($k in $map.Keys) { $new = $new.Replace($k, [string]$map[$k]) }
      if ($new -ne $raw -and -not $DryRun) {
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($p, $new, $utf8NoBom)
      }
    } catch { Warn "skip (binary/locked): $p" }
  }
}

function Copy-Tree($src, $dst) {
  if (-not (Test-Path $src)) { return }
  if ((Test-Path $dst) -and -not $Force) {
    Warn "$dst already exists. Merging (existing files overwritten). Use -Force to silence this warning."
  }
  if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    Copy-Item -Path (Join-Path $src '*') -Destination $dst -Recurse -Force
  }
  Info "copied $src -> $dst"
}

# ---- 2. copy vault + claude-global ----
Copy-Tree (Join-Path $RepoRoot 'vault')         $vaultRoot
Copy-Tree (Join-Path $RepoRoot 'claude-global') $claudeHome

# ---- 3. substitute placeholders in the installed trees ----
if (-not $DryRun) {
  Info "substituting machine placeholders..."
  Substitute-Tree $vaultRoot
  Substitute-Tree $claudeHome
  Ok "placeholders substituted"
}

# ---- 4. scheduled tasks (optional) ----
if ($cfg.registerScheduledTasks) {
  Info "registering scheduled tasks..."
  $tmp = Join-Path $env:TEMP ("oh-tasks-" + [System.Guid]::NewGuid().ToString('N'))
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  Get-ChildItem (Join-Path $RepoRoot 'runtime\scheduled-tasks') -Filter *.xml | ForEach-Object {
    $name = $_.BaseName
    $xml = [System.IO.File]::ReadAllText($_.FullName)
    foreach ($k in $map.Keys) { $xml = $xml.Replace($k, [string]$map[$k]) }
    $outXml = Join-Path $tmp ($name + '.xml')
    [System.IO.File]::WriteAllText($outXml, $xml, (New-Object System.Text.UnicodeEncoding))
    if (-not $DryRun) {
      try {
        schtasks /Create /TN $name /XML $outXml /F /RU $taskUser | Out-Null
        Ok "task: $name"
      } catch { Warn "task FAILED: $name — $($_.Exception.Message)" }
    } else { Info "would register task: $name" }
  }
  Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
} else {
  Warn "registerScheduledTasks=false — skipping. Set it true in config.json (after reviewing runtime\scheduled-tasks) to enable automation."
}

# ---- 5. daemons (optional) ----
if ($cfg.installDaemons) {
  Info "installing daemon launchers..."
  $dmap = @{
    'afk-code-claude2' = (Join-Path $userHome '.afk-code-claude2')
    'fs-claude-daemon' = (Join-Path $userHome '.fs-claude-daemon')
    'afk-code-feishu'  = (Join-Path $userHome '.afk-code')
  }
  foreach ($d in $dmap.Keys) {
    Copy-Tree (Join-Path $RepoRoot "runtime\daemons\$d") $dmap[$d]
    if (-not $DryRun) { Substitute-Tree $dmap[$d] }
  }
  Warn "daemons need tokens: create the .env / access.json files yourself (see INSTALL.md). Launchers are installed but will not run without them."
}

Write-Host ""
Ok "Install complete."
Write-Host @"

NEXT STEPS (manual — not done by this script):
  1. Personalize:  $vaultRoot\me.md , \CLAUDE.md , \MEMORY.md  (rewrite {{USER_NAME}}/{{ORG_*}}/{{PROJECT_*}} placeholders)
  2. Channel secrets: create Discord/Feishu tokens and place them in the gitignored
     .env / access.json files the daemons expect (see INSTALL.md).
  3. Claude Code settings: copy claude-global\settings.local.example.json -> $claudeHome\settings.local.json and wire per-machine hooks.
  4. Open the vault in Obsidian; install the community plugins listed in .obsidian (claudian, dataview, templater, smart-connections, operon, harness-dashboard).
  5. Verify a session: launch Claude Code in the vault and confirm the SessionStart hooks fire.
"@ -ForegroundColor Gray
