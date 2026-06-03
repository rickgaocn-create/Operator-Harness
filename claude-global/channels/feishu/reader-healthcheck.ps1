$ErrorActionPreference = 'Continue'

# Feishu (Business Morty) reader healthcheck + supervisor.
#
# The inbound queue is written 24/7 by the supervised feishu-event-consumer-daemon,
# but it is only DRAINED + delivered to Claude by an INTERACTIVE fs-claude session
# (the feishu plugin auto-responds to channel notifications only in TTY mode; a
# headless stream-json session claims the lock and delivers but never takes a turn).
# That reader session is otherwise unsupervised, so if it closes / crashes / the box
# reboots, inbound Feishu messages pile up undelivered. This task keeps one alive.
#
# Runs every 5 min (and at logon) in the user's interactive session. If no live
# reader holds the singleton lock, it relaunches launch-reader.cmd (which opens a
# console-hosted `fs-claude --dangerously-skip-permissions`). Silent on success.

$root      = "$env:USERPROFILE\.claude\channels\feishu"
$pidFile   = Join-Path $root 'queue\READER.pid'   # holds the reader's MCP server (bun) PID
$launcher  = Join-Path $root 'launch-reader.cmd'
$log       = Join-Path $root 'reader-healthcheck.log'
$cooldown  = Join-Path $root '.reader-launch.stamp'

function Reader-Alive {
  if (-not (Test-Path $pidFile)) { return $false }
  $rpid = (Get-Content $pidFile -Raw -ErrorAction SilentlyContinue).Trim()
  if ([string]::IsNullOrWhiteSpace($rpid)) { return $false }
  $p = Get-Process -Id ([int]$rpid) -ErrorAction SilentlyContinue
  return [bool]$p
}

if (Reader-Alive) { exit 0 }  # healthy — stay quiet (no log spam)

# Cooldown: don't relaunch if we launched within the last 120s (a freshly started
# reader needs a few seconds to spawn its MCP server and write READER.pid).
if (Test-Path $cooldown) {
  $age = (New-TimeSpan -Start (Get-Item $cooldown).LastWriteTime -End (Get-Date)).TotalSeconds
  if ($age -lt 120) {
    "[{0}] reader not yet up but launched {1:n0}s ago — within cooldown, skipping" -f (Get-Date -Format o), $age |
      Out-File -FilePath $log -Append -Encoding utf8
    exit 0
  }
}

"[{0}] no live reader (READER.pid missing/dead) — relaunching interactive reader" -f (Get-Date -Format o) |
  Out-File -FilePath $log -Append -Encoding utf8
Set-Content -Path $cooldown -Value (Get-Date -Format o) -Encoding ascii
Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $launcher
