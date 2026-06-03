#!/usr/bin/env python3
"""structure_graph.py — generated, read-only model of the VAULT's container structure.

The content-tree sibling of harness_map.py (which scans the HARNESS structure). This
scans the vault's folder structure and surfaces structural drift for human inspection —
the SENSE layer of the structure loop (Phase 0). It NEVER mutates the vault; it only
reads the tree + project CLAUDE.md files and emits findings.

Detects (deterministic, ~0 model tokens):
  - numbering-collision : two sibling dirs share a leading number (e.g. two `01`, two `09`)
  - template-drift      : a project CLAUDE.md documents folders that don't exist
  - stale-snapshot      : a project CLAUDE.md hand-maintains a "Folder Structure" map
                          (violates the generate-don't-hand-maintain principle)
  - orphan              : a truly-empty directory

Generated, so unlike a hand-maintained folder map it cannot silently rot — which is
exactly the debt class (the project CLAUDE.md fiction) that motivated this.

Usage:
  python structure_graph.py            # human-readable report + write cache
  python structure_graph.py --json     # machine-readable graph
  python structure_graph.py --check    # exit 1 if any drift finding (sanity/pulse gate)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT  # noqa: E402  (discovered path — no hardcoded drive)

STATE = VAULT / ".claude" / "_state"
CACHE = STATE / "structure-graph.json"

# Content dirs whose immediate children we check for numbering collisions / orphans.
# Discovered at runtime; this is only the exclude set (dotdirs + non-content surfaces).
EXCLUDE = {".git", ".obsidian", ".claude", ".codex", ".agents", ".harness",
           "node_modules", "_archive", ".trash", "99 Attachments", "Operon", "Workspaces"}
# Empty dirs that are intentional ACTIVE surfaces (referenced elsewhere, just currently
# empty) — not dead scaffolding. Excluded from the orphan finding. Keep tiny + justified;
# the distinguishing signal is inbound references (dead scaffolding has ~0).
ORPHAN_IGNORE = {
    "04 Notes/Session Logs",  # active session-log surface (~21 inbound mentions); fills as sessions are logged
}
NUM_PREFIX = re.compile(r"^(\d+)\s")
# folder tokens inside a CLAUDE.md, e.g. `00 Prospects/` or "00 Prospects/"
DOC_FOLDER = re.compile(r"`?(\d{2} [^\n`/|]+?)/")
STALE_MAP = re.compile(r"(?im)^#+\s*Folder Structure\b")


def _child_dirs(d: Path) -> list[Path]:
    try:
        return sorted(p for p in d.iterdir() if p.is_dir() and p.name not in EXCLUDE
                      and not p.name.startswith("."))
    except Exception:
        return []


def _collisions(d: Path) -> list[dict]:
    by_num: dict[str, list[str]] = {}
    for c in _child_dirs(d):
        m = NUM_PREFIX.match(c.name)
        if m:
            by_num.setdefault(m.group(1), []).append(c.name)
    out = []
    for num, names in by_num.items():
        if len(names) > 1:
            out.append({"level": "yellow", "kind": "numbering-collision",
                        "path": str(d.relative_to(VAULT)).replace("\\", "/"),
                        "detail": f"{len(names)} dirs share prefix '{num}': {', '.join(names)}"})
    return out


def _project_findings(proj: Path) -> list[dict]:
    out = []
    claude = proj / "CLAUDE.md"
    if not claude.exists():
        return out
    try:
        text = claude.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return out
    rel = str(proj.relative_to(VAULT)).replace("\\", "/")
    actual = {c.name for c in _child_dirs(proj)}
    vault_top = {c.name for c in _child_dirs(VAULT)}  # documented tokens that are OTHER vault dirs are cross-refs, not phantom subfolders
    documented = {t.strip() for t in DOC_FOLDER.findall(text)}
    absent = sorted(d for d in documented if d not in actual and d not in vault_top)
    if absent:
        out.append({"level": "yellow", "kind": "template-drift",
                    "path": f"{rel}/CLAUDE.md",
                    "detail": f"documents {len(absent)} folder(s) that don't exist: {', '.join(absent[:6])}"})
    if STALE_MAP.search(text):
        out.append({"level": "yellow", "kind": "stale-snapshot",
                    "path": f"{rel}/CLAUDE.md",
                    "detail": "hand-maintains a 'Folder Structure' map — generate it or drop it (it drifts)"})
    return out


def _orphans(d: Path) -> list[dict]:
    out = []
    for c in _child_dirs(d):
        rel = str(c.relative_to(VAULT)).replace("\\", "/")
        if rel in ORPHAN_IGNORE:
            continue
        try:
            if not any(True for _ in c.iterdir()):
                out.append({"level": "yellow", "kind": "orphan",
                            "path": rel,
                            "detail": "empty directory"})
        except Exception:
            continue
    return out


def scan() -> dict:
    """Pure compute — returns the structure graph + findings. Never writes, never raises."""
    findings: list[dict] = []
    scanned = 0
    content_dirs = _child_dirs(VAULT)
    for d in content_dirs:
        scanned += 1
        findings += _collisions(d)
        findings += _orphans(d)
        if d.name == "03 Projects":
            for proj in _child_dirs(d):
                scanned += 1
                findings += _collisions(proj)
                findings += _orphans(proj)
                findings += _project_findings(proj)
    summary = dict(Counter(f["kind"] for f in findings))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scanned_dirs": scanned,
        "findings": findings,
        "summary": summary,
    }


def write_cache(graph: dict) -> None:
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 1 if any drift finding")
    args = ap.parse_args()
    graph = scan()
    write_cache(graph)
    if args.check:
        n = len(graph["findings"])
        print(f"structure-graph: {n} drift finding(s) across {graph['scanned_dirs']} dirs"
              + ("" if n == 0 else " — " + ", ".join(f"{k}:{v}" for k, v in graph["summary"].items())))
        return 1 if n else 0
    if args.json:
        print(json.dumps(graph, ensure_ascii=False, indent=2))
        return 0
    print(f"# Vault Structure Graph · {graph['generated_at']}")
    print(f"scanned {graph['scanned_dirs']} dirs · {len(graph['findings'])} drift finding(s)")
    for k, v in graph["summary"].items():
        print(f"  {k}: {v}")
    for f in graph["findings"]:
        print(f"  [{f['level']}] {f['kind']}: {f['path']} — {f['detail']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
