# capability-dev-scan.ps1 — daily snapshot-diff of the "capability surface".
# Captures what bots/skills/capabilities changed across sessions (most of which
# live in code dirs OUTSIDE the vault, invisible to vault-evolve's vault-only
# telemetry). Deterministic, 0-token. Mirrors the harness-pulse role: CAPTURE.
# vault-evolve later CONSUMES the log it writes (see the 🟡 proposal in
# 04 Notes/vault-evolve/_decisions.md for the Phase-1/Phase-5 hook).
#
# Snapshot state: .claude/_state/capability-snapshot.json (prev run, for diffing)
# Human log:      04 Notes/_system/capability-dev-log.md (append-only)
# Scheduled via:  {{USER_NAME}}-capability-dev-scan (daily 23:35, before vault autocommit 23:50)
# Created 2026-05-29 (option 1 of the capability-autolog choice).

$ErrorActionPreference = 'Continue'
$snapFile = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\_state\capability-snapshot.json'
$log      = 'D:\Administrator\Documents\{{USER_NAME}}\04 Notes\_system\capability-dev-log.md'

function ObjToMap($o) {
  $h = @{}
  if ($o) { foreach ($p in $o.PSObject.Properties) { $h[$p.Name] = $p.Value } }
  return $h
}
function Diff-Map($old, $new, $label) {
  $c = @()
  foreach ($k in $new.Keys) {
    if (-not $old.ContainsKey($k)) { $c += "+ $label $k (new: $($new[$k]))" }
    elseif ("$($old[$k])" -ne "$($new[$k])") { $c += "~ $label ${k}: $($old[$k]) -> $($new[$k])" }
  }
  foreach ($k in $old.Keys) { if (-not $new.ContainsKey($k)) { $c += "- $label $k (removed)" } }
  return $c
}
function Diff-List($old, $new, $label) {
  $c = @()
  foreach ($x in $new) { if ($old -notcontains $x) { $c += "+ $label $x (new)" } }
  foreach ($x in $old) { if ($new -notcontains $x) { $c += "- $label $x (removed)" } }
  return $c
}

# --- snapshot the capability surface ---
$tasks = @{}
Get-ScheduledTask -ErrorAction SilentlyContinue |
  Where-Object { $_.TaskName -match '^({{USER_NAME}}-|afk-|feishu-|VaultEvolve)' } |
  ForEach-Object { $tasks[$_.TaskName] = [string]$_.State }

function Skill-Names($p) {
  if (Test-Path $p) { return @(Get-ChildItem $p -Directory -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object) }
  return @()
}
$skillsUser  = Skill-Names '{{USER_HOME}}\.claude\skills'
$skillsVault = Skill-Names 'D:\Administrator\Documents\{{USER_NAME}}\.claude\skills'

$launchers = @()
foreach ($d in '{{USER_HOME}}\bin','{{USER_HOME}}\.local\bin') {
  if (Test-Path $d) { $launchers += (Get-ChildItem $d -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) }
}
$launchers = @($launchers | Sort-Object -Unique)

$plugins = @{}
$pc = '{{USER_HOME}}\.claude\plugins\cache\local'
if (Test-Path $pc) {
  Get-ChildItem $pc -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $vers = @(Get-ChildItem $_.FullName -Directory -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object)
    $plugins[$_.Name] = ($vers -join ',')
  }
}

$afkHead = ''; $afkDirty = -1
$ad = '{{USER_HOME}}\Developer\afk-code'
if (Test-Path (Join-Path $ad '.git')) {
  try { $afkHead  = (& git -C $ad rev-parse --short HEAD 2>$null) } catch {}
  try { $afkDirty = @(& git -C $ad status --porcelain 2>$null).Count } catch {}
}

$routines = @{}
$rd = 'D:\Administrator\Documents\{{USER_NAME}}\.claude\routines'
if (Test-Path $rd) {
  Get-ChildItem $rd -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in '.ps1','.py' } |
    ForEach-Object { $routines[$_.Name] = $_.LastWriteTimeUtc.Ticks }
}

$watched = @{}
foreach ($f in @(
  '{{USER_HOME}}\.claude\plugins\marketplaces\local\feishu\server.ts',
  '{{USER_HOME}}\.afk-code-claude2\node_modules\afk-code\dist\cli\index.js'
)) { if (Test-Path $f) { $watched[$f] = (Get-Item $f).LastWriteTimeUtc.Ticks } }

$ts = Get-Date -Format 'yyyy-MM-dd HH:mm'
$snap = @{ ts=$ts; tasks=$tasks; skillsUser=$skillsUser; skillsVault=$skillsVault;
          launchers=$launchers; plugins=$plugins; afkHead=$afkHead; afkDirty=$afkDirty;
          routines=$routines; watched=$watched }

# --- diff vs prior snapshot ---
$old = $null
if (Test-Path $snapFile) {
  try { $old = Get-Content $snapFile -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $old = $null }
}

$changes = @()
$firstRun = ($null -eq $old)
if (-not $firstRun) {
  $changes += Diff-Map  (ObjToMap $old.tasks)   $tasks       'task'
  $changes += Diff-List @($old.skillsUser)      $skillsUser  'skill(user)'
  $changes += Diff-List @($old.skillsVault)     $skillsVault 'skill(vault)'
  $changes += Diff-List @($old.launchers)       $launchers   'launcher'
  $changes += Diff-Map  (ObjToMap $old.plugins) $plugins     'plugin'
  if ($old.afkHead -and $afkHead -and "$($old.afkHead)" -ne "$afkHead") { $changes += "~ afk-code git HEAD $($old.afkHead) -> $afkHead" }
  if ($afkDirty -ge 0 -and $null -ne $old.afkDirty -and [int]$old.afkDirty -ne $afkDirty) { $changes += "~ afk-code dirty-files $($old.afkDirty) -> $afkDirty" }
  $oldR = ObjToMap $old.routines
  foreach ($k in $routines.Keys) {
    if (-not $oldR.ContainsKey($k)) { $changes += "+ routine $k (new)" }
    elseif ("$($oldR[$k])" -ne "$($routines[$k])") { $changes += "~ routine $k (edited)" }
  }
  foreach ($k in $oldR.Keys) { if (-not $routines.ContainsKey($k)) { $changes += "- routine $k (removed)" } }
  $oldW = ObjToMap $old.watched
  foreach ($k in $watched.Keys) {
    if (-not $oldW.ContainsKey($k)) { $changes += "+ watched $(Split-Path $k -Leaf) (now tracked)" }
    elseif ("$($oldW[$k])" -ne "$($watched[$k])") { $changes += "~ edited $(Split-Path $k -Leaf)" }
  }
}

# --- write new snapshot ---
$snap | ConvertTo-Json -Depth 6 | Set-Content -Path $snapFile -Encoding UTF8

# --- append to human log ---
$out = @()
if (-not (Test-Path $log)) {
  $out += '---'
  $out += 'type: dev-log'
  $out += 'created: 2026-05-29'
  $out += 'created-by: claude'
  $out += 'project: harness'
  $out += 're: Daily capability/bot development autolog (append-only, machine-written; consumed by vault-evolve)'
  $out += '---'
  $out += ''
  $out += '# Capability / Bot Development Log'
  $out += ''
  $out += 'Append-only, one line per daily run by `{{USER_NAME}}-capability-dev-scan` (23:35). Tracks the capability surface that lives OUTSIDE the vault: scheduled tasks, skills (user + vault), launchers, plugin versions, `~/Developer/afk-code` git, vault routines, and key daemon files. Indented `+ / - / ~` detail lines list what changed since the prior snapshot. vault-evolve consumes this as a Phase-1 telemetry source.'
  $out += ''
}
if ($firstRun) {
  $out += "- $ts  baseline captured (tasks=$($tasks.Count) skills-user=$($skillsUser.Count) skills-vault=$($skillsVault.Count) launchers=$($launchers.Count) plugins=$($plugins.Count) routines=$($routines.Count); afk-code HEAD=$afkHead dirty=$afkDirty) - first run, no diff"
} else {
  $out += "- $ts  changes: $($changes.Count)"
  foreach ($c in $changes) { $out += "    $c" }
}
Add-Content -Path $log -Value $out -Encoding UTF8
