@echo off
rem Wrapper used by the feishu-event-consumer-daemon-personal scheduled task (PERSONAL tenant).
rem Sibling of launch-consumer.cmd — same pattern, points at the personal launcher script.
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%USERPROFILE%\.claude\channels\feishu\launch-consumer-personal.ps1"
