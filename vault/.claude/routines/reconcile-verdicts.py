#!/usr/bin/env python3
"""reconcile-verdicts.py — close the learning loop.

The L2 jury records a bucket verdict per prediction in _state/adjudicator-verdicts.json,
but nothing wrote it back into _state/promotion-predictions.jsonl — so loop_health (which
keys "open" on `verdict is None`) saw every adjudicated prediction as still open. This is
the missing write-back step: it propagates the jury verdict into the predictions file,
faithfully preserving the weak-signal/leaning nuance and noting that the recurrence window
is tracked separately. Never overwrites an already-set verdict. Backs up before writing.

Run this immediately after the adjudicator, or on the loop's daily cadence.
  python reconcile-verdicts.py            # DRY RUN (prints plan, writes nothing)
  python reconcile-verdicts.py --apply    # write + back up
"""
from __future__ import annotations
import argparse, io, json, os, shutil, sys
from datetime import date

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

STATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_state")
PRED = os.path.join(STATE, "promotion-predictions.jsonl")
ADJ  = os.path.join(STATE, "adjudicator-verdicts.json")
STAMP = date.today().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()
    if not (os.path.exists(PRED) and os.path.exists(ADJ)):
        print("missing predictions or adjudicator file; nothing to do"); return 0
    adj = json.load(open(ADJ, encoding="utf-8"))
    verdicts = {v["id"]: v for v in adj.get("verdicts", []) if v.get("id")}

    out, changed = [], 0
    for ln in (l.rstrip("\n") for l in open(PRED, encoding="utf-8", errors="replace")):
        if not ln.strip():
            out.append(ln); continue
        try:
            r = json.loads(ln)
        except json.JSONDecodeError:
            out.append(ln); continue
        v = verdicts.get(r.get("id"))
        if v and r.get("verdict") in (None, "", "null"):
            bucket = v.get("bucket") or "passed"
            r["verdict"] = bucket
            r["verdict_notes"] = (r.get("verdict_notes") or "") + (
                f"Closed by L2-jury ({v.get('source','jury')}) {str(adj.get('ts',''))[:10]}: "
                f"{v.get('verdict_candidate','')}; learning_verdict={v.get('learning_verdict','')}; "
                f"recurred={v.get('recurred',0)}; autonomy_ready={v.get('autonomy_ready',False)}. "
                f"Reconciled by reconcile-verdicts.py {STAMP} — jury closure (not recurrence-proven); "
                f"recurrence window tracked separately.")
            changed += 1
            print(f"  {r['id']}: null -> {bucket}")
        out.append(json.dumps(r, ensure_ascii=False))

    print(f"\n{changed} prediction(s) to close.")
    if not args.apply:
        print("(DRY RUN — re-run with --apply to write + back up)"); return 0
    if changed:
        shutil.copy2(PRED, PRED + f".bak-{STAMP}")
        open(PRED, "w", encoding="utf-8").write("\n".join(out) + "\n")
        print(f"wrote predictions (backup: promotion-predictions.jsonl.bak-{STAMP})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
