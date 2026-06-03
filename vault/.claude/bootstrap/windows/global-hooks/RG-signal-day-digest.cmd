@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{{VAULT_ROOT}}\.claude\_state\write_signal.ps1" -Skill "day-digest"
