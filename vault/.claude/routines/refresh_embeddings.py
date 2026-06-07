#!/usr/bin/env python3
"""refresh_embeddings.py — re-embed the live vault into a harness-owned vector store.

Closes the `.smart-env` freshness gap (stale post-reorg paths + unembedded new files) — feasible
headlessly now that embed_bge.py exists. Walks current vault `.md`, embeds the body (frontmatter
stripped) via the staged bge-micro-v2, and writes `{path, mtime, vec}` to
`.claude/_state/embed/vault-vectors.jsonl`. Incremental (skips files whose mtime is unchanged).

Tier A — regenerable derived state (like the underlays); 0 network, 0 model tokens.
  python refresh_embeddings.py [--limit N] [--rebuild]
"""
from __future__ import annotations
import argparse, glob, io, json, os, re, sys, time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # routines -> .claude -> {{USER_NAME}}
EMBED_DIR = os.path.join(VAULT, ".claude", "_state", "embed")
STORE = os.path.join(EMBED_DIR, "vault-vectors.jsonl")
SKIP_DIRS = {".git", ".smart-env", ".obsidian", ".trash", "node_modules", "__pycache__", ".agents", ".codex"}
MAX_BYTES = 200_000
sys.path.insert(0, EMBED_DIR)
import embed_bge  # noqa: E402  (the staged onnx embedder)

FM = re.compile(r"^---\n.*?\n---\n", re.S)


def _iter_md():
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(root, fn)


def _load_store():
    out = {}
    if os.path.exists(STORE):
        for ln in open(STORE, encoding="utf-8", errors="replace"):
            ln = ln.strip()
            if ln:
                try:
                    r = json.loads(ln)
                    out[r["path"]] = r
                except Exception:
                    pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="embed at most N changed files this run")
    ap.add_argument("--rebuild", action="store_true", help="ignore existing store, re-embed all")
    args = ap.parse_args()
    store = {} if args.rebuild else _load_store()
    t0 = time.time()
    embedded = kept = skipped = 0
    for p in _iter_md():
        rel = os.path.relpath(p, VAULT).replace("\\", "/")
        try:
            mtime = int(os.path.getmtime(p))
            if os.path.getsize(p) > MAX_BYTES:
                skipped += 1
                continue
        except OSError:
            continue
        prev = store.get(rel)
        if prev and prev.get("mtime") == mtime and prev.get("vec"):
            kept += 1
            continue
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        body = FM.sub("", text).strip() or text.strip()
        if len(body) < 1:
            continue
        try:
            vec = embed_bge.embed(body)
        except Exception:
            continue
        store[rel] = {"path": rel, "mtime": mtime, "vec": vec}
        embedded += 1
        if args.limit and embedded >= args.limit:
            break

    # prune entries whose file no longer exists (fix the stale-path problem at the source)
    on_disk = {os.path.relpath(p, VAULT).replace("\\", "/") for p in _iter_md()}
    pruned = [k for k in list(store) if k not in on_disk]
    for k in pruned:
        del store[k]

    with open(STORE, "w", encoding="utf-8") as f:
        for r in store.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"refresh_embeddings: embedded {embedded} · kept {kept} · pruned-stale {len(pruned)} · "
          f"skipped-large {skipped} · total {len(store)} · {time.time()-t0:.1f}s -> {os.path.relpath(STORE, VAULT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
