"""Distill brief generator — config-driven port, ~0 model tokens.

Capture fills the corrections log with `status:new` events. Distill turns the accumulated
events into a small per-node brief: the unfilled placeholder edges, the edges that are
mechanically DERIVABLE (a value <- the frameworks whose `embodies` lists it), and the
captured events that touch each node. The model reads this brief and writes concrete
PROPOSALS to the review queue. Nothing reaches the graph without human approval.

Threshold-triggered: meant to run when the new-event count >= threshold (event-driven,
not on a clock). `--status` just reports the count; `--brief` runs regardless.
"""
from __future__ import annotations

import glob
import json
import os
import re

from .config import Config

DEFAULT_THRESHOLD = 5
# Default convention for an unfilled edge: a bold label whose value is a parenthetical
# starting with a phase marker, e.g. `**Rules that serve it:** (J2 — ...)`. Configurable.
DEFAULT_PLACEHOLDER = r"^\*\*(?P<label>[^*]+?):\*\*\s*\((?P<marker>{marker})\b(?P<note>[^)]*)\)"


def fm_value(head, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", head, re.MULTILINE)
    return m.group(1).strip().strip('\'"') if m else ""


def fm_list(head, key):
    raw = fm_value(head, key).strip("[]")
    return [x.strip().strip('\'"') for x in raw.split(",") if x.strip()] if raw else []


def load_nodes(cfg: Config, placeholder_re):
    fm = cfg.graph.fm
    nodes = {}
    for path in sorted(glob.glob(os.path.join(cfg.judgment_dir, "*.md"))):
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        head = text[3:text.find("\n---", 3)] if text.startswith("---") and text.find("\n---", 3) > 0 else text[:600]
        nid = fm_value(head, fm["id"]) or os.path.splitext(os.path.basename(path))[0]
        placeholders = []
        for line in text.splitlines():
            m = placeholder_re.match(line.strip())
            if m:
                placeholders.append({"label": m.group("label").strip(),
                                     "marker": m.group("marker"),
                                     "note": m.group("note").strip(" —-")})
        nodes[nid] = {
            "id": nid, "path": path,
            "type": fm_value(head, fm["type"]),
            "name": fm_value(head, fm["name"]),
            "embodies": fm_list(head, fm["embodies"]),
            "placeholders": placeholders,
        }
    return nodes


def load_events(cfg: Config, corrections_path):
    events = []
    if not os.path.exists(corrections_path):
        return events
    for line in open(corrections_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    return events


def derivable_reverse_edges(nodes):
    """value-id -> [framework-ids whose `embodies` lists it]. Mechanically derivable."""
    rev = {nid: [] for nid in nodes}
    for nid, n in nodes.items():
        if n["type"] == "framework":
            for vid in n["embodies"]:
                rev.setdefault(vid, []).append(nid)
    return rev


def cluster_events_by_node(events, new_status):
    by_node = {}
    for e in events:
        if e.get("status") != new_status:
            continue
        touches = e.get("touches", {}) or {}
        for nid in (touches.get("values", []) or []) + (touches.get("frameworks", []) or []):
            by_node.setdefault(nid, []).append(e)
    return by_node


def build(cfg: Config, threshold=None):
    d = cfg.section("distill")
    threshold = threshold if threshold is not None else int(d.get("threshold", DEFAULT_THRESHOLD))
    corrections = cfg.resolve(d.get("corrections", ".claude/_state/corrections.jsonl"))
    proposals = cfg.resolve(d.get("proposals", ".claude/_state/distill-proposals.jsonl"))
    new_status = d.get("new_status", "new")
    marker = d.get("placeholder_marker", r"J\d\w*")
    placeholder_re = re.compile(DEFAULT_PLACEHOLDER.format(marker=marker))

    nodes = load_nodes(cfg, placeholder_re)
    events = load_events(cfg, corrections)
    new_events = [e for e in events if e.get("status") == new_status]
    rev = derivable_reverse_edges(nodes)
    by_node = cluster_events_by_node(events, new_status)
    touched = sorted(set(by_node) | {k for k, v in rev.items() if v})
    clusters = []
    for nid in touched:
        n = nodes.get(nid)
        clusters.append({
            "node": nid,
            "type": n["type"] if n else "(unknown — event references missing node)",
            "name": n["name"] if n else "",
            "placeholders": n["placeholders"] if n else [],
            "derivable_framework_edges": rev.get(nid, []),
            "events": [{"ts": e.get("ts"), "polarity": e.get("polarity"),
                        "candidate_rule": e.get("candidate_rule"), "why": e.get("why"),
                        "correction": e.get("correction")} for e in by_node.get(nid, [])],
        })
    return {
        "new_event_count": len(new_events),
        "threshold": threshold,
        "threshold_met": len(new_events) >= threshold,
        "proposals_path": proposals,
        "clusters": clusters,
    }
