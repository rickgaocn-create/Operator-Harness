@echo off
rem launch-reader.cmd - open an INTERACTIVE Business Morty (Feishu) queue-reader
rem session in its own console. The feishu plugin only auto-responds to channel
rem notifications in interactive (TTY) mode; headless stream-json delivers but
rem never takes a turn. fs-claude sets FEISHU_READ_QUEUE=1 so this session claims
rem the singleton reader role (queue/READER.pid) and drains inbound events.
rem /D launches the session INSIDE the {{USER_NAME}} vault so Claude loads the vault as its
rem project harness (vault CLAUDE.md + .claude/{settings,skills,agents,hooks}).
rem Mission-critical per {{USER_NAME}} 2026-05-26: AFK reader must be vault-rooted by default.
start "BusinessMortyReader" /D "{{VAULT_ROOT}}" cmd /k "fs-claude --dangerously-skip-permissions"
