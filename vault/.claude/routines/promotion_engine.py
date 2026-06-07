#!/usr/bin/env python3
"""promotion_engine.py — autonomous-but-verified promotion loop ([[09 Rules/promotion-loop.md]]).

Closes distilled->promoted at model speed via two independent verifiers (recurrence + jury); the
human audits the batch. Built ON the existing verifiers, not beside them:
  - promotion-predictions.jsonl   the held-out test set
  - harness_common.recurrence_hits the empirical no-regression matcher (class-key + Jaccard)
  - adjudicator-verdicts.json      the cross-family jury (reward-model ensemble)

State: .claude/_state/provisional-promotions.jsonl — soft rules on probation.

Modes (DRY-RUN by default — mutates nothing unless --apply):
  --land    pending distill proposals -> provisional (register; land soft rule)   [Tier A]
  --eval    evaluate provisionals past probation -> auto-revert fails / confirm passes  [default]
  --audit   emit the batch-audit report (auto-confirmed / in-probation / auto-reverted)
  --status  show verifier inputs available (open predictions, jury freshness)
Flags: --apply (perform writes; else dry-run) · env PROMO_AUTOCONFIRM=1 (else confirm = propose-only).
0 model tokens. Discovered VAULT. Never hard-crashes.
"""
from __future__ import annotations
import argparse, io, json, os, sys
from datetime import date, datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = Path(__file__).resolve().parents[2]
STATE = VAULT / ".claude" / "_state"
PROV = STATE / "provisional-promotions.jsonl"
PRED = STATE / "promotion-predictions.jsonl"
CORR = STATE / "corrections.jsonl"
PROPOSALS = STATE / "distill-proposals.jsonl"
JURY = STATE / "adjudicator-verdicts.json"
sys.path.insert(0, str(VAULT / ".claude" / "_eval-fixtures"))
try:
    import harness_common as _H
except Exception:
    _H = None


def _today() -> str:
    return date.today().isoformat()


def _read_jsonl(p: Path) -> list:
    if not p.exists():
        return []
    out = []
    for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def _jury_buckets() -> dict:
    try:
        c = json.loads(JURY.read_text(encoding="utf-8"))
        return {v["id"]: v.get("bucket") for v in c.get("verdicts", []) if v.get("id")}
    except Exception:
        return {}


def _recurrence_clean(pred: dict, corrections: list) -> bool:
    if _H is None:
        return False  # can't verify without the spine -> never auto-confirm (fail-safe)
    try:
        return len(_H.recurrence_hits(pred, corrections).get("hits", [])) == 0
    except Exception:
        return False


def gate(prov: dict, preds_by_id: dict, jury: dict, corrections: list) -> dict:
    """The dual-verifier gate. Returns {verdict: confirm|revert|hold, recurrence, jury}."""
    pred = preds_by_id.get(prov.get("prediction_id"))
    if not pred:
        return {"verdict": "hold", "why": "no prediction bound"}
    recurrence_clean = _recurrence_clean(pred, corrections)
    jb = jury.get(pred.get("id"))
    if not recurrence_clean or jb == "failed":
        return {"verdict": "revert", "why": f"recurrence_clean={recurrence_clean} jury={jb}"}
    if recurrence_clean and jb == "passed":
        return {"verdict": "confirm", "why": "recurrence-clean & jury-passed"}
    return {"verdict": "hold", "why": f"awaiting jury (recurrence_clean={recurrence_clean} jury={jb})"}


PROBATION_DAYS = 14


def _append(path: Path, obj: dict) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _rewrite(path: Path, rows: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""))


def _set_verdict(pred_id: str, verdict: str) -> None:
    rows = _read_jsonl(PRED)
    for r in rows:
        if r.get("id") == pred_id:
            r["verdict"] = verdict
            r["verdict_notes"] = f"set by promotion_engine ({_today()})"
    _rewrite(PRED, rows)


def _node_append_rule(target_node: str, rule_text: str) -> bool:
    """Append a confirmed rule to the target judgment node's Operationalized-by / Rules-that-serve
    line. Only fires on auto-CONFIRM (PROMO_AUTOCONFIRM=1) — the soft→hard escalation."""
    f = VAULT / "09 Rules" / "_judgment" / f"{target_node}.md"
    if not f.exists():
        return False
    txt = f.read_text(encoding="utf-8", errors="replace")
    for label in ("**Operationalized by:**", "**Rules that serve it:**"):
        i = txt.find(label)
        if i >= 0:
            eol = txt.find("\n", i)
            eol = len(txt) if eol < 0 else eol
            f.write_text(txt[:eol] + f"; {rule_text} _(auto-promoted {_today()})_" + txt[eol:], encoding="utf-8")
            return True
    return False


def _from_iso(d: str):
    try:
        return datetime.fromisoformat(str(d)).date()
    except Exception:
        return None


def _probation_until(today: str) -> str:
    from datetime import timedelta
    return (date.fromisoformat(today) + timedelta(days=PROBATION_DAYS)).isoformat()


def land_one(p: dict, today: str) -> dict:
    """proposal -> provisional: register the soft rule + mint its prediction (Tier A)."""
    pid = "prov-" + str(p.get("id", "?"))
    predid = "pp-" + pid
    _append(PRED, {
        "id": predid, "created": today, "source": f"provisional {pid}",
        "landed_in": f"{p.get('target_node')} (provisional)",
        "trigger_signature": {"kind": "behavior", "value": p.get("target_node", "")},
        "forbidden_behavior": "recurrence of: " + str(p.get("label", "")),
        "expected_behavior": str(p.get("proposal", ""))[:300],
        "replayable": False, "eval_after": {"min_occurrences": 3, "by": _probation_until(today)},
        "verdict": None, "class_key": None,
        "class_note": "provisional-promotion prediction", "class_key_source": "auto",
    })
    entry = {"id": pid, "source_proposal": p.get("id"), "target_node": p.get("target_node"),
             "rule_text": p.get("label"), "landed_on": today, "probation_until": _probation_until(today),
             "prediction_id": predid, "status": "provisional"}
    _append(PROV, entry)
    return entry


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--land", action="store_true")
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--apply", action="store_true", help="perform writes (else dry-run)")
    args = ap.parse_args()
    autoconfirm = os.environ.get("PROMO_AUTOCONFIRM") == "1"
    if not autoconfirm:  # reversible in-vault flag (preferred over scheduler env)
        try:
            autoconfirm = bool(json.loads((STATE / "promotion-config.json").read_text(encoding="utf-8")).get("autoconfirm"))
        except Exception:
            autoconfirm = False
    dry = not args.apply
    prov = _read_jsonl(PROV)
    preds = _read_jsonl(PRED)
    preds_by_id = {p["id"]: p for p in preds if p.get("id")}
    jury = _jury_buckets()
    corrections = _read_jsonl(CORR)
    today = _today()
    tag = "[dry-run] " if dry else ""

    if args.status or not (args.land or args.eval or args.audit):
        open_preds = [p for p in preds if p.get("verdict") is None]
        active = [p for p in prov if p.get("status") == "provisional"]
        print(f"promotion_engine status ({today}) {tag}")
        print(f"  provisional in-flight: {len(active)}")
        print(f"  predictions: {len(preds)} total · {len(open_preds)} open · jury verdicts cached: {len(jury)}")
        print(f"  recurrence spine: {'available' if _H else 'MISSING (auto-confirm disabled, fail-safe)'}")
        print(f"  posture: auto-revert ON · auto-confirm {'ON' if autoconfirm else 'PROPOSE-ONLY'}")
        if not active:
            print("  (no provisionals yet — loop arms as distill lands provisional promotions; --land to feed it)")
        if not args.status:
            return 0

    if args.land:
        proposals = _read_jsonl(PROPOSALS)
        pending = [p for p in proposals if p.get("status") == "pending-review"]
        print(f"\n--land {tag}: {len(pending)} pending proposal(s) -> provisional")
        for p in pending:
            print(f"  {'would land' if dry else 'land'}: {p.get('id')} -> {p.get('target_node')} ({p.get('label')})")
            if not dry:
                land_one(p, today)
                p["status"] = "provisional"
        if pending and not dry:
            _rewrite(PROPOSALS, proposals)
        if not pending:
            print("  (none pending — distill proposals are all applied/empty)")

    if args.eval:
        due = [pv for pv in prov if pv.get("status") == "provisional"
               and (pv.get("probation_until") or "9999") <= today]
        print(f"\n--eval {tag}: {len(due)} provisional(s) past probation · auto-confirm {'ON' if autoconfirm else 'PROPOSE-ONLY'}")
        changed = False
        for pv in due:
            g = gate(pv, preds_by_id, jury, corrections)
            v = g["verdict"]
            if v == "revert":
                print(f"  {pv['id']} [{pv['target_node']}] -> REVERT  ({g['why']})")
                if not dry:
                    pv["status"], pv["reverted_on"], pv["reason"] = "reverted", today, g["why"]
                    _set_verdict(pv.get("prediction_id"), "failed"); changed = True
            elif v == "confirm" and autoconfirm:
                print(f"  {pv['id']} [{pv['target_node']}] -> CONFIRM (auto)  ({g['why']})")
                if not dry:
                    _node_append_rule(pv["target_node"], pv.get("rule_text", ""))
                    pv["status"], pv["confirmed_on"] = "confirmed", today
                    _set_verdict(pv.get("prediction_id"), "passed"); changed = True
            elif v == "confirm":
                print(f"  {pv['id']} [{pv['target_node']}] -> PROPOSE-confirm (gate passed; awaiting batch approval)")
            else:
                print(f"  {pv['id']} [{pv['target_node']}] -> hold  ({g['why']})")
        if changed and not dry:
            _rewrite(PROV, prov)

    if args.audit:
        by = {}
        for pv in prov:
            by.setdefault(pv.get("status", "?"), []).append(pv.get("id"))
        print(f"\n--audit {tag}: " + " · ".join(f"{k}={len(v)}" for k, v in sorted(by.items())) or "  (empty)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:
        print(f"promotion_engine error: {e}")
        raise SystemExit(0)
