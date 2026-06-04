#!/usr/bin/env python3
"""mac-only: deliver a harness alert as a native macOS Notification Center banner.

A macOS-native upgrade over the Windows path (which pushes alerts to Feishu). Routines such
as harness-pulse / reminders can shell out to this for local, glanceable alerts — no phone,
no network. Falls back silently if not on macOS.

Usage:
  notify.py --title "Harness" --message "feishu consumer down" [--subtitle KR1] [--sound Submarine]
  echo "message" | notify.py --title "Harness"

Integration: set HARNESS_NOTIFY="python3 <path>/notify.py" and have a routine call it, or pair
with `terminal-notifier` (brew install terminal-notifier) for actionable/clickable banners.
"""
import argparse, shutil, subprocess, sys


def osascript_notify(title, message, subtitle, sound):
    def esc(s):
        return (s or "").replace("\\", "\\\\").replace('"', '\\"')
    script = f'display notification "{esc(message)}" with title "{esc(title)}"'
    if subtitle:
        script += f' subtitle "{esc(subtitle)}"'
    if sound:
        script += f' sound name "{esc(sound)}"'
    subprocess.run(["osascript", "-e", script], capture_output=True, timeout=10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", default="Operator Harness")
    ap.add_argument("--message", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--sound", default="")
    a = ap.parse_args()
    msg = a.message
    if not msg and not sys.stdin.isatty():
        msg = sys.stdin.read().strip()
    if not msg:
        msg = "(no message)"
    if sys.platform != "darwin":
        print("notify.py: not macOS — no-op", file=sys.stderr)
        return 0
    # prefer terminal-notifier (clickable) if installed, else osascript
    tn = shutil.which("terminal-notifier")
    try:
        if tn:
            args = [tn, "-title", a.title, "-message", msg]
            if a.subtitle:
                args += ["-subtitle", a.subtitle]
            if a.sound:
                args += ["-sound", a.sound]
            subprocess.run(args, capture_output=True, timeout=10)
        else:
            osascript_notify(a.title, msg, a.subtitle, a.sound)
    except Exception as e:
        print(f"notify.py: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
