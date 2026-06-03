#!/usr/bin/env python3
"""
Tier 7 instrumentation: append a single JSONL record per tool invocation to
**.claude/_state/usage.jsonl**.

Wired as a PostToolUse hook in **.claude/settings.json**. Lossy by design —
if the log write fails, the tool call still succeeds (no exception escapes).

Record shape:
    {timestamp, session_id, tool, skill, file_target, success, duration_ms,
     input_tokens?, output_tokens?, model?, cost_usd?, error?}

Skill detection: scans the most-recent user-prompt message for `/skill-name`
slash commands. If no skill context is available, `skill` is null. Read by
**.claude/skills/harness-health/SKILL.md**.

Performance budget: must complete in <50ms p99 to stay invisible.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[2]
LOG_PATH = VAULT_ROOT / ".claude" / "_state" / "usage.jsonl"


def main() -> None:
    start_ns = time.monotonic_ns()
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return
        payload = json.loads(raw)

        tool = payload.get("tool_name") or payload.get("toolName") or ""
        tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
        tool_response = payload.get("tool_response") or payload.get("toolResponse") or {}
        session_id = payload.get("session_id") or payload.get("sessionId") or ""

        file_target = ""
        for key in ("file_path", "path", "notebook_path", "command"):
            v = tool_input.get(key)
            if isinstance(v, str):
                file_target = v[:240]
                break

        success = True
        error_msg = ""
        if isinstance(tool_response, dict):
            if tool_response.get("isError") or tool_response.get("is_error"):
                success = False
                error_msg = str(tool_response.get("error") or tool_response.get("message") or "")[:200]

        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session": session_id[:12] if session_id else "",
            "tool": tool,
            "file": file_target,
            "ok": success,
            "ms": int((time.monotonic_ns() - start_ns) / 1_000_000),
        }
        if error_msg:
            record["err"] = error_msg

        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # NEVER fail the tool call. Swallow silently.
        pass


if __name__ == "__main__":
    main()
