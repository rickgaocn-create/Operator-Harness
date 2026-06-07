#!/usr/bin/env python3
"""context_assemble.py — the one-call context layer for /operate (B5).

Given a task/query, assembles the OPTIMAL context bundle within a token budget by CONSOLIDATING
the harness's retrievers (it adds no new retrieval — it orchestrates the existing ones, per the
budget gate):
  - relevant notes   : hybrid semantic+keyword (deep_retrieve)
  - the method        : the matching composition skeleton (method_retrieve)
  - the judgment      : the most relevant value/framework nodes (semantic, scoped to _judgment)
  - (grounding)       : source-graph entities/claims when forwardable (underlays, if present)

0 model tokens (the embedder is local). Read-only. Falls back gracefully if the embedder/store
or underlays are absent.

  python context_assemble.py "<task>" [--budget 2200] [--json]
"""
from __future__ import annotations
import argparse, io, json, os, sys
from pathlib import Path

if sys.platform == "win32" and (getattr(sys.stdout, "encoding", "") or "").lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(VAULT / ".claude" / "routines"))
sys.path.insert(0, str(VAULT / ".claude" / "_eval-fixtures"))
import deep_retrieve as dr  # noqa: E402

CHARS_PER_TOK = 4


def _scoped_semantic(query, prefix, k):
    """Top-k vault paths under `prefix` by cosine to the query (uses the fresh store)."""
    try:
        import numpy as np
        qv = dr._embed_query(query)
        if qv is None:
            return []
        vecs = {p: v for p, v in dr._load_smart_vectors().items() if prefix in p}
        if not vecs:
            return []
        paths = list(vecs)
        M = np.asarray([vecs[p] for p in paths], dtype=np.float32)
        M /= np.linalg.norm(M, axis=1, keepdims=True) + 1e-9
        q = np.asarray(qv, dtype=np.float32); q /= np.linalg.norm(q) + 1e-9
        sims = M @ q
        return [(float(sims[i]), paths[i]) for i in np.argsort(-sims)[:k]]
    except Exception:
        return []


def _match_method(query):
    try:
        import method_retrieve as mr
        methods = mr.load_methods()
        sem = mr._semantic_rank(query, methods) or []
        if sem:
            return sem[0]  # (cosine, method)
        kw = sorted(((mr.score(m, mr._tok(query)), m) for m in methods), key=lambda x: -x[0])
        return kw[0] if kw and kw[0][0] > 0 else None
    except Exception:
        return None


def assemble(query, budget_tokens=2200, hyde=None, avoid=None):
    notes = dr.retrieve(query, k=12, hyde=hyde, avoid=avoid, taste=False)  # QMD grafts: HyDE + avoid-steer
    notes = [(s, p, sn) for (s, p, sn) in notes if "09 Rules/_judgment/" not in p]
    notes = dr.taste_rerank(notes, (query + " " + hyde) if hyde else query)[:5]   # B4: bias toward the judgment graph
    judgment = _scoped_semantic(query, "09 Rules/_judgment/", 4)
    method = _match_method(query)
    sg = VAULT / ".claude" / "_state" / "underlays" / "source-graph.json"
    grounding = sg.exists()
    return {"query": query, "notes": notes, "judgment": judgment, "method": method,
            "grounding_available": grounding, "budget_tokens": budget_tokens,
            "embedder": dr._embed_query("x") is not None}


def render(b) -> str:
    L = [f"# Context for: {b['query']!r}",
         f"_(hybrid retrieval {'+ semantic' if b['embedder'] else '(keyword — embedder off)'}; budget ~{b['budget_tokens']} tok)_", ""]
    if b["method"]:
        sc, m = b["method"]
        L += ["## Method (composition skeleton)",
              f"- **{m['id']} {m['name']}** ({m['task_kind']}) — {m['deliverable']}",
              f"  `{m['path']}` · reuse its DAG; deviate per judgment.", ""]
    if b["judgment"]:
        L += ["## Judgment to apply (most relevant nodes)"]
        L += [f"- {p.split('/')[-1][:-3]}  ({s:.2f})" for s, p in b["judgment"]]
        L += [""]
    if b["notes"]:
        L += ["## Grounding notes (hybrid top)"]
        for s, p, sn in b["notes"]:
            L.append(f"- `{p}`" + (f" — …{sn[:90]}…" if sn else ""))
        L += [""]
    if b["grounding_available"]:
        L += ["## Source graph", "- available (`underlays/source-graph.json`) — pull entity/claim anchors before forwardable output.", ""]
    # budget trim
    text = "\n".join(L)
    cap = b["budget_tokens"] * CHARS_PER_TOK
    return text if len(text) <= cap else text[:cap] + "\n…(trimmed to budget)…"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", nargs="*")
    ap.add_argument("--budget", type=int, default=2200)
    ap.add_argument("--hyde", default=None, help="QMD HyDE: hypothetical-answer text to enrich the vector query")
    ap.add_argument("--avoid", default=None, help="QMD intent: comma-separated terms to steer away from")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    q = " ".join(args.query).strip()
    if not q:
        print("usage: context_assemble.py \"<task>\""); return 0
    avoid = [a for a in (args.avoid or "").split(",") if a.strip()] or None
    b = assemble(q, args.budget, hyde=args.hyde, avoid=avoid)
    if args.json:
        b["method"] = (b["method"][1] if b["method"] else None)
        print(json.dumps(b, ensure_ascii=False, indent=2, default=str))
    else:
        print(render(b))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
