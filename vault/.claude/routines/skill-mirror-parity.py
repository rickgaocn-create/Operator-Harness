#!/usr/bin/env python3
"""skill-mirror-parity.py — fail loud on skill-mirror drift.

`.agents/skills` is declared a neutral re-export of canonical `.claude/skills`
(runtime-manifest.toml). Nothing verified that, so it silently drifted (missing
skills + byte-divergent copies feeding a broken .codex junction). This check
compares the two trees by presence + content hash and EXITS 1 on any drift, so
/sanity or harness-pulse can surface it instead of it rotting invisibly.

  python skill-mirror-parity.py            # report; exit 1 if drift
  python skill-mirror-parity.py --json
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # routines -> .claude -> vault
CANON = os.path.join(VAULT, ".claude", "skills")
MIRROR = os.path.join(VAULT, ".agents", "skills")


def _sha(p):
    """Hash CONTENT, not bytes — normalize line endings so CRLF-vs-LF doesn't
    masquerade as drift (a parity check that cries wolf is useless)."""
    try:
        raw = open(p, "rb").read().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        return hashlib.sha256(raw).hexdigest()
    except OSError:
        return None


def _skill_names(root):
    if not os.path.isdir(root):
        return set()
    return {d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)) and not d.startswith("_")}


def scan():
    canon, mirror = _skill_names(CANON), _skill_names(MIRROR)
    missing = sorted(canon - mirror)         # in canonical, absent from mirror
    extra = sorted(mirror - canon)           # in mirror only (orphan)
    divergent = []
    for name in sorted(canon & mirror):
        a = _sha(os.path.join(CANON, name, "SKILL.md"))
        b = _sha(os.path.join(MIRROR, name, "SKILL.md"))
        if a and b and a != b:
            divergent.append(name)
    return {"canonical": len(canon), "mirror": len(mirror),
            "missing_from_mirror": missing, "orphan_in_mirror": extra,
            "divergent_SKILL_md": divergent}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = scan()
    drift = bool(r["missing_from_mirror"] or r["orphan_in_mirror"] or r["divergent_SKILL_md"])
    if a.json:
        print(json.dumps({**r, "drift": drift}, ensure_ascii=False, indent=2)); return 1 if drift else 0
    print(f"skill mirror parity: canonical={r['canonical']} mirror={r['mirror']}")
    if not drift:
        print("  OK — mirror in parity with canonical."); return 0
    if r["missing_from_mirror"]:
        print(f"  DRIFT missing from .agents ({len(r['missing_from_mirror'])}): {', '.join(r['missing_from_mirror'])}")
    if r["divergent_SKILL_md"]:
        print(f"  DRIFT byte-divergent SKILL.md ({len(r['divergent_SKILL_md'])}): {', '.join(r['divergent_SKILL_md'])}")
    if r["orphan_in_mirror"]:
        print(f"  DRIFT orphan in .agents ({len(r['orphan_in_mirror'])}): {', '.join(r['orphan_in_mirror'])}")
    print("  -> re-run the mirror sync (manifest: .claude canonical -> .agents neutral re-export).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
