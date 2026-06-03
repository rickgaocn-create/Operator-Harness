#!/usr/bin/env python3
"""judgment-loop CLI.

    python cli.py lens     --config <toml> --context "bd proposal partnership"
    python cli.py harvest  --config <toml> [--tier logic|prior|domain] [--json]
    python cli.py distill  --config <toml> [--status | --brief] [--threshold N]
    python cli.py registry --config <toml> [--out manifest.md] [--json]

Stdlib-only. Exit 0 on success.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from jloop import config as cfgmod          # noqa: E402
from jloop import lens as lensmod            # noqa: E402
from jloop import harvest as harvestmod      # noqa: E402
from jloop import distill as distillmod      # noqa: E402
from jloop import registry as registrymod    # noqa: E402


def cmd_lens(args):
    cfg = cfgmod.load(args.config)
    rep = lensmod.build(cfg, args.context, args.cap or cfg.lens_cap)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2)); return
    print(f"FRAME SET for context: {args.context!r}")
    print(f"graph: {cfg.judgment_dir}")
    print(f"{len(rep['frames'])} divergence frames (+ {len(rep['baseline_floor'])} baseline floor)\n")
    for f in rep["frames"]:
        print(f"[{f['role']:8}] {f['id']:22} — {f['name']}")
        print(f"           {f['vantage'][:160]}")
    if rep["baseline_floor"]:
        print(f"\nbaseline floor (carried, not diverged): {', '.join(b['id'] for b in rep['baseline_floor'])}")


def cmd_harvest(args):
    cfg = cfgmod.load(args.config)
    rep = harvestmod.build(cfg, tier=args.tier, cap=args.cap or None)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2)); return
    by_type, by_tier = {}, {}
    for c in rep["candidates"]:
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1
        by_tier[c.get("tier", "?")] = by_tier.get(c.get("tier", "?"), 0) + 1
    print("JUDGMENT BACKLOG HARVEST (scripted, 0 tokens)")
    print(f"root: {rep['root']}")
    print(f"returning {rep['returned']} of {rep['total_found']} (cap {rep['cap']}), logic-tier first — "
          + ", ".join(f"{k}={v}" for k, v in sorted(by_tier.items())) + "\n")
    for c in rep["candidates"]:
        hint = ",".join(c["touches_hint"]) or "—"
        secs = "+".join(k for k, v in c["passages"].items() if v)
        print(f"[{c['signal']}] {c.get('tier','?'):6} {c['type']:18} {c['status']:8} {c['title'][:54]}")
        print(f"      {c['source']}")
        print(f"      touches-hint: {hint}   sections: {secs}")
    print("\nNothing written to the loop. Next (off-path): a model reads --json, dedups vs the graph, clusters into patterns for approval.")


def cmd_distill(args):
    cfg = cfgmod.load(args.config)
    rep = distillmod.build(cfg, threshold=args.threshold)
    if args.status and not args.brief:
        print(json.dumps({"new_event_count": rep["new_event_count"],
                          "threshold": rep["threshold"], "threshold_met": rep["threshold_met"]})); return
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2)); return
    print("JUDGMENT DISTILL BRIEF")
    print(f"new events: {rep['new_event_count']}  |  threshold: {rep['threshold']}  |  "
          f"{'MET — distill due' if rep['threshold_met'] else 'NOT met (manual override only)'}")
    print(f"write proposals to: {rep['proposals_path']}  (status: pending-review)\n")
    for c in rep["clusters"]:
        print(f"NODE {c['node']}  ({c['type']}) {c['name']}")
        for p in c["placeholders"]:
            print(f"    placeholder edge: \"{p['label']}\"  [{p['marker']}: {p['note']}]")
        if c["derivable_framework_edges"]:
            print(f"    derivable reverse-edges (frameworks that embody this value): {', '.join(c['derivable_framework_edges'])}")
        for e in c["events"]:
            print(f"      - [{e['polarity']} {e['ts']}] rule: {e['candidate_rule']}")
            if e["why"]:
                print(f"          why: {e['why']}")
        print()
    print("Model step: per node, propose edge fills / rule promotions / new nodes as JSONL")
    print("(one per line) to the proposals file. Never edit node files here — human-approved only.")


def cmd_registry(args):
    cfg = cfgmod.load(args.config)
    rep = registrymod.build(cfg)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2)); return
    if args.out:
        out = cfg.resolve(args.out) if not os.path.isabs(args.out) else args.out
        with open(out, "w", encoding="utf-8") as f:
            f.write(registrymod.manifest_md(rep))
        print(f"manifest written: {out}")
    c = rep["counts"]
    g = rep["gaps"]
    print(f"graph: {rep['graph_dir']}")
    print(f"{c['total']} nodes — {c['values']} values · {c['frameworks']} frameworks · {len(rep['coverage'])} applies-to tags")
    print(f"gaps: values-no-framework={g['values_no_framework'] or '—'} | "
          f"dangling={['%s->%s' % (a, b) for a, b in g['frameworks_dangling_embodies']] or '—'} | "
          f"no-applies-to={g['nodes_no_applies_to'] or '—'}")


def main():
    ap = argparse.ArgumentParser(prog="judgment-loop")
    sub = ap.add_subparsers(dest="cmd", required=True)

    lp = sub.add_parser("lens", help="apply the graph to an output context (application arm)")
    lp.add_argument("--config", required=True); lp.add_argument("--context", required=True)
    lp.add_argument("--cap", type=int, default=0); lp.add_argument("--json", action="store_true")
    lp.set_defaults(fn=cmd_lens)

    hp = sub.add_parser("harvest", help="mine the corpus for judgment candidates (scripted)")
    hp.add_argument("--config", required=True)
    hp.add_argument("--tier", choices=["logic", "prior", "domain"])
    hp.add_argument("--cap", type=int, default=0); hp.add_argument("--json", action="store_true")
    hp.set_defaults(fn=cmd_harvest)

    dp = sub.add_parser("distill", help="brief the model on what to propose for the graph")
    dp.add_argument("--config", required=True)
    dp.add_argument("--threshold", type=int, default=None)
    dp.add_argument("--status", action="store_true"); dp.add_argument("--brief", action="store_true")
    dp.add_argument("--json", action="store_true")
    dp.set_defaults(fn=cmd_distill)

    rp = sub.add_parser("registry", help="manifest of the graph: nodes, edges, coverage, gaps")
    rp.add_argument("--config", required=True)
    rp.add_argument("--out", default=""); rp.add_argument("--json", action="store_true")
    rp.set_defaults(fn=cmd_registry)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
