#!/usr/bin/env python3
"""wechat_schedule_capture.py — the SCHEDULE-capture feeder (WeChat -> calendar).

Born from the 2026-06-02 vault-drift miss: meeting reschedules live in WeChat but never reach the
vault, so vault-first hands back stale reality. This is the meeting-capture twin of judgment_capture:
a scripted, ~0-token pre-filter that scans recent WeChat (via the WeFlow local API) for SCHEDULING
messages (a time/date + a meeting signal), and surfaces candidate meetings for a human-confirmed
calendar add. It does NOT write the calendar itself (propose-only, like the other capture feeders);
the in-session step reconciles against the calendar and adds on confirm (per 09 Rules/source-of-truth).

  python wechat_schedule_capture.py [--sessions 25] [--per-chat 12] [--days 14] [--drain] [--json]
Exit 0 always. READ-ONLY on WeChat; --drain appends candidates to _state/schedule-candidates.jsonl.
"""
from __future__ import annotations
import argparse, io, json, os, re, sys, time, urllib.request, urllib.error

if sys.platform == "win32" and not getattr(sys.stdout, "_h_utf8", False):  # sentinel: never double-wrap
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdout._h_utf8 = True

VAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # routines -> .claude -> {{USER_NAME}}
OUT = os.path.join(VAULT, ".claude", "_state", "schedule-candidates.jsonl")
BASE = os.environ.get("WEFLOW_BASE", "http://127.0.0.1:5031")
TOKEN = os.environ.get("WEFLOW_TOKEN", "1c6c31d82f8e5e2c912fc4f3cf763374")

# --- scheduling signal patterns (zh + en) ---------------------------------------------------------
TIME_RE = re.compile(r"(\d{1,2}[:：]\d{2})|([上下]午\s*\d{1,2}\s*点)|(\d{1,2}\s*点(?:半|\d{1,2}分?)?)"
                     r"|((?:两|三|四|五|六|七|八|九|十|十一|十二)\s*点(?:半)?)|(早上|晚上|中午|傍晚|凌晨)")
DATE_RE = re.compile(r"(\d{1,2}\s*月\s*\d{1,2}\s*[日号])|(\d{1,2}[/.]\d{1,2})|(今天|今晚|明天|明早|明晚|后天|大后天)"
                     r"|([下本这上]?\s*周\s*[一二三四五六日天])|(星期\s*[一二三四五六日天])|\b(mon|tue|wed|thu|fri|sat|sun)\b")
MEET_RE = re.compile(r"(约(?!定俗)|见个?面|碰个?(?:面|头)|会议|拜访|到访|过来|过去|面谈|开会|聚|饭局|晚宴|路演"
                     r"|定(?:在|个时间|下来)|安排在?|sync|meeting|catch ?up|见你|见一面)", re.I)
# noise: forwarded long text, links, pure stickers
SKIP_RE = re.compile(r"^(https?://|\[链接\]|\[图片\]|\[表情\]|\[视频\]|\[文件\]|\[语音\])")
# declines / non-commitments — a time word here is NOT a new meeting (e.g. "今天不过去了")
NEG_RE = re.compile(r"(不来|不过来|不过去|来不了|去不了|不参加|没法来|没空|改天再|下次吧|算了)")
# promotional / coupon group noise — skip the whole chat
PROMO_RE = re.compile(r"(优惠|立减|领\d|抢券|红包|抽奖|福利社|广告|特价|秒杀|拼团|饭票)")


def _norm_ts(m: dict) -> int:
    for k in ("timestamp", "createTime", "ts", "time", "createTimestamp"):
        v = m.get(k)
        if v:
            try:
                iv = int(float(v))
                if iv > 1_000_000_000_000:   # milliseconds -> seconds
                    iv //= 1000
                if iv > 1_000_000_000:        # plausible epoch seconds
                    return iv
            except Exception:
                pass
    return 0


def _get(path: str):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + TOKEN})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.load(r)


def is_scheduling(text: str) -> dict | None:
    t = str(text or "").strip()
    if not t or len(t) > 220 or SKIP_RE.match(t) or NEG_RE.search(t):
        return None
    has_time = bool(TIME_RE.search(t))
    has_date = bool(DATE_RE.search(t))
    has_meet = bool(MEET_RE.search(t))
    # a real scheduling line = (time or date) AND (a meeting signal OR both time+date present)
    if (has_time or has_date) and (has_meet or (has_time and has_date)):
        return {"time_hits": TIME_RE.findall(t) and [m for g in TIME_RE.findall(t) for m in g if m][:3],
                "date_hits": [m for g in DATE_RE.findall(t) for m in (g if isinstance(g, tuple) else (g,)) if m][:3],
                "meeting": has_meet}
    return None


def scan(sessions: int, per_chat: int, days: int):
    try:
        s = _get("/api/v1/sessions")
    except Exception as e:
        print(f"WeFlow unreachable ({e}) — is the WeChat bridge running at {BASE}?")
        return [], 0
    cutoff = time.time() - days * 86400
    chats = [x for x in s.get("sessions", [])
             if x.get("sessionType") in ("private", "group")
             and (x.get("lastTimestamp") or 0) >= cutoff]
    chats = chats[:sessions]
    cands, scanned = [], 0
    for c in chats:
        talker = c.get("username")
        name = c.get("displayName", "")
        if PROMO_RE.search(name):   # skip coupon / promo broadcast groups
            continue
        try:
            d = _get(f"/api/v1/messages?talker={talker}&limit={per_chat}")
        except Exception:
            continue
        for m in (d.get("messages") or []):
            scanned += 1
            txt = m.get("content") or m.get("text") or ""
            sig = is_scheduling(txt)
            if sig:
                ts = _norm_ts(m)
                cands.append({"talker": talker, "chat": name, "ts": ts,
                              "when": time.strftime("%m-%d %H:%M", time.localtime(ts)) if ts else "?",
                              "sender": m.get("senderName") or "", "text": str(txt)[:160], "signals": sig,
                              "status": "pending-confirm"})
    cands.sort(key=lambda x: x["ts"], reverse=True)
    return cands, scanned


def drain(cands):
    """Append only NEW candidates (dedup by talker+ts+text-prefix). Append-only; reversible."""
    seen = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8", errors="replace"):
            try:
                o = json.loads(line)
                seen.add((o.get("talker"), o.get("ts"), str(o.get("text", ""))[:40]))
            except Exception:
                pass
    new = [c for c in cands if (c["talker"], c["ts"], c["text"][:40]) not in seen]
    if new:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "a", encoding="utf-8") as fh:
            for c in new:
                fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    return len(new)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=int, default=25)
    ap.add_argument("--per-chat", type=int, default=12)
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--drain", action="store_true", help="append new candidates to schedule-candidates.jsonl")
    args = ap.parse_args()
    cands, scanned = scan(args.sessions, args.per_chat, args.days)
    n_new = drain(cands) if args.drain else 0
    if args.json:
        print(json.dumps(cands, ensure_ascii=False, indent=2)); return 0
    print(f"scanned ~{scanned} msgs across recent chats — {len(cands)} scheduling candidate(s)"
          f"{f' ({n_new} new drained)' if args.drain else ''}\n")
    for c in cands[:20]:
        print(f"  [{c['when']}] {c['chat'][:18]:18} {c['sender'][:8]:8}: {c['text'][:70]}")
    if cands:
        print("\nNext: reconcile each against the calendar (09 Rules/source-of-truth) + add on confirm. Propose-only — no auto-write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
