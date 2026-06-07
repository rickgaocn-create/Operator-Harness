@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\Administrator\Documents\{{USER_NAME}}\.claude\_state\write_signal.ps1" -Skill "card-lint"
