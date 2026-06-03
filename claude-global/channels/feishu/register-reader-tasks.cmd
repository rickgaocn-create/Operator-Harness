@echo off
rem Register the Feishu (Business Morty) reader supervisor tasks.
rem  - feishu-reader-daemon      : ONLOGON  -> launch an interactive reader at logon
rem  - feishu-reader-healthcheck : every 1h -> relaunch if no live reader holds the lock
rem Both run the same idempotent healthcheck (launches only when no reader is alive).
rem /IT = run only when the user is logged on, interactively (needed so the reader
rem gets a real console/TTY; the feishu plugin auto-responds only in interactive mode).
set "PS=powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File \"%USERPROFILE%\.claude\channels\feishu\reader-healthcheck.ps1\""
schtasks /Create /TN "feishu-reader-daemon" /TR "%PS%" /SC ONLOGON /RL HIGHEST /IT /F
schtasks /Create /TN "feishu-reader-healthcheck" /TR "%PS%" /SC HOURLY /MO 1 /RL HIGHEST /IT /F
