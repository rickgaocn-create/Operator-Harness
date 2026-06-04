#!/usr/bin/env python3
"""Stop hook (cross-platform port of mirror-to-feishu.ps1).

Mirrors the latest assistant text reply to the originating Feishu chat. No-op unless:
  (a) the prompting user message came from Feishu (a <channel source="...feishu..." chat_id="oc_…">
      tag, or an 'AFK session via Feishu' marker), AND
  (b) the assistant did NOT already call the Feishu reply tool this turn (avoid double-send), AND
  (c) the last assistant message hasn't already been mirrored (per-session dedup).

Sends via lark-cli (cross-platform npm), so it works on macOS unchanged. Never blocks Stop.
"""
import json, os, re, subprocess, sys

USER_HOME = os.path.expanduser(os.environ.get("HOME", "{{USER_HOME}}"))
STATE_DIR = os.path.join(USER_HOME, ".claude", "channels", "feishu")
LARK_PROFILE = os.environ.get("LARK_PROFILE", "business-morty")
CHAN_RE = re.compile(r'<channel\s+source="[^"]*feishu[^"]*"\s+chat_id="(oc_[^"]+)"', re.I)


def _read_transcript(path):
    try:
        if not path or not os.path.exists(path) or os.path.getsize(path) > 20_000_000:
            return []
        return [l for l in open(path, encoding="utf-8", errors="replace").read().splitlines() if l.strip()]
    except Exception:
        return []


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}
    session = payload.get("session_id") or "no-session"
    transcript = payload.get("transcript_path") or payload.get("transcriptPath") or ""
    lines = _read_transcript(transcript)
    if not lines:
        return 0

    # parse events; find feishu origin, whether reply tool used, last assistant text + id
    full = "\n".join(lines)
    chat_id = None
    m = CHAN_RE.search(full)
    if m:
        chat_id = m.group(1)
    is_afk_feishu = "AFK session via Feishu" in full
    if not chat_id and not is_afk_feishu:
        return 0  # not a Feishu-origin session

    reply_tool_used = False
    last_text, last_id = "", ""
    for ln in lines:
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        msg = ev.get("message") if isinstance(ev, dict) else None
        role = ev.get("role") or (msg or {}).get("role") or ev.get("type")
        if role != "assistant" or not isinstance(msg, dict):
            continue
        mid = msg.get("id") or ev.get("uuid") or ""
        texts = []
        for b in (msg.get("content") or []):
            if isinstance(b, dict):
                if b.get("type") == "tool_use" and "feishu" in str(b.get("name", "")).lower() and "reply" in str(b.get("name", "")).lower():
                    reply_tool_used = True
                if b.get("type") == "text":
                    texts.append(b.get("text", ""))
        t = "".join(texts).strip()
        if t:
            last_text, last_id = t, mid

    if reply_tool_used or not last_text:
        return 0  # assistant already replied via the tool, or nothing to mirror

    # resolve chat_id for AFK-feishu sessions (no inline tag) from feishu.env
    if not chat_id:
        envp = os.path.join(USER_HOME, ".afk-code", "feishu.env")
        try:
            for line in open(envp, encoding="utf-8"):
                if line.startswith("FEISHU_CHAT_ID"):
                    chat_id = line.split("=", 1)[1].strip().strip('"')
        except Exception:
            pass
    if not chat_id:
        return 0

    # per-session dedup: skip if we already mirrored this assistant message id
    os.makedirs(STATE_DIR, exist_ok=True)
    stamp = os.path.join(STATE_DIR, f"mirror-{session}.lastuuid")
    try:
        if last_id and os.path.exists(stamp) and open(stamp, encoding="utf-8").read().strip() == last_id:
            return 0
    except Exception:
        pass

    # send via lark-cli (bash single-quote safe; metachars handled by passing as argv, not shell)
    lark = "lark-cli"
    try:
        subprocess.run([lark, "--profile", LARK_PROFILE, "im", "+messages-send",
                        "--as", "bot", "--chat-id", chat_id, "--text", last_text],
                       capture_output=True, text=True, timeout=20)
    except FileNotFoundError:
        return 0  # lark-cli not installed -> silent no-op
    except Exception:
        return 0
    try:
        with open(stamp, "w", encoding="utf-8") as fh:
            fh.write(last_id)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # mirroring must never block Stop
