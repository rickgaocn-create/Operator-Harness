"""Corpus backlog harvester — config-driven port, with pluggable source adapters.

The graph is usually starved (a handful of interactive corrections), but your existing
notes already hold months of EXPRESSED judgment. This script does the SCRIPTED half of
backlog-mining: it walks the corpus SOURCES declared in config, lifts the high-signal
passages, scores + caps them, and emits a compact candidate set. ~0 model tokens; never
writes to the graph.

Two adapter kinds, both config-driven (see `[[harvest.sources]]` in the TOML):
  - markdown : glob + which frontmatter fields / `## sections` to lift + scoring + tier
  - jsonl    : a JSONL log (e.g. your corrections file), filtered by field == value

`touch_hints` (keyword -> node-id) are config too — instance-specific, since they name
your graph's nodes. They're only HINTS; the downstream model finalizes `touches`.
"""
from __future__ import annotations

import glob
import json
import os
import re

from .config import Config

PASSAGE_BUDGET = 600  # chars per section — keep the downstream brief compact


def split_frontmatter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            return text[3:end], text[end + 4:]
    return "", text


def fm_value(head, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", head, re.MULTILINE)
    return m.group(1).strip().strip('\'"') if m else ""


def fm_list(head, key):
    raw = fm_value(head, key).strip("[]")
    return [x.strip().strip('\'"') for x in raw.split(",") if x.strip()] if raw else []


def extract_sections(body, wanted):
    """Return {section_name: trimmed_text} for the wanted `## Section` headers present."""
    out = {}
    parts = re.split(r"^##\s+(.+?)\s*$", body, flags=re.MULTILINE)
    for i in range(1, len(parts) - 1, 2):
        name = parts[i].strip()
        for w in wanted:
            if name.lower().startswith(w.lower()):
                txt = parts[i + 1].strip()
                out[w] = txt[:PASSAGE_BUDGET] + ("…" if len(txt) > PASSAGE_BUDGET else "")
    return out


def lead_blockquote(body):
    quote = []
    for ln in body.splitlines():
        s = ln.strip()
        if s.startswith(">"):
            quote.append(s.lstrip("> ").rstrip())
        elif quote:
            break
    return " ".join(q for q in quote if q)[:PASSAGE_BUDGET]


def title_of(body):
    m = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _meaningful(t):  # real content vs empty template scaffolding
    return len(re.sub(r"[-*>#\s_]", "", t or "")) > 40


def compile_hints(raw_hints):
    return [(re.compile(h["pattern"]), h.get("nodes", [])) for h in (raw_hints or [])]


def touch_hints(text, compiled):
    hits, low = [], text.lower()
    for pat, nodes in compiled:
        if pat.search(low):
            hits.extend(nodes)
    return sorted(set(hits))


def _harvest_markdown(cfg: Config, src: dict, compiled):
    cands = []
    pattern = src.get("filename_pattern")
    skip_status = set(src.get("skip_status", []))
    sections = src.get("sections", [])
    fm_fields = src.get("frontmatter_fields", [])
    domain_from = src.get("domain_from", "folder")
    for path in sorted(glob.glob(cfg.resolve(src["glob"]), recursive=True)):
        base = os.path.basename(path)
        if pattern and not re.match(pattern, base):
            continue
        head, body = split_frontmatter(open(path, encoding="utf-8", errors="replace").read())
        status = fm_value(head, "status") or "?"
        if status in skip_status:
            continue
        domain = os.path.basename(os.path.dirname(path)) if domain_from == "folder" else fm_value(head, domain_from)
        secs = extract_sections(body, sections)
        if src.get("meaningful_gate") and not any(_meaningful(v) for v in secs.values()):
            continue  # near-empty — no revealed judgment to mine
        passages = {}
        if src.get("include_lead_blockquote"):
            passages["principle"] = lead_blockquote(body)
        for f in fm_fields:
            passages[f] = fm_value(head, f)
        passages.update(secs)
        blob = " ".join(v for v in passages.values() if v) + " " + " ".join(fm_list(head, "tags")) + " " + (domain or "")
        score = src.get("base_score", 2)
        score += src.get("score_bonus_domain", {}).get(domain, 0)
        score += src.get("score_bonus_status", {}).get(status, 0)
        for sec, bonus in src.get("score_bonus_section", {}).items():
            if sec in secs and _meaningful(secs[sec]):
                score += bonus
        tier = src.get("tier_when_domain", {}).get(domain) or src.get("tier", "prior")
        cands.append({
            "source": os.path.relpath(path, cfg.root).replace("\\", "/"),
            "type": src.get("label", "markdown"), "domain": domain, "status": status,
            "tier": tier, "title": title_of(body) or base[:-3],
            "tags": fm_list(head, "tags"), "touches_hint": touch_hints(blob, compiled),
            "signal": score, "passages": passages,
        })
    return cands


def _harvest_jsonl(cfg: Config, src: dict):
    cands = []
    path = cfg.resolve(src["path"])
    if not os.path.exists(path):
        return cands
    filt = src.get("filter", {})
    pf = src.get("passage_fields", {})
    tf = src.get("touches_field")
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        if any(e.get(k) != v for k, v in filt.items()):
            continue
        touches = []
        if tf:
            t = e.get(tf, {}) or {}
            touches = (t.get("values") or []) + (t.get("frameworks") or [])
        cands.append({
            "source": f"{os.path.basename(path)} [{e.get('ts')}]",
            "type": src.get("label", "jsonl-event"), "domain": e.get("skill", ""),
            "status": e.get("status", "?"), "tier": src.get("tier", "logic"),
            "title": e.get("artifact", ""), "tags": [],
            "touches_hint": sorted(set(touches)), "signal": src.get("base_score", 2),
            "passages": {k: e.get(v, "") for k, v in pf.items()},
        })
    return cands


def harvest(cfg: Config):
    h = cfg.section("harvest")
    compiled = compile_hints(h.get("touch_hints"))
    cands = []
    for src in h.get("sources", []):
        kind = src.get("kind", "markdown")
        if kind == "markdown":
            cands += _harvest_markdown(cfg, src, compiled)
        elif kind == "jsonl":
            cands += _harvest_jsonl(cfg, src)
    return cands


def build(cfg: Config, tier=None, cap=None):
    cap = cap or int(cfg.section("harvest").get("cap", 40))
    cands = harvest(cfg)
    if tier:
        cands = [c for c in cands if c.get("tier") == tier]
    # logic tier first (the graph target), then by signal — so scarce, most-distilled
    # sources are never crowded out by the larger pile of domain notes.
    cands.sort(key=lambda c: (c.get("tier") == "logic", c["signal"]), reverse=True)
    capped = cands[:cap]
    return {
        "root": cfg.root, "total_found": len(cands), "cap": cap, "returned": len(capped),
        "note": "scripted harvest, 0 model tokens. Feed to distill; dedup vs existing nodes "
                "+ corrections; cluster into a few patterns for human review.",
        "candidates": capped,
    }
