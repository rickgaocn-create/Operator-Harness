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
import argparse, io, json, os, re, sys

if sys.platform == "win32" and (getattr(sys.stdout, "encoding", "") or "").lower() != "utf-8":
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


SMART_MULTI = os.path.join(VAULT, ".smart-env", "multi")
SMART_MODEL = "TaylorAI/bge-micro-v2"
EMBED_DIR = os.path.join(VAULT, ".claude", "_state", "embed")  # staged onnx model + tokenizer land here


def _load_smart_vectors() -> dict:
    """{vault-rel path: [384 floats]} from Smart Connections' on-disk vectors.
    Each .ajson line is `"smart_sources:<path>": {..., embeddings:{MODEL:{vec:[...]}}},` — the KEY
    contains a colon, so wrap the line as one JSON object instead of splitting on ':'.
    Prefers the harness-owned FRESH store (current paths + new files, written by
    refresh_embeddings.py) over SC's snapshot; falls back to .smart-env if absent."""
    import glob
    fresh = os.path.join(EMBED_DIR, "vault-vectors.jsonl")
    if os.path.exists(fresh):
        out = {}
        for ln in open(fresh, encoding="utf-8", errors="replace"):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
                if r.get("vec") and r.get("path"):
                    out[r["path"]] = r["vec"]
            except Exception:
                continue
        if out:
            return out
    out = {}
    for fp in glob.glob(os.path.join(SMART_MULTI, "*.ajson")):
        try:
            for ln in open(fp, encoding="utf-8", errors="replace"):
                ln = ln.strip().rstrip(",")
                if not ln.startswith('"'):
                    continue
                try:
                    obj = json.loads("{" + ln + "}")
                except Exception:
                    continue
                for _k, v in obj.items():
                    if isinstance(v, dict):
                        vec = (v.get("embeddings") or {}).get(SMART_MODEL, {}).get("vec")
                        p = v.get("path")
                        if vec and p:
                            out[p] = vec
        except OSError:
            continue
    return out


def _embed_query(text: str):
    """384-d query vector matching the on-disk SC embeddings, or None -> keyword fallback.
    Wired when the bge-micro-v2 onnx + tokenizer are staged in EMBED_DIR (onnxruntime is already
    installed). The staged model MUST be the Xenova/bge-micro-v2 export SC used; fidelity is
    verified by embed_bge.selftest() (embed a known note -> cosine vs its stored vec ≈ 1.0)."""
    try:
        sys.path.insert(0, EMBED_DIR)
        import embed_bge  # staged helper; absent until the model is downloaded
        return embed_bge.embed(text)
    except Exception:
        return None


def semantic_search(query: str, k: int, hyde: str | None = None) -> list | None:
    """Cosine over the on-disk .smart-env note-vectors. None (-> keyword) if no embedder staged.
    QMD HyDE graft: if `hyde` (a hypothetical-answer text the caller supplies) is given, embed
    query+hyde so the vector channel matches *answer-shaped* wording, not just the question — the
    text is provided by the caller, so this stays 0-token-local (no extra model call here)."""
    qv = _embed_query((query + "\n" + hyde) if hyde else query)
    if qv is None:
        return None
    try:
        import numpy as np
    except Exception:
        return None
    vecs = _load_smart_vectors()
    if not vecs:
        return None
    paths = list(vecs)
    M = np.asarray([vecs[p] for p in paths], dtype=np.float32)
    M /= (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    q = np.asarray(qv, dtype=np.float32)
    q /= (np.linalg.norm(q) + 1e-9)
    sims = M @ q
    terms = _terms(query)
    out = []
    for i in np.argsort(-sims)[:k]:
        p = paths[i]
        try:
            text = open(os.path.join(VAULT, p), encoding="utf-8", errors="replace").read()
        except OSError:
            text = ""
        out.append((float(sims[i]), p, _snippet(text, terms) if text else ""))
    return out


def rrf_fuse(lists: list, k: int, c: int = 60) -> list:
    """Reciprocal-rank fusion of ranked [(score, path, snippet)] lists — hybrid semantic+keyword.
    Semantic gives concept-recall; keyword gives exact-referent precision (f-corpus-grounding).
    Neither alone."""
    agg, snip = {}, {}
    for lst in lists:
        for rank, (_s, p, sn) in enumerate(lst):
            agg[p] = agg.get(p, 0.0) + 1.0 / (c + rank + 1)
            snip.setdefault(p, sn)
    fused = sorted(((sc, p, snip.get(p, "")) for p, sc in agg.items()), key=lambda r: -r[0])
    return fused[:k]


def taste_rerank(results, query, lam=0.35):
    """B4 — re-rank hybrid results by proximity to the operator's JUDGMENT GRAPH (the taste signal).
    Blends incoming rank with each note's max cosine to the 3 most query-relevant _judgment nodes,
    so notes that resonate with the values/frameworks the operator actually holds rise. Learned, not
    fixed: as the judgment graph evolves (promotions), retrieval taste shifts with it. Falls back to
    the input order if the embedder/vectors are unavailable."""
    try:
        import numpy as np
        qv = _embed_query(query)
        if qv is None or not results:
            return results
        vecs = _load_smart_vectors()
        jnodes = {p: v for p, v in vecs.items() if "09 Rules/_judgment/" in p}
        if not jnodes:
            return results
        q = np.asarray(qv, dtype=np.float32); q /= np.linalg.norm(q) + 1e-9
        jp = list(jnodes)
        JM = np.asarray([jnodes[p] for p in jp], dtype=np.float32); JM /= np.linalg.norm(JM, axis=1, keepdims=True) + 1e-9
        top = [jp[i] for i in np.argsort(-(JM @ q))[:3]]
        TM = np.asarray([jnodes[p] for p in top], dtype=np.float32); TM /= np.linalg.norm(TM, axis=1, keepdims=True) + 1e-9
        scored = []
        for rank, (_s, p, sn) in enumerate(results):
            base = 1.0 / (rank + 1)
            rv = vecs.get(p)
            taste = 0.0
            if rv is not None:
                r = np.asarray(rv, dtype=np.float32); r /= np.linalg.norm(r) + 1e-9
                taste = float(np.max(TM @ r))
            scored.append((base + lam * taste, p, sn))
        scored.sort(key=lambda x: -x[0])
        return scored
    except Exception:
        return results


def _apply_avoid(results: list, avoid: list) -> list:
    """QMD `intent:` negative steering — SOFT-demote (don't drop) results whose path/snippet hits an
    'avoid' term, so near-but-wrong neighbours sink below the genuinely-relevant. Reversible: caller
    trims to k AFTER this, so demoted hits fall off only if better ones exist."""
    av = [a.lower().strip() for a in (avoid or []) if a and a.strip()]
    if not av:
        return results
    keep, sunk = [], []
    for r in results:
        blob = (str(r[1]) + " " + str(r[2])).lower()
        (sunk if any(a in blob for a in av) else keep).append(r)
    return keep + sunk


def retrieve(query: str, k: int = 6, hyde: str | None = None, avoid: list | None = None,
             semantic: bool = False, keyword: bool = False, taste: bool = True) -> list:
    """Unified hybrid retrieval with the QMD grafts. `hyde`: hypothetical-answer text for the vector
    channel. `avoid`: terms to steer away from (near-but-wrong). Reusable entry for context_assemble."""
    over = k * 2 if avoid else k                      # over-fetch so avoid-demotion has room to trim
    kw = [] if semantic else keyword_search(query, over)
    sem = None if keyword else semantic_search(query, over, hyde=hyde)
    if sem and not semantic:
        results = rrf_fuse([sem, kw], over)
    elif sem:
        results = sem
    else:
        results = kw
    results = _apply_avoid(results, avoid)[:k]
    if taste:
        results = taste_rerank(results, (query + " " + hyde) if hyde else query)[:k]
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--semantic", action="store_true", help="prefer the .smart-env semantic backend (falls back to keyword if unconfigured)")
    ap.add_argument("--keyword", action="store_true", help="force keyword-only (skip semantic/hybrid)")
    ap.add_argument("--hyde", default=None, help="QMD HyDE: a hypothetical-answer text to enrich the vector query")
    ap.add_argument("--avoid", default=None, help="QMD intent: comma-separated terms to steer AWAY from (near-but-wrong)")
    ap.add_argument("--no-taste", action="store_true", help="skip the judgment-graph taste rerank")
    args = ap.parse_args()
    avoid = [a for a in (args.avoid or "").split(",") if a.strip()] or None
    results = retrieve(args.query, args.k, hyde=args.hyde, avoid=avoid,
                       semantic=args.semantic, keyword=args.keyword, taste=not args.no_taste)
    mode = "hybrid+grafts" if (not args.keyword and semantic_search(args.query, 1) is not None) else "keyword"
    if args.hyde:
        mode += "+hyde"
    if avoid:
        mode += "+avoid"
    print(f"deep-retrieve [{mode}] — top {len(results)} for: {args.query!r}\n")
    for score, rel, snip in results:
        print(f"  [{float(score):>6.3f}] {rel}")
        print(f"         …{snip}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
