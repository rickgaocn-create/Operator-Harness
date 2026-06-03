#!/usr/bin/env python3
"""Run a harness hook through the runtime resolver."""
from __future__ import annotations

import subprocess
import sys

from resolve_runtime import resolve


HOOKS = {
    "codex-cn-zero-english-guard": "codex_cn_zero_english_guard",
    "claude-cn-zero-english-guard": "cn_zero_english_guard",
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in HOOKS:
        print(f"usage: {sys.argv[0]} <{'|'.join(HOOKS)}>", file=sys.stderr)
        return 2
    data = resolve()
    hook = data[HOOKS[sys.argv[1]]]
    result = subprocess.run(
        [data["python"], hook],
        input=sys.stdin.buffer.read(),
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

