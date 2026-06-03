"""Shared utilities for autonomous routines. Logging, dry-run, max-runs-per-day caps."""
from __future__ import annotations

import io
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = Path(__file__).resolve().parents[2]
LOG_PATH = VAULT / ".claude" / "_state" / "autonomous-log.jsonl"
LAST_RUN_PATH = VAULT / ".claude" / "_state" / "autonomous-last-run.json"
PENDING_DIR = VAULT / ".claude" / "_pending"


def is_dry_run() -> bool:
    """All routines support DRY_RUN=1 env. Default behavior: notification-only mode (Phase 4 launch posture)."""
    return os.environ.get("DRY_RUN", "1") != "0"


def under_run_cap(routine: str, max_per_day: int) -> bool:
    """Check if we've already run today >= max_per_day times. Updates counter."""
    today = date.today().isoformat()
    state: dict = {}
    if LAST_RUN_PATH.exists():
        try:
            state = json.loads(LAST_RUN_PATH.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    key = f"{routine}:{today}"
    count = state.get(key, 0)
    if count >= max_per_day:
        return False
    state[key] = count + 1
    LAST_RUN_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAST_RUN_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return True


def log_event(routine: str, level: str, message: str, **extras) -> None:
    """Append JSONL event. level ∈ {info, alert, error}. Never raises."""
    try:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "routine": routine,
            "level": level,
            "message": message[:500],
            "dry_run": is_dry_run(),
        }
        record.update(extras)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        # Echo to stdout for interactive runs
        if sys.stdout.isatty() or os.environ.get("ROUTINE_ECHO") == "1":
            tag = {"info": "ℹ", "alert": "⚠", "error": "✗"}.get(level, "·")
            print(f"{tag} [{routine}] {message}")
    except Exception:
        pass  # never fail the routine on logging issues


def notify_feishu(routine: str, message: str) -> bool:
    """Best-effort notification via lark-cli if available. Returns success.

    Back-compat path for the original notification-only routines (inbox-drift /
    pre-trip / eod-snapshot). Preserves the DRY_RUN gate + per-call logging they
    were built against. New routines that want channel-aware escalation should
    call notify() instead."""
    if is_dry_run():
        log_event(routine, "info", f"[DRY] would notify: {message}")
        return True
    ok, detail = _send_feishu(message)
    log_event(
        routine, "info" if ok else "error",
        f"notified: {message[:100]}" if ok else f"notify FAILED: {detail}",
    )
    return ok


# --- alert delivery (Feishu / morty lane) -----------------------------------
# notify() is the notification path for detector routines. Per
# 09 Rules/autonomous-routines.md Hard Rule 1, notification-only routines may
# skip the DRY_RUN gate (they never write vault content), so notify() delivers
# for real. It stays in ONE channel — the Feishu morty lane the routines already
# use — and never crosses to Discord (Discord keeps its own healthcheck). If the
# Feishu send fails, it drops a CRITICAL signal so the next SessionStart leads
# with the failure.


def _feishu_target() -> "str | None":
    """Operator's Feishu open_id = the allowlisted DM user. Single source of truth
    is the Feishu access.json; HARNESS_PULSE_FEISHU_USER overrides."""
    env = os.environ.get("HARNESS_PULSE_FEISHU_USER", "").strip()
    if env:
        return env
    try:
        access = json.loads(
            (Path.home() / ".claude" / "channels" / "feishu" / "access.json").read_text(encoding="utf-8")
        )
        allow = access.get("allowFrom") or []
        if allow:
            return allow[0]
    except Exception:
        pass
    return None


def _send_feishu(message: str) -> "tuple[bool, str]":
    """Raw Feishu DM via lark-cli (morty bot -> operator open_id). No gate, no
    logging — caller logs. Outbound send works even when the *inbound* consumer
    is down. Returns (ok, detail).

    NB: the command is `im +messages-send`. The old `+send` shortcut this used to
    call is not a real lark-cli command and silently failed every real send."""
    target = _feishu_target()
    if not target:
        return False, "no feishu target (access.json allowFrom empty / HARNESS_PULSE_FEISHU_USER unset)"
    try:
        import subprocess
        result = subprocess.run(
            ["lark-cli", "--profile", "morty", "im", "+messages-send",
             "--as", "bot", "--user-id", target, "--text", message[:1500]],
            capture_output=True, timeout=15, encoding="utf-8", errors="replace",
        )
        out = result.stdout or ""
        if result.returncode == 0 and '"ok": true' in out:
            return True, "feishu ok"
        return False, f"feishu rc={result.returncode}: {((result.stderr or '') + out)[:200]}"
    except FileNotFoundError:
        return False, "lark-cli not on PATH"
    except Exception as e:
        return False, f"feishu exception: {e}"


def _resolve_system_bin(name: str) -> str:
    # Why absolute paths: when this module runs from a child process spawned by a
    # parent whose PATH has unexpanded %SystemRoot% literals (Git Bash, Obsidian-
    # launched-from-Git-Bash), bare 'wmic'/'powershell' lookups fail silently and
    # _process_cmdlines returns []. That false-negative cascades into pulse writing
    # a phantom 'feishu-down' finding while the consumer is alive. Resolve to the
    # well-known absolute path via SystemRoot env (set on every Windows session).
    root = os.environ.get("SystemRoot") or os.environ.get("SYSTEMROOT") or r"C:\Windows"
    candidates = {
        "wmic": [os.path.join(root, "System32", "Wbem", "wmic.exe")],
        "powershell": [os.path.join(root, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")],
    }.get(name, [])
    for p in candidates:
        if os.path.isfile(p):
            return p
    return name  # fall back to PATH lookup


def _process_cmdlines() -> list[str]:
    """Command lines of running node.exe / lark-cli.exe processes (Windows).
    Mirrors check-channel-state.ps1: wmic primary, PowerShell CIM fallback."""
    import subprocess
    wmic = _resolve_system_bin("wmic")
    ps = _resolve_system_bin("powershell")
    out: list[str] = []
    for name in ("node.exe", "lark-cli.exe"):
        try:
            r = subprocess.run(
                [wmic, "process", "where", f"name='{name}'", "get", "commandline", "/value"],
                capture_output=True, timeout=15, encoding="utf-8", errors="replace",
            )
            for line in (r.stdout or "").splitlines():
                line = line.strip()
                if line.startswith("CommandLine="):
                    out.append(line[len("CommandLine="):])
        except Exception:
            pass
    if out:
        return out
    try:  # wmic gone (Win12+) — fall through to CIM via powershell
        r = subprocess.run(
            [ps, "-NoProfile", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='node.exe' OR Name='lark-cli.exe'\" "
             "| Select-Object -ExpandProperty CommandLine"],
            capture_output=True, timeout=20, encoding="utf-8", errors="replace",
        )
        out = [l for l in (r.stdout or "").splitlines() if l.strip()]
    except Exception:
        pass
    return out


def channel_liveness() -> dict:
    """{discord: bool, feishu: bool} — same classification as check-channel-state.ps1.
    Discord = afk-code-claude2 daemon; Feishu = lark-cli inbound event consumer."""
    cmdlines = _process_cmdlines()
    discord = any("afk-code-claude2" in (c or "") for c in cmdlines)
    feishu = any(
        re.search(r"event\s+consume", c or "")
        and (
            re.search(r"im\.message\.receive", c or "")
            or "lark-cli" in (c or "")
            or re.search(r"larksuite[\\/]cli", c or "")
            or re.search(r"scripts[\\/]run\.js", c or "")
        )
        for c in cmdlines
    )
    return {"discord": discord, "feishu": feishu}


def notify(routine: str, message: str) -> dict:
    """Deliver a detector alert on the Feishu (morty) lane — the channel the
    routines already use. Skips the DRY_RUN gate (Hard Rule 1). Deliberately does
    NOT cross to Discord (Discord keeps its own healthcheck). On send failure,
    drops a CRITICAL signal into _pending/ so the next SessionStart surfaces it.
    Never raises. Returns {delivered, channel}."""
    ok, detail = _send_feishu(message)
    if ok:
        log_event(routine, "info", f"alert delivered via feishu: {message[:80]}")
        return {"delivered": True, "channel": "feishu"}
    try:
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        (PENDING_DIR / f"CRITICAL-{routine}-{stamp}.signal").write_text(
            f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {routine}: "
            f"Feishu alert UNDELIVERED ({detail}) — surface immediately.\n{message}\n",
            encoding="utf-8",
        )
    except Exception:
        pass
    log_event(routine, "error", f"alert UNDELIVERED (feishu: {detail})")
    return {"delivered": False, "channel": None}
