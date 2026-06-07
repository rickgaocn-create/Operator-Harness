#!/usr/bin/env python3
"""
distill_autotrigger.py — close the learn-loop's one open joint: auto-INVOKE the
distill model-step instead of nagging the operator to remember it.

THE GAP THIS FIXES
  Capture (scripted) fills corrections.jsonl with status:new events. The distill
  model-step — read the brief, cluster events, write pending-review proposals — needs
  an AGENT, and nothing scheduled ever invoked it. So it last ran 2026-05-26 while 21
  events piled up and the SessionStart brief printed "distill due" every session,
  unanswered. The loop only "looped" when a human noticed the nag. That is the textbook
  open loop: a scripted producer, a human-pumped consumer, permanent growing backlog.

THE FIX
  When status:new >= threshold AND there is genuinely undistilled signal, drop a
  `distill-request-*.signal` into .claude/_pending/. The existing UserPromptSubmit
  signal-surfacing hook hands that task to the next agent ("handle, then delete"),
  which runs judgment_distill.py --brief, clusters, and appends proposals. The human is
  left exactly ONE job — the high-value gate (approve/reject in the review queue) — and
  never the low-value job of remembering to START the loop.

  This is the harness applying its OWN validated judgment to itself:
    - "prefer the harness auto-diagnosing over surfacing manual cards" (correction 2026-05-27)
    - "prefer the dashboard over manual input; reduce operator overhead"  (correction 2026-05-29)

DESIGN CONSTRAINTS (match the routine fleet)
  - 0 model tokens (pure scan + signal write); cross-platform (pathlib, discovered VAULT).
  - Never raises (degrades silently). Notification-class: writes NO vault content, only a
    _pending signal — so per 09 Rules/autonomous-routines.md Hard Rule 1 it skips the
    DRY_RUN gate on the signal-write path, but is bounded by a daily cap + dedup so it can
    never spam. Promotion stays 100% human-gated; this only stages the REQUEST.
  - Callable standalone (Tier-7 cron, every ~3h alongside the pulse) or from
    pulse_fixes.run_all_red(verdict) on a learning-debt red.

Usage:
  python distill_autotrigger.py            # evaluate + (if due) drop one request signal
  python distill_autotrigger.py --status   # report due/not-due; writes nothing
  python distill_autotrigger.py --json
Exit 0 always.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT, PENDING_DIR, log_event, under_run_cap  # noqa: E402

ROUTINE = "distill-autotrigger"
STATE = VAULT / ".claude" / "_state"
CORRECTIONS = STATE / "corrections.jsonl"
PROPOSALS = STATE / "distill-proposals.jsonl"
THRESHOLD = 5            # mirror judgment_distill.DEFAULT_THRESHOLD
MAX_REQUESTS_PER_DAY = 2  # at most two distill nudges/day even if signal keeps arriving


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _day(s) -> str:
    """YYYY-MM-DD prefix of any ISO-ish date/datetime string; '' if unparseable."""
    s = str(s or "")
    return s[:10] if len(s) >= 10 and s[4] == "-" and s[7] == "-" else ""


def evaluate() -> dict:
    """Decide whether the distill model-step is DUE, with the reason — no side effects."""
    events = _read_jsonl(CORRECTIONS)
    new_events = [e for e in events if e.get("status") == "new"]
    new_count = len(new_events)
    newest_event_day = max((_day(e.get("ts")) for e in new_events), default="")

    proposals = _read_jsonl(PROPOSALS)
    newest_proposal_day = max((_day(p.get("created")) for p in proposals), default="")

    # An already-queued, unconsumed request means the agent simply hasn't run yet —
    # don't stack a second one.
    existing_requests = (
        sorted(PENDING_DIR.glob("distill-request-*.signal")) if PENDING_DIR.exists() else []
    )

    threshold_met = new_count >= THRESHOLD
    # "Fresh signal" = the newest captured event POSTDATES the newest proposal, i.e. there
    # is genuinely undistilled material. If the last distill ran today (proposals created
    # >= newest event), we're caught up — don't re-fire. Day granularity = at most one
    # request per day of new signal, the right cadence for a human-gated review queue.
    fresh_signal = bool(newest_event_day) and newest_event_day > newest_proposal_day
    already_requested = bool(existing_requests)

    due = threshold_met and fresh_signal and not already_requested
    reason = (
        "request already queued (agent has not consumed it yet)" if already_requested
        else "below threshold" if not threshold_met
        else "no fresh signal since last distill (caught up)" if not fresh_signal
        else "DUE — fresh undistilled signal at/over threshold"
    )
    return {
        "due": due,
        "reason": reason,
        "new_count": new_count,
        "threshold": THRESHOLD,
        "threshold_met": threshold_met,
        "newest_event_day": newest_event_day,
        "newest_proposal_day": newest_proposal_day,
        "existing_requests": [p.name for p in existing_requests],
    }


SIGNAL_BODY = """[distill-request — auto-armed by distill_autotrigger.py at {ts}]

The judgment learn-loop has {n} undistilled status:new correction(s) (threshold {thr} met);
newest signal {ev} postdates the last proposal batch {prop}. The distill model-step is DUE
and needs an agent — that is you.

Do (the harness's own learn-loop; promotion is autonomous-but-verified — you stage, the
dual-verifier gate confirms, the operator audits the batch in /vault-evolve):
1. Run:  python .claude/_eval-fixtures/judgment_distill.py --brief
2. For each clustered node, collapse its events into a FEW high-signal, evidence-cited
   proposals (kind: edge | rule | node). Do not write one proposal per event — cluster.
3. Append each as one JSONL line to .claude/_state/distill-proposals.jsonl with
   "status":"pending-review". Fill mechanically-derivable reverse-edges for 0-event nodes.
4. Land them as PROVISIONAL (soft rules on probation — NOT yet in the nodes):
       python .claude/routines/promotion_engine.py --land --apply
   They auto-confirm to promoted only after the dual-verifier gate passes (recurrence-clean +
   jury-pass) per 09 Rules/promotion-loop.md. Do NOT hand-edit the _judgment nodes here.
5. Report the staged provisional set. Then delete this signal file.
"""


def run(verdict: dict | None = None) -> dict:
    """Drop a distill-request signal if due. Returns a pulse_fixes-style result dict."""
    ev = evaluate()
    if not ev["due"]:
        log_event(ROUTINE, "info", f"distill not due: {ev['reason']} "
                                   f"(new={ev['new_count']}/{ev['threshold']})")
        return {"ok": True, "code": ROUTINE, "acted": False, "msg": ev["reason"], "eval": ev}

    if not under_run_cap(ROUTINE, MAX_REQUESTS_PER_DAY):
        log_event(ROUTINE, "info", "distill due but daily request cap hit — skipping")
        return {"ok": True, "code": ROUTINE, "acted": False, "msg": "daily cap hit", "eval": ev}

    try:
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        body = SIGNAL_BODY.format(
            ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            n=ev["new_count"], thr=ev["threshold"],
            ev=ev["newest_event_day"], prop=ev["newest_proposal_day"] or "(none)",
        )
        path = PENDING_DIR / f"distill-request-{stamp}.signal"
        path.write_text(body, encoding="utf-8")
        log_event(ROUTINE, "alert", f"distill DUE — armed request signal {path.name} "
                                    f"({ev['new_count']} new events)", new=ev["new_count"])
        return {"ok": True, "code": ROUTINE, "acted": True, "msg": f"armed {path.name}", "eval": ev}
    except Exception as e:
        log_event(ROUTINE, "error", f"failed to arm distill request: {e}")
        return {"ok": False, "code": ROUTINE, "acted": False, "msg": str(e), "eval": ev}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", action="store_true", help="report due/not-due; write nothing")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.status:
        ev = evaluate()
        print(json.dumps(ev, ensure_ascii=False, indent=2) if args.json
              else f"distill due: {ev['due']} — {ev['reason']} "
                   f"(new={ev['new_count']}/{ev['threshold']}, "
                   f"newest_event={ev['newest_event_day']}, newest_proposal={ev['newest_proposal_day']})")
        return 0

    res = run()
    print(json.dumps(res, ensure_ascii=False, indent=2) if args.json
          else f"{'ARMED' if res.get('acted') else 'no-op'}: {res.get('msg')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # never hard-fail a routine
        print(f"distill_autotrigger error: {e}")
        sys.exit(0)
