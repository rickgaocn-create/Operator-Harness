/**
 * Markdown → Feishu post-tag rendering for outbound bridge messages.
 * Ported from fs-claude MCP plugin. Same parser, same payload shape.
 *
 * Why bypass `lark-cli ... --markdown`: lark-cli's own markdown→post conversion
 * reflows soft newlines and folds blank lines, which destroys multi-line codex
 * output (snippets, todos, paths). We build the post payload ourselves so each
 * source line becomes its own row.
 */

export type PostTextTag = { tag: 'text'; text: string; style?: string[] };
export type PostLinkTag = { tag: 'a'; text: string; href: string };
export type PostCodeBlockTag = { tag: 'code_block'; language?: string; text: string };
export type PostTag = PostTextTag | PostLinkTag | PostCodeBlockTag;
export type PostRow = PostTag[];

// Inline markdown → post tags. Matches **bold**, __bold__, *italic*, _italic_,
// ~~strike~~, `code`, [text](url). Single-pass, non-nesting (deliberate).
const INLINE_RE = /\*\*([^*\n]+)\*\*|__([^_\n]+)__|~~([^~\n]+)~~|(?<![*\w])\*([^*\n]+)\*(?!\w)|(?<![_\w])_([^_\n]+)_(?![_\w])|`([^`\n]+)`|\[([^\]\n]+)\]\(([^)\s]+)\)/g;

function isValidHref(s: string): boolean {
  return /^(https?:\/\/|mailto:|tel:|#)/i.test(s);
}

export function parseInline(s: string): PostTag[] {
  const out: PostTag[] = [];
  let last = 0;
  INLINE_RE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = INLINE_RE.exec(s)) !== null) {
    if (m.index > last) out.push({ tag: 'text', text: s.slice(last, m.index) });
    if      (m[1] !== undefined) out.push({ tag: 'text', text: m[1], style: ['bold'] });
    else if (m[2] !== undefined) out.push({ tag: 'text', text: m[2], style: ['bold'] });
    else if (m[3] !== undefined) out.push({ tag: 'text', text: m[3], style: ['lineThrough'] });
    else if (m[4] !== undefined) out.push({ tag: 'text', text: m[4], style: ['italic'] });
    else if (m[5] !== undefined) out.push({ tag: 'text', text: m[5], style: ['italic'] });
    else if (m[6] !== undefined) out.push({ tag: 'text', text: m[6], style: ['bold'] });
    else if (m[7] !== undefined && m[8] !== undefined) {
      if (isValidHref(m[8])) out.push({ tag: 'a', text: m[7], href: m[8] });
      else out.push({ tag: 'text', text: m[0] });
    }
    last = INLINE_RE.lastIndex;
  }
  if (last < s.length) out.push({ tag: 'text', text: s.slice(last) });
  return out.length > 0 ? out : [{ tag: 'text', text: s }];
}

export function parseMarkdownToRows(md: string): PostRow[] {
  const rows: PostRow[] = [];
  const lines = md.split('\n');
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const fence = /^```(\S*)\s*$/.exec(line);
    if (fence) {
      const lang = fence[1] || undefined;
      const body: string[] = [];
      i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i])) {
        body.push(lines[i]);
        i++;
      }
      if (i < lines.length) i++;  // consume closing fence
      const tag: PostCodeBlockTag = { tag: 'code_block', text: body.join('\n') };
      if (lang) tag.language = lang;
      rows.push([tag]);
      continue;
    }
    const header = /^(#{1,6})\s+(.+)$/.exec(line);
    let bodyLine = header ? header[2] : line;
    if (bodyLine.length === 0) {
      rows.push([{ tag: 'text', text: ' ' }]);
    } else {
      const tags = parseInline(bodyLine);
      if (header) {
        for (const t of tags) {
          if (t.tag === 'text') t.style = Array.from(new Set([...(t.style ?? []), 'bold']));
        }
      }
      rows.push(tags);
    }
    i++;
  }
  return rows;
}

export function plainTextToRows(text: string): PostRow[] {
  return text.split('\n').map(line =>
    line.length === 0
      ? [{ tag: 'text', text: ' ' } as PostTag]
      : [{ tag: 'text', text: line } as PostTag]
  );
}

export function buildPostContent(rows: PostRow[], title?: string): string {
  const inner: { title?: string; content: PostRow[] } = { content: rows };
  if (title) inner.title = title;
  return JSON.stringify({ zh_cn: inner });
}

export interface SendPostArgsInput {
  chatId: string;
  rows: PostRow[];
  title?: string;
  replyTo?: string;  // om_xxx message_id to thread under
}

/**
 * Build lark-cli argv for sending a post message. When `replyTo` is set, use
 * `im +messages-reply` with --message-id instead of `im +messages-send`.
 */
export function buildPostSendArgs(input: SendPostArgsInput): string[] {
  const content = buildPostContent(input.rows, input.title);
  if (input.replyTo) {
    return [
      'im', '+messages-reply',
      '--as', 'bot',
      '--message-id', input.replyTo,
      '--content', content,
      '--msg-type', 'post',
    ];
  }
  return [
    'im', '+messages-send',
    '--as', 'bot',
    '--chat-id', input.chatId,
    '--content', content,
    '--msg-type', 'post',
  ];
}
