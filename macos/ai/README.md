# Local AI layer (Apple Silicon)

The Mac's structural advantage over the Windows harness: **free, private, offline on-device inference.** This layer routes the harness's cheap/high-frequency ops to a local model and reserves cloud Opus for judgment-heavy work — fixing the per-session cost (≈$0.33 floor, $1.30/forwardable, 76K context tax) the cloud-only harness pays, and unlocking gates that were too costly to run on cloud (e.g. fresh-context `localize-cn`).

## Components

| File | Role |
|---|---|
| `local_llm.py` | dependency-free client (stdlib urllib). Backends: OpenAI-compatible server, Ollama, or `mock` for tests. |
| `router.py` | task-class → tier. Cheap tasks (residue-scan, classify, triage, distill-draft, success-mine, ocr-postprocess, summarize-short) run **local**; judgment tasks (biz-critic, strategy, forwardable, best-of-n) **defer to cloud**. |
| `residue_scan.py` | the `localize-cn` CN-residue gate: deterministic denylist (always) + free local-LLM semantic pass. Exit 2 = flagged. |
| `ocr.py` | on-device Vision OCR (pyobjc) → partial WeChat recovery + image-clipping capture. |

## Pick a backend (any one)

**Ollama (simplest):**
```bash
brew install ollama && ollama serve &
ollama pull qwen2.5:3b
export LOCAL_LLM_URL=http://127.0.0.1:11434 LOCAL_LLM_MODEL=qwen2.5:3b LOCAL_LLM_BACKEND=ollama
```

**MLX (native Apple Silicon, fastest):**
```bash
pip3 install mlx-lm
python3 -m mlx_lm.server --model mlx-community/Qwen2.5-3B-Instruct-4bit --port 8080 &
export LOCAL_LLM_URL=http://127.0.0.1:8080/v1 LOCAL_LLM_MODEL=Qwen2.5-3B-Instruct-4bit
```

**Apple Foundation Models (macOS 26+, system model, zero install):** the on-device system LLM has no HTTP/CLI surface — wrap it in a tiny Swift binary that exposes `/chat/completions` on localhost, then point `LOCAL_LLM_URL` at it. Stub + entitlements notes to come; the router treats it as just another OpenAI-compatible backend.

## Wire the harness through it

- **localize-cn gate** (the fresh-context check declined on cloud cost): `python3 ai/residue_scan.py --file <artifact>` → exit 2 blocks. Add as a PreToolUse matcher on CN artifacts, or call from the localize-cn skill.
- **Any cheap op**: `echo "<text>" | python3 ai/router.py --task classify` → `{tier, result|defer}`. If `defer`, the caller runs cloud.
- **Probe**: `python3 ../native/harness.py status` shows backend + availability.

Everything degrades safely: if no local model is reachable, `residue_scan` still runs its regex layer and `router` returns `defer` so cloud handles it. Nothing breaks when the model is off.
