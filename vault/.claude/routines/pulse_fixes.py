#!/usr/bin/env python3
"""Fix-recipe registry for harness-pulse findings.

Each recipe takes the full verdict dict (so it can read related state) and
returns {ok: bool, msg: str, details: dict}. Recipes are intentionally
defensive (verify before acting; idempotent; never raise).

Two entry points:
  - CLI: `python pulse_fixes.py --code <code> [--json]` — used by the
    dashboard's modal action buttons.
  - Importable: `from pulse_fixes import run_all_red, FIX_REGISTRY` — used by
    `harness-pulse.py` after writing a RED verdict (inline autofix).

Per Q2=2: every red finding gets a fix attempt; failures escalate via notify().
Per Q3=1: the inline run lives in `harness-pulse.py`, not a separate cron.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT, log_event, notify, channel_liveness, is_dry_run  # noqa: E402

STATE = VAULT / ".claude" / "_state"
PENDING = VAULT / ".claude" / "_pending"
ARCHIVE = VAULT / ".claude" / "_archive" / "pending-signals"
VERDICT_PATH = STATE / "harness-pulse.json"
AUTOFIX_LOG = STATE / "pulse-autofix-log.jsonl"

# Windows scheduled task names (verified via `schtasks /Query` 2026-05-28).
TASK_FEISHU_CONSUMER = "feishu-event-consumer-daemon"
TASK_TIER7_DRIVER = "RG-tier7-inbox-drift"
TASK_VAULT_EVOLVE_SIGNAL = "RG-signal-vault-evolve"

# How long the auto path waits before re-queuing a judgment-extraction signal for a
# debt that's still standing (see fix_learning_loop_debt).
EXTRACTION_COOLDOWN_H = 18

# --- execution mode --------------------------------------------------------
# Recipes can take REAL side effects: restart production scheduled tasks
# (_restart_task) and write signals into _pending/. Those must NOT fire from an
# ad-hoc or observation run of the pulse — that's the bug where a monitoring
# `harness-pulse.py` (or a direct import) silently restarted the Feishu daemon /
# spammed _pending/. So side effects are gated, SAFE-BY-DEFAULT:
#   _LIVE=False (default) → recipes log "[DRY] would ..." and skip the side effect.
#   _LIVE=True            → recipes act.
# The two entry points set the mode explicitly:
#   - run_all_red() (the autonomous pulse path) → _LIVE = not is_dry_run(), so the
#     scheduled pulse only acts when its task is run with DRY_RUN=0 (opt-in to
#     unattended auto-fix). Default posture (DRY_RUN unset) = detect+alert only.
#   - main() / CLI (operator + dashboard "Fix" buttons) → _LIVE=True unless --dry,
#     because an operator clicking a fix button explicitly asked for the action.
# _AUTO marks the autonomous path so cooldown self-suppression applies there but
# not to a deliberate operator click.
_LIVE = False
_AUTO = False


def _set_mode(live: bool, auto: bool) -> None:
    global _LIVE, _AUTO
    _LIVE, _AUTO = bool(live), bool(auto)


def _live() -> bool:
    return _LIVE


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_log_ts(ts):
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _hours_since_last_extraction_queue() -> "float | None":
    """Age (hours) of the most recent autofix-log row that actually QUEUED a
    judgment-extraction signal, or None if never. The SessionStart brief drains
    (deletes) the signal from _pending/ within seconds, so the _unconsumed_signals
    idempotency guard can't see it on the next pulse — without this, a standing
    debt re-queues every 3h (pure log spam). Never raises."""
    if not AUTOFIX_LOG.exists():
        return None
    newest = None
    try:
        for line in AUTOFIX_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("code") in ("learning-loop-debt", "judgment-queue-backlog") \
               and str(r.get("msg", "")).startswith("queued judgment extraction"):
                t = _parse_log_ts(r.get("ts"))
                if t and (newest is None or t > newest):
                    newest = t
    except Exception:
        return None
    if newest is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - newest).total_seconds() / 3600)


def _result(ok: bool, msg: str, **details) -> dict:
    return {"ok": bool(ok), "msg": msg, "details": details}


def _unconsumed_signals(skill: str) -> list[Path]:
    """Pending *-{skill}.signal files not yet drained. Used to make signal-queuing
    recipes IDEMPOTENT: re-queuing a fix nothing has consumed just grows _pending/
    without closing anything (the autofix-as-no-op loop). If one is already queued,
    the recipe reports it instead of writing a duplicate."""
    if not PENDING.exists():
        return []
    return sorted(PENDING.glob(f"*-{skill}.signal"))


def _restart_task(task_name: str) -> dict:
    """schtasks /End (best-effort) → /Run. Returns merged details.
    Dry-gated: an observation/ad-hoc pulse must not restart production tasks."""
    if not _live():
        return {"ok": True, "out": {"task": task_name, "dry": True,
                                    "note": "[DRY] would /End then /Run — set DRY_RUN=0 on the pulse task to act"}}
    out: dict = {"task": task_name, "ended": None, "started": None}
    try:
        r = subprocess.run(["schtasks", "/End", "/TN", task_name],
                           capture_output=True, encoding="utf-8", errors="replace", timeout=20)
        out["ended"] = {"rc": r.returncode, "stderr": (r.stderr or "").strip()[:200]}
    except Exception as e:
        out["ended"] = {"rc": -1, "stderr": f"exception: {e}"}
    try:
        r = subprocess.run(["schtasks", "/Run", "/TN", task_name],
                           capture_output=True, encoding="utf-8", errors="replace", timeout=20)
        out["started"] = {"rc": r.returncode, "stderr": (r.stderr or "").strip()[:200]}
        started_ok = r.returncode == 0
    except Exception as e:
        out["started"] = {"rc": -1, "stderr": f"exception: {e}"}
        started_ok = False
    return {"ok": started_ok, "out": out}


# ---------------- recipes ---------------------------------------------------

def fix_critical_signal(verdict: dict, finding: dict) -> dict:
    """Identify queued CRITICAL-*.signal, attempt redelivery via a live channel,
    then archive on success. If no channel is live, log and leave."""
    sigs = sorted(PENDING.glob("CRITICAL-*.signal")) if PENDING.exists() else []
    if not sigs:
        return _result(True, "no CRITICAL signal present (already drained)")
    if not _live():
        return _result(True, f"[DRY] would redeliver {len(sigs)} CRITICAL signal(s) — set DRY_RUN=0 to act",
                       dry=True, signals=[s.name for s in sigs])
    delivered = []
    failed = []
    live = channel_liveness()
    if not (live.get("feishu") or live.get("discord")):
        return _result(False, "no live channel — cannot redeliver",
                       signals=[s.name for s in sigs], channels=live)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for sig in sigs:
        try:
            content = sig.read_text(encoding="utf-8", errors="replace").strip()
        except Exception as e:
            failed.append({"signal": sig.name, "reason": f"read failed: {e}"})
            continue
        # notify() will pick the live channel; on send failure it drops a NEW
        # CRITICAL signal, so guard against the obvious infinite loop by
        # archiving the source first, then re-pushing.
        msg = f"🔁 [autofix] redelivering queued alert from {sig.name}:\n{content[:1200]}"
        res = notify("pulse-autofix", msg)
        if res.get("delivered"):
            try:
                target = ARCHIVE / f"{_now_iso().replace(':', '')}-{sig.name}"
                shutil.move(str(sig), str(target))
                delivered.append({"signal": sig.name, "channel": res.get("channel"), "archived_to": target.name})
            except Exception as e:
                delivered.append({"signal": sig.name, "channel": res.get("channel"), "archive_error": str(e)})
        else:
            failed.append({"signal": sig.name, "reason": "notify did not confirm delivery"})
    ok = bool(delivered) and not failed
    return _result(ok,
                   f"redelivered {len(delivered)}/{len(sigs)}; {len(failed)} failed",
                   delivered=delivered, failed=failed)


def fix_feishu_down(verdict: dict, finding: dict) -> dict:
    """Restart the feishu-event-consumer-daemon scheduled task."""
    res = _restart_task(TASK_FEISHU_CONSUMER)
    verb = "would restart" if res["out"].get("dry") else "restarted"
    return _result(res["ok"],
                   f"{verb} {TASK_FEISHU_CONSUMER} (verify next pulse for liveness)",
                   **res["out"])


def fix_scheduler_stalled(verdict: dict, finding: dict) -> dict:
    """Restart the Tier-7 hourly driver."""
    res = _restart_task(TASK_TIER7_DRIVER)
    verb = "would restart" if res["out"].get("dry") else "restarted"
    return _result(res["ok"],
                   f"{verb} {TASK_TIER7_DRIVER}; if next pulse still stalled, scheduler service itself is wedged",
                   **res["out"])


def fix_scheduler_unknown(verdict: dict, finding: dict) -> dict:
    """Same recipe as scheduler-stalled — no inbox-drift events seen, kick the driver."""
    return fix_scheduler_stalled(verdict, finding)


def fix_vault_evolve_missing(verdict: dict, finding: dict) -> dict:
    """Run the signal-vault-evolve task (drops a signal for next Claude session).
    /vault-evolve is LLM-required so we don't try to fix-it-now from a routine."""
    res = _restart_task(TASK_VAULT_EVOLVE_SIGNAL)
    if res["ok"]:
        verb = "would trigger" if res["out"].get("dry") else "triggered"
        return _result(True,
                       f"{verb} {TASK_VAULT_EVOLVE_SIGNAL} (drops signal → next Claude session runs /vault-evolve)",
                       **res["out"])
    # Fallback: write the signal directly (idempotent — skip if already pending).
    existing = _unconsumed_signals("vault-evolve")
    if existing:
        return _result(True,
                       f"vault-evolve already queued ({len(existing)} pending) — not duplicating",
                       pending=[p.name for p in existing])
    try:
        PENDING.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = PENDING / f"{ts}-vault-evolve.signal"
        path.write_text(json.dumps({
            "skill": "vault-evolve",
            "mode": "autonomous",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "scheduled-at": ts,
            "source": "pulse-autofix",
        }, ensure_ascii=False), encoding="utf-8")
        return _result(True, f"wrote fallback signal {path.name}", signal=path.name)
    except Exception as e:
        return _result(False, f"task restart and signal-write both failed: {e}", **res["out"])


def fix_corrections_stuck(verdict: dict, finding: dict) -> dict:
    """Drop a signal asking next Claude session to run judgment-distill.
    The distill itself is LLM work; we just queue it.
    Idempotent: if a distill signal is already pending, don't re-queue."""
    existing = _unconsumed_signals("judgment-distill")
    if existing:
        return _result(True,
                       f"judgment-distill already queued ({len(existing)} pending) — not duplicating",
                       pending=[p.name for p in existing])
    if not _live():
        return _result(True, "[DRY] would queue judgment-distill signal — set DRY_RUN=0 to act", dry=True)
    try:
        PENDING.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = PENDING / f"{ts}-judgment-distill.signal"
        path.write_text(json.dumps({
            "skill": "judgment-distill",
            "mode": "autonomous",
            "reason": finding.get("msg", "corrections stuck >5 days"),
            "scheduled-at": ts,
            "source": "pulse-autofix",
        }, ensure_ascii=False), encoding="utf-8")
        return _result(True, f"queued judgment-distill signal {path.name}", signal=path.name)
    except Exception as e:
        return _result(False, f"signal write failed: {e}")


def fix_learning_loop_debt(verdict: dict, finding: dict) -> dict:
    """Queue a judgment extraction pass. This does not promote rules.

    Two guards keep this from being a no-op spam loop:
      - idempotency: if an extraction signal is still pending, don't re-queue.
      - cooldown (auto path only): the SessionStart brief drains the signal within
        seconds, so the idempotency check goes blind on the next pulse and a
        standing (human-gated) debt would re-queue every 3h. Suppress auto
        re-queues within EXTRACTION_COOLDOWN_H. A deliberate operator click
        (_AUTO=False) always queues."""
    existing = _unconsumed_signals("judgment-extraction")
    if existing:
        return _result(True,
                       f"judgment-extraction already queued ({len(existing)} pending) — not duplicating; "
                       "drain it in a Claude session to clear the debt",
                       pending=[p.name for p in existing])
    if _AUTO:
        age = _hours_since_last_extraction_queue()
        if age is not None and age < EXTRACTION_COOLDOWN_H:
            return _result(True,
                           f"extraction last queued {age:.1f}h ago (<{EXTRACTION_COOLDOWN_H}h cooldown) — "
                           "debt is human-gated, suppressing auto re-queue",
                           suppressed=True, age_h=round(age, 1))
    if not _live():
        return _result(True, "[DRY] would queue judgment-extraction signal — set DRY_RUN=0 to act", dry=True)
    try:
        PENDING.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = PENDING / f"{ts}-judgment-extraction.signal"
        path.write_text(json.dumps({
            "skill": "judgment-extraction",
            "mode": "assisted",
            "reason": finding.get("msg", "learning loop debt threshold exceeded"),
            "scheduled-at": ts,
            "source": "pulse-autofix",
            "instructions": "Extract genuine judgment events from .claude/_state/judgment-queue/ into corrections.jsonl, dedupe first, then clear consumed queue files. Do not auto-promote judgment nodes.",
        }, ensure_ascii=False), encoding="utf-8")
        return _result(True, f"queued judgment extraction signal {path.name}", signal=path.name)
    except Exception as e:
        return _result(False, f"signal write failed: {e}")


def fix_pending_backlog(verdict: dict, finding: dict) -> dict:
    """Surface the oldest signals; can't actually consume them without context."""
    if not PENDING.exists():
        return _result(True, "_pending/ empty")
    sigs = sorted(PENDING.glob("*.signal"), key=lambda p: p.stat().st_mtime)
    oldest = [{"name": s.name, "age_h": round((datetime.now().timestamp() - s.stat().st_mtime) / 3600, 1)}
              for s in sigs[:5]]
    return _result(False, f"{len(sigs)} signals queued; manual triage required (run /catch-up or open a Claude session)",
                   count=len(sigs), oldest=oldest)


def fix_pending_stale(verdict: dict, finding: dict) -> dict:
    return fix_pending_backlog(verdict, finding)


def fix_error_rate_high(verdict: dict, finding: dict) -> dict:
    """Read-only diagnostic: surface the recent error rows over the SAME 24h window
    the detector (check_error_rate) uses, so the count here matches the finding.
    Reading is not a fix — a successful read returns ok:True (don't escalate); only
    a genuine read failure returns ok:False. (Was: last-1000-rows + always ok:False,
    which mismatched the detector and reported '0 errors → fail' on every run.)"""
    usage = STATE / "usage.jsonl"
    if not usage.exists():
        return _result(True, "usage.jsonl missing — error-rate instrumentation not running", errors=0, total=0)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    total = 0
    errs = []
    try:
        for line in usage.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            t = _parse_log_ts(r.get("ts"))
            if t is None or t < cutoff:
                continue
            total += 1
            if r.get("ok") is False:
                errs.append({"ts": r.get("ts"), "tool": r.get("tool"), "skill": r.get("skill")})
    except Exception as e:
        return _result(False, f"usage.jsonl read failed: {e}")
    pct = (100 * len(errs) / total) if total else 0
    return _result(True, f"{len(errs)}/{total} tool error(s) in last 24h ({pct:.0f}%) — diagnostic only",
                   errors=len(errs), total=total, sample=errs[-10:])


FIX_REGISTRY = {
    "critical-signal": fix_critical_signal,
    "feishu-down": fix_feishu_down,
    "scheduler-stalled": fix_scheduler_stalled,
    "scheduler-unknown": fix_scheduler_unknown,
    "vault-evolve-missing": fix_vault_evolve_missing,
    "corrections-stuck": fix_corrections_stuck,
    "learning-loop-debt": fix_learning_loop_debt,
    "judgment-queue-backlog": fix_learning_loop_debt,
    "pending-backlog": fix_pending_backlog,
    "pending-stale": fix_pending_stale,
    "error-rate-high": fix_error_rate_high,
}


# ---------------- public API -------------------------------------------------

def run_one(code: str, verdict: dict | None = None, finding: dict | None = None) -> dict:
    """Run a single recipe by code. Returns {ok, msg, details, code}.

    `verdict` is the harness-pulse.json contents (loaded if omitted).
    `finding` is the matching finding row; if omitted we find the first one
    in verdict.findings whose code matches."""
    if verdict is None:
        try:
            verdict = json.loads(VERDICT_PATH.read_text(encoding="utf-8")) if VERDICT_PATH.exists() else {}
        except Exception:
            verdict = {}
    if finding is None:
        for f in verdict.get("findings", []):
            if f.get("code") == code:
                finding = f
                break
        finding = finding or {"code": code, "level": "unknown", "msg": "(no finding row in verdict)"}
    fn = FIX_REGISTRY.get(code)
    if fn is None:
        return {"ok": False, "msg": f"no recipe for code: {code}", "details": {}, "code": code,
                "available_codes": sorted(FIX_REGISTRY.keys())}
    try:
        out = fn(verdict, finding)
    except Exception as e:
        out = _result(False, f"recipe raised: {e}")
    out["code"] = code
    _log_attempt(out, finding)
    return out


def run_all_red(verdict: dict) -> list[dict]:
    """Run a recipe for every red-level finding in the verdict. Returns the
    list of per-attempt results in finding order. Yellow/unknown findings are
    skipped (Q2=2 was 'every RED finding', not every level).

    This is the AUTONOMOUS path (called inline by harness-pulse.py). Side effects
    act only when the pulse task runs with DRY_RUN=0 — default posture is
    detect+alert, no unattended restarts/writes. Cooldown self-suppression on."""
    _set_mode(live=not is_dry_run(), auto=True)
    results: list[dict] = []
    for f in verdict.get("findings", []):
        if f.get("level") != "red":
            continue
        code = f.get("code", "")
        results.append(run_one(code, verdict=verdict, finding=f))
    return results


def _log_attempt(result: dict, finding: dict) -> None:
    """Append one row to pulse-autofix-log.jsonl. Never raises."""
    try:
        AUTOFIX_LOG.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts": _now_iso(),
            "code": result.get("code") or finding.get("code"),
            "level": finding.get("level"),
            "finding_msg": (finding.get("msg") or "")[:300],
            "ok": result.get("ok"),
            "msg": (result.get("msg") or "")[:300],
            "details": result.get("details") or {},
        }
        with AUTOFIX_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        log_event("pulse-autofix", "info" if result.get("ok") else "alert",
                  f"{row['code']}: {row['msg']}", code=row["code"], ok=row["ok"])
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=False, help="finding code to fix (omit + --all-red to fix every red finding)")
    ap.add_argument("--all-red", action="store_true", help="run every red recipe based on the current verdict")
    ap.add_argument("--list", action="store_true", help="list known codes and exit")
    ap.add_argument("--json", action="store_true", help="emit a single JSON object on stdout (default: human-readable)")
    ap.add_argument("--dry", action="store_true", help="simulate: log what each recipe would do, take no real side effect")
    ap.add_argument("--live", action="store_true", help="force real side effects (default for an explicit --code / --all-red)")
    args = ap.parse_args()

    if args.dry and args.live:
        ap.error("--dry and --live are mutually exclusive")

    if args.list:
        out = {"codes": sorted(FIX_REGISTRY.keys())}
        print(json.dumps(out, indent=2) if args.json else "\n".join(out["codes"]))
        return 0

    # CLI = explicit operator intent (incl. dashboard "Fix" buttons): act unless
    # --dry. --all-red mirrors the pulse sweep, so cooldown self-suppression applies;
    # a single --code is a deliberate one-shot, so it bypasses the cooldown.
    _set_mode(live=not args.dry, auto=bool(args.all_red))

    if args.all_red:
        try:
            verdict = json.loads(VERDICT_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(json.dumps({"ok": False, "msg": f"verdict read failed: {e}"}) if args.json else f"verdict read failed: {e}")
            return 1
        results = run_all_red(verdict)
        if args.json:
            print(json.dumps({"results": results}, ensure_ascii=False))
        else:
            for r in results:
                tag = "OK" if r.get("ok") else "FAIL"
                print(f"[{tag}] {r.get('code')}: {r.get('msg')}")
        return 0 if all(r.get("ok") for r in results) else 2

    if not args.code:
        ap.error("--code required (or pass --all-red / --list)")
    out = run_one(args.code)
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        tag = "OK" if out.get("ok") else "FAIL"
        print(f"[{tag}] {out.get('code')}: {out.get('msg')}")
        if out.get("details"):
            print(json.dumps(out["details"], ensure_ascii=False, indent=2))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
