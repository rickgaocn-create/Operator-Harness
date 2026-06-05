"""daily-wechat-ingest — pull last 24h of WeChat activity from priority chats,
download media, organize, surface into the day's daily note + Inbox.

Designed to run as a scheduled task (Windows Task Scheduler at 06:00) and also
on-demand via `--days N` for backfill.

Two-tier: works without ANTHROPIC_API_KEY (digest + media saved, no vision);
upgrades to OCR + task-extraction when key is present.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.parse, urllib.request, html, base64, mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# Force UTF-8 stdout for Chinese console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

VAULT_ROOT = Path(r'D:\Administrator\Documents\{{USER_NAME}}')
SCRIPT_DIR = Path(__file__).parent
QUEUE_DIR = VAULT_ROOT / '.claude' / '.daily-ingest-queue'
WEFLOW_BASE = os.environ.get('WEFLOW_BASE', 'http://127.0.0.1:5031')

# Token — try env first, fallback to known-good (re-rotates per session in practice; user can override via env)
WEFLOW_TOKEN = os.environ.get('WEFLOW_TOKEN', '1c6c31d82f8e5e2c912fc4f3cf763374')
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# ---------- HTTP helpers ----------

def api_get(path: str, params: dict | None = None, timeout: int = 30) -> dict:
    qs = '?' + urllib.parse.urlencode(params) if params else ''
    url = f'{WEFLOW_BASE}{path}{qs}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {WEFLOW_TOKEN}', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def http_download(url: str, out: Path) -> bool:
    if not url:
        return False
    try:
        headers = {}
        # WeFlow's /api/v1/media/* endpoints require the same Bearer token
        if url.startswith(WEFLOW_BASE) or '127.0.0.1:5031' in url:
            headers['Authorization'] = f'Bearer {WEFLOW_TOKEN}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as r:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  ! download failed for {url}: {e}", file=sys.stderr)
        return False

# ---------- Message parsing ----------

def clean_text(msg: dict) -> str:
    c = (msg.get('content') or '').strip()
    if not c:
        return ''
    if not c.lstrip().startswith('<'):
        return c
    title = re.search(r'<title>(.*?)</title>', c, re.DOTALL)
    if title:
        t = html.unescape(title.group(1)).strip()
        if t:
            return t
    desc = re.search(r'<des>(.*?)</des>', c, re.DOTALL)
    if desc:
        return f"[card] {html.unescape(desc.group(1)).strip()[:80]}"
    return ''

# crude task / timeline regex — keep small, layered with vision later
TASK_HINTS = re.compile(r'(确认|待办|todo|@\S+\s+请|麻烦|帮忙|跟进|follow up|deadline|截止|5/\d|6/\d|7/\d|周[一二三四五六日]|下周|本周|EOD|EOW)')
DATE_HINTS = re.compile(r'\b(\d{1,2}[/月]\d{1,2}|\d{4}-\d{2}-\d{2})\b')

def detect_task(text: str) -> bool:
    if not text or len(text) < 8:
        return False
    return bool(TASK_HINTS.search(text))

# ---------- Vision (Claude API, optional) ----------

def vision_extract(image_path: Path, context: str) -> str | None:
    """If ANTHROPIC_API_KEY set, call Claude vision to extract business info from an image."""
    if not ANTHROPIC_KEY:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
        mime = mimetypes.guess_type(image_path.name)[0] or 'image/jpeg'
        if mime not in ('image/jpeg', 'image/png', 'image/gif', 'image/webp'):
            return None
        data = base64.standard_b64encode(image_path.read_bytes()).decode('ascii')
        resp = client.messages.create(
            model='claude-haiku-4-5',
            max_tokens=600,
            messages=[{
                'role': 'user',
                'content': [
                    {'type': 'image', 'source': {'type': 'base64', 'media_type': mime, 'data': data}},
                    {'type': 'text', 'text': (
                        f"Context: this image was sent in a WeChat business chat ({context}). "
                        f"Extract any: (1) event names, (2) dates/times, (3) locations, (4) people names, "
                        f"(5) action items/tasks for the recipient. If the image is purely decorative or "
                        f"contains no actionable info, return 'NO-OP'. Be concise; bullet list."
                    )}
                ]
            }]
        )
        for block in resp.content:
            if getattr(block, 'type', '') == 'text':
                return block.text.strip()
        return None
    except Exception as e:
        print(f"  ! vision_extract failed: {e}", file=sys.stderr)
        return None

# ---------- Ingest core ----------

def load_priority() -> dict:
    return json.loads((SCRIPT_DIR / 'priority_chats.json').read_text(encoding='utf-8'))

def discover_active_chats(priority: dict, since_epoch: float, sessions_by_id: dict) -> tuple[list[dict], list[dict]]:
    """Filter pre-fetched sessions for chats active in window that match priority keywords
    but aren't already in priority_chats.json. Returns (extra_groups, extra_dms).

    Closes the gap where the priority list goes stale — new WeChat groups created last
    week / new contacts pinged last night were invisible until added by hand.
    """
    cfg = priority.get('auto_discover', {})
    if not cfg.get('enabled'):
        return [], []
    keywords = cfg.get('name_keywords', [])
    known_ids = {g['id'] for g in priority['groups']} | {d['id'] for d in priority['dms']}
    extra_groups, extra_dms = [], []
    for s in sessions_by_id.values():
        if s['username'] in known_ids:
            continue
        if s.get('lastTimestamp', 0) < since_epoch:
            continue
        name = s.get('displayName', '')
        if not any(k in name for k in keywords):
            continue
        # Skip subscription/service accounts ("channel" type — game media etc.)
        if s.get('sessionType') == 'channel':
            continue
        entry = {'id': s['username'], 'name': name}
        if s.get('sessionType') == 'group':
            extra_groups.append(entry)
        else:
            extra_dms.append(entry)
    return extra_groups, extra_dms

def diagnose_sync_lag(priority: dict, since_epoch: float, results: list[dict]) -> list[dict]:
    """Cross-check: any priority chat whose session.lastTimestamp is in window but
    where we pulled 0 messages is a SYNC LAG case — WeFlow has the session metadata
    but hasn't decrypted/exported the Msg table. User needs to open the chat in
    WeFlow's UI to trigger extraction. Returns lag-list for surfacing in digest.
    """
    try:
        r = api_get('/api/v1/sessions', {'limit': 2000})
    except Exception:
        return []
    by_id = {s['username']: s for s in r.get('sessions', [])}
    pulled_zero = {res['talker'] for res in results if res['count'] == 0}
    lag = []
    for chat in priority['groups'] + priority['dms']:
        if chat['id'] not in pulled_zero:
            continue
        s = by_id.get(chat['id'])
        if not s:
            continue
        if s.get('lastTimestamp', 0) >= since_epoch:
            ts = datetime.fromtimestamp(s['lastTimestamp']).strftime('%m-%d %H:%M')
            lag.append({'id': chat['id'], 'name': chat['name'], 'last_seen': ts})
    return lag

def pull_chat(talker: str, since_epoch: float, max_msgs: int = 200, expected_fresh: bool = False) -> list[dict]:
    """Pull recent messages; client-side filter on createTime since start/end YYYYMMDD silently returns 0.

    WeFlow notes (2026-05-28):
    - limit>=500 silently returns count=0 even when data exists. 200 works; bump only if a chat overflows.
    - Under burst load (>10 back-to-back queries), WeFlow occasionally returns 0 for chats that have data.
      Cursor likely gets evicted. Retry-on-empty when sessions endpoint says the chat is fresh.
    """
    def _one_call():
        r = api_get('/api/v1/messages', {'talker': talker, 'limit': max_msgs, 'media': 1, 'image': 1, 'voice': 0, 'video': 0, 'emoji': 0})
        return [m for m in r.get('messages', []) if m.get('createTime', 0) >= since_epoch]
    try:
        msgs = _one_call()
        if msgs or not expected_fresh:
            return msgs
        # Empty but caller expects data — retry up to 3x with backoff (let WeFlow re-warm cursor)
        for attempt in range(1, 4):
            time.sleep(0.5 * attempt)
            msgs = _one_call()
            if msgs:
                print(f"  ↻ pull_chat({talker[:20]}) recovered on retry {attempt}: {len(msgs)} msgs", file=sys.stderr)
                return msgs
        return []
    except Exception as e:
        print(f"  ! pull_chat({talker}) failed: {e}", file=sys.stderr)
        return []

def process_chat(name: str, talker: str, msgs: list[dict], attach_dir: Path, process_media: bool) -> dict:
    """Process one chat's window: organize media, build digest, detect tasks."""
    out = {'name': name, 'talker': talker, 'count': len(msgs), 'media': [], 'tasks': [], 'highlights': []}
    if not msgs:
        return out
    msgs.sort(key=lambda m: m.get('createTime', 0))
    for m in msgs:
        ts = datetime.fromtimestamp(m['createTime'])
        sender = m.get('senderUsername', '')
        text = clean_text(m)
        # media handling
        media_url = m.get('mediaUrl', '')
        media_fname = m.get('mediaFileName', '')
        if process_media and media_url and media_fname:
            safe = re.sub(r'[\\/:*?"<>|]', '_', media_fname)[:80]
            local = attach_dir / f"{ts.strftime('%H-%M')}-{name[:20]}-{safe}"
            if http_download(media_url, local):
                out['media'].append({'path': str(local.relative_to(VAULT_ROOT)), 'sender': sender, 'time': ts.isoformat(), 'kind': m.get('mediaType', '?'), 'vision': None})
                # vision pass (if key + image)
                if local.suffix.lower() in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                    vt = vision_extract(local, f"{name} / {sender}")
                    if vt and 'NO-OP' not in vt:
                        out['media'][-1]['vision'] = vt
                        # extract tasks from vision output
                        for line in vt.splitlines():
                            if line.strip().startswith(('-', '*')) and detect_task(line):
                                out['tasks'].append({'text': line.strip().lstrip('-* '), 'source': 'vision', 'chat': name, 'time': ts.isoformat()})
        # text task detection — but NOT for personal-mixed chats (process_media=False implies "personal channel, digest only")
        if process_media and text and detect_task(text):
            out['tasks'].append({'text': text[:200], 'source': 'text', 'chat': name, 'time': ts.isoformat(), 'sender': sender})
        # highlights
        if text and len(text) > 12:
            out['highlights'].append({'time': ts.strftime('%H:%M'), 'sender': sender, 'text': text[:140]})
    return out

def compose_digest(window_start: datetime, results: list[dict], lag: list[dict] | None = None) -> tuple[str, str]:
    """Return (daily-note-snippet, full-digest-md)."""
    lag = lag or []
    total_msgs = sum(r['count'] for r in results)
    total_media = sum(len(r['media']) for r in results)
    chats_with_activity = [r for r in results if r['count'] > 0]
    all_tasks = [t for r in results for t in r['tasks']]

    # daily note snippet (concise)
    lines = [
        f"\n### 🤖 daily-wechat-ingest {datetime.now().strftime('%H:%M')} → {total_msgs} messages from {len(chats_with_activity)} chats, {total_media} media files",
        f"*window: {window_start.strftime('%Y-%m-%d %H:%M')} → now · vision: {'ON' if ANTHROPIC_KEY else 'off (no API key)'}*",
        ''
    ]
    if all_tasks:
        lines.append('**Tasks surfaced:**')
        for t in all_tasks[:10]:
            tag = '#vision' if t.get('source') == 'vision' else ''
            lines.append(f"- [ ] {t['text']} — {t.get('chat','?')} {tag}".rstrip())
        if len(all_tasks) > 10:
            lines.append(f"- ...+{len(all_tasks) - 10} more in full digest")
        lines.append('')
    if total_media:
        lines.append('**Media saved:**')
        for r in chats_with_activity:
            for m in r['media']:
                vis = f" — *{m['vision'][:60]}…*" if m.get('vision') else ''
                lines.append(f"- `{m['path']}` — {r['name']} ({m['sender']}){vis}")
        lines.append('')
    if chats_with_activity:
        lines.append('**Chat threads (text content, newest 3 per chat):**')
        for r in chats_with_activity[:12]:
            if not r['highlights']:
                continue
            lines.append(f"\n*{r['name']}* ({r['count']} msgs)")
            for h in r['highlights'][-3:]:
                lines.append(f"  - `{h['time']}` **{h['sender']}**: {h['text']}")
        lines.append('')
    if lag:
        lines.append('**⚠ Sync lag — these chats had fresh activity but WeFlow didn\'t export messages:**')
        for L in lag:
            lines.append(f"- `{L['name']}` — session last active {L['last_seen']}; open in WeFlow UI to trigger export")
        lines.append('')
    snippet = '\n'.join(lines)

    # full digest
    full = [f"# WeChat Daily Ingest — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\nWindow: {window_start.strftime('%Y-%m-%d %H:%M')} → {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"\nTotal messages: {total_msgs} · media: {total_media} · vision: {'ON' if ANTHROPIC_KEY else 'off'}\n"]
    for r in chats_with_activity:
        full.append(f"\n## {r['name']}\n")
        full.append(f"- Messages: {r['count']}\n- Media: {len(r['media'])}\n- Tasks: {len(r['tasks'])}\n")
        if r['highlights']:
            full.append('### Highlights\n')
            for h in r['highlights']:
                full.append(f"- `{h['time']}` **{h['sender']}**: {h['text']}")
        if r['media']:
            full.append('\n### Media\n')
            for m in r['media']:
                full.append(f"- `{m['path']}` from {m['sender']} at {m['time']}")
                if m.get('vision'):
                    full.append(f"  - **vision says:** {m['vision']}")
        if r['tasks']:
            full.append('\n### Detected tasks\n')
            for t in r['tasks']:
                full.append(f"- [ ] {t['text']} — {t.get('sender','?')} @ {t['time']}")
    return snippet, '\n'.join(full)

def append_to_daily(snippet: str):
    today = datetime.now().strftime('%Y-%m-%d')
    daily = VAULT_ROOT / '04 Notes' / 'daily notes' / f'{today}.md'
    if not daily.exists():
        # create a minimal daily note if missing
        daily.parent.mkdir(parents=True, exist_ok=True)
        daily.write_text(f"---\ntype: daily\ndate: {today}\ncreated-by: daily-wechat-ingest\n---\n\n# {today}\n\n## Ingests\n", encoding='utf-8')
    content = daily.read_text(encoding='utf-8')
    if '## Ingests' not in content:
        content = content.rstrip() + '\n\n## Ingests\n'
    # insert after the Ingests header
    content = content.replace('## Ingests', f'## Ingests\n{snippet}', 1)
    daily.write_text(content, encoding='utf-8')
    print(f"appended to {daily}")

def append_to_inbox(tasks: list[dict]):
    if not tasks:
        return
    inbox = VAULT_ROOT / '06 Tasks' / 'Inbox.md'
    inbox.parent.mkdir(parents=True, exist_ok=True)
    if not inbox.exists():
        inbox.write_text('# Inbox\n\n', encoding='utf-8')
    lines = ['', f'<!-- daily-wechat-ingest {datetime.now().strftime("%Y-%m-%d %H:%M")} -->']
    for t in tasks:
        chat = t.get('chat', '?')
        src = '🤖vision' if t.get('source') == 'vision' else '📩'
        lines.append(f"- [ ] {t['text'][:180]} {src} #{chat.replace(' ', '_')[:30]} 📅 {datetime.now().strftime('%Y-%m-%d')}")
    with inbox.open('a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=float, default=1.0, help='Lookback window in days (default 1 = last 24h)')
    ap.add_argument('--dry-run', action='store_true', help='Pull + log; do not write to vault')
    ap.add_argument('--push-inbox', action='store_true',
                    help='Auto-push regex-detected tasks to Inbox.md. OFF by default since 2026-05-27 — '
                         'task intake now goes through /morning-sweep (confirm gate). Digest still writes regardless.')
    args = ap.parse_args()

    today_str = datetime.now().strftime('%Y-%m-%d')
    run_dir = QUEUE_DIR / today_str
    run_dir.mkdir(parents=True, exist_ok=True)
    attach_dir = VAULT_ROOT / '04 Notes' / 'daily notes' / f'{today_str}-attachments'
    attach_dir.mkdir(parents=True, exist_ok=True)

    window_start = datetime.now() - timedelta(days=args.days)
    since_epoch = window_start.timestamp()
    print(f"[ingest] window: {window_start.isoformat()} → now ({args.days} days)")
    print(f"[ingest] vision: {'ON' if ANTHROPIC_KEY else 'off (set ANTHROPIC_API_KEY)'}")

    # Health check
    try:
        api_get('/health')
    except Exception as e:
        print(f"ERROR: WeFlow API at {WEFLOW_BASE} not reachable. Is WeFlow running? {e}", file=sys.stderr)
        sys.exit(2)

    priority = load_priority()

    # One sessions sweep upfront — used for both auto-discover AND freshness-aware retry
    try:
        sess_resp = api_get('/api/v1/sessions', {'limit': 2000})
        sessions_by_id = {s['username']: s for s in sess_resp.get('sessions', [])}
    except Exception as e:
        print(f"  ! sessions sweep failed: {e}", file=sys.stderr)
        sessions_by_id = {}

    def _is_fresh(chat_id: str) -> bool:
        s = sessions_by_id.get(chat_id)
        return bool(s and s.get('lastTimestamp', 0) >= since_epoch)

    # Discover active chats matching keywords that aren't in the static priority list
    extra_groups, extra_dms = discover_active_chats(priority, since_epoch, sessions_by_id)
    if extra_groups or extra_dms:
        print(f"[discover] adding {len(extra_groups)} groups + {len(extra_dms)} DMs from sessions sweep")

    results = []
    for g in priority['groups'] + extra_groups:
        msgs = pull_chat(g['id'], since_epoch, expected_fresh=_is_fresh(g['id']))
        tag = ' [auto]' if g in extra_groups else ''
        print(f"  group {g['name']}{tag}: {len(msgs)} messages in window")
        results.append(process_chat(g['name'], g['id'], msgs, attach_dir, process_media=True))
        time.sleep(0.15)  # throttle — WeFlow cursor eviction under burst load
    for d in priority['dms'] + extra_dms:
        msgs = pull_chat(d['id'], since_epoch, expected_fresh=_is_fresh(d['id']))
        tag = ' [auto]' if d in extra_dms else ''
        print(f"  DM {d['name']}{tag}: {len(msgs)} messages in window")
        results.append(process_chat(d['name'], d['id'], msgs, attach_dir, process_media=d.get('process_media', True)))
        time.sleep(0.15)

    # Surface sync-lag chats (fresh in sessions, empty in messages — WeFlow needs UI touch)
    lag = diagnose_sync_lag(priority, since_epoch, results)
    if lag:
        print(f"\n[sync-lag] {len(lag)} priority chats have fresh sessions but empty message export:")
        for L in lag:
            print(f"  ⚠ {L['name']} — last activity {L['last_seen']} (open in WeFlow UI to force export)")

    snippet, full = compose_digest(window_start, results, lag)
    (run_dir / 'digest.md').write_text(full, encoding='utf-8')
    (run_dir / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(f"\ndigest: {run_dir / 'digest.md'}")

    if args.dry_run:
        print('--dry-run: not writing to vault.')
        print('\n--- snippet preview ---')
        print(snippet)
        return

    append_to_daily(snippet)
    all_tasks = [t for r in results for t in r['tasks']]
    if args.push_inbox:
        append_to_inbox(all_tasks)
        print(f"done. tasks queued to inbox: {len(all_tasks)}")
    else:
        print(f"done. {len(all_tasks)} candidate task(s) detected — NOT auto-pushed "
              f"(intake via /morning-sweep confirm gate; pass --push-inbox to restore old behavior).")

if __name__ == '__main__':
    main()
