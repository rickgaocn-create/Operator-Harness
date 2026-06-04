#!/usr/bin/env python3
"""Single dispatcher for the mac harness's native capabilities.

This is the one entry point you wrap in a macOS Shortcut, a Siri phrase, a Raycast script, or a
hotkey — so the whole harness is invocable from anywhere in the OS, not just a terminal.

  harness.py notify "msg" [--title T]      native Notification Center banner
  harness.py clip ["label"]                capture clipboard -> 00 Raw/Clippings
  harness.py ocr <image> [--to-vault]      on-device Vision OCR (-> vault)
  harness.py residue --file f              local-LLM CN residue gate (exit 2 = flagged)
  harness.py agenda [--days N]             today's Apple Calendar (JSON)
  harness.py remind "title" [--due ...]    add an Apple Reminder
  harness.py route --task T                local-vs-cloud route a stdin prompt
  harness.py status                        which mac capabilities are live

Bind example (Shortcuts "Run Shell Script"):  python3 ~/.claude/macos/native/harness.py clip
"""
import argparse, os, subprocess, sys

AI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai")
EXTRAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mac-extras")
HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(script, *args, stdin=None):
    return subprocess.run([PY, script, *args], input=stdin, text=True).returncode


def main():
    ap = argparse.ArgumentParser(add_help=True)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("notify"); n.add_argument("message"); n.add_argument("--title", default="Operator Harness")
    c = sub.add_parser("clip"); c.add_argument("label", nargs="?", default="clipboard")
    o = sub.add_parser("ocr"); o.add_argument("image"); o.add_argument("--to-vault", action="store_true")
    r = sub.add_parser("residue"); r.add_argument("--file", required=True)
    ag = sub.add_parser("agenda"); ag.add_argument("--days", type=int, default=1)
    rm = sub.add_parser("remind"); rm.add_argument("title"); rm.add_argument("--due", default="")
    rt = sub.add_parser("route"); rt.add_argument("--task", required=True)
    sub.add_parser("status")
    a = ap.parse_args()

    if a.cmd == "notify":
        return run(os.path.join(EXTRAS, "notify.py"), "--title", a.title, "--message", a.message)
    if a.cmd == "clip":
        return subprocess.run(["/bin/bash", os.path.join(EXTRAS, "clip-capture.sh"), a.label]).returncode
    if a.cmd == "ocr":
        args = [a.image] + (["--to-vault"] if a.to_vault else [])
        return run(os.path.join(AI, "ocr.py"), *args)
    if a.cmd == "residue":
        return run(os.path.join(AI, "residue_scan.py"), "--file", a.file)
    if a.cmd == "agenda":
        return run(os.path.join(HERE, "eventkit_bridge.py"), "agenda", "--days", str(a.days))
    if a.cmd == "remind":
        args = ["remind", a.title] + (["--due", a.due] if a.due else [])
        return run(os.path.join(HERE, "eventkit_bridge.py"), *args)
    if a.cmd == "route":
        return run(os.path.join(AI, "router.py"), "--task", a.task, stdin=sys.stdin.read() if not sys.stdin.isatty() else "")
    if a.cmd == "status":
        sys.path.insert(0, AI)
        try:
            import local_llm
            llm = f"local LLM: backend={local_llm._backend()} available={local_llm.available()}"
        except Exception as e:
            llm = f"local LLM: unavailable ({e})"
        mac = sys.platform == "darwin"
        print(f"platform: {sys.platform} ({'mac native ops live' if mac else 'mac ops disabled off-darwin'})")
        print(llm)
        for tool in ("osascript", "shortcuts", "pbpaste", "screencapture", "lark-cli", "ollama"):
            from shutil import which
            print(f"  {tool}: {'yes' if which(tool) else 'no'}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
