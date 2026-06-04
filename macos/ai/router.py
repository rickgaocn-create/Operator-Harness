#!/usr/bin/env python3
"""Local-vs-cloud router for harness AI ops.

Cheap, high-frequency, low-judgment tasks -> local model (free/private/offline).
Judgment-heavy, forwardable, high-stakes tasks -> cloud (caller handles; this returns tier='cloud').
This is the lever that fixes the per-session cost the cloud-only harness pays: the residue scans,
classifications, triage, and distillation drafts that fire constantly now run on-device.

Usage as a library:
    from router import route
    r = route("residue-scan", text)          # -> {'tier','result'|'defer'}
CLI:
    echo "<text>" | python3 router.py --task residue-scan
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_llm  # noqa: E402

# task class -> tier. LOCAL = run on-device; CLOUD = defer to the caller's cloud model.
LOCAL_TASKS = {
    "residue-scan",       # CN english-residue detection (the localize-cn gate, made cheap)
    "classify",           # correction class_key / signal type tagging
    "triage",             # is this inbox item urgent / which project
    "distill-draft",      # first-pass correction -> candidate-rule draft (human still gates)
    "success-mine",       # endorse-detection over a transcript window
    "ocr-postprocess",    # clean / structure raw OCR text
    "summarize-short",    # one-line summaries for digests
}
CLOUD_TASKS = {
    "biz-critic", "strategy", "forwardable", "best-of-n", "deep-meeting", "judgment",
}


def tier_for(task):
    if task in LOCAL_TASKS:
        return "local"
    if task in CLOUD_TASKS:
        return "cloud"
    return "cloud"  # unknown -> safe default is the smarter model


def route(task, prompt, system="", max_tokens=512, force=None):
    """Return {'tier', and either 'result' (local ran) or 'defer':True (caller should run cloud)}."""
    tier = force or tier_for(task)
    if tier == "local":
        if local_llm.available():
            try:
                return {"tier": "local", "result": local_llm.complete(
                    prompt, system=system, max_tokens=max_tokens)}
            except Exception as e:
                return {"tier": "local-failed", "error": str(e), "defer": True}
        # no local model up -> degrade to cloud
        return {"tier": "cloud", "defer": True, "reason": "no local model reachable"}
    return {"tier": "cloud", "defer": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--system", default="")
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--force", choices=["local", "cloud"])
    a = ap.parse_args()
    text = sys.stdin.read() if not sys.stdin.isatty() else ""
    out = route(a.task, text, system=a.system, max_tokens=a.max_tokens, force=a.force)
    print(json.dumps(out, ensure_ascii=False))
    # exit 0 always; the 'defer' flag tells the caller to run cloud
    return 0


if __name__ == "__main__":
    sys.exit(main())
