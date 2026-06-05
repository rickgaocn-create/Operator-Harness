#!/usr/bin/env python3
"""reflect.py — the REFLECTION feeder (Generative Agents' reflection step), deterministic v1.

Generative Agents periodically synthesize higher-order insight from the memory stream. The
SYNTHESIS is an LLM step; the part that must be deterministic + cheap (and is the hard part to
get right) is *what to reflect on* — gathering the stream, ranking by recency × salience, and
surfacing recurring THEMES. This script does exactly that and stages a "reflection input pack";
a downstream model step (in-session or a cron-fired skill) turns the pack into a higher-level
Card/rule candidate (human-gated, Tier-B). It does NOT call a model and does NOT write durable
memory itself — it prepares the input. Exit 0.

  python reflect.py [--window 14] [--top 8] [--json] [--drain]
"""
from __future__ import annotations
import argparse, glob, io, json, math, os, re, sys
from collections import Counter
from datetime import date

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

VAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # routines -> .claude -> {{USER_NAME}}
STATE = os.path.join(VAULT, ".claude", "_state")
CORRECTIONS = os.path.join(STATE, "corrections.jsonl")
SUCCESS = os.path.join(STATE, "success-traces.jsonl")
ERRPATTERNS = os.path.join(STATE, "error-patterns.jsonl")   # feeder #4 (machine-detected failures)
GRADER = os.path.join(STATE, "grader-verdicts.jsonl")       # the enforce-layer (was an orphan stream)
DECISIONS = os.path.join(VAULT, "05 Decisions")             # decision records feed reflection (rationale = judgment signal)
OUT = os.path.join(STATE, "reflections.jsonl")

# Shared spine (tokens / salience). Fail-safe: keep local fallbacks if the import ever fails (this
# runs on the weekly cron). H is None -> the local _STOP/regex/decay below are used.
sys.path.insert(0, os.path.join(VAULT, ".claude", "_eval-fixtures"))
try:
    import harness_common as H
except Exception:
    H = None

_STOP = {"the","a","an","to","of","and","or","as","is","it","in","on","for","with","that","this",
         "be","by","our","we","not","but","than","then","more","less","into","from","are","was",
         "did","does","while","even","its","their","they","you","your","i","me","my","at","if","so",
         "no","a","the","per","via","ai","rg","claude","should","must","when","what","how"}


def _read_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def _days_ago(ts: str, today: date) -> int | None:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(ts))
    if not m:
        return None
    try:
        d = date(int(m[1]), int(m[2]), int(m[3]))
        return (today - d).days
    except ValueError:
        return None


def _parse_md(path):
    """(frontmatter dict of str values, body) — tiny, dependency-free YAML-lite."""
    try:
        txt = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return {}, ""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", txt, re.DOTALL)
    if not m:
        return {}, txt
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"\s*([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", line)
        if mm:
            fm[mm.group(1).strip()] = mm.group(2).strip()
    return fm, m.group(2)


def _section(body, name):
    """Text under a '## name' heading, up to the next '## ' (or EOF)."""
    m = re.search(r"^##\s+" + re.escape(name) + r"\s*\n(.*?)(?=^##\s|\Z)", body, re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else ""


def _toks(text: str):
    if H is not None:
        return list(H.tokens(text))   # shared tokenizer + stopwords (was a private list that drifted)
    return [t for t in re.findall(r"[a-z][a-z0-9-]{3,}", str(text).lower()) if t not in _STOP]


def gather(window: int, today: date):
    """Pull recent stream items (corrections + success-traces), tag each with recency/salience."""
    items = []
    for c in _read_jsonl(CORRECTIONS):
        da = _days_ago(c.get("ts", ""), today)
        if da is None or da > window:
            continue
        # salience: a corrective is a stronger reflection signal than a one-off positive.
        sal = 1.0 if c.get("polarity") == "correction" else 0.8  # raised 0.6->0.8: reinforce endorsed judgment near-parity (goal: judgment optimization)
        text = " ".join(str(c.get(k, "")) for k in ("skill", "correction", "why", "candidate_rule"))
        items.append({"src": "correction", "days_ago": da, "salience": sal,
                      "text": text, "summary": str(c.get("candidate_rule") or c.get("correction") or "")[:140]})
    for s in _read_jsonl(SUCCESS):
        # success-traces may lack a ts; treat as recent (day 0). Raised 0.5->0.8 to weight endorsed judgment near parity with corrections (goal: judgment optimization).
        items.append({"src": "success", "days_ago": 0, "salience": 0.8,
                      "text": " ".join(str(s.get(k, "")) for k in ("endorsement", "trajectory_text")),
                      "summary": str(s.get("proposed_type", "") + ": " + str(s.get("trajectory_text", "")))[:140]})
    # Reflection now synthesizes from ALL loops (coherence-review fix): the machine-detected recurring
    # failures and the enforce-layer grader failures were previously invisible to the reflect-back digest.
    for e in _read_jsonl(ERRPATTERNS):
        items.append({"src": "error-pattern", "days_ago": 0, "salience": 0.9,  # cross-session machine signal — high
                      "text": str(e.get("signature", "")) + " " + str(e.get("proposed_intervention", "")),
                      "summary": f"{e.get('signature','')} x{e.get('count','?')}/{e.get('sessions','?')}sess: {e.get('proposed_intervention','')}"[:140]})
    for g in _read_jsonl(GRADER):
        v = str(g.get("verdict", "")).upper()
        if g.get("grader") == "_template" or v in ("", "PASS", "APPROVED", "OK"):
            continue  # only enforce-layer FAILURES carry a learning signal
        hf = ", ".join(g.get("hard_fails", []) or [])
        items.append({"src": "grader", "days_ago": _days_ago(g.get("ts", ""), today) or 0, "salience": 0.85,
                      "text": str(g.get("artifact", "")) + " " + hf + " " + str(g.get("notes", "")),
                      "summary": f"grader {v} [{g.get('grader','')}]: {hf or g.get('score','')}"[:140]})
    # Decision records (05 Decisions/) — a decision's rationale + what-to-watch is a first-class
    # judgment signal, on par with corrections. One-way (irreversible) calls weigh higher.
    for path in sorted(glob.glob(os.path.join(DECISIONS, "*.md"))):
        if os.path.basename(path).startswith("_"):
            continue  # dashboards / index notes
        fm, body = _parse_md(path)
        if fm.get("type") != "decision":
            continue
        da = _days_ago(fm.get("date", ""), today)
        if da is None or da > window:
            continue
        rev = fm.get("reversibility", "")
        decision = _section(body, "Decision")
        title = os.path.splitext(os.path.basename(path))[0]
        text = " ".join((title, decision, _section(body, "Rationale"),
                         _section(body, "Consequences / watch for"), _section(body, "Updates")))
        items.append({"src": "decision", "days_ago": da,
                      "salience": 0.85 if rev == "one-way" else 0.7,  # irreversible calls carry more learning weight
                      "text": text,
                      "summary": f"decision [{fm.get('status','')}/{rev}]: {decision or title}"[:140]})
    return items


def score(item) -> float:
    """recency (exp decay, ~2-week half-life) × salience. Shared decay when available."""
    if H is not None:
        return H.salience(item["days_ago"], item["salience"])
    return item["salience"] * math.exp(-item["days_ago"] / 14.0)


def themes(items, k: int = 8):
    """Recurring tokens across the window = candidate patterns worth a higher-order reflection."""
    c = Counter()
    for it in items:
        c.update(set(_toks(it["text"])))  # set() per item -> count documents, not raw freq
    return [w for w, n in c.most_common(k) if n >= 2]


def build_pack(window: int, top: int, today: date):
    items = gather(window, today)
    ranked = sorted(items, key=score, reverse=True)[:top]
    return {
        "kind": "reflection-input",
        "window_days": window,
        "stream_size": len(items),
        "top_items": [{"src": it["src"], "days_ago": it["days_ago"],
                       "score": round(score(it), 3), "summary": it["summary"]} for it in ranked],
        "recurring_themes": themes(items),
        "proposes": "needs-synthesis",
        "note": "deterministic input pack — a downstream model step synthesizes the higher-order Card/rule (human-gated)",
    }


def build_reflect_back(window: int, today: date):
    """The 'confirm / correct' digest — the reflect-BACK step that makes regular conversation the
    optimizer. Surfaces inferred judgment patterns + open predictions awaiting {{USER_NAME}}'s gold
    confirmation. Presenting this to {{USER_NAME}} and recording the reply (via
    promotion_predictions.py --observe / adjudicator) is what closes the learning loop on a cadence."""
    pack = build_pack(window, 8, today)
    preds = _read_jsonl(os.path.join(STATE, "promotion-predictions.jsonl"))
    open_preds = [{"id": p.get("id"), "expects": str(p.get("forbidden_behavior", ""))[:120]}
                  for p in preds if p.get("verdict") is None]
    return {"kind": "reflect-back", "window_days": window,
            "inferred_patterns": pack["recurring_themes"],
            "top_signals": [it["summary"] for it in pack["top_items"][:5]],
            "open_predictions_awaiting_confirm": open_preds,
            "ask": "Confirm these still hold / correct any — each reply is gold that closes a learning verdict."}


PATTERNS_DOC = os.path.join(VAULT, "04 Notes", "_system", "(C) inferred-judgment-patterns.md")
COUNTER = os.path.join(STATE, "reflect-counter.json")


def _entry_count() -> int:
    """Size of the memory stream synthesis draws on (corrections + observations + successes)."""
    n = 0
    for f in ("corrections.jsonl", "promotion-observations.jsonl", "success-traces.jsonl"):
        p = os.path.join(STATE, f)
        if os.path.exists(p):
            n += sum(1 for line in open(p, encoding="utf-8") if line.strip())
    return n


def regen(window: int, today: date) -> dict:
    """SRC (Synthesis Regen Cadence, borrow from TencentDB Agent Memory): regenerate the DERIVED
    inferred-judgment-patterns artifact from the memory stream + bump a counter. Overwrites the
    derived doc (regenerated, like a persona.md) — NEVER touches me.md. Full synthesis is refined
    via --reflect-back (human confirm); this is the deterministic draft."""
    pack = build_pack(window, 10, today)
    total = _entry_count()
    prev = {}
    if os.path.exists(COUNTER):
        try:
            prev = json.load(open(COUNTER, encoding="utf-8"))
        except Exception:
            prev = {}
    lines = [
        "---", "type: reference", "created-by: claude", f"last-regen: {today.isoformat()}",
        'description: "DERIVED judgment patterns synthesized from the memory stream (corrections + '
        'observations + successes). REGENERATED by reflect.py --regen — not hand-authored. Never '
        'overwrites me.md; confirmed patterns reach me.md/rules only via the human-gated learn-loop."',
        "---", "", "# Inferred Judgment Patterns (derived)", "",
        f"> Regenerated {today.isoformat()} from {total} memory entries (window {window}d). "
        "Deterministic draft — synthesis refined via `reflect.py --reflect-back` (confirm/correct).",
        "", "## Recurring themes", "", (" · ".join(pack["recurring_themes"]) or "(none yet)"), "",
        "## Top signals (evidence)", "",
    ]
    for it in pack["top_items"]:
        lines.append(f"- [{it['src']}/{it['days_ago']}d · {it['score']}] {it['summary']}")
    lines += ["", "## Status", "- Synthesis pending human confirm via the reflect-back cadence."]
    os.makedirs(os.path.dirname(PATTERNS_DOC), exist_ok=True)
    with open(PATTERNS_DOC, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(COUNTER, "w", encoding="utf-8") as fh:
        json.dump({"last_regen": today.isoformat(), "entries_at_last_regen": total}, fh, ensure_ascii=False)
    return {"doc": PATTERNS_DOC, "total_entries": total,
            "since_last_regen": total - prev.get("entries_at_last_regen", 0)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=14)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--drain", action="store_true")
    ap.add_argument("--reflect-back", action="store_true", help="emit the confirm/correct digest for {{USER_NAME}}")
    ap.add_argument("--regen", action="store_true", help="SRC: regenerate the derived inferred-judgment-patterns doc + bump the counter")
    args = ap.parse_args()
    if args.regen:
        r = regen(args.window, date.today())
        print(f"regenerated {r['doc']}")
        print(f"  {r['total_entries']} memory entries ({r['since_last_regen']:+d} since last regen)")
        return 0
    if args.reflect_back:
        rb = build_reflect_back(args.window, date.today())
        if args.json:
            print(json.dumps(rb, ensure_ascii=False, indent=2)); return 0
        print("REFLECT-BACK — confirm/correct (your reply is gold that closes learning verdicts):\n")
        print("inferred judgment patterns:", rb["inferred_patterns"])
        print("\ntop signals:")
        for s in rb["top_signals"]:
            print("  -", s[:100])
        print(f"\nopen predictions awaiting your confirm ({len(rb['open_predictions_awaiting_confirm'])}):")
        for p in rb["open_predictions_awaiting_confirm"]:
            print(f"  {p['id']}: {p['expects'][:90]}")
        print("\n" + rb["ask"])
        return 0
    pack = build_pack(args.window, args.top, date.today())
    if args.drain:
        os.makedirs(STATE, exist_ok=True)
        with open(OUT, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(pack, ensure_ascii=False) + "\n")
        print(f"staged reflection-input pack ({pack['stream_size']} stream items) -> {OUT}")
        return 0
    if args.json:
        print(json.dumps(pack, ensure_ascii=False, indent=2)); return 0
    print(f"reflection window {args.window}d  |  stream items: {pack['stream_size']}")
    print(f"recurring themes: {pack['recurring_themes']}\n")
    for it in pack["top_items"]:
        print(f"  [{it['score']}] {it['src']:10} {it['days_ago']}d ago  {it['summary'][:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
