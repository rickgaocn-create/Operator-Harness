#!/usr/bin/env python3
"""
relation-gaps — Wiki relationship-mapping DETECTOR.

Deterministic, read-only sweep over `01 Wiki/` that surfaces, for the in-session
`/relation-map` actor skill to judge + propose with approval:

  1. under_connected   — entries with too few inbound links from the REST of the KB
                         (cross-cluster inbound < CROSS_MIN). This is the signal that
                         matches "not connecting to the rest of the knowledge base":
                         a page whose only inbound is its own sub-folder is isolated
                         even if it looks linked.
  2. clusters_with_gaps — sub-folders that concentrate the under-connected entries
                         (a cluster where most members are isolated = an island, like
                         the 2026-05-29 游戏系统 drop).
  3. unlinked_mentions — an entity NAMED in a file's body but never `[[linked]]`
                         (the high-precision "create a relation node here" stream).

Inbound is counted across the durable KB (`01 Wiki` + `02 Cards` + `03 Projects`), and
those non-Wiki pillars count as cross-cluster sources — so a hub whose inbound is all
intra-cluster (channel people → platform) is NOT mistaken for isolated once a Card or
project doc points at it, while a fresh cluster nothing-outside references stays flagged.

NEVER edits vault content (writes only its report + autonomous log) — per
09 Rules/autonomous-routines.md, routines are detectors, not actors. Cross-lane
candidates ({{PROJECT_A}} ↔ {{ORG_B}}/{{ORG_A}}/{{ORG_D}}) are dropped by construction.

Schedule: weekly (Sun) via Windows Task Scheduler + after a source-ingest bulk import.
DRY_RUN default = notify-only (Feishu, edge-triggered on rising under-connected count).
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT, log_event, notify_feishu, under_run_cap

ROUTINE = "relation-gaps"
WIKI = VAULT / "01 Wiki"
REPORT = VAULT / ".claude" / "_state" / "relation-gaps.json"

CROSS_MIN = 2                  # under-connected if cross-cluster KB inbound < this
CLUSTER_MIN_SIZE = 3          # min cluster size to report a cluster-level gap rollup
MAX_MENTIONS_PER_SOURCE = 12  # recall cap per file (actor does precision)
MAX_ALERTS_PER_DAY = 2
KB_SOURCE_DIRS = ("02 Cards", "03 Projects")  # count inbound from these too (durable KB)

EXCLUDE_DIR_PARTS = {"_原始转录", "9-Templates", "_archive", "_templates", ".obsidian", "attachments"}
EXCLUDE_NAMES = {"index.md"}
PROJECT_LANES = {"wangyue", "{{ORG_B}}", "mifei", "denmu"}  # cross-lane links hard-blocked

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_RANK = {"high": 3, "med": 2, "low": 1}


def _conf_rank(c: str) -> int:
    return _RANK.get(c, 0)


def lane_of(rel: str) -> str:
    p = rel.replace("\\", "/")
    if re.search(r"(^|/){{ORG_B}}", p) or "{{ORG_B}}" in p or "{{ORG_B}}, Inc" in p:
        return "{{ORG_B}}"
    if "{{ORG_A}}" in p:
        return "mifei"
    if "{{ORG_D}}" in p:
        return "denmu"
    if "/{{PROJECT_A}}/" in p or p.startswith("{{PROJECT_A}}/"):
        return "wangyue"
    if "Private" in p:
        return "private"
    return "neutral"


def cluster_of(rel: str) -> str:
    d = os.path.dirname(rel).replace("\\", "/")
    return d or "(root)"


def strip_c_prefix(name: str) -> str:
    return name[4:] if name.startswith("(C) ") else name


def norm_link_target(raw: str) -> str:
    """Inside [[...]] → drop alias/section, take last path segment, strip .md + (C)."""
    t = raw.split("|", 1)[0].split("#", 1)[0].strip()
    t = t.replace("\\", "/").rstrip("/").split("/")[-1]
    if t.endswith(".md"):
        t = t[:-3]
    return strip_c_prefix(t).strip()


def parse_frontmatter(text: str) -> dict:
    out = {"aliases": [], "status": "", "type": ""}
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    if end == -1:
        return out
    fm = text[3:end]
    m = re.search(r"^status:\s*(.+)$", fm, re.MULTILINE)
    if m:
        out["status"] = m.group(1).strip().strip('"').strip("'")
    m = re.search(r"^type:\s*(.+)$", fm, re.MULTILINE)
    if m:
        out["type"] = m.group(1).strip().strip('"').strip("'")
    m = re.search(r"^aliases:\s*\[(.*?)\]", fm, re.MULTILINE)
    if m:
        out["aliases"] = [a.strip().strip('"').strip("'") for a in m.group(1).split(",") if a.strip()]
    else:
        am = re.search(r"^aliases:\s*$", fm, re.MULTILINE)
        if am:
            for line in fm[am.end():].splitlines():
                lm = re.match(r"^\s+-\s+(.+)$", line)
                if lm:
                    out["aliases"].append(lm.group(1).strip().strip('"').strip("'"))
                elif line.strip() and not line.startswith((" ", "\t")):
                    break
    return out


def core_person_name(basename: str):
    """'{{PERSON_4}} (TapTap)' → '{{PERSON_4}}' so a body mention of just the name still matches."""
    m = re.match(r"^(.+?)\s*[（(]", basename)
    if m:
        c = m.group(1).strip()
        if c and c != basename:
            return c
    return None


def body_after_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def collect_entries() -> dict:
    """Wiki content entries = link TARGETS we evaluate."""
    entries = {}
    for path in WIKI.rglob("*.md"):
        rel = str(path.relative_to(WIKI))
        if set(Path(rel).parts) & EXCLUDE_DIR_PARTS:
            continue
        if path.name in EXCLUDE_NAMES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        if fm.get("status", "").lower() == "redirect":
            continue
        clean = strip_c_prefix(path.stem)
        names = {clean}
        cp = core_person_name(clean)
        if cp:
            names.add(cp)
        names.update(a for a in fm.get("aliases", []) if a)
        outbound = {norm_link_target(m.group(1)) for m in WIKILINK_RE.finditer(text)}
        entries[rel] = {
            "rel": rel,
            "names": names,
            "cluster": cluster_of(rel),
            "lane": lane_of(rel),
            "outbound": outbound,
            "body": body_after_frontmatter(text),
            "is_index_like": bool(re.search(r"INDEX|index|导航|目录", path.stem))
            or fm.get("type", "") == "kb-index",
        }
    return entries


def gather_kb_sources():
    """Yield (pillar_label, outbound_set) for durable KB files outside 01 Wiki, so a
    Wiki page linked only from a Card/Project still counts as connected."""
    for d in KB_SOURCE_DIRS:
        base = VAULT / d
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            if set(path.parts) & EXCLUDE_DIR_PARTS:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            yield d, {norm_link_target(m.group(1)) for m in WIKILINK_RE.finditer(text)}


def run() -> dict:
    entries = collect_entries()

    name_to_rel = {}
    for rel, e in entries.items():
        for n in e["names"]:
            name_to_rel.setdefault(n, rel)

    # inbound[target_rel] = list of source CLUSTER labels (Wiki cluster, or pillar name).
    # Non-Wiki pillars (02 Cards / 03 Projects) are always cross-cluster by construction.
    inbound: dict[str, list[str]] = {rel: [] for rel in entries}
    for rel, e in entries.items():
        for tgt_name in e["outbound"]:
            tgt = name_to_rel.get(tgt_name)
            if tgt and tgt != rel:
                inbound[tgt].append(e["cluster"])
    for pillar, outset in gather_kb_sources():
        for tgt_name in outset:
            tgt = name_to_rel.get(tgt_name)
            if tgt:
                inbound[tgt].append(pillar)

    def cross_cluster_in(rel: str) -> int:
        c = entries[rel]["cluster"]
        return sum(1 for src_c in inbound[rel] if src_c != c)

    # --- under-connected: too few inbound links from the REST of the KB ---
    under = []
    for rel, e in entries.items():
        if e["is_index_like"]:
            continue
        xc = cross_cluster_in(rel)
        if xc < CROSS_MIN:
            under.append({
                "file": rel, "cluster": e["cluster"], "lane": e["lane"],
                "total_inbound": len(inbound[rel]), "cross_cluster_inbound": xc,
            })
    under.sort(key=lambda x: (x["cross_cluster_inbound"], x["total_inbound"]))

    # --- cluster gap rollup: sub-folders concentrating the under-connected entries
    #     (a cluster where most members are isolated = an island, e.g. 游戏系统) ---
    size_by_cluster: dict[str, int] = {}
    for e in entries.values():
        size_by_cluster[e["cluster"]] = size_by_cluster.get(e["cluster"], 0) + 1
    under_by_cluster: dict[str, int] = {}
    for u in under:
        under_by_cluster[u["cluster"]] = under_by_cluster.get(u["cluster"], 0) + 1
    clusters_with_gaps = sorted(
        ({"cluster": cl, "under_connected": n, "size": size_by_cluster.get(cl, n),
          "share": round(n / size_by_cluster.get(cl, n), 2)}
         for cl, n in under_by_cluster.items() if size_by_cluster.get(cl, n) >= CLUSTER_MIN_SIZE),
        key=lambda x: (-x["under_connected"], -x["share"]),
    )

    # --- unlinked mentions (Wiki body names another entity but never links it) ---
    match_names = sorted(
        ((n, r) for n, r in name_to_rel.items() if len(n) >= 2),
        key=lambda x: -len(x[0]),
    )
    raw = []
    cross_lane_excluded = 0
    for rel, e in entries.items():
        body, src_lane = e["body"], e["lane"]
        found = 0
        for name, tgt_rel in match_names:
            if tgt_rel == rel or name in e["names"]:
                continue
            tgt = entries[tgt_rel]
            if e["outbound"] & tgt["names"]:
                continue
            if name not in body:
                continue
            if src_lane in PROJECT_LANES and tgt["lane"] in PROJECT_LANES and src_lane != tgt["lane"]:
                cross_lane_excluded += 1
                continue
            conf = "high" if len(name) >= 4 else ("med" if len(name) >= 3 else "low")
            raw.append({
                "source": rel, "target": tgt_rel, "mention": name,
                "source_cluster": e["cluster"], "target_cluster": tgt["cluster"],
                "confidence": conf,
            })
            found += 1
            if found >= MAX_MENTIONS_PER_SOURCE:
                break

    dedup = {}
    for m in raw:
        key = (m["source"], m["target"])
        if key not in dedup or _conf_rank(m["confidence"]) > _conf_rank(dedup[key]["confidence"]):
            dedup[key] = m
    mentions = sorted(dedup.values(), key=lambda m: (-_conf_rank(m["confidence"]), m["source"]))

    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "params": {"cross_min": CROSS_MIN, "cluster_min_size": CLUSTER_MIN_SIZE,
                   "kb_source_dirs": list(KB_SOURCE_DIRS), "excluded_dirs": sorted(EXCLUDE_DIR_PARTS)},
        "summary": {
            "scanned": len(entries),
            "under_connected": len(under),
            "clusters_with_gaps": len(clusters_with_gaps),
            "unlinked_mentions": len(mentions),
            "cross_lane_excluded": cross_lane_excluded,
        },
        "clusters_with_gaps": clusters_with_gaps,
        "under_connected": under,
        "unlinked_mentions": mentions,
    }


def main() -> int:
    try:
        prev = 0
        if REPORT.exists():
            try:
                prev = json.loads(REPORT.read_text(encoding="utf-8")).get("summary", {}).get("under_connected", 0)
            except Exception:
                pass

        report = run()
        s = report["summary"]
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        log_event(ROUTINE, "info",
                  f"scanned={s['scanned']} under={s['under_connected']} clusters={s['clusters_with_gaps']} "
                  f"mentions={s['unlinked_mentions']} xlane_excl={s['cross_lane_excluded']}", **s)

        print(f"[relation-gaps] scanned {s['scanned']} Wiki entries")
        print(f"  under-connected (cross-cluster KB inbound < {CROSS_MIN}): {s['under_connected']}")
        print(f"  clusters concentrating the gap:")
        for c in report["clusters_with_gaps"][:8]:
            print(f"    · {c['cluster']}  ({c['under_connected']}/{c['size']} = {int(c['share']*100)}% under-connected)")
        print(f"  missing-link candidates: {s['unlinked_mentions']} (cross-lane dropped: {s['cross_lane_excluded']})")
        print(f"  report -> {REPORT}")

        if s["under_connected"] > prev and s["under_connected"] > 0:
            if under_run_cap(ROUTINE, MAX_ALERTS_PER_DAY):
                notify_feishu(
                    ROUTINE,
                    f"🔗 relation-gaps: {s['under_connected']} under-connected Wiki entries across "
                    f"{s['clusters_with_gaps']} cluster(s), {s['unlinked_mentions']} missing-link candidates. "
                    f"Run /relation-map to review + wire them.",
                )
        return 0
    except Exception as e:
        log_event(ROUTINE, "error", f"relation-gaps failed: {e}")
        print(f"[relation-gaps] ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
