"""morning-sweep — pull the previous day's messaging-platform dialogs into ONE raw bundle.

Channels: WeChat (via WeFlow @ :5031) + Feishu (via lark-cli profile morty).
Reuses the pull primitives from daily-wechat-ingest / daily-feishu-ingest (DRY).

Contract:
- NO vault writes except the raw bundle under .claude/.daily-ingest-queue/_sweep/.
- NO LLM calls (extraction is the /morning-sweep skill's job, reading this bundle).
- Source-resilient: each channel degrades independently and reports its own status,
  so a dead WeFlow or a blind Feishu profile never blocks the other channel.

stdout: one JSON line {bundle, status:[...]} for the skill to parse.
stderr: human-readable progress.
"""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

VAULT_ROOT = Path(r'{{VAULT_ROOT}}')
SKILLS = VAULT_ROOT / '.claude' / 'skills'
SWEEP_DIR = VAULT_ROOT / '.claude' / '.daily-ingest-queue' / '_sweep'
STATE_FILE = VAULT_ROOT / '.claude' / '_state' / 'dashboard' / 'sweep-state.json'


WEFLOW_EXE = r'{{USER_HOME}}\AppData\Local\Programs\WeFlow\WeFlow.exe'


def _load(modname: str, path: Path):
    """Import a sibling ingest script as a module without running its main()."""
    spec = importlib.util.spec_from_file_location(modname, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ensure_weflow(wx, attempts: int = 12) -> bool:
    """If WeFlow (:5031) is down, launch it and wait. Returns True once /health responds."""
    import subprocess, time
    try:
        wx.api_get('/health')
        return True
    except Exception:
        pass
    try:
        subprocess.Popen([WEFLOW_EXE], creationflags=getattr(subprocess, 'DETACHED_PROCESS', 0))
    except Exception:
        return False
    for _ in range(attempts):
        time.sleep(2)
        try:
            wx.api_get('/health')
            return True
        except Exception:
            continue
    return False


def pull_wechat(since_epoch: float, limit: int = 500):
    """-> (status_str, [{name, msgs:[{time,sender,text}]}]). Newest history wins per chat."""
    try:
        wx = _load('wx_ingest', SKILLS / 'daily-wechat-ingest' / 'scripts' / 'ingest.py')
    except Exception as e:
        return (f'LOAD_FAIL: {e}', [], None)
    if not _ensure_weflow(wx):
        return ('UNREACHABLE — WeFlow down and auto-start failed (launch WeFlow.exe manually; port :5031)', [], None)
    try:
        pri = wx.load_priority()
    except Exception as e:
        return (f'PRIORITY_FAIL: {e}', [], None)
    entries = [(g['name'], g['id']) for g in pri.get('groups', [])] + \
              [(d['name'], d['id']) for d in pri.get('dms', [])]
    out, latest_seen = [], 0
    for name, talker in entries:
        try:
            msgs = wx.pull_chat(talker, since_epoch, max_msgs=limit)
        except Exception:
            msgs = []
        rows = []
        for m in sorted(msgs, key=lambda x: x.get('createTime', 0)):
            text = wx.clean_text(m)
            if not text:
                continue
            ct = m.get('createTime', 0)
            latest_seen = max(latest_seen, ct)
            ts = datetime.fromtimestamp(ct)
            rows.append({'time': ts.strftime('%m-%d %H:%M'),
                         'sender': m.get('senderUsername', '?'), 'text': text[:300]})
        if rows:
            out.append({'name': name, 'msgs': rows})
    # If nothing in window, report the freshest history timestamp we *could* see (staleness signal).
    freshest = None
    if not out:
        peek = 0
        for name, talker in entries:
            try:
                r = wx.api_get('/api/v1/messages', {'talker': talker, 'limit': 1})
                for m in r.get('messages', []):
                    peek = max(peek, m.get('createTime', 0))
            except Exception:
                pass
        if peek:
            freshest = datetime.fromtimestamp(peek).strftime('%Y-%m-%d %H:%M')
    status = 'LIVE' if out else (f'EMPTY in window — freshest history msg = {freshest}' if freshest
                                 else 'EMPTY in window')
    return (status, out, freshest)


def pull_feishu(since_dt: datetime, max_chats: int = 50, max_msgs: int = 50):
    try:
        fs = _load('fs_ingest', SKILLS / 'daily-feishu-ingest' / 'scripts' / 'ingest.py')
    except Exception as e:
        return (f'LOAD_FAIL: {e}', [])
    try:
        chats_resp = fs.lark(['im', '+chat-list', '--as', 'user', '--page-size', str(max_chats)])
    except Exception as e:
        return (f'AUTH_FAIL: {e}', [])
    chats_a = chats_resp.get('data', {}).get('chats') or chats_resp.get('data', {}).get('items') or []
    pri_path = SKILLS / 'daily-feishu-ingest' / 'scripts' / 'priority_chats.json'
    chats_b = []
    if pri_path.exists():
        try:
            chats_b = json.loads(pri_path.read_text(encoding='utf-8')).get('chats', [])
        except Exception:
            pass
    seen, chats = set(), []
    for c in (chats_a + chats_b):
        cid = c.get('chat_id') or c.get('id')
        if cid and cid not in seen:
            seen.add(cid)
            chats.append(c)
    out = []
    for chat in chats:
        cid = chat.get('chat_id') or chat.get('id')
        name = chat.get('name') or chat.get('description') or '(unnamed)'
        if not cid or not str(cid).startswith('oc_'):
            continue
        try:
            mr = fs.lark(['im', '+chat-messages-list', '--as', 'user', '--chat-id', cid, '--page-size', str(max_msgs)])
        except Exception:
            continue
        rows = []
        for m in mr.get('data', {}).get('messages', []):
            ts = fs.parse_ts(m.get('create_time', ''))
            if not ts or ts < since_dt:
                continue
            sender = (m.get('sender') or {}).get('name') or (m.get('sender') or {}).get('id', '?')
            content = (m.get('content') or '')[:300].replace('\n', ' ')
            rows.append({'time': ts.strftime('%m-%d %H:%M'), 'sender': sender, 'text': content})
        if rows:
            out.append({'name': name, 'msgs': rows})
    status = 'LIVE' if out else 'EMPTY — no msgs in window (or bot not a member of more groups; see SKILL.md § Source coverage)'
    return (status, out)


def _load_state() -> dict:
    """Read sweep-state.json. Missing/corrupt → {}."""
    try:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        print(f'[sweep] state read failed: {e}', file=sys.stderr)
    return {}


def _save_state(patch: dict) -> None:
    """Merge patch into sweep-state.json; preserves keys we don't touch (e.g. lastCommitAt)."""
    cur = _load_state()
    cur.update(patch)
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f'[sweep] state write failed: {e}', file=sys.stderr)


def _parse_iso_local(s: str) -> datetime | None:
    """Parse ISO-8601 (with or without tz) into a NAIVE local datetime (matches the
    rest of this script, which uses datetime.now() naive). Returns None on failure."""
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        return dt
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since-days', type=float, default=1.0,
                    help='days back from start-of-today (1 = since yesterday 00:00). '
                         'Ignored when --since-last or --since is provided.')
    ap.add_argument('--since-last', action='store_true',
                    help='read lastRunAt from sweep-state.json and use that as the window start. '
                         'Falls back to --since-days if state is missing.')
    ap.add_argument('--since', default=None,
                    help='explicit ISO-8601 window start (overrides --since-last / --since-days)')
    ap.add_argument('--channels', default='wechat,feishu')
    args = ap.parse_args()

    now = datetime.now()
    state = _load_state()
    window_start = None
    window_source = None

    if args.since:
        window_start = _parse_iso_local(args.since)
        window_source = f'--since {args.since}' if window_start else None
    if window_start is None and args.since_last:
        last = _parse_iso_local(state.get('lastRunAt', ''))
        if last:
            window_start = last
            window_source = f'--since-last (lastRunAt={state.get("lastRunAt")})'
        else:
            print('[sweep] --since-last: no prior lastRunAt in state; falling back to --since-days',
                  file=sys.stderr)
    if window_start is None:
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        window_start = start_today - timedelta(days=args.since_days)
        window_source = f'--since-days {args.since_days}'

    since_epoch = window_start.timestamp()
    chans = [c.strip() for c in args.channels.split(',')]
    print(f'[sweep] window: {window_start.strftime("%Y-%m-%d %H:%M")} → {now.strftime("%Y-%m-%d %H:%M")} ({window_source})',
          file=sys.stderr)

    bundle = [f'# 昨日扫描原料 (raw) — generated {now.strftime("%Y-%m-%d %H:%M")}',
              f'\nWindow: {window_start.strftime("%Y-%m-%d %H:%M")} → {now.strftime("%Y-%m-%d %H:%M")} ({window_source})\n',
              '## Source status']
    status_lines, sections = [], []
    counts_by_channel = {}
    status_by_channel = {}

    if 'wechat' in chans:
        print('[sweep] pulling WeChat (WeFlow)...', file=sys.stderr)
        st, chats, _ = pull_wechat(since_epoch)
        n = sum(len(c['msgs']) for c in chats)
        status_lines.append(f'- WeChat (WeFlow): **{st}** — {n} msgs across {len(chats)} chats')
        sections.append(('WeChat', chats))
        counts_by_channel['wechat'] = {'msgs': n, 'chats': len(chats)}
        status_by_channel['wechat'] = st
    if 'feishu' in chans:
        print('[sweep] pulling Feishu (lark business-morty)...', file=sys.stderr)
        st, chats = pull_feishu(window_start)
        n = sum(len(c['msgs']) for c in chats)
        status_lines.append(f'- Feishu (lark business-morty): **{st}** — {n} msgs across {len(chats)} chats')
        sections.append(('Feishu', chats))
        counts_by_channel['feishu'] = {'msgs': n, 'chats': len(chats)}
        status_by_channel['feishu'] = st

    bundle.extend(status_lines)
    for chan, chats in sections:
        bundle.append(f'\n## {chan}')
        if not chats:
            bundle.append('_(no messages in window)_')
        for c in chats:
            bundle.append(f'\n### {c["name"]} ({len(c["msgs"])} msgs)')
            for r in c['msgs']:
                bundle.append(f'- [{r["time"]}] {r["sender"]}: {r["text"]}')

    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SWEEP_DIR / f'{now.strftime("%Y-%m-%d")}-raw.md'
    out_path.write_text('\n'.join(bundle), encoding='utf-8')
    for s in status_lines:
        print('[sweep] ' + s.replace('**', ''), file=sys.stderr)

    _save_state({
        'lastRunAt': now.isoformat(timespec='seconds'),
        'lastWindow': {
            'start': window_start.isoformat(timespec='seconds'),
            'end': now.isoformat(timespec='seconds'),
            'source': window_source,
        },
        'lastStatus': status_by_channel,
        'lastCounts': counts_by_channel,
        'lastBundle': str(out_path),
    })

    print(json.dumps({'bundle': str(out_path), 'status': status_lines,
                      'window': {'start': window_start.isoformat(timespec='seconds'),
                                 'end': now.isoformat(timespec='seconds'),
                                 'source': window_source}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
