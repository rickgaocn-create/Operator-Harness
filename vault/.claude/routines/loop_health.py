#!/usr/bin/env python3
"""loop_health.py — the learn-loop HEALTH VIEW (Phase 3 observability).

One glance answers "is the machine actually learning?" — feeder freshness, the verify-arrow state
(open/due/ready + distinct-session progress), class_key backbone coverage, evolution proposals, and
error-pattern trends. READ-ONLY; reuses the existing loaders (no reimplementation). Stdout wrap is in
main() so the module stays library-safe.

  python loop_health.py [--json]
"""
from __future__ import annotations
import io, json, os, sys
from datetime import date, datetime

VAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # routines -> .claude -> {{USER_NAME}}
STATE = os.path.join(VAULT, ".claude", "_state")
EF = os.path.join(VAULT, ".claude", "_eval-fixtures")
sys.path.insert(0, EF)
try:
    import harness_common as H
except Exception:
    H = None
try:
    import promotion_predictions as PP
except Exception:
    PP = None

TODAY = date.today()


def _count(path):
    if not os.path.exists(path):
        return 0
    return sum(1 for l in open(path, encoding="utf-8", errors="replace") if l.strip())


def _age_days(path):
    if not os.path.exists(path):
        return None
    try:
        return (datetime.now() - datetime.fromtimestamp(os.path.getmtime(path))).days
    except OSError:
        return None


def _read_jsonl(path):
    out = []
    if os.path.exists(path):
        for l in open(path, encoding="utf-8", errors="replace"):
            l = l.strip()
            if l:
                try:
                    out.append(json.loads(l))
                except json.JSONDecodeError:
                    pass
    return out


# (label, filename, stale-after-days) — feeders that should refresh on a cadence
FEEDERS = [
    ("corrections (capture)", "corrections.jsonl", 14),
    ("success-traces", "success-traces.jsonl", 14),
    ("error-patterns (daily)", "error-patterns.jsonl", 2),
    ("reflections", "reflections.jsonl", 14),
    ("evolution-proposals (weekly)", "evolution-proposals.jsonl", 9),
    ("predictions", "promotion-predictions.jsonl", 999),
    ("observations", "promotion-observations.jsonl", 999),
]


def gather():
    h = {"feeders": [], "loop": {}, "coverage": {}, "evolution": {}, "errors": []}
    for label, fn, stale in FEEDERS:
        p = os.path.join(STATE, fn)
        age = _age_days(p)
        h["feeders"].append({"label": label, "count": _count(p), "age_days": age,
                             "stale": (age is None or age > stale)})
    # verify arrow
    if PP is not None:
        from pathlib import Path
        root = Path(VAULT)
        rows, _ = PP.load_rows(PP.state_path(root))
        obs = PP.load_observations(PP.obs_path(root))
        open_p = [r for _ln, r in rows if r.get("verdict") is None]
        h["loop"] = {
            "total": len(rows), "open": len(open_p),
            "arrow": [{"id": r.get("id"), "class_key": r.get("class_key"),
                       "distinct_sessions": obs.get(r.get("id"), {}).get("distinct_sessions", 0),
                       "need": (r.get("eval_after") or {}).get("min_occurrences", 3),
                       "recurred": obs.get(r.get("id"), {}).get("recurred", 0)} for r in open_p],
        }
    # class_key coverage (the backbone realization metric)
    preds = _read_jsonl(os.path.join(STATE, "promotion-predictions.jsonl"))
    corrs = _read_jsonl(os.path.join(STATE, "corrections.jsonl"))
    h["coverage"] = {
        "predictions_keyed": sum(1 for r in preds if r.get("class_key") is not None),
        "predictions_total": len(preds),
        "corrections_keyed": sum(1 for r in corrs if r.get("class_key") is not None),
        "corrections_total": len(corrs),
    }
    # evolution proposals (shadow)
    props = _read_jsonl(os.path.join(STATE, "evolution-proposals.jsonl"))
    h["evolution"] = {"total": len(props),
                      "GRAD": sum(1 for p in props if p.get("autonomy") == "GRAD"),
                      "CAP": sum(1 for p in props if p.get("autonomy") == "CAP")}
    # error patterns top
    h["errors"] = sorted(_read_jsonl(os.path.join(STATE, "error-patterns.jsonl")),
                         key=lambda e: e.get("count", 0), reverse=True)[:4]
    return h


def verdict(h):
    fresh = sum(1 for f in h["feeders"] if not f["stale"])
    stale = [f["label"] for f in h["feeders"] if f["stale"]]
    arrow_moving = any(a["distinct_sessions"] > 0 for a in h["loop"].get("arrow", []))
    ready = any(a["distinct_sessions"] >= a["need"] for a in h["loop"].get("arrow", []))
    if ready:
        v = "LEARNING — a prediction is READY for a verdict"
    elif fresh >= 4 and h["loop"].get("open", 0) == 0 and h["loop"].get("total", 0) > 0:
        v = "LEARNING -- all " + str(h["loop"]["total"]) + " predictions adjudicated/closed; feeders fresh"
    elif fresh >= 4 and h["loop"].get("open", 0) > 0:
        v = "RUNNING — feeders fresh, loop open, arrow accruing" if arrow_moving else "RUNNING — feeders fresh; arrow not yet accruing (needs distinct-session confirms)"
    else:
        v = "PARTIAL — some feeders stale; check the schedule"
    return v, stale


def main():
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    h = gather()
    if "--json" in sys.argv:
        print(json.dumps(h, ensure_ascii=False, indent=2)); return 0
    v, stale = verdict(h)
    print(f"=== LEARN-LOOP HEALTH ({TODAY.isoformat()}) ===\n")
    print(f"VERDICT: {v}\n")
    print("Feeders (freshness):")
    for f in h["feeders"]:
        age = "missing" if f["age_days"] is None else f"{f['age_days']}d"
        mark = "STALE" if f["stale"] else "ok"
        print(f"  [{mark:5}] {f['label']:30} {f['count']:>4} rows  ({age})")
    lp = h["loop"]
    print(f"\nVerify arrow: {lp.get('open', 0)} open / {lp.get('total', 0)} total")
    for a in lp.get("arrow", []):
        ck = f"#{a['class_key']}" if a.get("class_key") else "#-(judgment-quality)"
        flag = " <- READY" if a["distinct_sessions"] >= a["need"] else ""
        rec = f" {a['recurred']} recurrence(s)!" if a["recurred"] else ""
        print(f"  {a['id']} {ck:>22}: {a['distinct_sessions']}/{a['need']} distinct sessions{rec}{flag}")
    cov = h["coverage"]
    print(f"\nclass_key coverage (backbone): predictions {cov['predictions_keyed']}/{cov['predictions_total']}"
          f"  ·  corrections {cov['corrections_keyed']}/{cov['corrections_total']}")
    ev = h["evolution"]
    print(f"evolution proposals (shadow): {ev['total']}  ({ev['GRAD']} GRAD / {ev['CAP']} CAP)")
    print("top recurring errors:")
    for e in h["errors"]:
        print(f"  {e.get('count','?'):>3}x / {e.get('sessions','?')}sess  {e.get('signature','')}")
    if stale:
        print(f"\n! stale feeders: {', '.join(stale)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
