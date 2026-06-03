#!/usr/bin/env python3
"""Resolve runtime-local harness execution details.

This is the thin Layer 3 seam. It discovers machine-specific values without
moving the current engine out of `.claude`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
DERIVED_VAULT = HERE.parent
EXAMPLE = HERE / "runtime.example.json"
LOCAL = HERE / "runtime.local.json"


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], val)
        else:
            out[key] = val
    return out


def _env_runtime() -> str | None:
    explicit = os.environ.get("HARNESS_RUNTIME")
    if explicit:
        return explicit.strip().lower()
    if os.environ.get("CODEX_HOME") or os.environ.get("CODEX_SANDBOX"):
        return "codex"
    if os.environ.get("CLAUDE_PROJECT_DIR") or os.environ.get("CLAUDECODE"):
        return "claude"
    return None


def _vault_root(cfg: dict) -> Path:
    raw = os.environ.get("HARNESS_VAULT_ROOT") or cfg.get("vault_root")
    if raw:
        return Path(raw).expanduser().resolve()
    return DERIVED_VAULT


def _candidate_python(cfg: dict) -> list[str]:
    candidates: list[str] = []
    for raw in (
        os.environ.get("HARNESS_PYTHON"),
        cfg.get("python"),
        sys.executable,
        shutil.which("python"),
        shutil.which("python3"),
        shutil.which("py"),
    ):
        if raw and raw not in candidates:
            candidates.append(str(raw))
    return candidates


def _python_ok(cmd: str) -> bool:
    try:
        result = subprocess.run(
            [cmd, "-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def _python_cmd(cfg: dict) -> str:
    for cmd in _candidate_python(cfg):
        if _python_ok(cmd):
            return cmd
    return sys.executable


def _rel(vault: Path, value: str | None) -> str | None:
    if not value:
        return None
    p = Path(value)
    if not p.is_absolute():
        p = vault / p
    return str(p.resolve())


def resolve() -> dict:
    cfg = _merge(_read_json(EXAMPLE), _read_json(LOCAL))
    runtime = _env_runtime() or str(cfg.get("runtime") or "unknown").lower()
    vault = _vault_root(cfg)
    paths = cfg.get("paths", {}) if isinstance(cfg.get("paths"), dict) else {}
    hooks = cfg.get("hooks", {}) if isinstance(cfg.get("hooks"), dict) else {}
    scheduler = cfg.get("scheduler", {}) if isinstance(cfg.get("scheduler"), dict) else {}

    resolved = {
        "version": 1,
        "runtime": runtime if runtime in {"claude", "codex"} else "unknown",
        "platform": sys.platform,
        "vault_root": str(vault),
        "python": _python_cmd(cfg),
        "state_dir": _rel(vault, paths.get("state_dir") or ".claude/_state"),
        "manifest": _rel(vault, paths.get("manifest") or ".claude/_state/harness-manifest.json"),
        "claude_hooks_dir": _rel(vault, paths.get("claude_hooks_dir") or ".claude/hooks"),
        "codex_hooks_dir": _rel(vault, paths.get("codex_hooks_dir") or ".codex/hooks"),
        "cn_zero_english_guard": _rel(vault, hooks.get("cn_zero_english_guard") or ".claude/hooks/cn-zero-english-guard.py"),
        "codex_cn_zero_english_guard": _rel(vault, hooks.get("codex_cn_zero_english_guard") or ".codex/hooks/cn-zero-english-guard.py"),
        "scheduler_adapter": scheduler.get("adapter") or "auto",
        "windows_setup": _rel(vault, scheduler.get("windows_setup") or ".claude/routines/_setup.ps1"),
    }
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("field", nargs="?", help="Field to print, e.g. python, vault-root, state-dir")
    parser.add_argument("--json", action="store_true", help="Print all resolved values as JSON")
    args = parser.parse_args()

    data = resolve()
    aliases = {
        "vault-root": "vault_root",
        "state-dir": "state_dir",
        "runtime": "runtime",
        "python": "python",
        "manifest": "manifest",
        "codex-cn-guard": "codex_cn_zero_english_guard",
        "claude-cn-guard": "cn_zero_english_guard",
    }
    if args.json or not args.field:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    key = aliases.get(args.field, args.field.replace("-", "_"))
    if key not in data:
        print(f"unknown field: {args.field}", file=sys.stderr)
        return 2
    print(data[key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
