#!/usr/bin/env python3
"""
harness_map.py — the GENERATED cognitive front-door of the harness.

The companion to harness_status.py: where /status answers "what's *firing*?"
(runtime liveness), this answers "what *exists*, and is it indexed?" (the
table-of-contents that lets you NOT hold the whole thing in your head).

It scans the live filesystem (skills, agents, judgment nodes, _state) and reads
the curated `state` / `docs` registries from harness-manifest.json, then writes
04 Notes/HARNESS-MAP.md between AUTO markers — so the inventory is generated, not
hand-maintained, and therefore can't drift the way a snapshot doc does.

It also emits a DRIFT report: state files present-but-undeclared, registry docs
missing-on-disk, judgment nodes still draft, skills not yet in the daily index.
That drift section is the verification surface the harness was missing.

Design constraints (09 Rules/harness-modularity.md + correction 2026-05-26 #8):
  - 0 model tokens (pure scan), cross-platform (pathlib, discovered VAULT),
  - never raises (degrades to a partial map), additive (touches no other file).

Usage:
  python harness_map.py            # regenerate 04 Notes/HARNESS-MAP.md + print summary
  python harness_map.py --check    # exit 1 if any drift found (gate mode; no write)
  python harness_map.py --json     # machine-readable inventory + drift
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT  # noqa: E402  (shared vault-discovery; never reinvent)

STATE = VAULT / ".claude" / "_state"
MANIFEST = STATE / "harness-manifest.json"
OUT = VAULT / "04 Notes" / "HARNESS-MAP.md"  # vault-visible (Obsidian excludes dot-folders)
BEGIN, END = "<!-- BEGIN AUTO-MAP -->", "<!-- END AUTO-MAP -->"

# Daily-driver index whose skill coverage we cross-check (drift if a skill is missing).
DAILY_INDEX = VAULT / "Skills I Use Daily.md"

# Method/composition layer (09 Rules/methods.md) — reusable task-kind templates.
METHODS_DIR = VAULT / "09 Rules" / "_methods"


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _frontmatter(text: str) -> dict:
    """Tiny single-line `key: value` parser for the leading --- block. Not YAML-complete."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fm


def _first_sentence(s: str, cap: int = 90) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    # cut at the first sentence-ending period that isn't a version/decimal dot
    m = re.search(r"\.(?:\s|$)", s)
    if m:
        s = s[: m.start()]
    return (s[: cap - 1] + "…") if len(s) > cap else s


def _rel(p: Path) -> str:
    try:
        return p.relative_to(VAULT).as_posix()
    except Exception:
        return p.name


def load_manifest() -> dict:
    try:
        return json.loads(_read(MANIFEST))
    except Exception:
        return {}


def scan_skills() -> list:
    out = []
    for sk in sorted((VAULT / ".claude" / "skills").glob("*/SKILL.md")):
        if "_archive" in sk.parts:
            continue
        fm = _frontmatter(_read(sk))
        out.append({
            "name": fm.get("name", sk.parent.name),
            "category": fm.get("category", "—"),
            "model": fm.get("model", "—"),
            "one_line": _first_sentence(fm.get("description", "")),
        })
    return out


def scan_agents() -> list:
    out = []
    adir = VAULT / ".claude" / "agents"
    for a in sorted(adir.glob("*.md")):
        fm = _frontmatter(_read(a))
        name = fm.get("name", a.stem)
        out.append({
            "name": name,
            "kind": "grader" if "grader" in name else "agent",
            "one_line": _first_sentence(fm.get("description", "")),
        })
    return out


def scan_judgment() -> list:
    out = []
    for n in sorted((VAULT / "09 Rules" / "_judgment").glob("*.md")):
        fm = _frontmatter(_read(n))
        out.append({
            "id": fm.get("id", n.stem),
            "name": fm.get("name", n.stem),
            "type": fm.get("type", "value" if n.name.startswith("v-") else "framework"),
            "status": fm.get("status", "?"),
        })
    return out


def scan_methods() -> list:
    """The composition layer: 09 Rules/_methods/m-*.md — reusable task-kind DAG templates."""
    out = []
    if not METHODS_DIR.is_dir():
        return out
    for m in sorted(METHODS_DIR.glob("m-*.md")):
        text = _read(m)
        fm = _frontmatter(text)
        out.append({
            "id": fm.get("id", m.stem),
            "name": fm.get("name", m.stem),
            "task_kind": fm.get("task-kind", "—"),
            "status": fm.get("status", "?"),
            "steps": len(re.findall(r"(?m)^###\s+\S", text)),  # ### <slug> step sections
        })
    return out


def scan_state_drift(manifest: dict) -> dict:
    """Declared (registry) vs present (disk). Returns {declared, present, undeclared}."""
    declared_globs = [e["id"] for e in manifest.get("state", [])]
    present = sorted(
        _rel(p) for p in STATE.iterdir()
        if p.is_file() and p.suffix in (".jsonl", ".json")
        and p.name not in ("harness-manifest.json",)
    )
    present_names = [Path(p).name for p in present]

    def is_declared(name: str) -> bool:
        for g in declared_globs:
            # Split only on the alternation separators ' / ' and ' + ' (space-padded), NOT on path
            # '/' — else a glob like 'underlays/*' or 'judgment-queue/*.json' leaks a bare '*'/'*.json'
            # token that matches EVERY state file, silently disabling the undeclared check.
            for token in re.split(r"\s+/\s+|\s+\+\s+", g):
                token = token.strip()
                if not token:
                    continue
                pat = "^" + re.escape(token).replace(r"\*", ".*") + "$"
                if re.match(pat, name):
                    return True
        return False

    undeclared = [n for n in present_names if not is_declared(n)]
    return {"declared": declared_globs, "present": present_names, "undeclared": sorted(undeclared)}


def scan_doc_drift(manifest: dict) -> list:
    """Registry docs that don't exist on disk."""
    missing = []
    for d in manifest.get("docs", []):
        if not (VAULT / d["path"]).exists():
            missing.append(d["path"])
    return missing


def build() -> dict:
    manifest = load_manifest()
    skills = scan_skills()
    agents = scan_agents()
    judgment = scan_judgment()
    methods = scan_methods()
    state = scan_state_drift(manifest)
    docs_missing = scan_doc_drift(manifest)

    # skills not referenced in the daily-driver index. If the human-facing index
    # declares itself non-exhaustive, it is a cockpit cheat sheet and the
    # generated HARNESS-MAP is the inventory.
    idx = _read(DAILY_INDEX)
    idx_fm = _frontmatter(idx)
    index_exhaustive = idx_fm.get("exhaustive-skill-index", "true").lower() != "false"
    skills_unindexed = [
        s["name"] for s in skills
        if idx and index_exhaustive and f"/{s['name']}" not in idx and s["name"] not in idx
    ]
    drafts = [j["id"] for j in judgment if j["status"] == "draft"]

    # Actionable drift (something needs registering/fixing) vs deliberate backlog
    # (judgment nodes legitimately sitting at draft until human-validated — never a gate failure).
    drift = {
        "state_undeclared": state["undeclared"],
        "docs_missing": docs_missing,
        "skills_unindexed": skills_unindexed if idx else [],
    }
    backlog = {"judgment_draft": drafts,
               "method_draft": [m["id"] for m in methods if m["status"] == "draft"]}
    return {
        "manifest": manifest, "skills": skills, "agents": agents,
        "judgment": judgment, "methods": methods, "state": state, "drift": drift, "backlog": backlog,
        "counts": {
            "skills": len(skills),
            "agents": len([a for a in agents if a["kind"] == "agent"]),
            "graders": len([a for a in agents if a["kind"] == "grader"]),
            "judgment": len(judgment),
            "methods": len(methods),
            "organs": len(manifest.get("organs", [])),
            "state_files": len(state["present"]),
        },
    }


def _table(rows: list, headers: list) -> list:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    return out


def render(snap: dict) -> str:
    c = snap["counts"]
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    L = [
        f"> **Generated** {now} by `harness_map.py` — do not hand-edit between the AUTO markers; "
        f"rerun the script. Liveness (what's *firing*) lives in `/status`, not here.",
        "",
        f"**Inventory:** {c['skills']} skills · {c['methods']} methods · {c['agents']} agents + {c['graders']} graders · "
        f"{c['judgment']} judgment nodes · {c['organs']} organs · {c['state_files']} state files.",
        "",
        "## Skills (work surface)",
    ]
    sk = sorted(snap["skills"], key=lambda s: (s["category"], s["name"]))
    L += _table([[s["name"], s["category"], s["model"], s["one_line"]] for s in sk],
                ["skill", "category", "model", "one-line"])

    L += ["", "## Methods (composition layer — how skills string together for a task-kind)"]
    mr = sorted(snap.get("methods", []), key=lambda m: m["id"])
    if mr:
        L += _table([[m["id"], m["status"], m["steps"], m["task_kind"], m["name"]] for m in mr],
                    ["method", "status", "steps", "task-kind", "name"])
    else:
        L += ["", "_(none yet — precipitate one from a completed run / a class of records; see [[09 Rules/methods]])_"]

    L += ["", "## Agents + graders (critic surface)"]
    L += _table([[a["name"], a["kind"], a["one_line"]] for a in snap["agents"]],
                ["agent", "kind", "one-line"])

    L += ["", "## Judgment graph (alignment core)"]
    jr = sorted(snap["judgment"], key=lambda j: (j["type"], j["id"]))
    L += _table([[j["id"], j["type"], j["status"], j["name"]] for j in jr],
                ["node", "type", "status", "name"])

    L += ["", "## State surfaces (the engine's data — contracts in harness-manifest.json)"]
    st = snap["manifest"].get("state", [])
    L += _table([[e["id"], e.get("writer", "—"), e.get("reader", "—"), e.get("purpose", "—")] for e in st],
                ["file", "writer", "reader", "purpose"])

    L += ["", "## Orientation docs"]
    dc = snap["manifest"].get("docs", [])
    L += _table([[d["path"], d.get("scope", "—"), d.get("loaded", "—")] for d in dc],
                ["doc", "scope", "loaded"])

    # Drift (actionable — should be empty) vs backlog (deliberate, human-gated)
    d = snap["drift"]
    L += ["", "## ⚠️ Drift report"]
    if not any(d.values()):
        L += ["", "✅ No actionable drift: every state file is declared, every registry doc exists, every skill is indexed."]
    else:
        if d["state_undeclared"]:
            L += [f"- **State files present but undeclared** ({len(d['state_undeclared'])}): "
                  f"`{'`, `'.join(d['state_undeclared'])}` — add a contract row to manifest `state[]` or retire."]
        if d["docs_missing"]:
            L += [f"- **Registry docs missing on disk** ({len(d['docs_missing'])}): "
                  f"`{'`, `'.join(d['docs_missing'])}` — fix the path or remove from manifest `docs[]`."]
        if d["skills_unindexed"]:
            L += [f"- **Skills not in `Skills I Use Daily.md`** ({len(d['skills_unindexed'])}): "
                  f"`{'`, `'.join(d['skills_unindexed'])}`."]
    drafts = snap.get("backlog", {}).get("judgment_draft", [])
    if drafts:
        L += ["", f"_Backlog (not drift — human-gated promotion): {len(drafts)} judgment node(s) at "
              f"`status: draft`, promote once validated — `{'`, `'.join(drafts)}`._"]
    mdrafts = snap.get("backlog", {}).get("method_draft", [])
    if mdrafts:
        L += ["", f"_Backlog: {len(mdrafts)} method(s) at `status: draft` (validate via a run, then promote) — "
              f"`{'`, `'.join(mdrafts)}`._"]
    return "\n".join(L)


HEADER = """---
type: harness-front-door
generated-by: harness_map.py
created-by: claude
status: generated
biz-eval: skip
localize-cn: skip
---

# THE HARNESS — generated front-door

> The single index of everything the harness *contains* — skills, agents, the judgment graph, state surfaces, orientation docs — plus a drift report. **Generated** by resolving Python through `.harness/resolve_runtime.py` and running `.claude/routines/harness_map.py`; the section between the AUTO markers is overwritten on every run, so never hand-edit it. New vocabulary lives in [[09 Rules/glossary]]; the unchanging Layer model in [[04 Notes/_system/(C) harness-map-2026-05-24]]; live firing-status in `/status`.

"""


def write_map(snap: dict) -> None:
    body = render(snap)
    block = f"{BEGIN}\n{body}\n{END}\n"
    existing = _read(OUT)
    if BEGIN in existing and END in existing:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?",
                     block, existing, flags=re.S)
    else:
        new = HEADER + block
    OUT.write_text(new, encoding="utf-8")


def main() -> int:
    args = sys.argv[1:]
    snap = build()
    if "--json" in args:
        print(json.dumps({k: snap[k] for k in ("counts", "drift", "backlog")}, ensure_ascii=False, indent=2))
        return 1 if ("--check" in args and any(snap["drift"].values())) else 0
    nd = sum(len(v) for v in snap["drift"].values())
    nb = sum(len(v) for v in snap["backlog"].values())
    if "--check" in args:
        print(f"harness_map --check: {'DRIFT' if nd else 'clean'} ({nd} actionable · {nb} backlog)")
        return 1 if nd else 0
    write_map(snap)
    c = snap["counts"]
    print(f"✅ wrote {_rel(OUT)} — {c['skills']} skills · {c['methods']} methods · {c['agents']}+{c['graders']} agents/graders · "
          f"{c['judgment']} judgment nodes · {c['organs']} organs · {c['state_files']} state files · "
          f"{'no actionable drift' if nd == 0 else f'{nd} drift item(s)'} · {nb} backlog")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # never hard-fail
        print(f"⚠️ harness_map error: {e}")
        sys.exit(0)
