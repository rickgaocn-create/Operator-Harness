#!/usr/bin/env python3
"""Build generated underlays for /operate and future model flows.

Contract:
- Source Graph indexes entities, claims, workstreams, decisions, open questions,
  tasks, and source anchors.
- Taste Engine v1 includes only 09 Rules/_judgment/* nodes and
  .claude/_state/corrections.jsonl.
- Cards-as-principles excluded. Cards may appear in Source Graph context only.
- Generated Cards, Actions, Wiki pages, and Tasks are abandoned by default.
- Writes only .claude/_state/underlays/* and never edits canonical vault files.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VAULT  # noqa: E402

RULE = "09 Rules/underlays.md"
OUT_DIR = VAULT / ".claude" / "_state" / "underlays"
SOURCE_GRAPH_PATH = OUT_DIR / "source-graph.json"
TASTE_ENGINE_PATH = OUT_DIR / "taste-engine.json"
REPORT_PATH = OUT_DIR / "underlay-report.md"

ACTION_DIR = VAULT / "10 Action"
CARD_DIR = VAULT / "02 Cards"
PROJECT_DIR = VAULT / "03 Projects"
TASK_ROOT = VAULT / "06 Tasks"
JUDGMENT_DIR = VAULT / "09 Rules" / "_judgment"
CORRECTIONS = VAULT / ".claude" / "_state" / "corrections.jsonl"
SOURCE_NOTE_DIRS = [
    VAULT / "00 Raw" / "Clippings",
    VAULT / "00 Raw" / "会议纪要",
    VAULT / "04 Notes" / "Research",
    VAULT / "04 Notes" / "Session Logs",
    VAULT / "04 Notes" / "auto-reports",
]

CONFIDENCE_LABELS = ["source-anchored", "file-derived", "inferred", "needs-review"]
KNOWN_ENTITY_PATTERNS = [
    ("B站", re.compile(r"哔哩哔哩|Bilibili|B\s*站|B站", re.I)),
    ("TapTap", re.compile(r"TapTap", re.I)),
    ("好游快爆", re.compile(r"好游快爆")),
    ("4399", re.compile(r"4399")),
]
SKIP_PARTS = {".git", ".obsidian", ".trash", "node_modules", "__pycache__"}


def rel(path: Path) -> str:
    try:
        return path.relative_to(VAULT).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_scalar(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    return value


def frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[3:end].strip("\n")
    out: dict[str, Any] = {}
    current: str | None = None
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if re.match(r"^\S[^:]*:\s*", line):
            key, val = line.split(":", 1)
            current = key.strip()
            out[current] = parse_scalar(val) if val.strip() else []
        elif current and line.strip().startswith("- "):
            if not isinstance(out.get(current), list):
                out[current] = [out[current]]
            out[current].append(parse_scalar(line.strip()[2:]))
    return out


def body_without_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    if end == -1:
        return text
    return text[end + 4 :].lstrip()


def title_from_body(text: str, fallback: str) -> str:
    for line in body_without_frontmatter(text).splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def wikilinks(text: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for m in re.finditer(r"!?\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]", text):
        target = m.group(1).strip()
        display = (m.group(2) or "").strip()
        name = display or target.split("/")[-1]
        if target:
            out.append({"target": target, "name": name})
    return out


def source_anchor_values(fm: dict[str, Any]) -> list[str]:
    vals: list[str] = []
    for key in ("source_anchors", "source-anchor", "source-note", "source-context", "source", "rule-source"):
        val = fm.get(key)
        if not val:
            continue
        if isinstance(val, list):
            vals.extend(str(v) for v in val if str(v).strip())
        else:
            vals.append(str(val))
    return vals


def iter_markdown(root: Path) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for p in root.rglob("*.md"):
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        out.append(p)
    return sorted(out)


def clean_text(value: str, cap: int = 500) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    return value[: cap - 1] + "…" if len(value) > cap else value


def section(text: str, heading: str) -> str:
    pat = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.M)
    m = pat.search(text)
    if not m:
        return ""
    nxt = re.search(r"^##\s+", text[m.end() :], re.M)
    return text[m.end() : m.end() + nxt.start()] if nxt else text[m.end() :]


def table_rows(block: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and cells[0].lower() == "date":
            continue
        if len(cells) >= 2:
            rows.append(cells)
    return rows


def task_fields(line: str) -> dict[str, str]:
    return {m.group(1).strip(): m.group(2).strip() for m in re.finditer(r"\{\{([^:}]+)::\s*([^}]*)\}\}", line)}


def task_clean_text(line: str) -> str:
    line = re.sub(r"\{\{[^}]+}}", "", line)
    line = re.sub(r"^\s*-\s*\[[^\]]*]\s*", "", line)
    return clean_text(line, 300)


def task_chain_anchor(cleaned: str) -> str | None:
    marker = r"\|" if r"\|" in cleaned else "|"
    if marker not in cleaned:
        return None
    prefix = cleaned.split(marker, 1)[0].strip()
    prefix = re.sub(r"^[^\w\u4e00-\u9fff]+", "", prefix).strip()
    if 1 <= len(prefix) <= 40:
        return prefix
    return None


def add_entity(
    entities: dict[str, dict[str, Any]],
    name: str,
    source_path: str,
    entity_type: str,
    confidence: str,
    evidence: str = "",
    aliases: list[str] | None = None,
) -> None:
    name = clean_text(name, 120)
    if not name:
        return
    item = entities.setdefault(
        name,
        {
            "name": name,
            "types": [],
            "aliases": [],
            "sources": [],
            "confidence": confidence,
        },
    )
    if entity_type not in item["types"]:
        item["types"].append(entity_type)
    for alias in aliases or []:
        alias = clean_text(alias, 80)
        if alias and alias not in item["aliases"] and alias != name:
            item["aliases"].append(alias)
    source = {"path": source_path, "confidence": confidence}
    if evidence:
        source["evidence"] = clean_text(evidence, 240)
    if source not in item["sources"]:
        item["sources"].append(source)
    if item["confidence"] != "source-anchored" and confidence == "source-anchored":
        item["confidence"] = confidence


def add_known_entities(entities: dict[str, dict[str, Any]], text: str, source_path: str, entity_type: str) -> None:
    for canonical, pattern in KNOWN_ENTITY_PATTERNS:
        if pattern.search(text or ""):
            add_entity(entities, canonical, source_path, entity_type, "file-derived", evidence=text)


def counterparty_segments(value: str) -> list[str]:
    pieces = re.split(r"[；;]\s*", value or "")
    return [clean_text(p, 160) for p in pieces if clean_text(p)]


def is_internal_ratio_target(text: str) -> bool:
    if not re.search(r"7:3|７:３|73\s*分|5:5", text or ""):
        return False
    return bool(re.search(r"目标|非已达成|不对外|TBD-内部|我方|{{PROJECT_A}}|CP|分阶段|谈判", text or ""))


def scan_tasks() -> list[dict[str, Any]]:
    files = list(TASK_ROOT.glob("*.md"))
    files.extend(PROJECT_DIR.glob("*/Tasks.md"))
    bindings: list[dict[str, Any]] = []
    for path in sorted(set(files)):
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            if "{{operonId::" not in line:
                continue
            fields = task_fields(line)
            cleaned = task_clean_text(line)
            contexts = [c.strip() for c in fields.get("contexts", "").split(";") if c.strip()]
            state_match = re.match(r"\s*-\s*\[([^\]]*)]", line)
            binding = {
                "operonId": fields.get("operonId", ""),
                "status": fields.get("status", ""),
                "priority": fields.get("priority", ""),
                "dateDue": fields.get("dateDue", ""),
                "contexts": contexts,
                "chain_anchor": task_chain_anchor(cleaned),
                "text": cleaned,
                "checked_state": state_match.group(1) if state_match else "",
                "source_path": rel(path),
                "line": line_no,
                "confidence": "file-derived",
            }
            bindings.append(binding)
    return bindings


def scan_actions(entities: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    workstreams: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    open_questions: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    for path in iter_markdown(ACTION_DIR):
        text = read_text(path)
        fm = frontmatter(text)
        rpath = rel(path)
        title = title_from_body(text, path.stem)
        source_vals = source_anchor_values(fm)
        for value in source_vals:
            anchors.append({"source_path": rpath, "anchor": value, "confidence": "source-anchored"})
        for link in wikilinks(text):
            add_entity(entities, link["name"], rpath, "wikilink", "file-derived", evidence=link["target"])
        counterparty = str(fm.get("counterparty", ""))
        add_known_entities(entities, counterparty + "\n" + text[:2500], rpath, "counterparty")
        for seg in counterparty_segments(counterparty):
            add_entity(entities, seg, rpath, "counterparty", "file-derived", evidence=counterparty)
        ws = {
            "id": path.stem,
            "title": title,
            "source_path": rpath,
            "project": fm.get("project", ""),
            "horizon": fm.get("horizon", ""),
            "status": fm.get("status", ""),
            "owner": fm.get("owner", ""),
            "counterparty": counterparty,
            "chain_anchor": fm.get("chain-anchor", ""),
            "okr_link": fm.get("okr-link", ""),
            "next_action": fm.get("next-action", ""),
            "confidence": "file-derived",
        }
        workstreams.append(ws)

        for row in table_rows(section(text, "Decisions")):
            date = row[0] if len(row) > 0 else ""
            decision = row[1] if len(row) > 1 else ""
            rationale = row[2] if len(row) > 2 else ""
            item = {
                "date": date,
                "decision": clean_text(decision, 500),
                "rationale": clean_text(rationale, 500),
                "source_path": rpath,
                "workstream": path.stem,
                "confidence": "file-derived",
            }
            if is_internal_ratio_target(decision + " " + rationale):
                item["counterparty_agreement"] = False
                item["agreement_note"] = "Internal target or negotiation posture; not a counterparty agreement."
            decisions.append(item)
            claims.append({
                "claim": clean_text(decision, 500),
                "kind": "decision",
                "source_path": rpath,
                "confidence": "file-derived",
                "counterparty_agreement": item.get("counterparty_agreement"),
            })

        oq = section(text, "Open Questions / Blockers")
        for line_no, line in enumerate(text.splitlines(), 1):
            if not oq or line not in oq or not re.match(r"\s*-\s*\[[ xX-]?]\s+", line):
                continue
            open_questions.append({
                "question": task_clean_text(line),
                "source_path": rpath,
                "line": line_no,
                "workstream": path.stem,
                "confidence": "file-derived",
            })
    return workstreams, decisions, open_questions, claims, anchors


def scan_cards(entities: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    cards: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    for path in iter_markdown(CARD_DIR):
        if path.name.startswith("_card-lint-log") or path.name == "(C) README.md":
            continue
        text = read_text(path)
        fm = frontmatter(text)
        rpath = rel(path)
        title = title_from_body(text, path.stem)
        source_vals = source_anchor_values(fm)
        confidence = "source-anchored" if source_vals else "file-derived"
        for value in source_vals:
            anchors.append({"source_path": rpath, "anchor": value, "confidence": "source-anchored"})
        for link in wikilinks(text):
            add_entity(entities, link["name"], rpath, "wikilink", "file-derived", evidence=link["target"])
        cards.append({
            "id": path.stem,
            "title": title,
            "source_path": rpath,
            "source_note": fm.get("source-note", ""),
            "status": fm.get("status", ""),
            "confidence": confidence,
            "taste_engine_source": False,
        })
        claims.append({
            "claim": title,
            "kind": "card-title",
            "source_path": rpath,
            "confidence": confidence,
            "taste_engine_source": False,
        })
    return cards, claims, anchors


def scan_project_artifacts(entities: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    artifacts: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    for path in iter_markdown(PROJECT_DIR):
        if path.name == "Tasks.md":
            continue
        text = read_text(path)
        fm = frontmatter(text)
        rpath = rel(path)
        for link in wikilinks(text):
            add_entity(entities, link["name"], rpath, "wikilink", "file-derived", evidence=link["target"])
        add_known_entities(entities, text[:4000], rpath, "project-artifact")
        source_vals = source_anchor_values(fm)
        for value in source_vals:
            anchors.append({"source_path": rpath, "anchor": value, "confidence": "source-anchored"})
            claims.append({
                "claim": f"{title_from_body(text, path.stem)} source anchor: {value}",
                "kind": "source-anchor",
                "source_path": rpath,
                "confidence": "source-anchored",
            })
        artifacts.append({
            "id": path.stem,
            "title": title_from_body(text, path.stem),
            "source_path": rpath,
            "type": fm.get("type", ""),
            "project": fm.get("project", path.parent.name),
            "source_anchor_count": len(source_vals),
            "confidence": "file-derived",
        })
    return artifacts, claims, anchors


def scan_source_notes(entities: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    notes: list[dict[str, Any]] = []
    claims: list[dict[str, Any]] = []
    anchors: list[dict[str, Any]] = []
    paths: set[Path] = set()
    for root in SOURCE_NOTE_DIRS:
        paths.update(iter_markdown(root))
    for path in iter_markdown(VAULT / "04 Notes"):
        if any(part in {"daily notes", "weekly", "12-week", "vault-evolve", "_system"} for part in path.parts):
            continue
        text = read_text(path)
        fm = frontmatter(text)
        doc_type = str(fm.get("type", "")).lower()
        if re.search(r"meeting|summary|bd-update|market-intel|research|source", doc_type):
            paths.add(path)

    for path in sorted(paths):
        text = read_text(path)
        fm = frontmatter(text)
        rpath = rel(path)
        title = title_from_body(text, path.stem)
        for link in wikilinks(text):
            add_entity(entities, link["name"], rpath, "wikilink", "file-derived", evidence=link["target"])
        add_known_entities(entities, text[:4000], rpath, "source-note")
        source_vals = source_anchor_values(fm)
        for value in source_vals:
            anchors.append({"source_path": rpath, "anchor": value, "confidence": "source-anchored"})
        notes.append({
            "id": path.stem,
            "title": title,
            "source_path": rpath,
            "type": fm.get("type", ""),
            "source_anchor_count": len(source_vals),
            "confidence": "source-anchored" if source_vals else "file-derived",
        })
        if source_vals:
            claims.append({
                "claim": f"{title} source anchored",
                "kind": "source-note",
                "source_path": rpath,
                "confidence": "source-anchored",
            })
    return notes, claims, anchors


def build_source_graph() -> dict[str, Any]:
    entities: dict[str, dict[str, Any]] = {}
    task_bindings = scan_tasks()
    workstreams, decisions, open_questions, claims, anchors = scan_actions(entities)
    cards, card_claims, card_anchors = scan_cards(entities)
    artifacts, artifact_claims, artifact_anchors = scan_project_artifacts(entities)
    source_notes, source_note_claims, source_note_anchors = scan_source_notes(entities)
    claims.extend(card_claims)
    claims.extend(artifact_claims)
    claims.extend(source_note_claims)
    anchors.extend(card_anchors)
    anchors.extend(artifact_anchors)
    anchors.extend(source_note_anchors)

    by_chain: dict[str, list[str]] = defaultdict(list)
    for task in task_bindings:
        if task.get("chain_anchor") and task.get("operonId"):
            by_chain[task["chain_anchor"]].append(task["operonId"])
    for ws in workstreams:
        ws["task_operonIds"] = sorted(set(by_chain.get(str(ws.get("chain_anchor", "")), [])))

    fixture = source_graph_fixture(workstreams, decisions, open_questions, task_bindings, entities)
    return {
        "version": 1,
        "generated_at": now_iso(),
        "rule": RULE,
        "confidence_labels": CONFIDENCE_LABELS,
        "scope": {
            "included": ["Actions", "Operon task lines", "Cards as source context", "Project docs", "source anchors"],
            "excluded": ["Taste inference from Cards", "generated Cards", "generated Actions", "generated Wiki replacements"],
        },
        "counts": {
            "entities": len(entities),
            "workstreams": len(workstreams),
            "task_bindings": len(task_bindings),
            "decisions": len(decisions),
            "open_questions": len(open_questions),
            "claims": len(claims),
            "cards_as_context": len(cards),
            "project_artifacts": len(artifacts),
            "source_notes": len(source_notes),
            "source_anchors": len(anchors),
        },
        "entities": sorted(entities.values(), key=lambda e: e["name"]),
        "workstreams": workstreams,
        "task_bindings": task_bindings,
        "decisions": decisions,
        "open_questions": open_questions,
        "claims": claims,
        "cards_as_source_context": cards,
        "project_artifacts": artifacts,
        "source_notes": source_notes,
        "source_anchors": anchors,
        "fixture_checks": fixture,
    }


def extract_bold_field(body: str, label: str) -> str:
    m = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", body)
    return clean_text(m.group(1), 800) if m else ""


def build_taste_engine() -> dict[str, Any]:
    values: list[dict[str, Any]] = []
    frameworks: list[dict[str, Any]] = []
    for path in sorted(JUDGMENT_DIR.glob("*.md")):
        text = read_text(path)
        fm = frontmatter(text)
        body = body_without_frontmatter(text)
        node_type = fm.get("type", "value" if path.name.startswith("v-") else "framework")
        entry = {
            "id": fm.get("id", path.stem),
            "name": fm.get("name", path.stem),
            "type": node_type,
            "status": fm.get("status", ""),
            "applies_to": fm.get("applies-to", []),
            "source": fm.get("source", ""),
            "source_path": rel(path),
            "source_type": "value_node" if node_type == "value" else "framework_node",
            "confidence": "file-derived",
        }
        if node_type == "value":
            entry["statement"] = extract_bold_field(body, "Statement")
            entry["tells_honored"] = extract_bold_field(body, "Tells when it's being honored")
            values.append(entry)
        else:
            entry["procedure"] = extract_bold_field(body, "Procedure")
            entry["embodies"] = fm.get("embodies", [])
            frameworks.append(entry)

    correction_rules: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    if CORRECTIONS.exists():
        for line_no, raw in enumerate(CORRECTIONS.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                record = json.loads(raw)
            except Exception as e:
                skipped.append({"line": line_no, "reason": str(e)[:160]})
                continue
            reusable = any(record.get(k) for k in ("candidate_rule", "correction", "touches", "promoted_to"))
            if not reusable:
                continue
            correction_rules.append({
                "ts": record.get("ts", ""),
                "skill": record.get("skill", ""),
                "artifact": record.get("artifact", ""),
                "correction": record.get("correction", ""),
                "why": record.get("why", ""),
                "candidate_rule": record.get("candidate_rule", ""),
                "status": record.get("status", ""),
                "promoted_to": record.get("promoted_to", ""),
                "touches": record.get("touches", {}),
                "source_path": f"{rel(CORRECTIONS)}:{line_no}",
                "source_type": "correction",
                "confidence": "file-derived",
            })

    fixture = taste_fixture(values, frameworks, correction_rules)
    return {
        "version": 1,
        "generated_at": now_iso(),
        "rule": RULE,
        "scope": {
            "included": ["09 Rules/_judgment/v-*.md", "09 Rules/_judgment/f-*.md", ".claude/_state/corrections.jsonl"],
            "excluded": ["Cards-as-principles", "general Card corpus", "Action prose", "unvalidated model-classified principles"],
        },
        "counts": {
            "values": len(values),
            "frameworks": len(frameworks),
            "correction_rules": len(correction_rules),
            "skipped_correction_lines": len(skipped),
        },
        "values": values,
        "frameworks": frameworks,
        "correction_rules": correction_rules,
        "skipped_corrections": skipped,
        "fixture_checks": fixture,
    }


def source_graph_fixture(
    workstreams: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    open_questions: list[dict[str, Any]],
    task_bindings: list[dict[str, Any]],
    entities: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    channel_path = "10 Action/12 Active/T260526-channel-resource-push.md"
    channel_workstreams = [w for w in workstreams if w["source_path"] == channel_path]
    channel_decisions = [d for d in decisions if d["source_path"] == channel_path]
    channel_questions = [q for q in open_questions if q["source_path"] == channel_path]
    channel_tasks = [t for t in task_bindings if t.get("chain_anchor") == "渠道争取"]
    ratio_flags = [
        d for d in channel_decisions
        if re.search(r"7:3|5:5", d.get("decision", "") + d.get("rationale", ""))
        and d.get("counterparty_agreement") is False
    ]
    return [
        {"check": "channel workstream found", "pass": bool(channel_workstreams)},
        {"check": "B站 entity found", "pass": "B站" in entities},
        {"check": "TapTap entity found", "pass": "TapTap" in entities},
        {"check": "好游快爆 entity found", "pass": "好游快爆" in entities},
        {"check": "4399 entity found", "pass": "4399" in entities},
        {"check": "渠道争取 task bindings found", "pass": bool(channel_tasks), "count": len(channel_tasks)},
        {"check": "channel decisions found", "pass": bool(channel_decisions), "count": len(channel_decisions)},
        {"check": "channel open questions found", "pass": bool(channel_questions), "count": len(channel_questions)},
        {"check": "7:3 not treated as counterparty agreement", "pass": bool(ratio_flags)},
    ]


def taste_fixture(values: list[dict[str, Any]], frameworks: list[dict[str, Any]], correction_rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    value_ids = {v.get("id") for v in values}
    framework_ids = {f.get("id") for f in frameworks}
    every_source = all(e.get("source_path") and e.get("source_type") for e in [*values, *frameworks, *correction_rules])
    return [
        {"check": "v-truth-over-comfort found", "pass": "v-truth-over-comfort" in value_ids},
        {"check": "f-rigor-verification found", "pass": "f-rigor-verification" in framework_ids},
        {"check": "v-resource-exchange found", "pass": "v-resource-exchange" in value_ids},
        {"check": "correction-derived rules found", "pass": bool(correction_rules), "count": len(correction_rules)},
        {"check": "every taste entry has source path and type", "pass": every_source},
    ]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def report_lines(source_graph: dict[str, Any], taste: dict[str, Any]) -> list[str]:
    source_pass = sum(1 for c in source_graph["fixture_checks"] if c["pass"])
    taste_pass = sum(1 for c in taste["fixture_checks"] if c["pass"])
    lines = [
        "---",
        "type: generated-underlay-report",
        "generated-by: build_underlays.py",
        "created-by: codex",
        "status: generated",
        "biz-eval: skip",
        "localize-cn: skip",
        "---",
        "",
        "# Underlay Report",
        "",
        f"Generated: {source_graph['generated_at']}",
        f"Rule: [[{RULE[:-3]}]]",
        "",
        "## Outputs",
        "",
        f"- `source-graph.json`: {source_graph['counts']['entities']} entities, {source_graph['counts']['claims']} claims, {source_graph['counts']['workstreams']} workstreams, {source_graph['counts']['task_bindings']} task bindings.",
        f"- `taste-engine.json`: {taste['counts']['values']} values, {taste['counts']['frameworks']} frameworks, {taste['counts']['correction_rules']} correction-derived rules.",
        f"- Skipped correction lines: {taste['counts']['skipped_correction_lines']}.",
        "",
        "## Fixture Checks",
        "",
        f"Source Graph: {source_pass}/{len(source_graph['fixture_checks'])} passed.",
    ]
    for check in source_graph["fixture_checks"]:
        suffix = f" ({check.get('count')})" if "count" in check else ""
        lines.append(f"- [{'x' if check['pass'] else ' '}] {check['check']}{suffix}")
    lines.extend(["", f"Taste Engine v1: {taste_pass}/{len(taste['fixture_checks'])} passed."])
    for check in taste["fixture_checks"]:
        suffix = f" ({check.get('count')})" if "count" in check else ""
        lines.append(f"- [{'x' if check['pass'] else ' '}] {check['check']}{suffix}")
    lines.extend([
        "",
        "## Guardrails",
        "",
        "- Cards-as-principles excluded.",
        "- Cards are Source Graph context only.",
        "- Generated Cards/Wiki/Actions are abandoned by default.",
        "- Builder writes only `.claude/_state/underlays/*`.",
        "- `7:3` in `T260526-channel-resource-push.md` is flagged as an internal target / negotiation posture, not a counterparty agreement.",
    ])
    if taste["skipped_corrections"]:
        lines.extend(["", "## Skipped Corrections", ""])
        for item in taste["skipped_corrections"][:10]:
            lines.append(f"- line {item['line']}: {item['reason']}")
    return lines


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_graph = build_source_graph()
    taste = build_taste_engine()
    write_json(SOURCE_GRAPH_PATH, source_graph)
    write_json(TASTE_ENGINE_PATH, taste)
    REPORT_PATH.write_text("\n".join(report_lines(source_graph, taste)) + "\n", encoding="utf-8")
    failed = [c for c in source_graph["fixture_checks"] + taste["fixture_checks"] if not c["pass"]]
    print(
        f"wrote {rel(SOURCE_GRAPH_PATH)}, {rel(TASTE_ENGINE_PATH)}, {rel(REPORT_PATH)} "
        f"({len(failed)} fixture failure(s))"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
