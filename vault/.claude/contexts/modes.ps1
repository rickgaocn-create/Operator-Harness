# Claude Code context-mode launchers — the HARD (interactive) variant of the /mode skill.
#
# Appends a persona to the DEFAULT system prompt via --append-system-prompt
# (verified on Claude Code 2.1.150). It NEVER uses --system-prompt, which REPLACES the
# default and would strip your CLAUDE.md + SessionStart vault load. A normal
# --append launch keeps hooks + CLAUDE.md (only --bare skips those).
#
# Activate: add this line to your PowerShell $PROFILE, then open a new shell —
#   . "D:\Administrator\Documents\{{USER_NAME}}\.claude\contexts\modes.ps1"
#
# Usage:  claude-bd            # interactive Claude, BD lens appended
#         claude-research
#         claude-afk
#         claude-mode bd       # generic form; extra args pass through

$script:EccCtxDir = $PSScriptRoot   # = .claude/contexts (portable; no hardcoded drive)

function claude-mode {
    $Mode = $args[0]
    $rest = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
    if (-not $Mode) { Write-Host "usage: claude-mode <bd|research|afk> [claude args...]"; return }
    $persona = Join-Path $script:EccCtxDir "$Mode.md"
    if (-not (Test-Path -LiteralPath $persona)) {
        $avail = (Get-ChildItem $script:EccCtxDir -Filter *.md |
                  Where-Object { $_.BaseName -notlike '_*' } |
                  ForEach-Object BaseName) -join ', '
        Write-Error "context mode '$Mode' not found. Available: $avail"
        return
    }
    $text = Get-Content -LiteralPath $persona -Raw
    claude --append-system-prompt $text @rest
}

function claude-bd       { claude-mode bd @args }
function claude-research { claude-mode research @args }
function claude-afk      { claude-mode afk @args }
