#!/usr/bin/env python3
"""Stop hook: Middleware Lite pre-completion checklist.

Blocks only when this session's middleware state shows files were edited and
the required checks/explanation are missing. It intentionally ignores pre-
existing dirty worktree state.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

for stream in (sys.stdin, sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

VAULT_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = VAULT_ROOT / ".claude" / "_state"
EVENTS_PATH = STATE_DIR / "middleware-events.jsonl"
SESSION_DIR = STATE_DIR / "middleware"

# Baseline foundational set (the live gate's historical coverage). The unified source of truth is
# _state/behavior-classes.json (foundational_paths); we UNION the two so the consolidation can
# never WEAKEN this gate, and fall back to the baseline alone on any read error. This is a live
# blocking hook — it must never crash or lose coverage.
_FOUNDATIONAL_BASELINE = {
    "me.md",
    "CLAUDE.md",
    "AGENTS.md",
    "MEMORY.md",
    "GOALS.md",
    "vault-map.md",
    "Skills I Use Daily.md",
    "09 Rules/operator-intents.md",
    "09 Rules/harness-instrumentation.md",
    "09 Rules/harness-surfaces.md",
    "09 Rules/skill-eval-gate.md",
    "09 Rules/memory-os.md",
}


def _load_foundational() -> set:
    """Union of the baseline and the shared taxonomy ceiling. Union (never subset); fail to baseline."""
    foundational = set(_FOUNDATIONAL_BASELINE)
    try:
        data = json.loads((STATE_DIR / "behavior-classes.json").read_text(encoding="utf-8"))
        for p in data.get("foundational_paths", []):
            if isinstance(p, str) and p:
                foundational.add(p)
    except Exception:
        pass
    return foundational


FOUNDATIONAL = _load_foundational()
IGNORED_PREFIXES = (
    ".claude/_state/",
    ".claude/.daily-ingest-queue/",
    "04 Notes/daily notes/2026-05-28-attachments/",
)
NO_TESTS_PAT = re.compile(
    r"(tests?|checks?|validation).{0,80}(not run|did not run|weren't run|were not run|unable to run|couldn't run)|"
    r"(not run|did not run|unable to run|couldn't run).{0,80}(tests?|checks?|validation)",
    re.I | re.S,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def session_key(raw: str) -> str:
    s = (raw or "no-session").strip()
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", s)[:80] or "no-session"


def emit(session: str, severity: str, message: str, file: str = "") -> None:
    rec = {
        "ts": utc_now(),
        "session": session_key(session),
        "kind": "completion_check",
        "severity": severity,
        "message": message,
        "source": "stop-check",
    }
    if file:
        rec["file"] = file
    append_jsonl(EVENTS_PATH, rec)


def load_state(session: str) -> dict | None:
    path = SESSION_DIR / f"{session_key(session)}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def has_no_tests_explanation(transcript_path: str) -> bool:
    if not transcript_path:
        return False
    try:
        p = Path(transcript_path)
        if not p.exists() or p.stat().st_size > 20_000_000:
            return False
        tail = p.read_text(encoding="utf-8", errors="replace")[-250_000:]
        return bool(NO_TESTS_PAT.search(tail))
    except Exception:
        return False


def validation_set(state: dict) -> set[str]:
    vals = set()
    for v in state.get("validations", []) or []:
        kind = v.get("kind")
        target = v.get("target")
        if kind:
            vals.add(str(kind))
            if target:
                vals.add(f"{kind}:{target}")
    return vals


def changed_files(state: dict) -> list[str]:
    files = sorted((state.get("changed_files") or {}).keys())
    return [f for f in files if not any(f.startswith(prefix) for prefix in IGNORED_PREFIXES)]


def packaged_skill_for(rel: str) -> str | None:
    m = re.match(r"\.claude/skills/([^/]+)/", rel)
    if not m:
        return None
    skill = m.group(1)
    if (VAULT_ROOT / ".claude" / "skills" / skill / "skill-package.yaml").exists():
        return skill
    return None


def run_check(args: list[str], label: str, timeout: int = 80) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            [sys.executable] + args,
            cwd=str(VAULT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        out = (r.stdout + "\n" + r.stderr).strip()
        return r.returncode == 0, f"{label}: exit {r.returncode}\n{out[-1200:]}"
    except Exception as e:
        return False, f"{label}: runner error {e}"


def block(reason: str) -> int:
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    print(reason, file=sys.stderr)
    return 2


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    session = payload.get("session_id") or payload.get("sessionId") or "no-session"
    state = load_state(session)
    if not state:
        return 0

    files = changed_files(state)
    if not files:
        emit(session, "ok", "Completion check passed: no tracked file edits.")
        return 0

    vals = validation_set(state)
    transcript = payload.get("transcript_path") or payload.get("transcriptPath") or ""
    explained_no_tests = has_no_tests_explanation(transcript)
    failures: list[str] = []

    foundational_changed = [f for f in files if f in FOUNDATIONAL]
    if foundational_changed:
        ok1, msg1 = run_check([".claude/_eval-fixtures/foundational-lint.py"], "foundational-lint")
        ok2, msg2 = run_check([".claude/_eval-fixtures/verify-load.py"], "verify-load")
        vals.update({"foundational-lint", "verify-load"})
        if not ok1 or not ok2:
            failures.append("Foundational checks failed after editing core files:\n" + msg1 + "\n" + msg2)

    packaged = sorted({s for f in files for s in [packaged_skill_for(f)] if s})
    for skill in packaged:
        ok, msg = run_check([".claude/_eval-fixtures/runner.py", skill], f"skill-eval:{skill}")
        vals.add(f"skill-eval:{skill}")
        if not ok:
            failures.append(msg)

    loop_gates = sorted((state.get("loop_gate_files") or {}).keys())
    if loop_gates and not (vals or explained_no_tests):
        failures.append(
            "LoopDetectionMiddleware saw 5+ edits to: "
            + ", ".join(loop_gates[:5])
            + ". Run a check/test or explicitly explain why validation was not run."
        )

    if not vals and not explained_no_tests:
        failures.append(
            "Files changed in this session but no validation was detected. Run the relevant check/test, "
            "or state clearly in the final answer that validation was not run and why."
        )

    if failures:
        reason = "\n\n".join(failures)
        emit(session, "block", reason, files[0] if files else "")
        return block(reason)

    emit(session, "ok", "Completion check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
