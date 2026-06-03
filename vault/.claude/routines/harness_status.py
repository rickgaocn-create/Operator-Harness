#!/usr/bin/env python3
"""
harness_status.py — pull-on-demand operator snapshot for AFK (Discord / Feishu).

The PULL counterpart to harness-pulse (which is the every-3h PUSH/auto side). Fire
`/status` from your phone mid-AFK and get back a compact, channel-readable card of
what's alive, what's quiet, and today's progress — instead of waiting for the next
pulse or a new session.

Composition (does NOT rebuild anything):
  - re-runs harness-pulse SILENTLY for a fresh verdict (severity + findings), falling
    back to the cached verdict if that fails;
  - reads .claude/_state/harness-manifest.json for the full organ list and resolves
    each organ's last-fired from the source it already writes (autonomous-log, the
    produced artifact, usage.jsonl, grader-verdicts.jsonl, or a live process probe);
  - renders one markdown card.

Read-only: writes ZERO vault content (the silent pulse only updates its own verdict
file, which is its job). Never raises — degrades to partial cards on any error.

Usage:
  python harness_status.py            # fresh pulse + full card (default)
  python harness_status.py --cached   # skip the pulse refresh (faster, may be ≤3h stale)
  python harness_status.py --json     # machine-readable
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT, channel_liveness, LOG_PATH  # noqa: E402

STATE = VAULT / ".claude" / "_state"
MANIFEST_PATH = STATE / "harness-manifest.json"
PULSE_PATH = STATE / "harness-pulse.json"
PROFILES_PATH = VAULT / ".claude" / "profiles" / "harness-profiles.json"
HERE = Path(__file__).resolve().parent

# A persisted pulse verdict older than 1.5× the 180-min pulse cadence is "stale":
# its severity may predate recent state/threshold changes. The default path refreshes
# (refresh_pulse), but --cached and any other reader of harness-pulse.json cannot — so
# flag it rather than show an old severity as authoritative.
PULSE_STALE_AFTER_MIN = 270


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(ts) -> "datetime | None":
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _read_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    rows = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return rows


def _ago(dt: "datetime | None") -> str:
    if dt is None:
        return "—"
    secs = (_now() - dt).total_seconds()
    if secs < 0:
        secs = 0
    if secs < 90 * 60:
        return f"{int(secs // 60)}m"
    if secs < 36 * 3600:
        return f"{secs / 3600:.1f}h"
    return f"{int(secs // 86400)}d"


def refresh_pulse() -> None:
    """Run harness-pulse silently for a fresh verdict. Best-effort; never blocks long."""
    try:
        env = dict(os.environ, PULSE_SILENT="1")
        subprocess.run(
            [sys.executable, str(HERE / "harness-pulse.py")],
            env=env, capture_output=True, timeout=60,
        )
    except Exception:
        pass  # fall back to whatever verdict is on disk


def load_manifest() -> list:
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8")).get("organs", [])
    except Exception:
        return []


def load_pulse() -> dict:
    try:
        return json.loads(PULSE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_profile() -> dict:
    try:
        data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        active = data.get("active")
        current = (data.get("profiles") or {}).get(active) or {}
        return {"active": active, **current} if active else {}
    except Exception:
        return {}


def surface_diet() -> dict:
    skills_dir = VAULT / ".claude" / "skills"
    skills = [p for p in skills_dir.glob("*/SKILL.md") if "_archive" not in p.parts]
    packaged = [p for p in skills if (p.parent / "skill-package.yaml").exists()]
    uncategorized = 0
    for p in skills:
        text = ""
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
        if "\ncategory:" not in text and not text.startswith("category:"):
            uncategorized += 1
    coverage = (len(packaged) / len(skills)) if skills else 0.0
    yellow = len(skills) > 50 and coverage < 0.20 or uncategorized > 0
    return {
        "active_skills": len(skills),
        "packaged_skills": len(packaged),
        "thin_skills": max(0, len(skills) - len(packaged)),
        "package_coverage": round(coverage, 3),
        "uncategorized": uncategorized,
        "level": "yellow" if yellow else "green",
    }


def _last_from_log(match_routine: str) -> "datetime | None":
    for r in reversed(_read_jsonl(LOG_PATH)):
        if r.get("routine") == match_routine:
            return _parse_ts(r.get("ts"))
    return None


def _last_from_graderlog(match: str) -> "datetime | None":
    latest = None
    for r in _read_jsonl(STATE / "grader-verdicts.jsonl"):
        blob = json.dumps(r, ensure_ascii=False).lower()
        if r.get("template") or "example" in blob and "verdict" not in blob:
            continue
        if match.lower() in blob:
            t = _parse_ts(r.get("ts") or r.get("timestamp"))
            if t and (latest is None or t > latest):
                latest = t
    return latest


def _mtime(path: Path) -> "datetime | None":
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except Exception:
        return None


def resolve(organ: dict, live_channels: dict) -> dict:
    """-> {id,label,kind,glyph,detail,optional}."""
    kind = organ.get("kind")
    src = organ.get("source")
    cadence = organ.get("cadence_min")
    last = None
    out = {"id": organ.get("id"), "label": organ.get("label", organ.get("id")),
           "kind": kind, "optional": bool(organ.get("optional"))}

    if src == "process":
        alive = bool(live_channels.get(organ.get("probe")))
        out["glyph"] = "🟢" if alive else "🔴"
        out["detail"] = "live" if alive else "DOWN"
        out["down"] = not alive
        return out

    if src == "autonomous-log":
        last = _last_from_log(organ.get("match_routine", organ.get("id")))
    elif src == "artifact-today":
        p = VAULT / organ["path"].replace("{today}", datetime.now().strftime("%Y-%m-%d"))
        last = _mtime(p) if p.exists() else None
    elif src in ("log-mtime",):
        last = _mtime(VAULT / organ["path"])
    elif src == "usage-recent":
        rows = _read_jsonl(STATE / "usage.jsonl")
        last = _parse_ts(rows[-1].get("ts")) if rows else _mtime(STATE / "usage.jsonl")
    elif src == "grader-verdicts":
        last = _last_from_graderlog(organ.get("match_grader", organ.get("id")))

    # classify
    if cadence is None:  # event-driven (graders)
        if last is None:
            out["glyph"], out["detail"], out["never"] = "⚪", "never fired", True
        else:
            out["glyph"], out["detail"] = "🟢", _ago(last)
        return out

    if last is None:
        out["glyph"], out["detail"], out["down"] = "⚪", "no signal", not out["optional"]
        return out
    age_min = (_now() - last).total_seconds() / 60
    if age_min <= cadence * 1.5:
        out["glyph"] = "🟢"
    elif age_min <= cadence * 3:
        out["glyph"] = "🟡"
        out["quiet"] = True
    else:
        out["glyph"] = "🔴"
        out["down"] = True
    out["detail"] = _ago(last)
    return out


def _today_top3() -> list:
    p = VAULT / "04 Notes" / "daily notes" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    if not p.exists():
        return []
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    out, grabbing = [], False
    for ln in lines:
        s = ln.strip()
        if s.startswith("## "):
            grabbing = "Top 3" in s or "Top3" in s
            continue
        if grabbing and s.startswith("- "):
            txt = s.lstrip("-[ ]x").strip()
            if txt:
                out.append(txt)
        if len(out) >= 3:
            break
    return out


def build(cached: bool = False) -> dict:
    if not cached:
        refresh_pulse()
    pulse = load_pulse()
    organs = load_manifest()
    live = channel_liveness()
    resolved = [resolve(o, live) for o in organs]
    attention = [r for r in resolved if r.get("down") or r.get("quiet")]
    return {
        "ts": _now().isoformat(timespec="seconds"),
        "pulse": pulse,
        "organs": resolved,
        "attention": attention,
        "top3": _today_top3(),
        "profile": load_profile(),
        "surface_diet": surface_diet(),
        "cached": cached,
    }


def render(snap: dict) -> str:
    pulse = snap.get("pulse", {})
    sev = pulse.get("severity", "unknown")
    head = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(sev, "⚪")
    p_ts = _parse_ts(pulse.get("ts"))
    p_age = _ago(p_ts) if pulse.get("ts") else "—"
    p_stale = p_ts is not None and (_now() - p_ts) > timedelta(minutes=PULSE_STALE_AFTER_MIN)
    stale_tag = " ⚠️stale" if p_stale else ""
    nfind = len(pulse.get("findings", []))
    local = datetime.now().strftime("%Y-%m-%d %H:%M")

    by = {}
    for r in snap["organs"]:
        by.setdefault(r["kind"], []).append(r)

    def row(rs):
        return " · ".join(f"{r['glyph']} {r['label'].split('(')[0].strip()} {r['detail']}".strip() for r in rs)

    lines = [f"{head} **Harness Status** · {local} · pulse `{sev}`{stale_tag} ({nfind} findings, {p_age} ago)"]
    if p_stale:
        lines.append(f"> ⚠️ pulse verdict is {p_age} old (> one cadence) — severity may be stale; "
                     f"run `/status` (default refreshes) or `harness-pulse.py` to recompute")
    prof = snap.get("profile") or {}
    if prof.get("active"):
        surfaces = prof.get("live_surfaces") or []
        tail = " · " + ", ".join(surfaces[:3]) if surfaces else ""
        lines.append(f"**Profile:** `{prof['active']}`{tail}")
    if by.get("bridge"):
        lines.append("**Channels:** " + " · ".join(f"{r['glyph']} {r['label']}" for r in by["bridge"]))
    if by.get("routine"):
        lines.append("**Routines:** " + row(by["routine"]))
    if by.get("signal"):
        lines.append("**Signals:** " + row(by["signal"]))
    if by.get("hook"):
        lines.append("**Hooks:** " + row(by["hook"]))
    if by.get("grader"):
        lines.append("**Graders:** " + row(by["grader"]))
    if snap.get("top3"):
        lines.append("**Today's Top 3:** " + " | ".join(snap["top3"]))
    diet = snap.get("surface_diet") or {}
    if diet:
        lines.append(
            f"**Surface Diet:** {diet.get('active_skills')} active · "
            f"{diet.get('packaged_skills')} packaged · {diet.get('thin_skills')} thin · "
            f"{diet.get('uncategorized')} uncategorized"
        )

    att = [r for r in snap["attention"] if not r.get("optional")]
    pulse_findings = [
        f for f in pulse.get("findings", [])
        if isinstance(f, dict) and f.get("level") in ("yellow", "red")
    ]
    if att:
        lines.append("")
        lines.append("⚠️ **Needs attention:** " + ", ".join(
            f"{r['label']} ({r['detail']})" for r in att) +
            "  → `/rearm <id>` to re-arm")
    elif pulse_findings:
        lines.append("")
        lines.append("**Pulse findings:** " + " | ".join(
            f.get("msg") or f.get("code") or "pulse finding" for f in pulse_findings))
    else:
        lines.append("")
        lines.append("✅ all non-optional organs firing")
    return "\n".join(lines)


def main() -> int:
    args = sys.argv[1:]
    snap = build(cached="--cached" in args)
    if "--json" in args:
        print(json.dumps(snap, ensure_ascii=False, indent=2, default=str))
    else:
        print(render(snap))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"⚠️ harness_status error: {e}")
        sys.exit(0)
