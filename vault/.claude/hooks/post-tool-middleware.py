#!/usr/bin/env python3
"""PostToolUse middleware multiplexer for the {{USER_NAME}} harness.

Owns the lightweight post-tool layer:
- append the existing usage telemetry record to `.claude/_state/usage.jsonl`
- track per-session edit counts by file
- emit loop-detection events to `.claude/_state/middleware-events.jsonl`

This hook is intentionally lossy. It must never fail the tool call it observes.
"""
from __future__ import annotations

import json
import re
import sys
import time
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
USAGE_PATH = STATE_DIR / "usage.jsonl"
EVENTS_PATH = STATE_DIR / "middleware-events.jsonl"
SESSION_DIR = STATE_DIR / "middleware"

EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
VALIDATION_HINTS = (
    ("foundational-lint", re.compile(r"foundational-lint\.py", re.I)),
    ("verify-load", re.compile(r"verify-load\.py", re.I)),
    ("portability", re.compile(r"portability\.py", re.I)),
    ("skill-surface-lint", re.compile(r"skill_surface_lint\.py", re.I)),
    ("generic-test", re.compile(r"\b(pytest|npm\s+test|pnpm\s+test|yarn\s+test|cargo\s+test)\b", re.I)),
)
SKILL_EVAL_RE = re.compile(r"runner\.py(?:[^\r\n;&|]*?)(?:\s+([a-z0-9_-]+))?(?:\s|$)", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def session_key(raw: str) -> str:
    s = (raw or "no-session").strip()
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", s)[:80] or "no-session"


def session_file(session: str) -> Path:
    return SESSION_DIR / f"{session_key(session)}.json"


def load_session(session: str) -> dict:
    path = session_file(session)
    if not path.exists():
        return {"session": session_key(session), "changed_files": {}, "validations": [], "loop_gate_files": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("changed_files", {})
            data.setdefault("validations", [])
            data.setdefault("loop_gate_files", {})
            return data
    except Exception:
        pass
    return {"session": session_key(session), "changed_files": {}, "validations": [], "loop_gate_files": {}}


def save_session(session: str, state: dict) -> None:
    path = session_file(session)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def rel_path(raw: str) -> str:
    if not raw:
        return ""
    text = str(raw).strip().replace("\\", "/")
    try:
        p = Path(raw).expanduser()
        if p.is_absolute():
            try:
                return p.resolve().relative_to(VAULT_ROOT.resolve()).as_posix()
            except Exception:
                return text
    except Exception:
        pass
    return text


def file_target(tool_input: dict) -> str:
    for key in ("file_path", "path", "notebook_path"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            return val[:300]
    cmd = tool_input.get("command")
    if isinstance(cmd, str):
        return cmd[:300]
    return ""


def maybe_probe(raw: str) -> None:
    """One-shot schema diagnostic. When `_state/_payload-probe.on` exists, append the
    raw PostToolUse payload (size-capped) to `_payload-probe.jsonl` so the REAL Claude
    Code schema — especially the tool-error shape — can be inspected, then patched into
    is_success(). Off by default; `touch _state/_payload-probe.on` to arm, delete to
    disarm. Never raises (PostToolUse is lossy by contract)."""
    try:
        if not (STATE_DIR / "_payload-probe.on").exists():
            return
        probe = STATE_DIR / "_payload-probe.jsonl"
        if probe.exists() and probe.stat().st_size > 300_000:
            return
        append_jsonl(probe, {"ts": utc_now(), "raw": raw[:4000]})
    except Exception:
        pass


def is_success(payload: dict) -> tuple[bool, str]:
    resp = payload.get("tool_response") or payload.get("toolResponse") or {}
    # Claude Code records tool errors as a tool_result block with is_error:true; the
    # PostToolUse payload surfaces that as tool_response.is_error (dict shape) OR, for
    # tools whose response is a string/list, as a top-level isError/is_error flag.
    # Cover both so a failed Read/Bash is logged ok:false instead of silently passing.
    if isinstance(resp, dict):
        if resp.get("isError") or resp.get("is_error") or resp.get("success") is False:
            return False, str(resp.get("error") or resp.get("message") or resp.get("content") or "")[:240]
    if payload.get("isError") or payload.get("is_error") or payload.get("success") is False:
        return False, str(payload.get("error") or payload.get("message") or "")[:240]
    return True, ""


def emit_event(session: str, kind: str, severity: str, message: str, file: str = "", source: str = "post-tool-middleware") -> None:
    rec = {
        "ts": utc_now(),
        "session": session_key(session),
        "kind": kind,
        "severity": severity,
        "message": message,
        "source": source,
    }
    if file:
        rec["file"] = file
    append_jsonl(EVENTS_PATH, rec)


def record_usage(payload: dict, tool: str, tool_input: dict, ok: bool, err: str, started_ns: int) -> None:
    rec = {
        "ts": utc_now(),
        "session": session_key(payload.get("session_id") or payload.get("sessionId") or "")[:12],
        "tool": tool,
        "file": file_target(tool_input),
        "ok": ok,
        "ms": int((time.monotonic_ns() - started_ns) / 1_000_000),
    }
    if err:
        rec["err"] = err
    append_jsonl(USAGE_PATH, rec)


def validation_hits(text: str) -> list[dict]:
    hits: list[dict] = []
    if not text:
        return hits
    m = SKILL_EVAL_RE.search(text)
    if m:
        target = m.group(1) or "all"
        if target.startswith("--"):
            target = "all"
        hits.append({"kind": "skill-eval", "target": target})
    for name, pattern in VALIDATION_HINTS:
        if pattern.search(text):
            hits.append({"kind": name, "target": "all"})
    return hits


def track_session(payload: dict, tool: str, tool_input: dict, ok: bool) -> None:
    session = payload.get("session_id") or payload.get("sessionId") or "no-session"
    state = load_session(session)
    now = utc_now()

    scan_text = json.dumps(tool_input, ensure_ascii=False)
    for hit in validation_hits(scan_text):
        hit["ts"] = now
        state["validations"].append(hit)

    if ok and tool in EDIT_TOOLS:
        target = rel_path(file_target(tool_input))
        if target and not target.startswith(".claude/_state/"):
            info = state["changed_files"].setdefault(target, {"edit_count": 0})
            info["edit_count"] = int(info.get("edit_count", 0)) + 1
            info["last_ts"] = now
            count = info["edit_count"]
            if count == 3:
                emit_event(
                    session,
                    "loop_detection",
                    "warn",
                    "Third edit to the same file this session; reconsider, test, or step back.",
                    target,
                )
            elif count == 5:
                state["loop_gate_files"][target] = {"count": count, "ts": now}
                emit_event(
                    session,
                    "loop_detection",
                    "gate_hint",
                    "Fifth edit to the same file this session; run/verify before claiming done.",
                    target,
                )

    save_session(session, state)


def main() -> None:
    started_ns = time.monotonic_ns()
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        payload = json.loads(raw)
        maybe_probe(raw)
        tool = payload.get("tool_name") or payload.get("toolName") or ""
        tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
        if not isinstance(tool_input, dict):
            tool_input = {}
        ok, err = is_success(payload)
        record_usage(payload, tool, tool_input, ok, err, started_ns)
        track_session(payload, tool, tool_input, ok)
    except Exception:
        # PostToolUse instrumentation is lossy by contract.
        pass


if __name__ == "__main__":
    main()
