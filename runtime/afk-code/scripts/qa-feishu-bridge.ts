import assert from 'node:assert/strict';
import {
  buildFeishuHistoryListArgs,
  buildFeishuMarkdownSendArgs,
  buildFeishuTextSendArgs,
  feishuHistoryMessageToReceiveEvent,
  stripLeadingAssistantLabel,
} from '../src/feishu/message-utils.js';
import { resolveLarkCli } from '../src/feishu/feishu-app.js';
import { parseMarkdownToRows, parseInline, buildPostSendArgs } from '../src/feishu/rich-message.js';
import {
  acceptsDaemonSessionToken,
  buildSessionInputPayloads,
  codexSessionTimestampMatchesStart,
  sessionsHaveSameIdentity,
} from '../src/slack/session-manager.js';
import { getCodexHome, getEffectiveCwd, getTranscriptConfig, terminalLooksReady } from '../src/cli/run.js';

const chatId = 'oc_test_chat';
const multiline = 'First line\nSecond line\nThird line';
const args = buildFeishuMarkdownSendArgs(chatId, multiline);

// All outbound messages now use Feishu `post` payloads (own-parser) so that
// multi-line replies preserve their line structure. The `--markdown` arg
// path is intentionally removed — lark-cli's markdown→post conversion
// reflows soft newlines and drops blank lines.
assert.deepEqual(args.slice(0, 6), [
  'im', '+messages-send',
  '--as', 'bot',
  '--chat-id', chatId,
]);
assert.equal(args.includes('--markdown'), false, 'we now build post payloads ourselves; --markdown path is gone');
assert.equal(args.includes('--text'), false, 'rich sends must avoid --text on Windows');
const contentIdx = args.indexOf('--content');
assert.notEqual(contentIdx, -1, 'expected --content argument');
assert.equal(args[args.indexOf('--msg-type') + 1], 'post');

const parsedPost = JSON.parse(args[contentIdx + 1]);
const rows = parsedPost?.zh_cn?.content;
assert.equal(Array.isArray(rows), true, 'post payload must carry zh_cn.content rows');
assert.equal(rows.length, 3, 'three input lines → three post rows');
assert.equal(rows[0][0].text, 'First line');
assert.equal(rows[2][0].text, 'Third line');

const markdownProbe = [
  '# Header',
  '',
  '- list item',
  '- another item',
  '',
  '```ts',
  'const value = `inline`;',
  '```',
  '',
  '**bold** _italic_ `code` [link](https://open.feishu.cn/)',
].join('\n');
const probeArgs = buildFeishuMarkdownSendArgs(chatId, markdownProbe);
const probeRows = JSON.parse(probeArgs[probeArgs.indexOf('--content') + 1]).zh_cn.content;
// row 0 = header (bold), row 1 = blank, rows 2/3 = list items, row 4 = blank,
// row 5 = code block, row 6 = blank, row 7 = inline mix
assert.equal(probeRows[0][0].text, 'Header');
assert.deepEqual(probeRows[0][0].style, ['bold']);
assert.equal(probeRows[5][0].tag, 'code_block');
assert.equal(probeRows[5][0].language, 'ts');
assert.equal(probeRows[5][0].text, 'const value = `inline`;');
const inlineRow = probeRows[7];
assert.equal(inlineRow.find((t: any) => t.text === 'bold')?.style?.[0], 'bold');
assert.equal(inlineRow.find((t: any) => t.text === 'italic')?.style?.[0], 'italic');
assert.equal(inlineRow.find((t: any) => t.tag === 'a')?.href, 'https://open.feishu.cn/');

// Plain text path: every line still gets its own row, no inline parsing.
const textArgs = buildFeishuTextSendArgs(chatId, multiline);
const textRows = JSON.parse(textArgs[textArgs.indexOf('--content') + 1]).zh_cn.content;
assert.equal(textRows.length, 3, 'plain text path: 1 row per line');
assert.equal(textRows[1][0].text, 'Second line');

// Reply threading: replyTo flips to im +messages-reply with --message-id.
const replyArgs = buildFeishuMarkdownSendArgs(chatId, 'thread response', 'om_user_msg_42');
assert.equal(replyArgs[1], '+messages-reply', 'replyTo must switch to +messages-reply');
assert.equal(replyArgs[replyArgs.indexOf('--message-id') + 1], 'om_user_msg_42');
assert.equal(replyArgs.includes('--chat-id'), false, '+messages-reply does not take --chat-id');

// Block-level parser sanity at the module boundary.
const headerRows = parseMarkdownToRows('## Title\nbody');
assert.deepEqual(headerRows[0][0].style, ['bold']);
assert.equal(headerRows[1][0].text, 'body');
assert.equal(parseInline('plain text').length, 1);

// Reply args via buildPostSendArgs directly (used by access.ts/feishu-app.ts).
const direct = buildPostSendArgs({ chatId, rows: [[{ tag: 'text', text: 'x' }]], replyTo: 'om_x' });
assert.equal(direct[direct.indexOf('--message-id') + 1], 'om_x');

assert.equal(stripLeadingAssistantLabel('Codex:\nReceived.'), 'Received.');
assert.equal(stripLeadingAssistantLabel('Codex: Received.'), 'Received.');
assert.equal(stripLeadingAssistantLabel('Claude Code:\nDone.'), 'Done.');
assert.equal(stripLeadingAssistantLabel('Claude:\nDone.'), 'Done.');
assert.equal(
  stripLeadingAssistantLabel('A sentence mentioning Codex: should remain intact.'),
  'A sentence mentioning Codex: should remain intact.',
  'only leading assistant labels should be stripped'
);

assert.deepEqual(
  buildFeishuHistoryListArgs(chatId),
  [
    'im', '+chat-messages-list',
    '--as', 'bot',
    '--chat-id', chatId,
    '--page-size', '50',
    '--sort', 'desc',
    '--format', 'json',
  ],
  'history fallback must use bot-readable chat history'
);
assert.deepEqual(
  feishuHistoryMessageToReceiveEvent({
    chat_id: chatId,
    content: 'missed event fallback',
    message_id: 'om_test',
    msg_type: 'text',
    sender: { sender_type: 'user', id: 'ou_test' },
  }),
  {
    chat_id: chatId,
    chat_type: 'p2p',
    content: 'missed event fallback',
    create_time: '',
    id: 'om_test',
    message_id: 'om_test',
    message_position: undefined,
    message_type: 'text',
    sender_id: 'ou_test',
    timestamp: '',
    type: 'im.message.receive_v1',
  },
  'history user messages must normalize to the event handler shape'
);
assert.equal(
  feishuHistoryMessageToReceiveEvent({
    chat_id: chatId,
    content: 'bot echo',
    message_id: 'om_bot',
    msg_type: 'text',
    sender: { sender_type: 'app', id: 'cli_test' },
  }),
  null,
  'history fallback must not feed bot messages back into Codex'
);

assert.deepEqual(
  buildSessionInputPayloads('codex', 'hello from feishu'),
  [{ submitText: 'hello from feishu' }],
  'Codex text messages must be submitted atomically'
);
assert.deepEqual(
  buildSessionInputPayloads('codex', '\x1b[Z'),
  [{ text: '\x1b[Z' }],
  'Codex raw terminal keys must stay raw'
);
assert.deepEqual(
  buildSessionInputPayloads('codex', 'line one\nline two'),
  [{ submitText: 'line one\nline two' }],
  'Codex multiline Feishu messages must still be submitted with Enter'
);
assert.deepEqual(
  buildSessionInputPayloads('claude', 'hello from feishu'),
  [{ text: 'hello from feishu' }],
  'Claude submit behavior must remain unchanged'
);
assert.equal(
  getEffectiveCwd(
    '{{USER_HOME}}\\Documents\\Codex\\scratch',
    ['codex.exe', '-C', '{{USER_HOME}}\\Developer\\afk-code']
  ),
  '{{USER_HOME}}\\Developer\\afk-code',
  'Open Morty must register Codex sessions with the -C directory, not the launching shell cwd'
);

const originalCodexHome = process.env.CODEX_HOME;
try {
  process.env.CODEX_HOME = '{{USER_HOME}}\\.codex-feishu-afk';
  assert.equal(
    getCodexHome(),
    '{{USER_HOME}}\\.codex-feishu-afk',
    'feishu-codex must honor isolated CODEX_HOME on Windows'
  );
  assert.equal(
    getTranscriptConfig('{{USER_HOME}}\\Developer\\afk-code', ['codex.exe']).projectDir,
    '{{USER_HOME}}\\.codex-feishu-afk\\sessions',
    'Open Morty must watch the isolated Codex transcript directory'
  );
} finally {
  if (originalCodexHome === undefined) {
    delete process.env.CODEX_HOME;
  } else {
    process.env.CODEX_HOME = originalCodexHome;
  }
}

assert.equal(acceptsDaemonSessionToken(undefined, undefined), true);
assert.equal(acceptsDaemonSessionToken('expected-token', 'expected-token'), true);
assert.equal(
  acceptsDaemonSessionToken('expected-token', undefined),
  false,
  'Open Morty daemon must reject sessions that did not come from feishu-codex'
);
assert.equal(
  acceptsDaemonSessionToken('expected-token', 'wrong-token'),
  false,
  'Open Morty daemon must reject sessions from other Codex launches'
);
assert.equal(
  sessionsHaveSameIdentity(
    {
      name: 'codex.exe -C {{USER_HOME}}\\Developer\\afk-code',
      cwd: '{{USER_HOME}}\\Developer\\afk-code',
      projectDir: '{{USER_HOME}}\\.codex\\sessions',
      transcriptBackend: 'codex',
    },
    {
      name: 'different transcript slug after startup',
      cwd: '{{USER_HOME}}/Developer/afk-code/',
      projectDir: '{{USER_HOME}}/.codex/sessions/',
      transcriptBackend: 'codex',
    }
  ),
  true,
  'Open Morty must treat duplicate Codex runners in the same cwd as one session'
);
assert.equal(
  sessionsHaveSameIdentity(
    {
      name: 'codex.exe -C {{USER_HOME}}\\Developer\\afk-code',
      cwd: '{{USER_HOME}}\\Developer\\afk-code',
      projectDir: '{{USER_HOME}}\\.codex\\sessions',
      transcriptBackend: 'codex',
    },
    {
      name: 'codex.exe -C {{USER_HOME}}\\Developer\\other-project',
      cwd: '{{USER_HOME}}\\Developer\\other-project',
      projectDir: '{{USER_HOME}}\\.codex\\sessions',
      transcriptBackend: 'codex',
    }
  ),
  false,
  'Open Morty must keep genuinely different Codex workspaces separate'
);

const startedAt = new Date('2026-05-27T13:00:00.000Z');
assert.equal(
  codexSessionTimestampMatchesStart(startedAt, Date.parse('2026-05-27T12:59:30.000Z')),
  true,
  'Codex transcript created shortly before wrapper startup can belong to that session'
);
assert.equal(
  codexSessionTimestampMatchesStart(startedAt, Date.parse('2026-05-27T13:01:00.000Z')),
  true,
  'Codex transcript timestamp may be slightly after wrapper startup'
);
assert.equal(
  codexSessionTimestampMatchesStart(startedAt, Date.parse('2026-05-27T13:05:00.000Z')),
  false,
  'Open Morty must not claim a later unrelated Codex session in the same cwd'
);
assert.equal(
  codexSessionTimestampMatchesStart(startedAt, Date.parse('2026-05-27T12:58:30.000Z')),
  false,
  'Open Morty must not claim an old unrelated Codex session in the same cwd'
);
assert.equal(
  terminalLooksReady('Do you trust the contents of this directory?\n› Find and fix a bug in @filename\n  gpt-5.5 high'),
  false,
  'remote prompts must not submit while Codex is still behind the trust gate'
);
assert.equal(
  terminalLooksReady('Working (14s - esc to interrupt)\n› Find and fix a bug in @filename\n  gpt-5.5 high'),
  false,
  'remote prompts must wait while Codex is busy'
);
assert.equal(
  terminalLooksReady('› Find and fix a bug in @filename\n  gpt-5.5 high - ~\\Developer\\afk-code'),
  true,
  'remote prompts can submit once the Codex composer is idle'
);
assert.equal(
  terminalLooksReady('Codex:\nI’m here. Send the task or file you want me to work on.\n\n›\n  gpt-5.5 high - ~\\Developer\\afk-code'),
  true,
  'remote prompts must submit when the Codex composer is empty after a reply'
);
assert.equal(
  terminalLooksReady('› test\n\n• I’m here. Send the task or file you want me to work on.\n\n›\n  gpt-5.5 high'),
  true,
  'remote prompts must submit follow-up messages after a completed turn'
);

assert.equal(
  terminalLooksReady(
    'Working (14s - esc to interrupt)\n'.repeat(25) +
    'assistant reply\n'.repeat(25) +
    '\u203a Find and fix a bug in @filename\n  gpt-5.5 high'
  ),
  true,
  'old busy output must not block later idle Codex prompts'
);

if (process.platform === 'win32') {
  assert.match(
    resolveLarkCli().toLowerCase(),
    /lark-cli\.exe$/,
    'Windows must call lark-cli.exe directly so message text is not shell-parsed'
  );
}

// --- AccessStore gate (in-process, no real lark-cli call) ---
import { AccessStore, defaultAccess } from '../src/feishu/access.js';
import { mkdtempSync, rmSync } from 'fs';
import { tmpdir } from 'os';
import { join as joinPath } from 'path';

const tmp = mkdtempSync(joinPath(tmpdir(), 'fa-qa-'));
const accessFile = joinPath(tmp, 'access.json');
const store = new AccessStore({ larkProfile: 'test', larkCli: 'lark-cli-nonexistent', filePath: accessFile });

// Seed allowlist DM mode with a single allowed sender.
const seeded = defaultAccess();
seeded.dmPolicy = 'allowlist';
seeded.allowFrom = ['ou_alice'];
seeded.groups = { oc_explicit_group: { requireMention: false, allowFrom: ['ou_alice'] } };
store.save(seeded);

// DM from allowed sender → deliver
const r1 = await store.gate({
  chat_id: 'oc_alice_dm', chat_type: 'p2p', content: '', message_id: 'om_1',
  sender_id: 'ou_alice', message_type: 'text',
});
assert.equal(r1.action, 'deliver', 'allowlisted DM should deliver');

// DM from unknown sender → drop (allowlist policy, no pairing)
const r2 = await store.gate({
  chat_id: 'oc_bob_dm', chat_type: 'p2p', content: '', message_id: 'om_2',
  sender_id: 'ou_bob', message_type: 'text',
});
assert.equal(r2.action, 'drop', 'non-allowlisted DM under allowlist policy must drop');

// Group with explicit policy (requireMention=false, allowFrom includes sender) → deliver
const r3 = await store.gate({
  chat_id: 'oc_explicit_group', chat_type: 'group', content: '', message_id: 'om_3',
  sender_id: 'ou_alice', message_type: 'text',
});
assert.equal(r3.action, 'deliver', 'explicit group policy that allows sender must deliver');

// Group with explicit policy but sender NOT in group allowFrom → drop
const r4 = await store.gate({
  chat_id: 'oc_explicit_group', chat_type: 'group', content: '', message_id: 'om_4',
  sender_id: 'ou_carol', message_type: 'text',
});
assert.equal(r4.action, 'drop', 'group policy must drop senders not in groupAllowFrom');

// Group not in groups{}, but permissive open-for-allowlisted-senders is on (default true).
// The gate will try to fetchMessageContext via lark-cli; since lark-cli doesn't exist,
// it returns null → drop (fail-closed). That's the correct behavior we want to verify.
const r5 = await store.gate({
  chat_id: 'oc_random_group', chat_type: 'group', content: '', message_id: 'om_5',
  sender_id: 'ou_alice', message_type: 'text',
});
assert.equal(r5.action, 'drop', 'permissive group gate fails closed when message-context fetch fails');

// Pair mode: empty allowlist + pairing → first DM from unknown sender returns a pair code
const pairStore = new AccessStore({
  larkProfile: 'test', larkCli: 'lark-cli-nonexistent',
  filePath: joinPath(tmp, 'pair-access.json'),
});
const pairing = defaultAccess();
pairing.dmPolicy = 'pairing';
pairStore.save(pairing);
const r6 = await pairStore.gate({
  chat_id: 'oc_unknown', chat_type: 'p2p', content: '', message_id: 'om_6',
  sender_id: 'ou_new_user', message_type: 'text',
});
assert.equal(r6.action, 'pair', 'pairing policy issues pair code for first contact');
if (r6.action === 'pair') assert.match(r6.code, /^[a-f0-9]{6}$/);

// Sent-id tracking — used for "user replied to bot's message" detection.
store.noteSent('om_sent_1');
assert.equal(store.hasSent('om_sent_1'), true);
assert.equal(store.hasSent('om_unsent'), false);

rmSync(tmp, { recursive: true, force: true });

console.log('feishu bridge qa ok');
