---
layer: platform
pillar: Harness engineering · cross-platform
created: 2026-05-26
created-by: claude
---

# Harness Portability Rules · cross-platform by default

> The harness must run on any OS and let a new user onboard onto their own. Windows-dependence is a weakness. Engine and config are separate; the engine is path-agnostic and OS-agnostic.

## Principles

1. **Engine vs config.** The engine (skills, hooks, rules, judgment-loop) is user- and OS-agnostic. Per-user / per-machine specifics — vault location, identity, secrets, interpreter, OS scheduler — live in a thin config the engine *discovers*, never hardcodes.

2. **No new hardcoded paths (the ratchet).** Any script built or touched discovers its paths — derive the vault root from `__file__` (`os.path.dirname` / `parents[n]`), or read one env/config value. Never bake `D:\…`, `{{USER_HOME}}`, or a `python.exe` path into a script. See [[T260526-harness-cross-platform]].

3. **No new OS-locked languages for hooks.** New hooks are cross-platform Python — not PowerShell / `.cmd` / `.sh`. Existing `.ps1` are ported opportunistically, not big-bang.

4. **Vault-resident config + memory.** Anything the harness must carry across machines lives in the **synced vault**, not in non-syncing global dirs (`~/.claude/projects/<slug>/memory/`). A `<slug>` keyed to a machine path does not travel — that's a portability bug, not a store.

5. **Scheduling via a per-OS adapter.** One job manifest; a thin adapter emits launchd / cron / Task Scheduler. No scheduler-specific assumptions baked into the jobs.

## Why

OS-portability and new-user onboarding are the same problem — solved once by separating a path-agnostic engine from discovered config. Backlog + live diagnosis: [[T260526-harness-cross-platform]]. Building principle also logged in `.claude/_state/corrections.jsonl`.

## Verify-arrow on a fresh client (onboarding runbook)

The verify-arrow (the learn-loop's decision-observability ratchet) has ONE client-agnostic front door: `.claude/_eval-fixtures/verify_arrow.py`. It drives all three stages — promotion-prediction schema/due check, the adjudicator verdict-candidate pass, and the grader-verdicts enforce-layer surface — resolving the interpreter and vault root through the existing runtime adapter. No hardcoded paths, no `python.exe`, no PowerShell.

Stand it up on a new machine:

1. **Set machine-specific config** in `.harness/runtime.local.json` (gitignored; copy `.harness/runtime.example.json` as the template). Only what's actually machine-specific:
   - `vault_root` — leave `null` to auto-derive from the repo location, or set an absolute path if the vault lives elsewhere. (Env override: `HARNESS_VAULT_ROOT`.)
   - `python` — leave `null` to let the adapter discover a Python 3.10+ on PATH, or pin an interpreter. (Env override: `HARNESS_PYTHON`.)
   - `jury` block — OPTIONAL. Only needed for the adjudicator's L2 cross-family juror (a non-Claude API). Without it the adjudicator simply abstains — that is NOT a failure. Set `provider`/`base_url`/`model`/`api_key` (or the `BH_JURY_*` env vars). The secret stays only in this gitignored file. The confidential-lane firewall in `adjudicator.py` blocks personal-track predictions from ever egressing to it.
2. **Invoke** (resolve the interpreter once via the adapter, then call the front door):
   ```bash
   python .harness/resolve_runtime.py python                       # -> the interpreter for THIS machine
   <that-python> .claude/_eval-fixtures/verify_arrow.py            # human-readable
   <that-python> .claude/_eval-fixtures/verify_arrow.py --json     # machine-readable
   ```
   Flags: `--predictions` / `--adjudicate` run a single stage; `--refresh` writes the adjudicator verdict cache.
3. **Schedule the weekly closure** (optional, the one cron thread): `.claude/_state/setup_all_schedules.ps1` (Windows) derives its vault root from `$PSScriptRoot` and resolves Python via the adapter — run it as-is. On macOS/Linux there is no PowerShell scheduler yet; invoke the front door from a client/skill or a per-OS cron until the scheduling adapter (Principle 5) is built. **Routines are detectors, not actors** — the runner is called by a client/skill, never by a Tier-7 detector, and it never invokes Claude.

Exit codes: `0` green · `1` a schema failure in the predictions surface · `2` a verify-arrow script missing/unrunnable. The portability ratchet (`.claude/_eval-fixtures/portability.py`) now scans all verify-arrow surfaces, so a re-welded path fails CI.
