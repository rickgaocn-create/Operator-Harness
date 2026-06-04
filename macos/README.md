# macOS Port

This brings the operator harness to macOS with **full capability parity** plus a few mac-only extras. The Windows side is untouched — this is an additive overlay (`macos/` + `install/bootstrap.sh` + `install/macos/`).

## Capability parity

| Capability | Windows | macOS (this port) | How |
|---|---|---|---|
| Vault framework, rules, skills, agents | ✅ | ✅ | identical markdown (portable) |
| Lifecycle hooks (memory inject, channel probe, signal drain, Feishu mirror) | `.ps1` | ✅ | ported to python3 in `macos/hooks/` |
| Write-guard / usage-log / middleware / stop-check / judgment / success-miner | `.py` | ✅ | already cross-platform; just rewired |
| 38 autonomous routines (daily/weekly/interval/daemon) | Task Scheduler | ✅ | **launchd** via `taskxml_to_launchd.py` |
| Remote control (Discord/Feishu AFK) | `.ps1` daemons | ✅ | bash launchers + launchd KeepAlive |
| Learning loop (feeders, judgment, reflect) | ✅ | ✅ | Python; runs under launchd |
| WeChat ingest | ✅ | ❌ | WeFlow reads the Windows WeChat DB — no mac equivalent |
| Native notifications | via Feishu push | ✅ **mac-only** | `mac-extras/notify.py` (Notification Center) |
| One-key clipboard capture | FileSystemWatcher | ✅ **mac-only** | `mac-extras/clip-capture.sh` (`pbpaste`) |
| **Local on-device inference** | ❌ cloud-only | ✅ **mac-only** | `ai/` router (MLX / Ollama / Foundation Models) |
| **Free fresh-context localize-cn gate** | ❌ too costly | ✅ **mac-only** | `ai/residue_scan.py` (regex + local LLM) |
| **On-device OCR** (partial WeChat recovery) | ❌ | ✅ **mac-only** | `ai/ocr.py` (Vision framework) |
| **Apple Calendar / Reminders sync** | Feishu calendar | ✅ **mac-only** | `native/eventkit_bridge.py` (osascript) |
| **Siri / Shortcuts / hotkey invocation** | ❌ | ✅ **mac-only** | `native/harness.py` dispatcher |
| **Event-driven capture** | polling watcher | ✅ **upgraded** | launchd `WatchPaths` (event-driven) |

The one genuine loss is **WeChat ingest** (platform-bound to the Windows WeChat client) — and even that is partially recovered via on-device OCR of WeChat screenshots.

## Mac-native AI + surface (beyond parity)

These exploit what the Mac can do that the Windows box structurally can't:

- **Local-inference router** ([`ai/README.md`](ai/README.md)) — runs cheap/high-frequency ops (CN-residue scans, classification, triage, distillation drafts, success-mining) on a local model (MLX / Ollama / Apple Foundation Models), reserving cloud Opus for judgment work. Fixes the per-session cost and unlocks gates that were too costly on cloud. Degrades safely to cloud/regex when no model is up.
- **OS-native invocation** ([`native/shortcuts-setup.md`](native/shortcuts-setup.md)) — `native/harness.py` exposes every capability (notify / clip / ocr / residue / agenda / remind / route) as one dispatcher you wrap in a Shortcut, Siri phrase, Raycast command, or hotkey — and via Continuity, your iPhone.
- **launchd-native triggers** — the clippings watcher is now an event-driven `WatchPaths` agent (fires on change, not on a poll loop).

## How the autonomy port works

The 38 scheduled jobs ship as Task Scheduler XML in `runtime/scheduled-tasks/`. The routines they run are already portable Python/Node — only the *scheduler binding* was Windows. `install/macos/taskxml_to_launchd.py` reads each XML and emits an equivalent `~/Library/LaunchAgents/com.operator-harness.<name>.plist`:

- `ScheduleByDay` → `StartCalendarInterval {Hour, Minute}`
- `ScheduleByWeek` → `StartCalendarInterval {Weekday, Hour, Minute}`
- `Repetition/Interval` (PT3H…) → `StartInterval` (seconds)
- `LogonTrigger`/`BootTrigger` → `RunAtLoad` + `KeepAlive` (daemons)

Verified: all 38 translate and produce valid plists.

## Install

```bash
git clone https://github.com/<you>/Operator-Harness.git operator-harness
cd operator-harness
# dry run first
bash install/bootstrap.sh --vault-root "$HOME/Documents/RG" --dry-run
# real install + register the 38 launchd routines
bash install/bootstrap.sh --vault-root "$HOME/Documents/RG" --register-agents
# add remote-control daemons too (then supply tokens):
# bash install/bootstrap.sh --vault-root "$HOME/Documents/RG" --register-agents --install-daemons
```

What it does: copies `vault/` → vault root and `claude-global/` → `~/.claude`, overlays the python hook ports, substitutes machine placeholders, writes `~/.claude/settings.local.json` from `macos/settings.local.darwin.json`, generates + `launchctl load`s the launchd agents.

**Prereqs:** `python3` (3.12+), Node 18+, Obsidian, `lark-cli` (for Feishu), and optionally `brew install terminal-notifier` for clickable banners.

Verify routines: `launchctl list | grep operator-harness`

## Mac-only extras

- **Native alerts** — point a routine's notifier at `mac-extras/notify.py` to get Notification Center banners instead of (or alongside) Feishu push: `python3 macos/mac-extras/notify.py --title "Harness" --message "feishu consumer down" --sound Submarine`.
- **Clipboard capture** — bind `mac-extras/clip-capture.sh` to a macOS Shortcut / Raycast / Quick-Action hotkey to drop the clipboard into `00 Raw/Clippings` from anywhere.

## Known partial ports

Two Windows niceties are not ported (low value): `inject-catchup-brief.ps1` (its gap-detection overlaps `check-pending-signals`, which **is** ported) and `discord-topic-rename-counter.ps1` (cosmetic channel-rename counter). The macOS settings wire the high-value hooks; add these later if wanted.
