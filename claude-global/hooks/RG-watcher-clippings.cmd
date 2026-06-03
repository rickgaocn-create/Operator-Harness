@echo off
start "" /MIN powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{{VAULT_ROOT}}\.claude\_state\watch_clippings.ps1"
