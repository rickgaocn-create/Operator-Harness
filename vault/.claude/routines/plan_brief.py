#!/usr/bin/env python3
"""plan_brief.py - the GENERATIVE-planning assembly (scripted, ~0 model tokens).

The reactive loop fires on triggers/cron; nothing read GOALS and asked "what's the marginal
highest-leverage move?". This closes that gap WITHOUT a planner engine (Opus decomposes goals
natively): it assembles GOALS tracks/OKRs + the live cycle file + open Action workstreams
(their next-actions) + due reviews into one compact brief, then the model step (in /operate's
"what's the move" intent) applies the lens (f-2080 / f-strategic-systems) + the grounding gate
to propose ONE next action, tied to a track, human-gated.

Hard constraint: Action files with `sensitivity: confidential` (Track 3 / Lane B) are SEGREGATED
into a private section and never co-mingled with {{ORG_E}} / {{ORG_B}} tracks — surface to {{USER_NAME}} directly only,
never into a daily note (the lane-isolation contract).

stdlib-only · discovered VAULT · never crashes · 0 tokens."""
from __future__ import annotations
import io
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parents[2]
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TODAY = date.today().isoformat()
ACTION_LIVE = ["10 Action/11 12-Week", "10 Action/12 Active"]

# Lane-isolation signals — shared by BOTH the Action-file gate and the GOALS-track gate so they
# can never diverge. A confidential/personal lane must never co-locate with {{ORG_E}}/{{ORG_B}} or reach a
# daily note. Over-segregate rather than leak (red-line); match substrings, not exact values.
CONF_SIGNALS = ("confidential", "lane-b", "lane b", "denmu", "电梦", "personal-career",
                "personal-job", "mifei", "{{ORG_A}}", "⛔")


def _conf_hit(*parts: str) -> bool:
    blob = " ".join(p for p in parts if p).lower()
    return any(sig in blob for sig in CONF_SIGNALS)


def _fm(text: str) -> dict:
    """Parse leading YAML-ish frontmatter into a flat dict (string values only)."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", line)
        if mm:
            out[mm.group(1).strip()] = mm.group(2).strip().strip('"').strip("'")
    return out


def _is_confidential(fm: dict, name: str) -> bool:
    """Defense-in-depth: lane-isolation is a red-line, so over-segregate rather than leak.
    Any signal -> confidential. (The sensitivity value may carry trailing prose.)"""
    return _conf_hit(fm.get("sensitivity", ""), fm.get("tags", ""), fm.get("project", ""),
                     fm.get("chain-anchor", ""), name)


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def goals_tracks() -> list:
    """Lift each '### Track N · ...' heading + its Role/Strategy/Targets summary lines."""
    t = read(VAULT / "GOALS.md")
    if not t:
        return []
    tracks = []
    for block in re.split(r"\n### ", t)[1:]:
        head = block.splitlines()[0].strip()
        if not head.lower().startswith("track"):
            continue
        # keep the first ~6 non-empty summary lines (role / strategy / targets headers)
        body = [ln.strip() for ln in block.splitlines()[1:] if ln.strip()][:6]
        conf = _conf_hit(head, block)
        tracks.append({"track": head, "summary": body, "confidential": conf})
    return tracks


def action_workstreams() -> tuple:
    """Open Action workstreams with their next-action, split public vs confidential."""
    pub, conf = [], []
    for d in ACTION_LIVE:
        base = VAULT / d
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*.md")):
            fm = _fm(read(p))
            if not fm or fm.get("type") != "action":
                continue
            if fm.get("status") == "done":
                continue
            row = {
                "file": p.name,
                "project": fm.get("project", "?"),
                "horizon": fm.get("horizon", "?"),
                "status": fm.get("status", "open"),
                "okr_link": fm.get("okr-link", ""),
                "next_action": fm.get("next-action", "").strip(),
                "chain": fm.get("chain-anchor", ""),
            }
            (conf if _is_confidential(fm, p.name) else pub).append(row)
    return pub, conf


def due_reviews() -> list:
    base = VAULT / "05 Decisions"
    out = []
    if base.is_dir():
        for p in sorted(base.glob("*.md")):
            fm = _fm(read(p))
            r = fm.get("review_on", "")
            if r and re.match(r"\d{4}-\d{2}-\d{2}", r) and r <= TODAY:
                out.append({"file": p.name, "review_on": r, "status": fm.get("status", "")})
    return out


def live_cycle() -> str:
    base = VAULT / "04 Notes" / "12-week"
    if not base.is_dir():
        return ""
    files = sorted(base.glob("20*.md"))
    if not files:
        return ""
    t = read(files[-1])
    m = re.search(r"(?im)^\*\*?status.*$", t)
    return f"{files[-1].name}" + (f" — {m.group(0).strip()}" if m else "")


def build() -> dict:
    pub, conf = action_workstreams()
    return {
        "today": TODAY,
        "live_cycle": live_cycle(),
        "tracks": goals_tracks(),
        "workstreams_public": pub,
        "workstreams_confidential": conf,
        "due_reviews": due_reviews(),
    }


def render(rep: dict) -> str:
    L = [f"PLAN BRIEF (scripted, 0 tokens) — {rep['today']}",
         f"live cycle: {rep['live_cycle'] or '(no 12-week file found)'}", ""]
    L.append("STRATEGIC TRACKS (from GOALS.md):")
    for t in rep["tracks"]:
        if t["confidential"]:
            L.append(f"  · {t['track']}  [CONFIDENTIAL — see private section]")
            continue
        L.append(f"  · {t['track']}")
        for s in t["summary"][:3]:
            L.append(f"      {s[:140]}")
    L.append("")
    L.append("IN-MOTION WORKSTREAMS (open Action files + their next-action):")
    if not rep["workstreams_public"]:
        L.append("  (none open — every track without a live workstream is a planning gap)")
    for w in rep["workstreams_public"]:
        flag = "" if w["next_action"] else "  <-- NO next-action set"
        okr = f" {w['okr_link']}" if w["okr_link"] else ""
        L.append(f"  [{w['status']:7}] {w['project']:10} {w['file']}{okr}")
        L.append(f"      next: {w['next_action'] or '(unset)'}{flag}")
    L.append("")
    if rep["due_reviews"]:
        L.append("DUE REVIEWS (review_on <= today):")
        for d in rep["due_reviews"]:
            L.append(f"  - {d['file']} ({d['review_on']}, {d['status']})")
        L.append("")
    if rep["workstreams_confidential"]:
        L.append("=== CONFIDENTIAL — {{USER_NAME}} ONLY · never co-locate with {{ORG_E}}/{{ORG_B}}, never into a daily note ===")
        for w in rep["workstreams_confidential"]:
            L.append(f"  [{w['status']:7}] {w['file']} — next: {w['next_action'] or '(unset)'}")
        L.append("=== end confidential ===\n")
    L.append("MODEL STEP (the generative move — done by you/Opus, not this script):")
    L.append("  Apply the lens (f-2080 leverage · f-strategic-systems) to the above. Propose the")
    L.append("  ONE marginal highest-leverage next action — not a tree. Run it through the grounding")
    L.append("  gate: it must name a party + a number/date + a first action, and tie to a track/OKR,")
    L.append("  with a one-line why-this-over-the-alternatives. Then PROPOSE it as an Action/Task")
    L.append("  (human-gated — never auto-create; see 09 Rules/action.md Auto-Creation Policy).")
    L.append("  Confidential items: surface to {{USER_NAME}} directly, never co-located.")
    return "\n".join(L)


def main() -> int:
    rep = build()
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(render(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
