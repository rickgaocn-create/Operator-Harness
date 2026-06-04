#!/usr/bin/env python3
"""SessionStart hook (macOS/cross-platform port of check-channel-state.ps1).

Probes which inbound channel daemons are alive and injects a one-line state banner so the
session knows whether Discord / Feishu remote control is live. Uses `ps` (mac/linux);
falls back to `tasklist` on Windows. Never blocks; on any error, injects nothing.
"""
import json, os, subprocess, sys


def _process_cmdlines():
    """Return a list of full process command lines, cross-platform."""
    try:
        if sys.platform == "win32":
            out = subprocess.run(["tasklist", "/v", "/fo", "csv"], capture_output=True,
                                 text=True, timeout=8).stdout
            return out.splitlines()
        out = subprocess.run(["ps", "-axww", "-o", "command"], capture_output=True,
                             text=True, timeout=8).stdout
        return out.splitlines()
    except Exception:
        return []


def main():
    lines = _process_cmdlines()
    blob = "\n".join(lines).lower()

    def alive(*markers):
        return any(all(m in ln.lower() for m in markers) for ln in lines)

    discord = alive("afk-code", "launch-daemon") or alive("node", "afk-code-claude2") \
        or ("afk-code-claude2" in blob and "node" in blob)
    feishu = alive("lark-cli", "consume") or alive("launch-consumer") \
        or ("event" in blob and "consume" in blob and "lark" in blob)

    if not (discord or feishu):
        return 0  # nothing live -> say nothing (matches Windows no-op behavior)

    parts = []
    parts.append("🟢 Discord (afk) LIVE" if discord else "⚪ Discord not detected")
    parts.append("🟢 Feishu inbound LIVE" if feishu else "⚪ Feishu not detected")
    banner = ("Inbound channel state (macOS probe): " + " · ".join(parts) +
              ". Replies you make may be mirrored to the originating channel.")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SessionStart", "additionalContext": banner}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # a probe must never break SessionStart
