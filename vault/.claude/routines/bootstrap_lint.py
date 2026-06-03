#!/usr/bin/env python3
"""bootstrap_lint.py - drift gate for OUT-OF-VAULT global hooks vs the in-vault baseline.

The live SessionStart/signal hooks live at ~/.claude/hooks (machine-local, OUTSIDE the
vault); the vault keeps recovery copies under .claude/bootstrap/windows/global-hooks.
A mirror that silently drifts gives false recovery confidence (the brief-deploy-gap that
motivated this: bootstrap was ahead of live, unnoticed). This compares them.

  --check : report in-sync / drifted / unmirrored / orphan; exit 1 on drift or unmirrored.
  --sync  : promote live -> bootstrap (copy every live hook into the baseline). Deliberate.
  (default): human-readable report.

Windows-scoped (this machine's hooks); the macOS baseline lives under a sibling dir.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT  # noqa: E402  (discovered vault root)

LIVE = Path.home() / ".claude" / "hooks"
BOOT = VAULT / ".claude" / "bootstrap" / "windows" / "global-hooks"


def scan() -> dict:
    """Compare live hooks to the baseline. Never raises."""
    insync, drift, unmirrored, orphan = [], [], [], []
    try:
        live_files = sorted(p for p in LIVE.glob("*") if p.is_file()) if LIVE.exists() else []
    except Exception:
        live_files = []
    for f in live_files:
        b = BOOT / f.name
        try:
            if not b.exists():
                unmirrored.append(f.name)
            elif filecmp.cmp(str(f), str(b), shallow=False):
                insync.append(f.name)
            else:
                drift.append(f.name)
        except Exception:
            continue
    if BOOT.exists():
        for b in sorted(BOOT.glob("*")):
            if b.is_file() and not (LIVE / b.name).exists():
                orphan.append(b.name)
    return {"insync": insync, "drift": drift, "unmirrored": unmirrored, "orphan": orphan}


def sync() -> int:
    BOOT.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(LIVE.glob("*")):
        if f.is_file():
            shutil.copy2(str(f), str(BOOT / f.name))
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 on drift/unmirrored")
    ap.add_argument("--sync", action="store_true", help="promote live hooks -> baseline")
    args = ap.parse_args()
    if args.sync:
        print(f"bootstrap sync: copied {sync()} live hook(s) -> baseline")
        return 0
    s = scan()
    bad = len(s["drift"]) + len(s["unmirrored"])
    if args.check:
        print(f"bootstrap-drift: {len(s['insync'])} in-sync, {len(s['drift'])} drifted, "
              f"{len(s['unmirrored'])} unmirrored, {len(s['orphan'])} orphan")
        for d in s["drift"]:
            print(f"  DRIFT: {d}")
        for u in s["unmirrored"]:
            print(f"  UNMIRRORED: {u}")
        return 1 if bad else 0
    for k in ("insync", "drift", "unmirrored", "orphan"):
        print(f"{k}: {s[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
