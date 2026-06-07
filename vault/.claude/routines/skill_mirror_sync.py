#!/usr/bin/env python3
"""skill_mirror_sync.py — the missing OTHER HALF of skill-mirror-parity.py.

parity checks `.claude/skills` (canonical) == `.agents/skills` (neutral re-export) and
exits 1 on drift — but nothing ever PERFORMED the re-export, so the mirror silently rotted
(9 missing / 43 byte-divergent at the 2026-06-06 pulse). A check with no paired sync is a
nag, not a loop. This re-exports canonical -> mirror: copies every canonical skill dir into
`.agents/skills`, overwriting divergent files and adding missing ones. Idempotent.

"Neutral re-export" = a runtime-neutral LOCATION, not transformed content: parity hashes
SKILL.md (EOL-normalized) and expects identity, so a faithful copy is exactly what restores
parity. Orphans (skill dirs only in the mirror) are left alone unless --prune (non-destructive
by default).

  python skill_mirror_sync.py            # sync canonical -> mirror; print what changed
  python skill_mirror_sync.py --prune    # also remove orphan dirs present only in the mirror
  python skill_mirror_sync.py --json
Exit 0 on success (even no-op); 1 only on a copy error.
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = Path(__file__).resolve().parents[2]  # routines -> .claude -> vault
CANON = VAULT / ".claude" / "skills"
MIRROR = VAULT / ".agents" / "skills"


def _skill_names(root: Path) -> set:
    if not root.is_dir():
        return set()
    return {d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith("_")}


def sync(prune: bool = False) -> dict:
    """Re-export canonical skill dirs into the mirror. Returns a change report. Never raises
    per-skill (records the error, continues)."""
    MIRROR.mkdir(parents=True, exist_ok=True)
    canon, mirror = _skill_names(CANON), _skill_names(MIRROR)
    added, refreshed, errors, pruned = [], [], [], []
    for name in sorted(canon):
        src, dst = CANON / name, MIRROR / name
        existed = dst.exists()
        try:
            shutil.copytree(src, dst, dirs_exist_ok=True)  # overlay: add missing, overwrite divergent
            (refreshed if existed else added).append(name)
        except Exception as e:
            errors.append({"skill": name, "error": str(e)})
    if prune:
        for name in sorted(mirror - canon):
            try:
                shutil.rmtree(MIRROR / name)
                pruned.append(name)
            except Exception as e:
                errors.append({"skill": name, "error": f"prune: {e}"})
    return {"added": added, "refreshed": refreshed, "pruned": pruned,
            "orphans_kept": sorted(mirror - canon) if not prune else [], "errors": errors}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prune", action="store_true", help="remove skill dirs present only in the mirror")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = sync(prune=args.prune)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"skill mirror sync: +{len(rep['added'])} added, {len(rep['refreshed'])} refreshed, "
              f"{len(rep['pruned'])} pruned, {len(rep['orphans_kept'])} orphan(s) kept, {len(rep['errors'])} error(s)")
        if rep["added"]:
            print(f"  ADDED: {', '.join(rep['added'])}")
        if rep["orphans_kept"]:
            print(f"  ORPHAN (mirror-only, kept; use --prune to remove): {', '.join(rep['orphans_kept'])}")
        for e in rep["errors"]:
            print(f"  ERROR {e['skill']}: {e['error']}")
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
