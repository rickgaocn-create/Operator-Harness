@echo off
rem Wrapper used by the feishu-event-consumer-daemon scheduled task.
rem Keeps the schtasks /TR string flag-free so schtasks doesn't misparse
rem the embedded powershell arguments.
powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%USERPROFILE%\.claude\channels\feishu\launch-consumer.ps1"
