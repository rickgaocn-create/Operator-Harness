#!/usr/bin/env python3
"""harness_common.py — the shared spine for the learn-loop feeders.

Coherence backbone (per the 2026-06-02 coherence review): every loop was re-implementing its
own stopword list, tokenizer, salience decay, reversibility classifier, and foundational set.
This module is the ONE source for all of them, reading the single machine-readable taxonomy
(`_state/behavior-classes.json`, projected from the behavior-class taxonomy doc).

It exposes the `class_key` join (the universal key threaded through capture -> prediction ->
adjudicator -> evolution_engine), the GRAD/CAP + foundational lookups (table, not guesswork),
and the shared text utilities. FAIL-SAFE: if the JSON is missing or corrupt, it falls back to
conservative defaults (no class match -> caller treats as CAP; the core files stay foundational)
so an importer can never crash or fail-open.

Import from anywhere under the vault:
    import sys, os
    sys.path.insert(0, os.path.join(VAULT, ".claude", "_eval-fixtures"))
    import harness_common as H
"""
from __future__ import annotations
import json
import math
import os
import re
from functools import lru_cache

VAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # _eval-fixtures -> .claude -> {{USER_NAME}}
STATE = os.path.join(VAULT, ".claude", "_state")
CLASSES_JSON = os.path.join(STATE, "behavior-classes.json")

# Conservative fallback if the JSON can't be read — the 6 always-on core files stay protected,
# and with no class table every classify() returns None so callers default to CAP.
_FALLBACK_FOUNDATIONAL = ["me.md", "CLAUDE.md", "MEMORY.md", "GOALS.md", "vault-map.md", "AGENTS.md"]

# ONE canonical stopword list (was duplicated in adjudicator.py and reflect.py with drift).
STOPWORDS = {
    "the", "a", "an", "to", "of", "and", "or", "as", "is", "it", "in", "on", "for", "with",
    "that", "this", "be", "by", "our", "we", "not", "but", "than", "then", "more", "less",
    "into", "from", "are", "was", "did", "does", "while", "even", "its", "their", "they",
    "you", "your", "i", "me", "my", "at", "if", "so", "no", "per", "via", "ai", "rg",
    "claude", "should", "must", "when", "what", "how", "do",
    # common CJK particles (the vault is bilingual) — so the ONE shared list covers Chinese stop-tokens
    "的", "了", "是", "在", "和", "我", "你", "也", "就", "都", "有", "这", "那",
}


@lru_cache(maxsize=1)
def load_classes() -> dict:
    """Load the taxonomy JSON once. Returns a dict with classes/grad/cap/foundational_paths.
    Fail-safe to a conservative minimal structure."""
    try:
        with open(CLASSES_JSON, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("classes"), list):
            return data
    except Exception:
        pass
    return {"classes": [], "grad_class_ids": [], "cap_class_ids": [],
            "native_a_ids": [], "foundational_paths": _FALLBACK_FOUNDATIONAL}


def tokens(text: str) -> set:
    """ONE tokenizer (latin words >=2 chars + CJK runs), stopwords removed."""
    return {t for t in re.findall(r"[a-z0-9一-鿿]{2,}", str(text).lower()) if t not in STOPWORDS}


def jaccard(a: set, b: set) -> float:
    """Jaccard over token sets — the SECONDARY (fallback) match signal, never the primary."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def recency_decay(days_ago: float, half_life: float = 14.0) -> float:
    """ONE recency decay (exp, ~2-week half-life). Multiply by a salience weight at the call site."""
    try:
        return math.exp(-float(days_ago) / half_life)
    except Exception:
        return 0.0


def salience(days_ago: float, weight: float = 1.0, half_life: float = 14.0) -> float:
    """recency x salience-weight — the ONE ranking score the feeders share."""
    return weight * recency_decay(days_ago, half_life)


# ---- the class_key join + GRAD/CAP/foundational lookups (table, not guesswork) ----

def class_meta(class_id) -> dict | None:
    """Return the taxonomy row for a class id (int or numeric str), or None."""
    if class_id is None:
        return None
    try:
        cid = int(class_id)
    except (TypeError, ValueError):
        return None
    for c in load_classes().get("classes", []):
        if c.get("id") == cid:
            return c
    return None


def classify_text_to_class(text: str, min_score: float = 2.0) -> tuple[int | None, float]:
    """Map free text (a correction, a prediction's forbidden_behavior, a candidate summary) to the
    best-matching behavior-class id by keyword hit-count. Returns (class_id, confidence in 0..1).
    Returns (None, 0.0) when nothing matches — callers should treat that as 'unknown -> CAP'.
    This is the bridge that lets the class_key join work on records authored before tagging, and
    a far better recurrence signal than raw Jaccard (it keys on the CLASS, not surface words)."""
    low = str(text).lower()
    if not low.strip():
        return None, 0.0
    best_id, best_score = None, 0.0
    for c in load_classes().get("classes", []):
        kws = c.get("keywords", []) or []
        strong = c.get("strong_keywords", []) or []
        if not kws and not strong:
            continue
        # Multiword/phrase keywords are more discriminative than single common words that collide
        # across classes, so weight them 2.0. strong_keywords are class-UNIQUE single cues (".ps1",
        # "feishu", "fabricate") that should cross the threshold alone. This is the coarse BRIDGE for
        # untagged records; persisted records carry an explicit, human-confirmable class_key.
        score = sum((2.0 if " " in kw else 1.0) for kw in kws if kw.lower() in low)
        score += sum(2.0 for kw in strong if kw.lower() in low)
        if score > best_score:
            best_id, best_score = c.get("id"), score
    # HIGH-PRECISION + SAFE-LEANING: a single common-word hit (score 1.0) is too weak to trust
    # (common words like "deal"/"artifact"/"task" collide across classes), so require a phrase hit
    # or >=2 keyword hits. Below that -> None, which callers treat as unknown->CAP (the conservative
    # default). Errs toward 'human-gated', never toward a wrong GRAD.
    if best_id is None or best_score < min_score:
        return None, 0.0
    return best_id, round(min(1.0, best_score / 3.0), 2)


# ---- recurrence attribution (the ONE matcher; both adjudicator L1 + harness-pulse call it) ----

def resolve_class_key(pred: dict):
    """A prediction's behavior-class id — the declared `class_key`, or one derived from its text via
    classify_text_to_class when the record predates tagging. Returns None when nothing classifies
    (callers then fall back to Jaccard / treat as unknown)."""
    ck = pred.get("class_key")
    if ck is not None:
        return ck
    ck, _ = classify_text_to_class(
        str(pred.get("forbidden_behavior", "")) + " "
        + str((pred.get("trigger_signature") or {}).get("value", "")))
    return ck


def recurrence_hits(pred: dict, corrections: list, match_thresh: float = 0.18) -> dict:
    """Corrections logged AFTER `pred` that are attributable to its behavior CLASS — i.e. evidence the
    forbidden behavior RECURRED. This is the ONE recurrence-attribution shared by the adjudicator
    (L1 gold) and harness-pulse's promotion-ineffective sensor, so the two can never disagree on what
    counts as a recurrence by construction.

    PRIMARY signal = exact class_key join (the taxonomy id — keys on the behavior CLASS, not surface
    words, which is what made the old ≥2-shared-token heuristic over-flag on generic vocab like
    'only'/'without'/'artifact'). SECONDARY = Jaccard token overlap >= match_thresh, used ONLY for
    records that lack a class_key. Only polarity=='correction' rows dated strictly after the
    prediction count. Returns {'pred_class_key', 'hits':[{ts,match,overlap,correction}]}."""
    created = str(pred.get("created", ""))
    pred_ck = resolve_class_key(pred)
    target = tokens(pred.get("forbidden_behavior", "")) | tokens(
        (pred.get("trigger_signature") or {}).get("value", ""))
    hits = []
    for c in corrections:
        if c.get("polarity") != "correction":
            continue
        if str(c.get("ts", "")) <= created:  # only corrections AFTER the prediction count as recurrence
            continue
        c_ck = c.get("class_key")
        if c_ck is None:
            c_ck, _ = classify_text_to_class(
                str(c.get("correction", "")) + " " + str(c.get("why", "")) + " " + str(c.get("ai_output", "")))
        matched, how, ov = False, "", 0.0
        if pred_ck is not None and c_ck is not None and int(pred_ck) == int(c_ck):
            matched, how = True, f"class-key #{pred_ck}"
        else:
            ctoks = tokens(c.get("correction", "")) | tokens(c.get("why", "")) | tokens(c.get("ai_output", ""))
            ov = jaccard(target, ctoks)
            if ov >= match_thresh:
                matched, how = True, f"jaccard {round(ov, 2)} (fallback)"
        if matched:
            hits.append({"ts": c.get("ts"), "match": how, "overlap": round(ov, 2),
                         "correction": str(c.get("correction", ""))[:120]})
    return {"pred_class_key": pred_ck, "hits": hits}


def is_cap(class_id) -> bool:
    """Unknown/unloadable class -> True (conservative), matching the unknown->CAP default everywhere."""
    m = class_meta(class_id)
    if m is None:
        return True
    return m.get("autonomy") == "CAP"


def is_grad(class_id) -> bool:
    """Unknown -> False (never auto-graduate something we can't classify)."""
    m = class_meta(class_id)
    return bool(m and m.get("autonomy") == "GRAD")


def is_irreversible(class_id) -> bool:
    """Unknown/unloadable class -> True (conservative: assume irreversible -> tighter closure bound),
    so a corrupt or missing taxonomy can never RELAX a safety threshold."""
    m = class_meta(class_id)
    if m is None:
        return True
    return m.get("reversibility") == "irreversible"


def is_foundational_class(class_id) -> bool:
    m = class_meta(class_id)
    return bool(m and m.get("foundational"))


def foundational_paths() -> set:
    """The ONE unified irreversibility-ceiling path set (union of the old three sources)."""
    return set(load_classes().get("foundational_paths", _FALLBACK_FOUNDATIONAL))


def is_foundational_path(relpath: str) -> bool:
    """True if a vault-relative path is in the foundational ceiling. Matches on basename OR the
    forward-slash relpath, so callers needn't normalize identically."""
    if not relpath:
        return False
    rel = str(relpath).replace("\\", "/")
    base = rel.rsplit("/", 1)[-1]
    fset = foundational_paths()
    return rel in fset or base in fset


if __name__ == "__main__":
    # Smoke test / introspection.
    import sys, io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    d = load_classes()
    print(f"classes loaded: {len(d.get('classes', []))}")
    print(f"GRAD: {d.get('grad_class_ids')}  CAP: {d.get('cap_class_ids')}")
    print(f"foundational paths: {len(foundational_paths())}")
    for probe in ["attribute synthesized judgment as a counterparty quote",
                  "edit me.md the foundational file",
                  "write today's daily note",
                  "send the partner an invite on feishu",
                  "completely unrelated gibberish xyzzy"]:
        cid, conf = classify_text_to_class(probe)
        m = class_meta(cid)
        print(f"  '{probe[:40]}...' -> class {cid} ({m['autonomy'] if m else 'NONE->CAP'}) conf={conf}")
