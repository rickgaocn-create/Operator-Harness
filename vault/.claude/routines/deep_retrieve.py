#!/usr/bin/env python3
"""deep_retrieve.py — Tier-2 deep retrieval for the retrieval-scheduler (09 Rules/retrieval-scheduler).

The cost-bearing tier the scheduler escalates to only on a trigger (unfamiliar entity / specifics /
own-work-factual / multi-domain). v1 is a dependency-free **keyword / term-density** retriever over
the vault markdown (reliable, no model needed). A **semantic** backend over `.smart-env`
(Smart Connections embeddings) is pluggable: the stored note-vectors are on disk, so the only
missing piece is a *query embedder* — wired via BH_EMBED_PROVIDER (falls back to keyword until then,
same stub discipline as the adjudicator jury). READ-ONLY — no writes, no autonomy.

  python deep_retrieve.py "<query>" [--k 6] [--semantic]
"""
from __future__ import annotations
import argparse, io, os, re, sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # routines -> .claude -> {{USER_NAME}}
SKIP_DIRS = {".git", ".smart-env", ".obsidian", ".trash", "node_modules", "__pycache__"}
MAX_BYTES = 200_000   # skip very large files
# Shared stopword list (coherence-review fix — kills the private copy). Tokenizer regex below stays
# purpose-tuned for bilingual retrieval. Fail-safe to a local set if the shared spine is unavailable.
sys.path.insert(0, os.path.join(VAULT, ".claude", "_eval-fixtures"))
try:
    import harness_common as _H
    _STOP = set(_H.STOPWORDS)
except Exception:
    _STOP = {"the", "a", "an", "to", "of", "and", "or", "as", "is", "it", "in", "on", "for", "with",
             "that", "this", "be", "by", "我", "的", "了", "是", "在", "和", "what", "how", "do", "my"}


def _terms(q: str) -> list:
    return [t for t in re.findall(r"[A-Za-z0-9]{2,}|[一-鿿]{2,}", q.lower()) if t not in _STOP]


def _iter_md():
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".md"):
                p = os.path.join(root, fn)
                try:
                    if os.path.getsize(p) <= MAX_BYTES:
                        yield p
                except OSError:
                    pass


def _snippet(text: str, terms: list, width: int = 120) -> str:
    low = text.lower()
    for t in terms:
        i = low.find(t)
        if i >= 0:
            s = max(0, i - width // 2)
            return re.sub(r"\s+", " ", text[s:s + width]).strip()
    return re.sub(r"\s+", " ", text[:width]).strip()


def keyword_search(query: str, k: int) -> list:
    terms = _terms(query)
    if not terms:
        return []
    out = []
    for p in _iter_md():
        try:
            text = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        low = text.lower()
        rel = os.path.relpath(p, VAULT).replace("\\", "/")
        rell = rel.lower()
        score = 0
        for t in terms:
            score += low.count(t)
            if t in rell:            # filename match = strong signal
                score += 8
        # first-heading bonus
        head = (text[:200].lower())
        score += sum(3 for t in terms if t in head)
        if score:
            out.append((score, rel, _snippet(text, terms)))
    out.sort(key=lambda r: r[0], reverse=True)
    return out[:k]


def semantic_search(query: str, k: int) -> list | None:
    """Pluggable: cosine over `.smart-env` note-vectors once a query embedder is configured
    (BH_EMBED_PROVIDER). Vectors are already on disk; only the query embedding is missing.
    Returns None (-> caller falls back to keyword) until wired — no same-path guessing."""
    if not os.environ.get("BH_EMBED_PROVIDER"):
        return None
    # Wiring point: embed `query`, load .smart-env/**/*.ajson vectors, cosine top-k.
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--semantic", action="store_true", help="prefer the .smart-env semantic backend (falls back to keyword if unconfigured)")
    args = ap.parse_args()
    results, mode = None, "keyword"
    if args.semantic:
        results = semantic_search(args.query, args.k)
        mode = "semantic" if results is not None else "keyword (semantic backend not configured)"
    if results is None:
        results = keyword_search(args.query, args.k)
    print(f"deep-retrieve [{mode}] — top {len(results)} for: {args.query!r}\n")
    for score, rel, snip in results:
        print(f"  [{score:>4}] {rel}")
        print(f"         …{snip}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
