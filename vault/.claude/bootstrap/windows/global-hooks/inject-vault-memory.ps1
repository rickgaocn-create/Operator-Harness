[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

# Opt-in kill-switch: skip injection entirely when BH_NO_INJECT=1 (behavioral-ablation naked arm).
if ($env:BH_NO_INJECT -eq "1") { exit 0 }

$vault = "{{VAULT_ROOT}}"

# cwd-aware skip: when the session is launched INSIDE the vault (Claudian), vault CLAUDE.md
# auto-loads and @imports me.md + MEMORY.md in full natively — so this static injection would be
# pure redundancy. Skip it. Only inject for sessions launched OUTSIDE the vault (AFK / CLI from
# another cwd), where CLAUDE.md is not auto-discovered. cwd comes from the SessionStart hook's
# stdin JSON. On ANY uncertainty (no stdin / parse fail / no cwd) -> fall through and inject
# (safe default: never silently drop the core).
try {
    if ([Console]::IsInputRedirected) {
        $stdin = [Console]::In.ReadToEnd()
        if ($stdin) {
            $cwd = ($stdin | ConvertFrom-Json -ErrorAction Stop).cwd
            if ($cwd) {
                $cwdN = $cwd.Replace('/', '\').TrimEnd('\').ToLower()
                $vaultN = $vault.ToLower()
                if ($cwdN -eq $vaultN -or $cwdN.StartsWith($vaultN + '\')) { exit 0 }
            }
        }
    }
} catch { }

# Session-start vault memory injection — ALWAYS-ON CORE ONLY (fallback for non-vault-cwd sessions).
# History: 2026-05-25 shrank 109KB(10 files) -> ~17KB(core) so output lands INLINE rather than
# being persisted-to-file entirely (the 2026-05-21 class); the 6 09 Rules/*.md (~53KB) + vault-map
# (~11KB) + MEMORY.md (~21KB) moved ON-DEMAND (index below). Then made cwd-aware (skip in-vault,
# where CLAUDE.md @imports deliver the core natively). Verify: .claude/_eval-fixtures/verify-load.py.

$files = @(
    "$vault\me.md",       # Identity, current focus, work preferences, hard lines
    "$vault\CLAUDE.md"    # Claude operating instructions (role, tone, frameworks, auto-chain)
)

$sections = New-Object System.Collections.Generic.List[string]
foreach ($f in $files) {
    if (Test-Path -LiteralPath $f) {
        try {
            $content = Get-Content -LiteralPath $f -Raw -Encoding UTF8
            $sections.Add("===== Vault file: $f =====`n`n$content")
        } catch {
            $sections.Add("===== Vault file: $f (read error: $($_.Exception.Message)) =====")
        }
    } else {
        $sections.Add("===== Vault file: $f (not found) =====")
    }
}

$header = @"
The following files from the user's Obsidian vault ($vault) are the ALWAYS-ON CORE — identity + operating instructions. Treat them as the permanent memory bank. Write durable behavioral feedback / preferences / identity into the vault (me.md / 09 Rules / Cards / MEMORY.md incident log), where the learn-loop governs it. The Claude Code auto-memory directory is for MACHINE-LOCAL ops/infra pointers only (bridge recovery, tool setup) — never durable knowledge.

ON-DEMAND — NOT loaded here. READ the file (Read tool) before the relevant op:
  - MEMORY.md             — incident-driven hard rules — READ before any high-stakes / forwardable write (CN artifacts, summaries, anything to leadership)
  - vault-map.md          — folder routing, skills index — read when navigating the vault
  - 09 Rules/file-types.md — (C)-prefix, frontmatter, naming — before creating/renaming framework files
  - 09 Rules/cards.md      — Card pillar — before any 02 Cards/ op
  - 09 Rules/action.md     — Action pillar + chain anchors — before any 10 Action/ op
  - 09 Rules/time.md       — Time pillar (12-week/weekly/daily) — before time-cascade ops
  - 09 Rules/tasks.md      — Task Capture Protocol (batch ceiling, routing) — before bulk task writes
  - 09 Rules/raw-immutable.md — 00 Raw/ immutability, 01 Wiki conventions — before 00 Raw/ or 01 Wiki ops

Binding hierarchy when files disagree: 09 Rules/* (framework ops) -> project CLAUDE.md -> root CLAUDE.md -> MEMORY.md (index, not source of truth).

Skills: $vault\.claude\skills\<name>\SKILL.md (auto-trigger via frontmatter). Subagents: $vault\.claude\agents\<name>.md (vault-scoped).

"@

$ctx = $header + "`n" + ($sections -join "`n`n")

$payload = @{
    hookSpecificOutput = @{
        hookEventName     = "SessionStart"
        additionalContext = $ctx
    }
}

$payload | ConvertTo-Json -Depth 10 -Compress
