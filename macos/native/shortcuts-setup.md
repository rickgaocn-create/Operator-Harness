# Native surface — make the harness OS-invocable

`harness.py` is the single dispatcher for every native capability. Wrap it in a macOS Shortcut, a Siri phrase, a Raycast script, or a hotkey so the harness is reachable from anywhere — not just a terminal.

```
python3 ~/.claude/macos/native/harness.py <command>
  notify "msg" [--title T]     native Notification Center banner
  clip ["label"]              capture clipboard -> 00 Raw/Clippings
  ocr <image> [--to-vault]    on-device Vision OCR (optionally into the vault)
  residue --file f            local-LLM CN residue gate (exit 2 = flagged)
  agenda [--days N]           today's Apple Calendar (JSON)
  remind "title" [--due ...]  add an Apple Reminder
  route --task T              local-vs-cloud route a stdin prompt
  status                      which mac capabilities are live
```

## Wire it (pick what you use)

**Shortcuts.app** — New Shortcut → add **Run Shell Script** → `python3 "$HOME/.claude/macos/native/harness.py" clip`. Name it "Clip to Vault." Now it's:
- **Siri-invocable:** "Hey Siri, Clip to Vault."
- **Hotkey-invocable:** System Settings → Keyboard → assign a shortcut.
- **iPhone-invocable:** the Shortcut syncs via iCloud (runs on the Mac via Continuity, or re-point at the iPhone).

**Raycast** — Create Script Command → call the same dispatcher. Gives a fuzzy-searchable palette of harness actions.

**Quick Action (Finder/Services)** — Automator → Quick Action → Run Shell Script with `harness.py ocr "$1" --to-vault`, set to receive image files → right-click any image → OCR into the vault.

## Two suggested Shortcuts to import

- **"OCR Image"** — needed as the fallback in `ocr.py` if you don't install pyobjc: Shortcut takes an image, runs the built-in *Extract Text from Image* action, returns text. Name it exactly `OCR Image`.
- **"Capture to Harness"** — Run Shell Script `harness.py clip "$(date)"` + a confirmation. Bind to a global hotkey for one-key capture from any app.

## Permissions

The first run of `agenda` / `remind` (AppleScript → Calendar/Reminders) and `clip` (Accessibility/Automation) will trigger a one-time macOS permission prompt. Approve in System Settings → Privacy & Security → Automation / Reminders / Calendar.
