# afk-bridges-healthlog.ps1 — daily health snapshot of the 4 AFK bridges.
# Appends ONE summary line per run; adds indented detail lines only on anomaly/drift.
# Scheduled via task RG-afk-bridges-healthlog (daily 23:40, before RG-vault-autocommit
# 23:50 so the line is committed same night). Deterministic, no LLM / token cost.
# Design map: 04 Notes\_system\(C) afk-bridges-overview-2026-05-28.md
# Created 2026-05-29 (option 1 of the autolog choice).

$ErrorActionPreference = 'Continue'
$log = '{{VAULT_ROOT}}\04 Notes\_system\afk-bridges-healthlog.md'

function Get-TaskState($name) {
  $t = Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
  if ($t) { return [string]$t.State } else { return 'MISSING' }
}

$pipes = @()
try { $pipes = [System.IO.Directory]::GetFiles('\\.\pipe\') } catch {}
function Test-Pipe($frag) { return [bool]($pipes | Where-Object { $_ -like "*$frag*" }) }

$nodes = @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue)
function Test-NodeCmd($pat) { return [bool]($nodes | Where-Object { $_.CommandLine -match $pat }) }

$anomalies = @()

# 1. afk-claude2 — active Discord bridge (must be up)
$c2task = Get-TaskState 'afk-code-claude2-daemon'
$c2pipe = Test-Pipe 'afk-code-claude2-daemon'
$c2ok = ($c2task -eq 'Running') -and $c2pipe
if (-not $c2ok) { $anomalies += "claude2 DOWN: task=$c2task pipe-up=$c2pipe (expected Running + pipe present)" }

# 2. rickgao#1495 retirement backstops — today's fix MUST stay in place
$oldTask = Get-TaskState 'afk-code-daemon'
$discordEnv = Test-Path '{{USER_HOME}}\.afk-code\discord.env'
$npxSess = Test-NodeCmd '_npx.*afk-code'
$rickOk = ($oldTask -eq 'Disabled') -and (-not $discordEnv) -and (-not $npxSess)
if ($oldTask -ne 'Disabled') { $anomalies += "rickgao REGRESSION: afk-code-daemon task=$oldTask (expected Disabled)" }
if ($discordEnv)            { $anomalies += "rickgao REGRESSION: ~/.afk-code/discord.env REAPPEARED (token un-retired — contamination risk)" }
if ($npxSess)               { $anomalies += "rickgao REGRESSION: a _npx afk-code session proc is ALIVE (old-stack relaunch via bare 'npx afk-code')" }

# 3. fs-claude — Feishu (Business Morty + Agent Morty)
$fsConsumer = Get-TaskState 'feishu-event-consumer-daemon'
$qdir = '{{USER_HOME}}\.claude\channels\feishu\queue\events'
$qdepth = 0
if (Test-Path $qdir) { $qdepth = @(Get-ChildItem $qdir -File -ErrorAction SilentlyContinue).Count }
$fsOk = ($fsConsumer -eq 'Running') -and ($qdepth -le 20)
if ($fsConsumer -ne 'Running') { $anomalies += "fs-claude: consumer task=$fsConsumer (expected Running)" }
if ($qdepth -gt 20)            { $anomalies += "fs-claude: queue backlog depth=$qdepth (reader may be stalled)" }

# 4. feishu-codex — on-demand daemon; absent pipe is NORMAL (not an anomaly)
$cxPipe = Test-Pipe 'codex-afk-feishu-daemon'

# --- compose ---
$ts  = Get-Date -Format 'yyyy-MM-dd HH:mm'
$c2s = if ($c2ok)  { 'OK' } else { 'WARN' }
$rks = if ($rickOk) { 'OK' } else { 'WARN' }
$fss = if ($fsOk)  { 'OK' } else { 'WARN' }
$cxs = if ($cxPipe) { 'up' } else { 'idle' }
$summary = "- $ts  claude2:$c2s  rickgao-retired:$rks  fs-claude:$fss(q=$qdepth)  feishu-codex:$cxs"

$out = @()
if (-not (Test-Path $log)) {
  $out += '---'
  $out += 'type: dev-log'
  $out += 'created: 2026-05-29'
  $out += 'created-by: claude'
  $out += 'project: harness'
  $out += 're: Daily health snapshot of the 4 AFK bridges (append-only, machine-written)'
  $out += '---'
  $out += ''
  $out += '# AFK Bridges - Daily Health Log'
  $out += ''
  $out += 'Append-only, one line per daily run by `RG-afk-bridges-healthlog` (23:40). Indented `WARN` detail lines appear only when a bridge drifted from its expected state. Curated architecture + fixes live in `(C) afk-bridges-overview-2026-05-28.md`; this file is the diary.'
  $out += ''
  $out += 'Legend: claude2 = active Discord bridge | rickgao-retired = the disabled old stack stays disabled (token retired, no old-stack proc) | fs-claude q= = Feishu inbound queue depth | feishu-codex up/idle = on-demand daemon (idle is normal).'
  $out += ''
}
$out += $summary
foreach ($a in $anomalies) { $out += "    - [!] $a" }

Add-Content -Path $log -Value $out -Encoding UTF8
