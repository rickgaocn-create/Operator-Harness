"""daily-feishu-ingest — pull recent 飞书 activity from user's chats, organize, surface into daily note.

Runs every 6 hours via Windows Task Scheduler. Uses lark-cli (--profile business-morty) to fetch messages.
"""
from __future__ import annotations
import argparse, json, os, sys, subprocess
from pathlib import Path
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

VAULT_ROOT = Path(r'D:\Administrator\Documents\{{USER_NAME}}')
SCRIPT_DIR = Path(__file__).parent
QUEUE_DIR = VAULT_ROOT / '.claude' / '.daily-ingest-queue' / 'feishu'
LARK_CLI = r'{{USER_HOME}}\AppData\Roaming\npm\lark-cli.cmd'
# Corporate Feishu bot ("Business Morty"). Switched from personal 'morty' 2026-05-27:
# the personal bot saw only its own p2p; the corporate profile sees real work groups.
LARK_PROFILE = os.environ.get('LARK_PROFILE', 'business-morty')


def lark(args: list, timeout: int = 60) -> dict:
    cmd = [LARK_CLI, '--profile', LARK_PROFILE] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace')
    except Exception as e:
        print(f'  ! lark failed: {e}', file=sys.stderr)
        return {}
    out = r.stdout or ''
    # Strip deprecation banner if present
    if out.startswith('[deprecated]'):
        nl = out.find('\n')
        if nl > 0:
            out = out[nl + 1:]
    try:
        return json.loads(out)
    except Exception:
        if out.strip():
            print(f'  ! lark non-json output: {out[:200]}', file=sys.stderr)
        return {}


def parse_ts(s: str) -> datetime | None:
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=float, default=6.0)
    ap.add_argument('--max-chats', type=int, default=50)
    ap.add_argument('--max-msgs', type=int, default=50)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    now = datetime.now()
    since = now - timedelta(hours=args.hours)
    print(f'[feishu-ingest] window: {since.isoformat()} -> {now.isoformat()} ({args.hours}h)')

    # 1) list chats — PAGINATE chat-list (reads --as user → every group {{USER_NAME}} is in).
    #    Feishu is the primary work platform going forward (2026-05-27); new groups {{USER_NAME}} joins
    #    are auto-discovered here with no code change. Coverage scales with {{USER_NAME}}'s membership,
    #    NOT with bot membership (the user token, not the bot, enumerates the chats).
    chats_a, page_token, pages = [], '', 0
    while True:
        cmd = ['im', '+chat-list', '--as', 'user', '--page-size', '100']
        if page_token:
            cmd += ['--page-token', page_token]
        resp = lark(cmd)
        data = resp.get('data', {})
        chats_a += (data.get('chats') or data.get('items') or [])
        page_token = data.get('page_token') or ''
        pages += 1
        if not data.get('has_more') or not page_token or pages >= 20:  # 20×100 = 2000-chat safety cap
            break
    # Load priority pins (must-always-poll groups; also covers any the bot can't enumerate)
    pri_path = SCRIPT_DIR / 'priority_chats.json'
    chats_b = []
    if pri_path.exists():
        try:
            pri = json.loads(pri_path.read_text(encoding='utf-8'))
            chats_b = pri.get('chats', [])
        except Exception as e:
            print(f'[feishu-ingest] priority_chats.json parse failed: {e}', file=sys.stderr)
    # Dedup by chat_id
    seen = set()
    chats = []
    for c in chats_a + chats_b:
        cid = c.get('chat_id') or c.get('id')
        if cid and cid not in seen:
            seen.add(cid)
            chats.append(c)
    if not chats:
        print(f'[feishu-ingest] no chats to ingest', file=sys.stderr)
        return
    print(f'[feishu-ingest] {len(chats)} chats listed ({len(chats_a)} from API + {len(chats_b)} from priority list)')

    # 2) for each, pull recent messages, filter by time
    digest_chats = []
    for chat in chats:
        chat_id = chat.get('chat_id') or chat.get('id')
        name = chat.get('name') or chat.get('description') or '(unnamed)'
        if not chat_id or not str(chat_id).startswith('oc_'):
            continue
        msgs_resp = lark(['im', '+chat-messages-list', '--as', 'user', '--chat-id', chat_id, '--page-size', str(args.max_msgs)])
        msgs = msgs_resp.get('data', {}).get('messages', [])
        recent = []
        for m in msgs:
            ts = parse_ts(m.get('create_time', ''))
            if ts and ts >= since:
                recent.append(m)
        if recent:
            digest_chats.append({'name': name, 'chat_id': chat_id, 'msgs': recent})

    total = sum(len(c['msgs']) for c in digest_chats)
    print(f'[feishu-ingest] {total} messages from {len(digest_chats)} chats in last {args.hours}h')

    if not digest_chats:
        print(f'[feishu-ingest] nothing recent, exit')
        return

    # 3) write digest file
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime('%Y-%m-%d-%H%M')
    digest_path = QUEUE_DIR / f'{stamp}-digest.md'
    lines = [f'# 飞书 ingest {now.strftime("%Y-%m-%d %H:%M")} (last {args.hours}h)\n']
    for c in digest_chats:
        lines.append(f'\n## {c["name"]} ({len(c["msgs"])} msgs)\n')
        for m in c['msgs']:
            sender = (m.get('sender') or {}).get('name', m.get('sender', {}).get('id', '?'))
            content = (m.get('content') or '')[:200].replace('\n', ' ')
            ts = m.get('create_time', '')
            lines.append(f'- **{ts}** {sender}: {content}')
    digest_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'[feishu-ingest] digest -> {digest_path}')

    if args.dry_run:
        print('[feishu-ingest] dry-run, not appending to daily note')
        return

    # 4) append to daily note (if exists)
    today = now.strftime('%Y-%m-%d')
    daily_note = VAULT_ROOT / '04 Notes' / 'daily notes' / f'{today}.md'
    if not daily_note.exists():
        print(f'[feishu-ingest] daily note {daily_note} not found, skip append')
        return

    snippet = (
        f'\n### 🤖 daily-feishu-ingest {now.strftime("%H:%M")} -> {total} messages from {len(digest_chats)} chats\n'
        f'\n*Full digest: `{digest_path.relative_to(VAULT_ROOT).as_posix()}`*\n'
    )
    content = daily_note.read_text(encoding='utf-8')
    if '## Ingests' in content:
        content = content.replace('## Ingests\n', '## Ingests\n' + snippet, 1)
    else:
        content += '\n## Ingests\n' + snippet
    daily_note.write_text(content, encoding='utf-8')
    print(f'[feishu-ingest] appended to {daily_note.relative_to(VAULT_ROOT)}')


if __name__ == '__main__':
    main()
