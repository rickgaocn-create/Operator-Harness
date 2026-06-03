---
category: work
name: claude-for-excel
description: Drive the Claude for Excel desktop add-in from AFK. Use when Excel itself must be opened, prompted, formatted, saved, or recovered through the Office task pane.
model: claude-sonnet-4-6
allowed-tools: Bash, PowerShell, Read, Write, Edit, mcp__windows-mcp__Snapshot, mcp__windows-mcp__Screenshot, mcp__windows-mcp__Click, mcp__windows-mcp__Type, mcp__windows-mcp__Clipboard, mcp__windows-mcp__Shortcut, mcp__windows-mcp__App
---

# Skill: Claude for Excel

Drive the Claude for Excel Office Add-in (the in-Excel task pane) from automation when the user is AFK on Discord. Captures the workflow that took multiple iterations to figure out the first time — read this before driving the pane so you don't re-discover the same gotchas.

## The single most important fact

The Claude pane is rendered inside a **WebView2 iframe** hosted by Excel's Office Add-in task pane. The Reply textarea is a DOM element inside that iframe. UI Automation does not expose it, and OS-level keyboard input does not reach it cleanly until the pane is refreshed.

**If typing/pasting silently fails into the Reply box: click the "A new version is available — Refresh" link in the pane (or any reload action). After reload, `[System.Windows.Forms.SendKeys]::SendWait()` + `mouse_event` click into the textarea start working.** This is the breakthrough; without it `mcp__windows-mcp__Type`, `mcp__windows-mcp__Shortcut "ctrl+v"`, and PowerShell SendKeys all fail.

## End-to-end workflow

### 1. Launch Excel

```powershell
Start-Process excel
```

`mcp__windows-mcp__App mode=launch name=excel` returns `PermissionError [WinError 5]` on this user's machine. Use the PowerShell path.

### 2. Open the Claude pane

Snapshot monitor 2 to find the **Claude** button on the Excel Home ribbon (right side of the ribbon, has been around virtual coords `(3419, 248)` but always re-discover via Snapshot — Office layout shifts). Click it.

First load almost always shows: **"ADD-IN ERROR: This add-in could not be started."** Click **Restart**. After restart the pane loads with skill buttons (`/audit-xls`, `/clean-data-xls`, `/dcf-model`, `/comps-analysis`) and the Reply input.

### 3. Refresh if input fails

If you can't paste into the Reply box (see "single most important fact" above), click the "**A new version is available — Refresh**" banner. If the banner isn't visible, close and re-open the pane via the ribbon Claude button.

### 4. Send a prompt

Stage the prompt on the clipboard, foreground Excel reliably, click the Reply textarea, then paste + submit. The reliable PowerShell sequence:

```powershell
Add-Type -AssemblyName System.Windows.Forms
$sig = '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd); [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x, int y, int cx, int cy, uint flags); [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y); [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, System.UIntPtr dwExtraInfo);'
$t = Add-Type -MemberDefinition $sig -Name Win -Namespace Native -PassThru
$h = (Get-Process EXCEL).MainWindowHandle

# Reliable foreground: topmost-toggle beats stale window order
[void]$t::ShowWindow($h, 9); [void]$t::BringWindowToTop($h)
[void]$t::SetWindowPos($h, [IntPtr](-1), 0,0,0,0, 0x0003)  # HWND_TOPMOST
Start-Sleep -Milliseconds 200
[void]$t::SetWindowPos($h, [IntPtr](-2), 0,0,0,0, 0x0003)  # HWND_NOTOPMOST
[void]$t::SetForegroundWindow($h)
Start-Sleep -Milliseconds 400

# Click into Reply textarea (verify coords via Snapshot — typically near y=773 on monitor 2)
[void]$t::SetCursorPos(3320, 773)
Start-Sleep -Milliseconds 150
$t::mouse_event(0x02, 0,0,0,0, [System.UIntPtr]::Zero)
Start-Sleep -Milliseconds 80
$t::mouse_event(0x04, 0,0,0,0, [System.UIntPtr]::Zero)
Start-Sleep -Milliseconds 450

# Paste + submit
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 500
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
```

### 5. Handle the permission dialog

Every edit fires: **"Permission required — Claude wants to execute office js"** with three buttons:
- Deny (Esc)
- **Dangerously always allow (Ctrl+Enter) ← this user's default**
- Allow once (Enter)

Use **Dangerously always allow**. The user is typically AFK during these sessions and `Allow once` stalls multi-step tasks. The dialog lives in the same WebView, so:

- First try: `[System.Windows.Forms.SendKeys]::SendWait("^{ENTER}")` *only* after re-foregrounding Excel.
- If that doesn't dismiss it (check via Screenshot), click the button directly via `mouse_event` at the button's virtual coords — historically around `(3325, 707)` on monitor 2, verify per session.

### 6. Save the workbook

Excel's COM `[Runtime.InteropServices.Marshal]::GetActiveObject('Excel.Application')` is unreliable on this machine — it often returns a fresh instance with `Workbooks.Count == 0` even with Book1 open. **Drive Save As via the UI:**

```powershell
# Open classic Save As dialog (bypasses Backstage)
[System.Windows.Forms.SendKeys]::SendWait("{F12}")
Start-Sleep -Seconds 2

# Filename field is auto-focused
[System.Windows.Forms.SendKeys]::SendWait("^a")
[System.Windows.Forms.SendKeys]::SendWait("WCAL_260512")  # [PREFIX]_[YYMMDD]
Start-Sleep -Milliseconds 300

# Enter often doesn't trigger Save — click the Save button via mouse_event
# Save button has been near (2839, 663); verify via Snapshot
[void]$t::SetCursorPos(2839, 663)
$t::mouse_event(0x02, 0,0,0,0, [System.UIntPtr]::Zero); Start-Sleep -Milliseconds 60
$t::mouse_event(0x04, 0,0,0,0, [System.UIntPtr]::Zero)
```

**Critical: Documents is redirected on this user's machine.** Test-Path against `{{USER_HOME}}\Documents` will fail. Always resolve via:

```powershell
[Environment]::GetFolderPath('MyDocuments')
# → {{USER_HOME}}\Documents
```

The Save As dialog opens at the right location by default, so just type the bare filename. After first save, subsequent saves are plain `Ctrl+S`.

### 7. Re-engage for follow-ups

The pane keeps conversation state across messages. Paste a new prompt the same way (steps 4–5). No need to re-refresh unless input regresses again.

## Prompt-crafting patterns that work

The pane handles dense, structured natural language well. Effective patterns from the calendar + sales-table tests:

- **Exact cell anchors**: "starting at cell A1 of Sheet1"
- **Layout → Data → Formatting sections** clearly delimited
- **Explicit FORMULA marker**: `Revenue MUST be a live FORMULA = Units * UnitPrice * (1 - Discount)` (caps "FORMULA" reliably gets a real formula, not a value)
- **Hex fill colors**: `#DDEBF7` (meetings light blue), `#E2EFDA` (personal light green), `#FFF2CC` (focus light yellow)
- **Explicit widths/heights/wrap-text** in their own section
- **Verification ask at end**: "Confirm cell count populated and total hours scheduled" — Claude reports back so you can sanity-check

## Common traps

| Trap | Symptom | Fix |
|---|---|---|
| Iframe input black hole | Paste / SendKeys silently fail | Click "Refresh" in pane (step 3) |
| Cell-edit-mode lockup | Status bar shows "Enter", Claude refuses to format | Send `{ESC}` via SendKeys |
| Wrong Excel COM instance | `Workbooks.Count == 0` despite Book1 open | Don't use COM — drive via F12 / SendKeys |
| Focus theft | SetForegroundWindow returns true but Excel stays behind Chrome | Use SetWindowPos HWND_TOPMOST → HWND_NOTOPMOST toggle |
| Wrong Documents path | `Test-Path` fails post-save | Resolve via `[Environment]::GetFolderPath('MyDocuments')` |
| Multi-monitor coord drift | Click lands on wrong app | Snapshot `display=[1]` for fresh virtual-desktop coords each session |

## User preferences (from memory)

- **Permission dialogs**: always pick "Dangerously always allow" — see [`feedback_claude_excel_permissions`](file:///{{USER_HOME}}/.claude/projects/C--Users-Administrator/memory/feedback_claude_excel_permissions.md) auto-memory entry.
- **File naming**: `[XXXX]_[YYMMDD].xlsx` — 4-char descriptive prefix (e.g., `WCAL` for weekly calendar, `SALE` for sales table), then 6-digit date.
- **Save target**: `{{USER_HOME}}\Documents\<filename>` (redirected Documents folder).
- **AFK reality**: user monitors this via Discord and can't respond to mid-task prompts. Bias toward completing the whole multi-step task in one go rather than pausing for each permission.

## When this skill does NOT apply

- User asks for a workbook from the **terminal** with no Excel UI involvement → use `excel-cli` for viewing/JSON-export, and PowerShell COM / Python `openpyxl` / Rust `rust_xlsxwriter` for *writing* xlsx files. The Office Add-in pane has no CLI equivalent.
- User wants Claude to **generate the data only** (no Excel formatting work) → just produce the data here in the Claude Code session and write the xlsx directly without involving the pane.
- User explicitly says "do this without Excel open" or similar → respect it; don't launch Excel.
