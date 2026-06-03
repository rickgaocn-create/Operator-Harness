---
layer: runtime
type: adapter-contract
created: 2026-05-27
created-by: codex
---

# Runtime Adapter Contract

This folder is the Layer 3 seam. It does not replace `.claude`, the current
engine implementation, or `.claude/_state/harness-manifest.json`, the current
inventory and liveness spine. It only provides runtime-neutral discovery for
machine-specific execution details.

## Boundary

- **Machine layer stays in `.claude`:** skills, agents, evals, routines, state,
  generated maps, and manifests remain where the existing harness expects them.
- **Runtime adapters live at the edge:** Claude Code, Codex, schedulers, hooks,
  and channel bridges call the same resolver before invoking machine-local
  commands.
- **Per-machine values are local:** executable paths, vault location overrides,
  scheduler type, and hook command templates belong in `runtime.local.json`, not
  in tracked skill or rule files.

## Required Primitives

| Primitive | Contract |
|---|---|
| `resolve_runtime` | Return runtime name, platform, vault root, Python command, state paths, and scheduler adapter. |
| `locate_vault` | Prefer `HARNESS_VAULT_ROOT`, then local config, then derive from this file's parent. |
| `run_python` | Provide a command that can execute harness Python scripts on this machine. |
| `locate_state` | Return `.claude/_state` without moving existing state. |
| `run_eval` | Invoke existing eval scripts through the resolved Python command. |
| `rearm_organ` | Run the manifest-declared rearm command after resolving relative paths and runtime command prefixes. |
| `notify` | Keep channel delivery in the existing runtime/channel implementations; the seam only resolves configuration. |

## Rules

- Do not create a second manifest of organs, state files, or docs here.
- Do not move `.claude` components into `.harness` in v1.
- Do not put secrets in tracked files.
- New runtime-facing scripts should import or call `resolve_runtime.py` instead
  of hardcoding `D:\...`, `C:\Users\...\python.exe`, or raw `python .claude/...`.

