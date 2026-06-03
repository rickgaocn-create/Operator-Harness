"""The application arm — config-driven port of the in-vault judgment_lens.

Given an output context (artifact type + domain + audience), match it against each
graph node's `applies-to` tags and return the FRAME SET for an idea-divergence pass:
the relevant lenses (ranked, lead first), the always-on `baseline` lenses (the floor —
carried, not diverged), plus one WILD outside frame for range. Each frame carries a
generator vantage-prompt.

This is the cheap, scripted half. The application is AMBIENT: when drafting an open-
ended output, run this and let the lenses shape the angle. For a rare make-or-break
artifact, escalate by hand to a hard divergence (one isolated generator pass per frame,
then a critic). No standing command, no model tokens here.
"""
from __future__ import annotations

import glob
import os
import re

from .config import Config

# Outside-view frames (the reserved wild slot). NOT personal lenses — deliberate
# distortions that surface angles your own values wouldn't. One is rotated in per run.
WILD_FRAMES = [
    {"id": "wild-counterparty", "name": "the counterparty across the table",
     "vantage": "Argue this from the other side's seat: what makes THEM say yes fastest, and what are they really optimizing for that you're not naming?"},
    {"id": "wild-first-principles", "name": "remove the load-bearing assumption",
     "vantage": "Name the one assumption everyone treats as fixed here, delete it, and re-approach the whole problem from there."},
    {"id": "wild-competitor", "name": "a sharper competitor",
     "vantage": "You are a faster, more ruthless competitor handed this same problem. What angle do you take that the incumbent never would?"},
]

# Appended to every generated frame prompt — the corpus-grounding/rigor floor, ENFORCED
# (not just nominally "carried"). Kills the abstract-drift failure mode where a value frame
# wanders into "define the category / publish a whitepaper / reshape the ecosystem" instead
# of a move someone can make on Monday. See evals/RESULTS.md (the A′ test).
GROUNDING_RIDER = (
    "Every angle must name a concrete lever — a specific party, number, date, or a first "
    "action taken on day one. Do not offer a category, standard, ecosystem, or whitepaper "
    "as an end in itself; if you invoke one it must reduce to a named action with a deadline, "
    "or be cut."
)


def split_fm(text):
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


def body_field(body, label):
    m = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$", body, re.MULTILINE)
    return m.group(1).strip() if m else ""


def load_nodes(cfg: Config):
    fm, bd = cfg.graph.fm, cfg.graph.body
    nodes = []
    for path in sorted(glob.glob(os.path.join(cfg.judgment_dir, "*.md"))):
        head, body = split_fm(open(path, encoding="utf-8", errors="replace").read())
        nid = fm_value(head, fm["id"]) or os.path.splitext(os.path.basename(path))[0]
        nodes.append({
            "id": nid,
            "name": fm_value(head, fm["name"]),
            "type": fm_value(head, fm["type"]),
            "applies_to": fm_list(head, fm["applies_to"]),
            "essence": body_field(body, bd["statement"]) or body_field(body, bd["procedure"]),
            "rules": body_field(body, bd["rules"]) or body_field(body, bd["operationalized"]),
        })
    return nodes


def select(cfg: Config, context, cap):
    terms = set(re.findall(r"[a-z0-9\-]+", context.lower()))
    scored, baseline = [], []
    for n in load_nodes(cfg):
        at = set(n["applies_to"])
        if cfg.graph.baseline_tag in at:
            baseline.append(n)
            continue
        s = len(terms & at)
        if s:
            scored.append((s, n))
    scored.sort(key=lambda x: x[0], reverse=True)
    lead = scored[0][1] if scored else None
    support = [n for _, n in scored[1:cap]]
    return lead, support, baseline


def vantage_prompt(n):
    bits = [f"Re-frame this entire problem through the lens of '{n['name']}'."]
    if n["essence"]:
        bits.append(n["essence"])
    if n["rules"]:
        bits.append(f"It serves: {n['rules']}.")
    bits.append("Generate 4-6 distinct candidate angles for the output from THIS lens only. Do not evaluate, rank, or hedge.")
    bits.append(GROUNDING_RIDER)
    return " ".join(bits)


def build(cfg: Config, context, cap=None):
    cap = cap or cfg.lens_cap
    lead, support, baseline = select(cfg, context, cap)
    frames = []
    if lead:
        frames.append({"id": lead["id"], "name": lead["name"], "role": "lead", "vantage": vantage_prompt(lead)})
    for n in support:
        frames.append({"id": n["id"], "name": n["name"], "role": "support", "vantage": vantage_prompt(n)})
    wild = WILD_FRAMES[sum(ord(c) for c in context) % len(WILD_FRAMES)]  # deterministic per context
    frames.append({"id": wild["id"], "name": wild["name"], "role": "wild", "vantage": wild["vantage"]})
    floor = [{"id": n["id"], "name": n["name"], "essence": (n["essence"] or "")[:120]} for n in baseline]
    return {
        "context": context,
        "frames": frames,
        "baseline_floor": floor,
        "note": "Each frame -> ONE isolated generator pass (no shared context, generator-only). "
                "Then a critic scores/clusters/flags-traps and picks the lead angle, ENFORCING the "
                "grounding gate: drop any angle that doesn't reduce to a named party + number/date + "
                "first action. Baseline floor (corpus-grounding + rigor) is enforced at synthesis, not "
                "just carried. This full pipeline (priors + frames + grounding) IS the quality bar: a "
                "human comparison scored it 7/10 vs 3/10 for a stripped priors-only draft (see evals/RESULTS.md). "
                "For a major output, run best-of-N on top — a few independent full-pipeline passes, then keep/merge "
                "the best — as a reliability multiplier against run-to-run variance, NOT a replacement for the frames. "
                "The terminal judge is the human: in the same eval an LLM judge rated the 3/10 draft ~= the 7/10 one.",
    }
