#!/usr/bin/env python3
"""Dependency-free local-LLM client for the mac harness (stdlib only).

The point: Apple Silicon can run a capable small model locally for free/private/offline, so the
harness can stop paying cloud Opus for high-frequency cheap ops (residue scans, classification,
triage, distillation drafts). This module exposes one call — complete() — over a pluggable backend.

Backends (auto-detected via env, in order):
  1. openai   — any OpenAI-compatible local server: LM Studio, `mlx_lm.server`, llama.cpp server.
                Set LOCAL_LLM_URL (e.g. http://127.0.0.1:8080/v1) + LOCAL_LLM_MODEL.
  2. ollama   — native Ollama (LOCAL_LLM_URL=http://127.0.0.1:11434, LOCAL_LLM_MODEL=qwen2.5:3b).
  3. mock     — deterministic echo for tests (LOCAL_LLM_BACKEND=mock). No network.
Apple Foundation Models (on-device system model, macOS 26+) has no CLI/HTTP surface — drive it via
a tiny Swift helper and point this client at it through a localhost shim; see ai/README.md.

No third-party deps: pure urllib + json so it runs under the stock python3 the harness already uses.
"""
import json, os, sys, urllib.request, urllib.error

DEFAULT_OPENAI_URL = "http://127.0.0.1:8080/v1"
OLLAMA_URL = "http://127.0.0.1:11434"


def _backend():
    b = os.environ.get("LOCAL_LLM_BACKEND", "").lower()
    if b:
        return b
    url = os.environ.get("LOCAL_LLM_URL", "")
    if "11434" in url or "ollama" in url:
        return "ollama"
    return "openai"


def _http_json(url, payload, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def available(timeout=2):
    """Cheap reachability probe so callers can fall back to cloud/regex when no model is up."""
    backend = _backend()
    if backend == "mock":
        return True
    try:
        if backend == "ollama":
            base = os.environ.get("LOCAL_LLM_URL", OLLAMA_URL)
            urllib.request.urlopen(base + "/api/tags", timeout=timeout)
        else:
            base = os.environ.get("LOCAL_LLM_URL", DEFAULT_OPENAI_URL)
            urllib.request.urlopen(base.rstrip("/") + "/models", timeout=timeout)
        return True
    except Exception:
        return False


def complete(prompt, system="", max_tokens=512, temperature=0.0, timeout=60):
    """Return the model's text completion. Raises RuntimeError if the backend is unreachable."""
    backend = _backend()
    model = os.environ.get("LOCAL_LLM_MODEL", "qwen2.5-3b-instruct")

    if backend == "mock":
        # deterministic, inspectable echo for unit tests
        return json.dumps({"_mock": True, "system": system[:60], "prompt": prompt[:80]})

    try:
        if backend == "ollama":
            base = os.environ.get("LOCAL_LLM_URL", OLLAMA_URL)
            out = _http_json(base.rstrip("/") + "/api/generate", {
                "model": model, "prompt": (system + "\n\n" + prompt) if system else prompt,
                "stream": False, "options": {"temperature": temperature, "num_predict": max_tokens},
            }, timeout)
            return (out.get("response") or "").strip()
        # openai-compatible
        base = os.environ.get("LOCAL_LLM_URL", DEFAULT_OPENAI_URL)
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
        out = _http_json(base.rstrip("/") + "/chat/completions", {
            "model": model, "messages": msgs, "temperature": temperature, "max_tokens": max_tokens,
        }, timeout)
        return (out["choices"][0]["message"]["content"] or "").strip()
    except urllib.error.URLError as e:
        raise RuntimeError(f"local LLM unreachable ({backend}): {e}")


def complete_json(prompt, system="", max_tokens=512, timeout=60):
    """complete() + best-effort JSON extraction (local models often wrap JSON in prose/fences)."""
    raw = complete(prompt, system=system, max_tokens=max_tokens, timeout=timeout)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1] if "```" in raw[3:] else raw.strip("`")
        raw = raw[4:] if raw.lower().startswith("json") else raw
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw[start:end + 1])
        except Exception:
            pass
    return {"_unparsed": raw}


if __name__ == "__main__":
    # quick manual probe:  echo "你好 backlog" | python3 local_llm.py "find english residue"
    sys_prompt = sys.argv[1] if len(sys.argv) > 1 else ""
    user = sys.stdin.read() if not sys.stdin.isatty() else "ping"
    print(f"backend={_backend()} available={available()}")
    if available():
        print(complete(user, system=sys_prompt, max_tokens=128))
