#!/usr/bin/env python3
"""On-device OCR via the macOS Vision framework — free, offline, no API.

Recovers part of the WeChat gap (OCR a WeChat screenshot instead of reading the Windows client DB)
and powers image-clipping capture. Primary path uses pyobjc's Vision (VNRecognizeTextRequest, the
real on-device engine); falls back to a Shortcuts action if pyobjc isn't installed.

Setup (primary): pip3 install pyobjc-framework-Vision pyobjc-framework-Quartz
Usage:
  python3 ocr.py <image.png> [--lang zh-Hans en-US]            # print recognized text
  python3 ocr.py <image.png> --to-vault ["source label"]       # OCR -> 00 Raw/Clippings
  screencapture -i -x /tmp/s.png && python3 ocr.py /tmp/s.png   # capture a region then OCR
"""
import argparse, os, subprocess, sys


def vision_ocr(path, langs):
    """Real on-device OCR via Vision. Returns recognized text or raises if pyobjc unavailable."""
    import Vision
    import Quartz
    from Foundation import NSURL

    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        raise RuntimeError(f"cannot read image: {path}")
    cg = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)

    results = []

    def handler(request, error):
        for obs in (request.results() or []):
            cand = obs.topCandidates_(1)
            if cand and cand.count():
                results.append(cand.objectAtIndex_(0).string())

    req = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    req.setRecognitionLevel_(1)  # accurate
    req.setUsesLanguageCorrection_(True)
    try:
        req.setRecognitionLanguages_(langs)
    except Exception:
        pass
    Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg, {}) \
        .performRequests_error_([req], None)
    return "\n".join(results)


def shortcuts_ocr(path):
    """Fallback: a Shortcuts action named 'OCR Image' that takes a file and returns text."""
    try:
        out = subprocess.run(["shortcuts", "run", "OCR Image", "-i", path,
                              "-o", "-"], capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError("no pyobjc Vision and no `shortcuts` CLI — install pyobjc-framework-Vision")


def ocr(path, langs):
    if sys.platform != "darwin":
        raise RuntimeError("OCR uses macOS Vision — run on macOS")
    try:
        return vision_ocr(path, langs)
    except ImportError:
        return shortcuts_ocr(path)


def to_vault(text, source):
    vault = os.path.expanduser(os.environ.get("OPERATOR_VAULT_ROOT", "{{VAULT_ROOT}}"))
    inbox = os.path.join(vault, "00 Raw", "Clippings")
    os.makedirs(inbox, exist_ok=True)
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    out = os.path.join(inbox, f"(C) ocr-{ts}.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"---\ntype: clipping\ncreated-by: ocr\nsource: {source}\n---\n\n{text}\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--lang", nargs="+", default=["zh-Hans", "en-US"])
    ap.add_argument("--to-vault", nargs="?", const="ocr", default=None)
    a = ap.parse_args()
    text = ocr(a.image, a.lang)
    if a.to_vault is not None:
        path = to_vault(text, a.to_vault)
        print(f"OCR -> {path}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
