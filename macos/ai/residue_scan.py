#!/usr/bin/env python3
"""CN english-residue scanner — the localize-cn quality gate, made cheap via local inference.

Two layers:
  1. Deterministic denylist/whitelist regex pass (always runs, zero deps, no model). Catches the
     known residue words; respects the brand/acronym whitelist.
  2. Optional local-LLM semantic pass (free, on-device) for residue the regex misses — the
     "fresh-context" check that was too costly to run on cloud for every CN artifact.

This is what makes the localize-cn fresh-context promotion (declined earlier on cost) viable on mac.

Usage:
    python3 residue_scan.py --file path.md        # or pipe text on stdin
Output: JSON {verdict: pass|flag, regex_hits:[...], semantic_hits:[...], used_local: bool}
Exit:   0 = pass, 2 = flagged (so it can act as a PreToolUse/quality gate)
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import router
except Exception:
    router = None

# English residue commonly leaking into CN work artifacts (from the 2026-05-28 incident set).
RESIDUE = [
    "backlog", "framing", "partition", "starving", "bolt-on", "closeout", "fallback", "mandate",
    "re-date", "spec", "handoff", "dormant", "benchmark", "roadmap", "scope", "stakeholder",
    "alignment", "leverage", "bandwidth", "deliverable", "milestone", "cadence", "blocker",
    "actionable", "takeaway", "synergy", "onboarding", "pipeline", "rollout", "touchpoint",
]
# allowed: brand names, industry acronyms, versions/paths/code (mirror of the CLAUDE.md whitelist)
WHITELIST = {
    "taptap", "bilibili", "anthropic", "epic", "wegame", "lenovo", "ai", "bd", "sdk", "mcp",
    "pmo", "kol", "ip", "ott", "mau", "pv", "vt", "qte", "poi", "pbr", "t0", "url", "okr", "kr",
    "html", "md", "json", "api", "llm", "ui", "cli", "ttl", "os",
}
WORD = re.compile(r"[A-Za-z][A-Za-z\-]+")


def regex_scan(text):
    hits = []
    low = text.lower()
    for w in RESIDUE:
        if re.search(r"\b" + re.escape(w) + r"\b", low):
            hits.append(w)
    # any other latin word not whitelisted, not in a code/URL context, flanked by CJK -> suspect
    for m in WORD.finditer(text):
        w = m.group(0)
        if w.lower() in WHITELIST or w.lower() in RESIDUE:
            continue
        i = m.start()
        # heuristic: flanked by CJK on either side => inline english in a CN sentence
        around = text[max(0, i - 2):m.end() + 2]
        if re.search(r"[一-鿿]", around) and len(w) > 3:
            hits.append(w)
    return sorted(set(hits))


SEM_SYS = (
    "You are a Chinese-writing residue auditor. The user text is a Chinese work artifact that must "
    "be monolingual Chinese. Allowed exceptions: brand names, industry acronyms, version numbers, "
    "file paths, code, URLs. Find any ENGLISH words/phrases that are NOT allowed exceptions and "
    "should be Chinese. Reply ONLY JSON: {\"residue\":[\"word\",...]} (empty list if clean)."
)


def semantic_scan(text):
    if router is None:
        return [], False
    r = router.route("residue-scan", text[:6000], system=SEM_SYS, max_tokens=256)
    if r.get("tier") != "local" or "result" not in r:
        return [], False
    raw = r["result"]
    s, e = raw.find("{"), raw.rfind("}")
    if s != -1 and e > s:
        try:
            data = json.loads(raw[s:e + 1])
            return [str(x) for x in (data.get("residue") or [])], True
        except Exception:
            pass
    return [], True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    ap.add_argument("--no-semantic", action="store_true", help="regex layer only")
    a = ap.parse_args()
    text = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
    rx = regex_scan(text)
    sem, used_local = ([], False) if a.no_semantic else semantic_scan(text)
    # keep only semantic hits that are real latin tokens present in the text
    sem = [w for w in sem if re.search(r"[A-Za-z]", w) and w.lower() in text.lower()]
    flagged = sorted(set(rx) | set(sem))
    out = {"verdict": "flag" if flagged else "pass", "regex_hits": rx,
           "semantic_hits": sorted(set(sem)), "used_local": used_local}
    print(json.dumps(out, ensure_ascii=False))
    return 2 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
