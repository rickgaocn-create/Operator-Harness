#!/usr/bin/env python3
"""UserPromptSubmit hook (cross-platform port of check-pending-signals.ps1).

If .claude/_pending/ has *.signal files created since the last check, inject them so the
session knows to handle them (invoke the corresponding skills, then delete each signal).
Cheap: no output unless there are new signals.
"""
import json, os, sys
from datetime import datetime

VAULT = os.path.expanduser(os.environ.get("OPERATOR_VAULT_ROOT", "{{VAULT_ROOT}}"))
PENDING = os.path.join(VAULT, ".claude", "_pending")
STATE = os.path.join(VAULT, ".claude", "_state")
LAST = os.path.join(STATE, "last-pending-check.timestamp")


def main():
    if not os.path.isdir(PENDING):
        return 0
    os.makedirs(STATE, exist_ok=True)
    last = 0.0
    try:
        last = datetime.fromisoformat(open(LAST, encoding="utf-8").read().strip()).timestamp()
    except Exception:
        last = 0.0

    new = []
    try:
        for fn in sorted(os.listdir(PENDING)):
            if not fn.endswith(".signal"):
                continue
            p = os.path.join(PENDING, fn)
            ctime = os.path.getctime(p)
            if ctime > last:
                try:
                    content = open(p, encoding="utf-8").read().strip()
                except Exception:
                    content = ""
                new.append((datetime.fromtimestamp(ctime).strftime("%H:%M"), fn, content))
    except Exception:
        pass

    try:
        with open(LAST, "w", encoding="utf-8") as fh:
            fh.write(datetime.now().astimezone().isoformat(timespec="seconds"))
    except Exception:
        pass

    if not new:
        return 0
    lines = [f"===== Pending Automation Signals ({len(new)} new) ====="]
    for created, fn, content in new:
        lines.append(f"  - [{created}] {fn}")
        if content:
            lines.append(f"      {content}")
    lines.append("")
    lines.append(f"Action: handle these signals (invoke corresponding skills), then delete each signal file. Signal dir: {PENDING}")
    lines.append("===== End Pending Signals =====")
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit", "additionalContext": "\n".join(lines)}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
