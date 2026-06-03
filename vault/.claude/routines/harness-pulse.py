#!/usr/bin/env python3
"""
Harness pulse — consolidated liveness heartbeat for the operator harness.

Runs every ~3h (RG-tier7-harness-pulse). The reflex the harness was missing: it
consolidates signals that already exist but were scattered + pull-only —

  - channel liveness   (Discord daemon, Feishu consumer)  [mirror of check-channel-state.ps1]
  - Tier-7 scheduler   (is the hourly routine still firing?)
  - daily cortex       (/vault-evolve report present for today)
  - queue backlogs     (_pending signals, corrections stuck unpromoted in 'new')
  - tool error rate    (transcript tool_result is_error, last 24h — usage.jsonl CANNOT
                        see failures: PostToolUse does not fire on a failed tool call)

— into ONE verdict at .claude/_state/harness-pulse.json (green|yellow|red + findings).

Push is EDGE-TRIGGERED: it alerts only when severity WORSENS vs the previous pulse
(plus a one-line note on recovery to green). Steady state is silent — the
SessionStart brief reads the verdict file for the pull view. This is what stops
"Feishu died at 01:29 and nothing told me for 8h": the green→yellow transition
pushes once, via whichever channel is live (see _common.notify).

Notification-only routine — never writes vault content, so per
09 Rules/autonomous-routines.md Hard Rule 1 it skips the DRY_RUN gate on the
alert path. Set PULSE_SILENT=1 to compute+log the verdict WITHOUT pushing
(observation posture for the first days, before the SessionStart/vault-evolve
consumers are wired).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    VAULT, LOG_PATH, channel_liveness, log_event, notify, under_run_cap,
)

ROUTINE = "harness-pulse"
MAX_ALERTS_PER_DAY = 6
STATE = VAULT / ".claude" / "_state"
VERDICT_PATH = STATE / "harness-pulse.json"
SEV_RANK = {"green": 0, "yellow": 1, "red": 2}
JUDGMENT_QUEUE = STATE / "judgment-queue"
CORRECTIONS = STATE / "corrections.jsonl"
PROMOTION_PREDICTIONS = STATE / "promotion-predictions.jsonl"
GRADER_VERDICTS = STATE / "grader-verdicts.jsonl"
LEARNING_DEBT_YELLOW_QUEUE = 5
# RED is driven by candidate VOLUME or AGE — not raw queue-file count. A handful of
# thin session files (the normal carry) is a yellow "worth a pass", not an emergency.
# Queue-file count survives only as a high runaway backstop (producer wedged open).
LEARNING_DEBT_RED_QUEUE = 40
LEARNING_DEBT_YELLOW_CANDIDATES = 25
LEARNING_DEBT_RED_CANDIDATES = 75
LEARNING_DEBT_YELLOW_AGE_H = 24
LEARNING_DEBT_RED_AGE_H = 72
LEARNING_DEBT_NEW_CORRECTIONS = 5


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(ts) -> datetime | None:
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _read_jsonl(path: Path, limit: int | None = None) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        return []
    return rows[-limit:] if limit else rows


def _transcript_error_counts(cutoff: datetime) -> "tuple[int, int] | None":
    """True (total, errors) tool counts from Claude Code transcripts within the window.

    usage.jsonl CANNOT carry tool errors here: PostToolUse does not fire on a failed
    tool call in this CC build (verified — a forced Read-of-missing-file produced no
    hook event, and Bash tool_response has no error field). The transcript is the only
    ground truth: every tool_result block records is_error. Scans
    ~/.claude/projects/*/*.jsonl touched within the window, counts tool_result blocks
    and is_error:true among them. Returns None when no transcripts are found so the
    caller can fall back to the (lossy) usage.jsonl path on non-CC runtimes."""
    root = Path.home() / ".claude" / "projects"
    if not root.exists():
        return None
    total = err = 0
    seen_any = False
    win_start = cutoff.timestamp()
    for fp in root.glob("*/*.jsonl"):
        try:
            if fp.stat().st_mtime < win_start:
                continue
        except Exception:
            continue
        seen_any = True
        try:
            with fp.open(encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"tool_result"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    t = _parse_ts(d.get("timestamp"))
                    if t is None or t < cutoff:
                        continue
                    msg = d.get("message") or {}
                    content = msg.get("content") if isinstance(msg, dict) else None
                    if not isinstance(content, list):
                        continue
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "tool_result":
                            total += 1
                            if b.get("is_error"):
                                err += 1
        except Exception:
            continue
    return (total, err) if seen_any else None


def _judgment_queue_debt() -> dict:
    files = sorted(JUDGMENT_QUEUE.glob("*.json")) if JUDGMENT_QUEUE.exists() else []
    candidates = 0
    oldest = None
    for p in files:
        try:
            t = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            oldest = t if oldest is None or t < oldest else oldest
        except Exception:
            pass
        try:
            j = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if isinstance(j.get("flagged"), int):
            candidates += int(j["flagged"])
        elif isinstance(j.get("candidates"), list):
            candidates += len(j["candidates"])
    new_corrections = sum(1 for r in _read_jsonl(STATE / "corrections.jsonl") if r.get("status") == "new")
    oldest_age_h = None
    if oldest is not None:
        oldest_age_h = max(0.0, (_now() - oldest).total_seconds() / 3600)
    return {
        "queue_files": len(files),
        "candidates": candidates,
        "new_corrections": new_corrections,
        "oldest_age_h": oldest_age_h,
    }


def check_channels(findings: list, live: dict) -> None:
    # Record both channels in the verdict's info field, but only ALERT on Feishu.
    # Discord keeps its own dedicated healthcheck (afk-code-claude2-healthcheck);
    # routine alerts stay in the single Feishu lane (channels unmixed).
    live.update(channel_liveness())
    if not live.get("feishu"):
        findings.append({"level": "yellow", "code": "feishu-down",
                         "msg": "Feishu (feishu@local) inbound consumer not detected — inbound Feishu messages are not delivered."})


def check_scheduler(findings: list) -> None:
    # inbox-drift fires hourly; if its last autonomous-log event is >150 min old,
    # the Tier-7 scheduler itself is likely stalled (Windows disabled the task, etc.).
    last = None
    for r in reversed(_read_jsonl(LOG_PATH, limit=500)):
        if r.get("routine") == "inbox-drift":
            last = _parse_ts(r.get("ts"))
            break
    if last is None:
        findings.append({"level": "yellow", "code": "scheduler-unknown",
                         "msg": "No inbox-drift events in autonomous-log — Tier-7 scheduler health unknown."})
    elif _now() - last > timedelta(minutes=150):
        mins = int((_now() - last).total_seconds() // 60)
        findings.append({"level": "yellow", "code": "scheduler-stalled",
                         "msg": f"Last hourly routine fired {mins} min ago (>150) — Tier-7 scheduler may be stalled."})


def check_cortex(findings: list) -> None:
    # /vault-evolve writes 04 Notes/vault-evolve/YYYY-MM-DD.md daily ~06:00.
    now_local = datetime.now()
    if now_local.hour < 9:  # don't fire before the daily run is due
        return
    today = now_local.strftime("%Y-%m-%d")
    if not (VAULT / "04 Notes" / "vault-evolve" / f"{today}.md").exists():
        findings.append({"level": "yellow", "code": "vault-evolve-missing",
                         "msg": f"No /vault-evolve report for {today} after 09:00 — daily cortex did not run."})


def check_pending(findings: list) -> None:
    pend = VAULT / ".claude" / "_pending"
    sigs = list(pend.glob("*.signal")) if pend.exists() else []
    if not sigs:
        return
    # A CRITICAL-* signal is the all-channels-failed marker — always escalate.
    if any(p.name.startswith("CRITICAL-") for p in sigs):
        findings.append({"level": "red", "code": "critical-signal",
                         "msg": "A CRITICAL-* signal is queued in _pending/ — a prior alert could not be delivered."})
    oldest_age_h = 0.0
    try:
        oldest_age_h = (datetime.now().timestamp() - min(p.stat().st_mtime for p in sigs)) / 3600
    except Exception:
        pass
    if len(sigs) > 12:
        findings.append({"level": "yellow", "code": "pending-backlog",
                         "msg": f"{len(sigs)} unconsumed signals in _pending/ (>12)."})
    elif oldest_age_h > 36:
        findings.append({"level": "yellow", "code": "pending-stale",
                         "msg": f"Oldest _pending signal is {oldest_age_h:.0f}h old (>36h) — signals not being drained."})


def check_corrections(findings: list) -> None:
    cutoff = _now() - timedelta(days=5)
    stuck = 0
    for r in _read_jsonl(STATE / "corrections.jsonl"):
        # The live schema + judgment_distill.py use status "new" for captured-but-
        # unpromoted corrections (NOT "raw" — that term only survives in stale docs).
        if r.get("status") == "new":
            t = _parse_ts(r.get("ts"))
            if t is None or t < cutoff:
                stuck += 1
    if stuck:
        findings.append({"level": "yellow", "code": "corrections-stuck",
                         "msg": f"{stuck} correction(s) stuck unpromoted ('new') >5 days — judgment promotions stalled."})


def _real_grader_verdicts() -> int:
    """Count REAL grader verdicts — excluding the documented `_template` example row."""
    n = 0
    for r in _read_jsonl(GRADER_VERDICTS):
        grader = str(r.get("grader", ""))
        artifact = str(r.get("artifact", ""))
        if grader and not grader.startswith("_") and not artifact.startswith("(example"):
            n += 1
    return n


def check_feedback_surfaces(findings: list) -> None:
    """Verify the learn/enforce feedback surfaces are actually WRITTEN to — not just
    configured. Pulse historically checked that organs FIRE but never that their
    feedback surfaces gained rows, so an all-template grader log or a
    promotion->prediction contract gap was invisible to the very system built to
    catch 'configured != working'. This closes that blind spot.
      (a) promotion->prediction contract: every promoted correction needs a row.
      (b) grader feedback surface must carry at least one real verdict."""
    promoted = sum(1 for r in _read_jsonl(CORRECTIONS) if r.get("status") == "promoted")
    pred_rows = sum(1 for r in _read_jsonl(PROMOTION_PREDICTIONS) if r.get("id"))
    if promoted > pred_rows:
        findings.append({"level": "yellow", "code": "prediction-contract-drift",
                         "msg": (f"promotion->prediction contract drift: {promoted} promoted "
                                 f"correction(s) but {pred_rows} prediction row(s) — "
                                 f"{promoted - pred_rows} promotion(s) have no testable prediction."),
                         "metrics": {"promoted": promoted, "predictions": pred_rows}})
    if GRADER_VERDICTS.exists() and _real_grader_verdicts() == 0:
        findings.append({"level": "yellow", "code": "grader-surface-unwritten",
                         "msg": ("grader-verdicts.jsonl carries no real verdicts (template only) — "
                                 "enforce-layer feedback is configured but never written; graders "
                                 "may be running in-session without appending their VERDICT-LOG.")})


def check_structure_drift(findings: list) -> None:
    """Vault container-structure drift (Phase 0 of the structure loop): numbering
    collisions, project CLAUDE.md documenting non-existent folders, hand-maintained
    folder maps, and orphan dirs. Generated/derived — the structure analog of the
    feedback-surface check. Cheap scoped scan; never blocks pulse."""
    try:
        import structure_graph
        graph = structure_graph.scan()
    except Exception:
        return
    fs = graph.get("findings", [])
    if not fs:
        return
    s = graph.get("summary", {})
    parts = ", ".join(f"{k}:{v}" for k, v in s.items())
    findings.append({"level": "yellow", "code": "structure-drift",
                     "msg": (f"Vault structure drift: {len(fs)} finding(s) — {parts}. "
                             "Run structure_graph.py for detail (Phase 0 sense-only; reorg stays human-gated)."),
                     "metrics": s})


def check_bootstrap_drift(findings: list) -> None:
    """Recovery-baseline drift: OUT-OF-VAULT global hooks (~/.claude/hooks) vs the in-vault
    bootstrap copies. A stale mirror = false recovery confidence (the brief deploy-gap).
    Cheap file-compare; never blocks pulse."""
    try:
        import bootstrap_lint
        s = bootstrap_lint.scan()
    except Exception:
        return
    if len(s.get("drift", [])) + len(s.get("unmirrored", [])):
        findings.append({"level": "yellow", "code": "bootstrap-drift",
                         "msg": (f"Recovery baseline drift: {len(s['drift'])} hook(s) drifted, "
                                 f"{len(s['unmirrored'])} unmirrored vs ~/.claude/hooks - out-of-vault "
                                 "recovery copy stale. Run routines/bootstrap_lint.py --sync."),
                         "metrics": {"drift": s["drift"], "unmirrored": s["unmirrored"]}})


def check_learning_debt(findings: list) -> None:
    debt = _judgment_queue_debt()
    q = debt["queue_files"]
    c = debt["candidates"]
    n = debt["new_corrections"]
    age = debt["oldest_age_h"]
    age_txt = f"{age:.0f}h" if age is not None else "n/a"
    neg, pos = _new_correction_polarity()
    mix = f" [polarity: {neg} corrective / {pos} positive]" if n else ""
    msg = (
        f"Learning loop debt: {q} judgment queue file(s), ~{c} candidate(s), "
        f"{n} new correction(s){mix}, oldest {age_txt}. Extract genuine judgment events; promotion remains human-reviewed."
    )
    if n and pos == 0:
        msg += (" 0 positive — discovery signal not being captured; the loop is patching errors only. "
                "Log unprompted catches as polarity:positive (see 09 Rules/discovery-pass).")
    if q > LEARNING_DEBT_RED_QUEUE or c > LEARNING_DEBT_RED_CANDIDATES or (age is not None and age > LEARNING_DEBT_RED_AGE_H):
        findings.append({"level": "red", "code": "learning-loop-debt", "msg": msg, "metrics": debt})
    elif (
        q > LEARNING_DEBT_YELLOW_QUEUE
        or c > LEARNING_DEBT_YELLOW_CANDIDATES
        or n >= LEARNING_DEBT_NEW_CORRECTIONS
        or (age is not None and age > LEARNING_DEBT_YELLOW_AGE_H)
    ):
        findings.append({"level": "yellow", "code": "judgment-queue-backlog", "msg": msg, "metrics": debt})


def check_error_rate(findings: list) -> None:
    cutoff = _now() - timedelta(hours=24)
    counts = _transcript_error_counts(cutoff)
    source = "transcript"
    if counts is None:
        # Fallback for runtimes without CC transcripts. NB: usage.jsonl structurally
        # under-reports — PostToolUse never sees failures here — so this branch is
        # best-effort only and will read ~0% on a pure-CC box.
        total = err = 0
        for r in _read_jsonl(STATE / "usage.jsonl"):
            t = _parse_ts(r.get("ts"))
            if t is None or t < cutoff:
                continue
            total += 1
            if r.get("ok") is False:
                err += 1
        source = "usage"
    else:
        total, err = counts
    if total >= 20 and err / total > 0.15:
        findings.append({"level": "yellow", "code": "error-rate-high",
                         "msg": f"Tool error rate {err}/{total} ({100 * err / total:.0f}%) in last 24h (>15%, src={source})."})


# Shared stopword list (coherence-review fix — kills the private copy). Fail-safe to a local set so
# this LIVE pulse cron can never break on a shared-spine import error. Tokenizer regex stays local.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "_eval-fixtures"))
try:
    import harness_common as _H
    _TOKEN_STOP = set(_H.STOPWORDS)
except Exception:
    _TOKEN_STOP = {"the", "a", "an", "to", "of", "and", "or", "as", "is", "it", "in",
                   "on", "for", "with", "that", "this", "be", "by", "our", "we", "not",
                   "but", "than", "then", "more", "less", "into", "from", "are", "was"}


def _norm_tokens(text: str) -> set:
    import re as _re
    return {t for t in _re.findall(r"[a-z0-9]{3,}", str(text).lower()) if t not in _TOKEN_STOP}


def _new_correction_polarity() -> "tuple[int, int]":
    """(corrective, positive) split of status==new corrections. Surfaces whether the
    learn loop is taking BOTH-pole signal or only patching errors. polarity 'positive'
    = an endorsed-good judgment call (reinforcement); anything else counts as corrective."""
    neg = pos = 0
    for r in _read_jsonl(CORRECTIONS):
        if r.get("status") != "new":
            continue
        if r.get("polarity") == "positive":
            pos += 1
        else:
            neg += 1
    return neg, pos


def check_promotion_efficacy(findings: list) -> None:
    """Close the back half of the learn loop. A promotion is fire-and-forget unless
    something checks whether the forbidden behavior RECURRED. promotion-predictions.jsonl
    already carries trigger_signature + eval_after; this SENSES (does not auto-verdict —
    that stays human in /vault-evolve):
      (a) predictions past their review date with no verdict → rotting, surface them;
      (b) open predictions whose trigger appears to have recurred in a NEW corrective
          entry since promotion → likely-ineffective → escalation candidate (the only
          honest trigger to move a soft rule toward a grader/gate).
    Conservative match (≥2 shared significant tokens, correction dated after promotion)
    so it under-flags rather than nags."""
    preds = [p for p in _read_jsonl(PROMOTION_PREDICTIONS)
             if isinstance(p, dict) and p.get("verdict") is None and p.get("id")]
    if not preds:
        return
    today = datetime.now().date()
    corrections = _read_jsonl(CORRECTIONS)
    due, ineffective = [], []
    for p in preds:
        pid = p.get("id", "?")
        created = str(p.get("created", ""))
        by = (p.get("eval_after") or {}).get("by", "")
        try:
            if by and datetime.fromisoformat(str(by)).date() <= today:
                due.append(pid)
        except Exception:
            pass
        trig = p.get("trigger_signature") or {}
        sig = _norm_tokens(f"{trig.get('value', '')} {p.get('forbidden_behavior', '')}")
        if not sig:
            continue
        hits = 0
        for c in corrections:
            if c.get("polarity") == "positive":  # endorsements are not recurrences
                continue
            cts = str(c.get("ts", ""))
            if created and cts and cts <= created:  # recurrence must post-date the promotion
                continue
            ctext = f"{c.get('skill', '')} {c.get('artifact', '')} {c.get('why', '')} {c.get('candidate_rule', '')} {c.get('correction', '')}"
            if len(sig & _norm_tokens(ctext)) >= 2:
                hits += 1
        if hits:
            ineffective.append((pid, hits))
    if due:
        findings.append({"level": "yellow", "code": "promotion-due",
                         "msg": (f"{len(due)} promotion prediction(s) past review date, no verdict "
                                 f"({', '.join(due[:4])}). Score passed/failed/unobserved in /vault-evolve "
                                 "so the learn loop closes.")})
    if ineffective:
        tail = ", ".join(f"{pid}×{n}" for pid, n in ineffective[:4])
        findings.append({"level": "yellow", "code": "promotion-ineffective",
                         "msg": (f"{len(ineffective)} promoted rule(s) may be INEFFECTIVE — the forbidden behavior "
                                 f"recurred in new corrections since promotion ({tail}). Escalation candidate "
                                 "(soft→grader→gate); confirm the verdict in /vault-evolve.")})


def check_obsidian_sensor(findings: list) -> None:
    # Obsidian is a sensor/UI layer, not the harness engine. Missing snapshot is
    # informational because Obsidian may be closed; a stale snapshot means the
    # sensor was active but stopped refreshing.
    path = STATE / "obsidian-runtime.json"
    if not path.exists():
        return
    try:
        snap = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        findings.append({"level": "yellow", "code": "obsidian-sensor-invalid",
                         "msg": "obsidian-runtime.json exists but is not valid JSON — Obsidian sensor snapshot unreadable."})
        return
    t = _parse_ts(snap.get("generatedAt"))
    if t is None:
        findings.append({"level": "yellow", "code": "obsidian-sensor-invalid",
                         "msg": "obsidian-runtime.json has no valid generatedAt timestamp."})
        return
    age = _now() - t
    if age > timedelta(minutes=15):
        mins = int(age.total_seconds() // 60)
        findings.append({"level": "yellow", "code": "obsidian-sensor-stale",
                         "msg": f"Obsidian runtime sensor snapshot is {mins} min old (>15); Obsidian API observability may be stale."})


def severity_of(findings: list) -> str:
    if any(f["level"] == "red" for f in findings):
        return "red"
    if any(f["level"] == "yellow" for f in findings):
        return "yellow"
    return "green"


def main() -> int:
    findings: list = []
    live: dict = {"discord": None, "feishu": None}
    checks = (
        lambda: check_channels(findings, live),
        lambda: check_scheduler(findings),
        lambda: check_cortex(findings),
        lambda: check_pending(findings),
        lambda: check_corrections(findings),
        lambda: check_feedback_surfaces(findings),
        lambda: check_structure_drift(findings),
        lambda: check_bootstrap_drift(findings),
        lambda: check_learning_debt(findings),
        lambda: check_promotion_efficacy(findings),
        lambda: check_error_rate(findings),
        lambda: check_obsidian_sensor(findings),
    )
    for check in checks:
        try:
            check()
        except Exception as e:
            log_event(ROUTINE, "error", f"check failed: {e}")

    sev = severity_of(findings)

    prev = {}
    try:
        if VERDICT_PATH.exists():
            prev = json.loads(VERDICT_PATH.read_text(encoding="utf-8"))
    except Exception:
        prev = {}
    prev_sev = prev.get("severity", "green")

    worsened = SEV_RANK.get(sev, 0) > SEV_RANK.get(prev_sev, 0)
    recovered = sev == "green" and prev_sev != "green"
    silent = os.environ.get("PULSE_SILENT") == "1"

    pushed, push_channel = False, None
    if (worsened or recovered) and not silent:
        if recovered:
            msg = "✅ Harness recovered — all checks green again."
        else:
            head = "🔴" if sev == "red" else "🟡"
            detail = "; ".join(f["msg"] for f in findings[:4])
            msg = f"{head} Harness pulse {prev_sev}→{sev}: {detail}"
        if under_run_cap(ROUTINE, MAX_ALERTS_PER_DAY):
            res = notify(ROUTINE, msg)
            pushed, push_channel = res.get("delivered", False), res.get("channel")
        else:
            log_event(ROUTINE, "info", "push skipped — daily alert cap hit")

    verdict = {
        "ts": _now().isoformat(timespec="seconds"),
        "severity": sev,
        "findings": findings,
        "channels": live,
        "pushed": pushed,
        "push_channel": push_channel,
    }
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        VERDICT_PATH.write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log_event(ROUTINE, "error", f"verdict write failed: {e}")

    # ---------- inline autofix on RED (Q3=1; per-finding recipes in pulse_fixes.py) ----------
    # PULSE_AUTOFIX_OFF=1 disables the autofix path (e.g. when iterating manually).
    # SAFE-BY-DEFAULT: pulse_fixes side effects (task restarts, signal writes) are
    # gated on DRY_RUN — run_all_red() acts only when DRY_RUN=0. The default posture
    # (DRY_RUN unset) is detect+alert; recipes log "[DRY] would ...". Set DRY_RUN=0 on
    # the RG-tier7-harness-pulse task to opt into unattended auto-fix.
    autofix_results: list = []
    if sev == "red" and not silent and os.environ.get("PULSE_AUTOFIX_OFF") != "1":
        try:
            import pulse_fixes
            autofix_results = pulse_fixes.run_all_red(verdict)
        except Exception as e:
            log_event(ROUTINE, "error", f"autofix dispatcher failed: {e}")
            autofix_results = [{"ok": False, "code": "dispatcher", "msg": f"{e}"}]
        # Escalate if any recipe failed — same daily cap as the worsening alert so
        # we don't double-spam on a stuck red.
        failed = [r for r in autofix_results if not r.get("ok")]
        if failed and under_run_cap(ROUTINE + "-autofix-escalate", MAX_ALERTS_PER_DAY):
            tail = "; ".join(f"{r.get('code')}: {r.get('msg','')[:80]}" for r in failed[:3])
            notify(ROUTINE, f"⚠️ autofix could not resolve {len(failed)} red finding(s): {tail}")
        # Persist autofix outcomes alongside the verdict so the dashboard can read them.
        try:
            verdict["autofix"] = {
                "ran_at": _now().isoformat(timespec="seconds"),
                "results": autofix_results,
                "failed_count": len(failed),
            }
            VERDICT_PATH.write_text(json.dumps(verdict, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            log_event(ROUTINE, "error", f"verdict re-write failed: {e}")

    log_event(ROUTINE, "alert" if sev != "green" else "info",
              f"pulse={sev} (prev={prev_sev}) findings={len(findings)} pushed={pushed} autofix={len(autofix_results)}",
              severity=sev, findings=len(findings), autofix=len(autofix_results))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        try:
            log_event(ROUTINE, "error", f"fatal: {e}")
        except Exception:
            pass
        sys.exit(0)
