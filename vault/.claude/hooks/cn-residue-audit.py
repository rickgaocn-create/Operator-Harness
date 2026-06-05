#!/usr/bin/env python3
"""Standalone audit script — scan all CN-audience .md files in vault for English residue.

Outputs a violation report grouped by file. Use to identify top offenders for batch cleanup.

Usage:
    python cn-residue-audit.py
    python cn-residue-audit.py --top 20            # only show top 20 files by violation count
    python cn-residue-audit.py --output report.md  # write report to file
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VAULT_ROOT = Path(r'D:\Administrator\Documents\{{USER_NAME}}')

CN_AUDIENCE_GLOBS = [
    '01 Wiki/{{PROJECT_A}}/**/*.md',
    '01 Wiki/{{ORG_B}}/**/*.md',
    '01 Wiki/AIX/**/*.md',
    '01 Wiki/{{ORG_D}}/**/*.md',
    '02 Cards/**/*.md',
    '03 Projects/{{PROJECT_A}}/04 会议纪要/**/*.md',
    '03 Projects/{{PROJECT_A}}/09 Reports/**/*.md',
    '03 Projects/{{ORG_B}}/04 会议纪要/**/*.md',
    '04 Notes/**/*.md',
    '06 Tasks/**/*.md',
    '10 Action/**/*.md',
]

WHITELIST = {
    'taptap', 'bilibili', 'anthropic', 'claude', 'opus', 'sonnet', 'haiku',
    'openai', 'gpt', 'mcp', 'obsidian', 'notion', 'cursor', 'epic', 'sega',
    'hoyoverse', 'nuverse', 'bytedance', 'tiktok', 'mixue', 'xpeng', 'tesla',
    'bmw', 'audi', 'toyota', 'honda', 'mona', 'menko', 'wecom', 'wechat',
    'feishu', 'lark', 'slack', 'discord', 'zoom', 'meet', 'teams',
    'github', 'gitlab', 'jira', 'confluence', 'asana', 'trello', 'airtable',
    'bubble', 'tinyhumansai', 'openhuman', 'firecrawl', 'defuddle',
    'linux', 'windows', 'macos', 'ios', 'android', 'unix',
    'html', 'json', 'csv', 'xlsx', 'pdf', 'yaml', 'rest', 'api', 'sdk',
    'cli', 'ssh', 'http', 'https', 'xml', 'sql', 'css', 'svg', 'png', 'jpg',
    'jpeg', 'gif', 'webp', 'mp4', 'mp3', 'wav', 'usb', 'gpu', 'cpu', 'ram',
    'ssd', 'hdd', 'wifi', 'gps', 'vpn', 'vps', 'qr', 'cdn', 'crud', 'ddl',
    'dml', 'graphql', 'grpc', 'tcp', 'udp', 'ip', 'mqtt', 'oauth', 'jwt',
    'kol', 'koc', 'bd', 'pmo', 'ceo', 'coo', 'cfo', 'cto', 'roi', 'ltv',
    'dau', 'mau', 'wau', 'vt', 'arpu', 'arppu', 'cpa', 'cpm', 'cpi', 'cpc',
    'ctr', 'cvr', 'roi', 'roas', 'mrr', 'arr', 'gmv', 'tps', 'sla', 'slo',
    'ux', 'ui', 'qa', 'qc', 'qe', 'eod', 'eow', 'eom', 'eoy', 'sop',
    'ipo', 'mou', 'nda', 'loi', 'rofr', 'mba', 'pe', 'vc', 'ic', 'dd',
    'jgc', 'jbr', 'fo', 'saas', 'iaas', 'paas', 'daas', 'faas',
    'bw', 'pv', 'mv', 'qte', 'poi', 'pbr', 'npr', 'ott', 'tgs', 'ugc',
    'pc', 'cj', 'acg', 'gba', 'nds', 'fps', 'rpg', 'mmo', 'mmorpg',
    'pvp', 'pve', 'cbt', 'obt', 'mvp', 'boss', 'coser', 'cosplay', 'aigc',
    'ai', 'ml', 'llm', 'nlp', 'asr', 'tts', 'stt', 'ocr', 'crm', 'erp',
    'cms', 'ide', 'oss', 'cs', 'oem', 'odm',
    'card', 'cards', 'memory', 'skill', 'skills', 'agent', 'agents',
    'subagent', 'subagents', 'frontmatter', 'wiki', 'markdown', 'block',
    'tag', 'tags', 'hooks', 'hook', 'cron', 'task', 'tasks', 'auto',
    'autonomous', 'inline', 'pipeline', 'workflow', 'workspace', 'vault',
    'beta', 'alpha', 'demo', 'roadmap', 'sprint', 'pilot',
    'docx', 'xlsm', 'kanban',
    'app', 'apps', 'web', 'tab', 'tabs', 'menu', 'panel',
}


def strip_safe_blocks(text: str) -> str:
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end > 0:
            text = text[end + 4:]
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`\n]+`', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\[\[[^\]]+\]\]', '', text)
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)
    text = re.sub(r'\[[^\]]+\]\([^)]+\)', '', text)
    text = re.sub(r'[A-Z]:[\\/][\w\\/\-\.一-鿿]+', '', text)
    text = re.sub(r'(?<![\w])/(?:\w[\w\-\.]*[\\/])+\w[\w\-\.]*', '', text)
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    text = re.sub(r'\b[\w\-]+\.(?:md|py|json|cmd|ps1|sh|js|ts|yaml|yml|toml|html|css|cfg|conf|log|txt|csv|xlsx|pptx|docx|pdf)\b', '', text)
    return text


def find_violations(content: str) -> list[str]:
    head = content[:2000]
    if 'localize-cn: skip' in head or 'audience: en' in head or 'audience: jp' in head:
        return []
    body = strip_safe_blocks(content)
    english_chunks = re.findall(r'[A-Za-z]+(?:[-_][A-Za-z]+)*', body)
    seen = set()
    violations = []
    for chunk in english_chunks:
        if len(chunk) < 3:
            continue
        lc = chunk.lower()
        if lc in WHITELIST:
            continue
        if re.match(r'^v\d', chunk, re.IGNORECASE):
            continue
        if re.match(r'^t\d', chunk, re.IGNORECASE):
            continue
        if re.match(r'^(?:cbt|obt|ubt|pre|alpha|beta|gamma)\d?$', lc):
            continue
        if re.match(r'^p\d$', lc):
            continue
        if lc in seen:
            continue
        seen.add(lc)
        violations.append(chunk)
    return violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=0, help='Only show top N files by violation count')
    ap.add_argument('--output', type=str, default='', help='Write report to file')
    args = ap.parse_args()

    files = []
    for g in CN_AUDIENCE_GLOBS:
        files.extend(VAULT_ROOT.glob(g))
    files = sorted(set(files))
    print(f'[audit] scanning {len(files)} CN-audience files...')

    results = []
    total_violations = Counter()
    for f in files:
        try:
            content = f.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        violations = find_violations(content)
        if violations:
            results.append((str(f.relative_to(VAULT_ROOT)), violations))
            for v in violations:
                total_violations[v.lower()] += 1

    results.sort(key=lambda r: -len(r[1]))
    if args.top > 0:
        results = results[:args.top]

    lines = [
        f'# CN-residue audit report — {len(results)} files with violations',
        f'(out of {len(files)} CN-audience files scanned)',
        '',
        '## Top 30 offender words (across all files):',
        ''
    ]
    for word, count in total_violations.most_common(30):
        lines.append(f'- **{word}** × {count}')
    lines.append('')
    lines.append('## Per-file violations:')
    lines.append('')
    for path, vs in results:
        lines.append(f'### {path} ({len(vs)} unique)')
        lines.append(f'  {", ".join(vs[:20])}{" ..." if len(vs) > 20 else ""}')
        lines.append('')

    report = '\n'.join(lines)
    if args.output:
        Path(args.output).write_text(report, encoding='utf-8')
        print(f'[audit] report written to {args.output}')
    else:
        print(report)


if __name__ == '__main__':
    main()
