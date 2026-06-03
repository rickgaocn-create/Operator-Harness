$ErrorActionPreference = 'SilentlyContinue'
$log = "$env:USERPROFILE\.afk-code-claude2\healthcheck.log"
$pipeName = 'afk-code-claude2-daemon'
$entryMatch = '*afk-code-claude2\node_modules\afk-code\dist\cli\index.js discord*'
function Log($m) { "[{0}] {1}" -f (Get-Date -Format o), $m | Out-File -FilePath $log -Append -Encoding utf8 }

# 1) Pipe reachable?
$pipeOk = $false
try {
  $pipe = New-Object System.IO.Pipes.NamedPipeClientStream('.', $pipeName, [System.IO.Pipes.PipeDirection]::Out)
  $pipe.Connect(500); $pipe.Dispose(); $pipeOk = $true
} catch { $pipeOk = $false }

# 2) Orphan check — a daemon whose parent launcher died is a zombie: its inherited
#    stdout is broken (logs vanish) and, pre-shield-hardening, channel creation
#    aborts. The pipe stays open so step 1 alone can't see this. Recycle it.
$orphan = $false
$daemons = @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like $entryMatch })
foreach ($d in $daemons) {
  $parent = Get-CimInstance Win32_Process -Filter "ProcessId=$($d.ParentProcessId)"
  if (-not $parent) {
    $orphan = $true
    Log "daemon PID=$($d.ProcessId) ORPHANED (parent $($d.ParentProcessId) dead) — recycling"
  }
}

# 3) Functional wedge (2026-05-29 incident) — daemon alive + parented + pipe-up
#    but NOT PROCESSING. A stale Discord gateway makes the awaited channel-create
#    hang, so a fresh session_start is received yet nothing is ever logged; the
#    pipe + orphan probes above both stay green. Signature: a client logged a
#    "daemon connected" newer than daemon.log's last write, and enough time has
#    passed that the daemon should have responded. Only meaningful when NOT an
#    orphan (parent alive => stdout intact => a frozen log truly means stuck).
$wedged = $false
$clientLog = "$env:USERPROFILE\afk-client.log"
$daemonLog = "$env:USERPROFILE\.afk-code-claude2\daemon.log"
if ($pipeOk -and -not $orphan -and (Test-Path $clientLog) -and (Test-Path $daemonLog)) {
  try {
    $connectLine = Select-String -Path $clientLog -Pattern 'daemon connected: yes' | Select-Object -Last 1
    if ($connectLine -and $connectLine.Line -match '^\[(?<ts>[^\]]+)\]') {
      $lastConnectUtc = ([datetimeoffset]$Matches.ts).UtcDateTime
      $daemonWriteUtc = (Get-Item $daemonLog).LastWriteTimeUtc
      $sinceConnect = ((Get-Date).ToUniversalTime() - $lastConnectUtc).TotalSeconds
      if ($lastConnectUtc -gt $daemonWriteUtc -and $sinceConnect -gt 120) {
        $wedged = $true
        Log ("daemon WEDGED — client connect {0:o} is newer than daemon.log write {1:o} and {2:n0}s elapsed with no daemon activity — recycling" -f $lastConnectUtc, $daemonWriteUtc, $sinceConnect)
      }
    }
  } catch { Log "wedge-check error: $_" }
}

if ($pipeOk -and -not $orphan -and -not $wedged) { exit 0 }   # healthy: quiet exit, no log spam

# Unhealthy: tear down every claude2 daemon so the pipe frees, then relaunch once.
if (-not $pipeOk) { Log "pipe '$pipeName' unreachable" }
foreach ($d in @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -like $entryMatch })) {
  Stop-Process -Id $d.ProcessId -Force
  Log "killed daemon PID=$($d.ProcessId)"
}
& schtasks /End /TN "afk-code-claude2-daemon" 2>&1 | Out-Null
$kick = & schtasks /Run /TN "afk-code-claude2-daemon" 2>&1
Log "relaunched daemon task: $($kick -join ' ')"
