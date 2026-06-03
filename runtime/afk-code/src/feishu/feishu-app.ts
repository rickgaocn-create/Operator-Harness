import { type ChildProcess } from 'child_process';
import spawn from 'cross-spawn';
import { existsSync } from 'fs';
import { mkdir, writeFile } from 'fs/promises';
import { dirname, join } from 'path';
import type { FeishuConfig } from './types.js';
import { SessionManager } from '../slack/session-manager.js';
import { formatTodos } from '../slack/message-formatter.js';
import { AccessStore, type Access, type FeishuEvent, type GateResult } from './access.js';
import {
  buildFeishuHistoryListArgs,
  buildFeishuMarkdownSendArgs,
  buildFeishuTextSendArgs,
  feishuHistoryMessageToReceiveEvent,
  FEISHU_MAX_MESSAGE_LENGTH,
  stripLeadingAssistantLabel,
} from './message-utils.js';

export function resolveLarkCli(): string {
  if (process.env.LARK_CLI_PATH) return process.env.LARK_CLI_PATH;

  if (process.platform === 'win32' && process.env.APPDATA) {
    const exe = join(process.env.APPDATA, 'npm', 'node_modules', '@larksuite', 'cli', 'bin', 'lark-cli.exe');
    if (existsSync(exe)) return exe;
  }

  return 'lark-cli';
}

const LARK_CLI = resolveLarkCli();

interface SessionTracking {
  sessionId: string;
  sessionName: string;
  projectName: string;
  cwd: string;
  projectDir: string;
  lastActivity: Date;
  transcriptBackend: 'claude' | 'codex';
  /** Last chat that sent input to this session — assistant output goes here. */
  outboundChatId?: string;
  /** Last inbound message_id from the outbound chat — used to thread the first reply. */
  outboundReplyTo?: string;
  /** Once we've threaded the first reply, subsequent assistant chunks should NOT thread (keeps replies inline). */
  firstReplyThreaded?: boolean;
}

export function createFeishuApp(config: FeishuConfig) {
  const activeSessions = new Map<string, SessionTracking>();
  const feishuSentMessages = new Set<string>();
  const handledFeishuMessages = new Set<string>();
  let historyWatermarkPosition = 0;
  let historySeeded = false;
  let currentSessionId: string | null = null;
  const startCommandHint = config.startCommandHint || 'afk-code run -- claude';

  // Legacy single-chat mode (FEISHU_CHAT_ID env) bypasses access.json: pre-allowlists
  // the bound chat as a "primary" channel. New deployments leave chatId unset and
  // use access.json (allowlist of ou_ ids + optional groups). Both can coexist —
  // the legacy chat is always allowed even if access.json says otherwise.
  const legacyBoundChatId: string | null = config.chatId ?? null;

  const access = new AccessStore({
    larkProfile: config.larkProfile,
    larkCli: LARK_CLI,
    filePath: config.accessFilePath,
  });

  // Bootstrap allowlist when legacy chatId is set but access.json doesn't exist.
  // Lets first-time users keep doing the env-based config without touching access.json.
  // We don't know the sender's open_id yet (env config doesn't carry it), so we
  // leave allowFrom empty but flip dmPolicy=allowlist with the legacy chat
  // pre-trusted. Actual allowlist learning happens on first inbound: record sender.
  if (legacyBoundChatId) {
    const a = access.load();
    if (a.dmPolicy === 'allowlist' && a.allowFrom.length === 0 && Object.keys(a.groups).length === 0) {
      // Empty allowlist — would block everyone. Permit pairing for the legacy chat instead.
      a.dmPolicy = 'pairing';
      access.save(a);
    }
  }

  const messageQueue: Array<() => Promise<void>> = [];
  let processingQueue = false;

  async function processQueue() {
    if (processingQueue) return;
    processingQueue = true;
    while (messageQueue.length > 0) {
      const fn = messageQueue.shift();
      if (fn) {
        try {
          await fn();
        } catch (err) {
          console.error('[Feishu] Send failed:', err);
        }
        if (messageQueue.length > 0) {
          await new Promise((r) => setTimeout(r, 50));
        }
      }
    }
    processingQueue = false;
  }

  function runLark(args: string[]): Promise<{ ok: boolean; stdout: string; stderr: string }> {
    return new Promise((resolve) => {
      const proc = spawn(LARK_CLI, ['--profile', config.larkProfile, ...args], {
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      let stdout = '';
      let stderr = '';
      proc.stdout?.on('data', (d) => { stdout += d.toString(); });
      proc.stderr?.on('data', (d) => { stderr += d.toString(); });
      proc.on('exit', (code) => resolve({ ok: code === 0, stdout, stderr }));
      proc.on('error', (err) => resolve({ ok: false, stdout, stderr: stderr + String(err) }));
    });
  }

  async function persistBoundChat(chatId: string) {
    if (!config.configFilePath) return;
    await mkdir(dirname(config.configFilePath), { recursive: true });
    const envContent = `# AFK Code Feishu Configuration
FEISHU_LARK_PROFILE=${config.larkProfile}
FEISHU_CHAT_ID=${chatId}
`;
    await writeFile(config.configFilePath, envContent, 'utf-8');
  }

  /**
   * Send raw post args to a chat, capture the resulting message_id, and
   * register it with the access store so future "user replied to bot's
   * message" detection works in group chats.
   */
  async function sendArgs(chatId: string, args: string[]): Promise<string> {
    return new Promise((resolve) => {
      messageQueue.push(async () => {
        const r = await runLark(args);
        if (!r.ok) {
          console.error(`[Feishu] lark-cli send failed (chat=${chatId}): ${r.stderr || r.stdout}`);
          resolve('');
          return;
        }
        try {
          const parsed = JSON.parse(r.stdout);
          const id = parsed?.data?.message_id ?? parsed?.message_id ?? '';
          if (id) access.noteSent(id);
          resolve(id);
        } catch {
          resolve('');
        }
      });
      processQueue();
    });
  }

  async function sendMarkdown(chatId: string, text: string, replyTo?: string): Promise<string> {
    return sendArgs(chatId, buildFeishuMarkdownSendArgs(chatId, text, replyTo));
  }

  async function sendText(chatId: string, text: string, replyTo?: string): Promise<string> {
    return sendArgs(chatId, buildFeishuTextSendArgs(chatId, text, replyTo));
  }

  /** Convenience for system messages that broadcast to "the default chat" — falls back to legacy bound chat. */
  async function sendDefault(text: string): Promise<void> {
    const chat = chooseDefaultOutboundChat();
    if (!chat) {
      console.error('[Feishu] outbound skipped: no bound chat yet');
      return;
    }
    await sendMarkdown(chat, text);
  }

  function chooseDefaultOutboundChat(): string | null {
    // Prefer the most-recently-active session's outbound chat (so /sessions etc.
    // go to whoever last interacted). Fall back to the legacy env chat.
    const recent = getMostRecentSession();
    if (recent?.outboundChatId) return recent.outboundChatId;
    return legacyBoundChatId;
  }

  const sessionManager = new SessionManager({
    onSessionStart: async (session) => {
      const projectName = session.cwd.split(/[\\/]/).filter(Boolean).pop() || 'unknown';
      activeSessions.set(session.id, {
        sessionId: session.id,
        sessionName: session.name,
        projectName,
        cwd: session.cwd,
        projectDir: session.projectDir,
        lastActivity: new Date(),
        transcriptBackend: session.transcriptBackend,
      });
      currentSessionId = session.id;

      const parts = session.name.split(' ');
      const cmd = parts[0];
      const args = parts.slice(1).map((a) => a.replace(/^-+/, ''));
      const sessionLabel = args.length > 0 ? `${cmd} (${args.join(', ')})` : cmd;

      await sendDefault(`Session started: ${sessionLabel}\nDirectory: ${session.cwd}`);
    },

    onSessionEnd: async (sessionId) => {
      const tracking = activeSessions.get(sessionId);
      const name = tracking?.sessionName || sessionId;
      const outboundChat = tracking?.outboundChatId;
      activeSessions.delete(sessionId);
      if (currentSessionId === sessionId) currentSessionId = null;
      if (outboundChat) await sendMarkdown(outboundChat, `Session ended: ${name}`);
      else await sendDefault(`Session ended: ${name}`);
    },

    onSessionUpdate: async (sessionId, name) => {
      const tracking = activeSessions.get(sessionId);
      if (tracking) {
        tracking.sessionName = name;
        tracking.lastActivity = new Date();
      }
    },

    onSessionStatus: async (sessionId) => {
      const tracking = activeSessions.get(sessionId);
      if (tracking) tracking.lastActivity = new Date();
    },

    onMessage: async (sessionId, role, content) => {
      const tracking = activeSessions.get(sessionId);
      if (!tracking) return;
      tracking.lastActivity = new Date();

      if (role === 'user') {
        const contentKey = content.trim();
        if (feishuSentMessages.has(contentKey)) {
          feishuSentMessages.delete(contentKey);
          return;
        }
        const chat = tracking.outboundChatId ?? legacyBoundChatId;
        if (chat) await sendMarkdown(chat, `**User (terminal):**\n${content}`);
        return;
      }

      // Assistant. Send to the session's outbound chat (whichever Feishu chat
      // last messaged this session). Falls back to legacy bound chat. Thread
      // the FIRST chunk under the user's input message_id; subsequent chunks
      // (when content is huge) flow inline so they group naturally.
      const stripped = stripLeadingAssistantLabel(content);
      if (!stripped.trim()) return;
      const chat = tracking.outboundChatId ?? legacyBoundChatId;
      if (!chat) {
        console.error('[Feishu] assistant text dropped: no outbound chat for session', sessionId);
        return;
      }

      const replyTo = tracking.firstReplyThreaded ? undefined : tracking.outboundReplyTo;
      if (replyTo) tracking.firstReplyThreaded = true;
      await sendMarkdown(chat, stripped, replyTo);
    },

    onTodos: async (sessionId, todos) => {
      const tracking = activeSessions.get(sessionId);
      if (!tracking || todos.length === 0) return;
      const chat = tracking.outboundChatId ?? legacyBoundChatId;
      if (chat) await sendMarkdown(chat, `**Tasks:**\n${formatTodos(todos)}`);
    },

    onToolCall: async (_sessionId, _tool) => {
      // Disabled to keep message volume sane.
    },

    onToolResult: async (_sessionId, _result) => {
      // Disabled to keep message volume sane.
    },

    onPlanModeChange: async (sessionId, inPlanMode) => {
      const tracking = activeSessions.get(sessionId);
      if (!tracking) return;
      const chat = tracking.outboundChatId ?? legacyBoundChatId;
      if (chat) await sendMarkdown(chat, inPlanMode ? '_Planning mode_' : '_Execution mode_');
    },
  }, { replaceDuplicateSessions: true });

  function getCurrentSession(): SessionTracking | null {
    if (currentSessionId) {
      const s = activeSessions.get(currentSessionId);
      if (s) return s;
      currentSessionId = null;
    }
    if (activeSessions.size === 1) {
      return activeSessions.values().next().value ?? null;
    }
    return null;
  }

  function getSessionByName(name: string): SessionTracking | null {
    const nl = name.toLowerCase();
    for (const t of activeSessions.values()) {
      if (t.sessionName.toLowerCase().startsWith(nl)) return t;
    }
    return null;
  }

  function getMostRecentSession(): SessionTracking | null {
    let recent: SessionTracking | null = null;
    for (const t of activeSessions.values()) {
      if (!recent || t.lastActivity > recent.lastActivity) recent = t;
    }
    return recent;
  }

  function plaintextOf(ev: FeishuEvent): string {
    if (ev.message_type === 'text') {
      try {
        const c = JSON.parse(ev.content);
        return typeof c?.text === 'string' ? c.text : ev.content;
      } catch {
        return ev.content;
      }
    }
    // Non-text inbound (image/file/post/card) — surface a placeholder so the
    // model knows something arrived. Codex may not be able to act on it but
    // shouldn't see it as silence.
    return `(${ev.message_type}) ${ev.content}`.slice(0, 4000);
  }

  function rememberHandledFeishuMessage(ev: any): boolean {
    const id = ev?.message_id || ev?.id || ev?.event_id;
    if (!id) return false;
    if (handledFeishuMessages.has(id)) return true;
    handledFeishuMessages.add(id);
    if (handledFeishuMessages.size > 500) {
      const first = handledFeishuMessages.values().next().value;
      if (first) handledFeishuMessages.delete(first);
    }
    return false;
  }

  /**
   * Inbound gate: combine legacy single-chat bypass with the access-store gate.
   * Legacy chat skips access.json entirely (back-compat). Everyone else flows
   * through access.gate() — p2p uses allowlist/pairing, groups use either an
   * explicit per-group policy or the permissive open-for-allowlisted-senders mode.
   */
  async function gateInbound(ev: FeishuEvent): Promise<GateResult> {
    if (legacyBoundChatId && ev.chat_id === legacyBoundChatId && ev.chat_type === 'p2p') {
      return { action: 'deliver', access: access.load() };
    }
    return access.gate(ev);
  }

  async function handleInbound(ev: any, source = 'event') {
    if (rememberHandledFeishuMessage(ev)) return;
    if (!ev.chat_id || !ev.sender_id) return;

    const trimmedPreview = plaintextOf(ev).slice(0, 120).replace(/\s+/g, ' ');
    console.error(`[Feishu] inbound ${source}: type=${ev.chat_type} chat=${ev.chat_id} from=${ev.sender_id} msg="${trimmedPreview}"`);

    const gate = await gateInbound(ev);

    if (gate.action === 'drop') {
      console.error(`[Feishu] gate drop: ${gate.reason}`);
      return;
    }

    if (gate.action === 'pair') {
      const lead = gate.isResend ? 'Still pending' : 'Pairing required';
      try {
        await sendText(ev.chat_id, `${lead} — run on the host:\n\nafk-code feishu access pair ${gate.code}`);
      } catch (err) {
        console.error('[Feishu] failed to send pairing code:', err);
      }
      return;
    }

    // Persist legacy bound chat on first DM in (matches old behavior).
    if (!legacyBoundChatId && ev.chat_type === 'p2p' && config.configFilePath) {
      try {
        await persistBoundChat(ev.chat_id);
      } catch (err) {
        console.error('[Feishu] failed to persist bound chat:', err);
      }
    }

    const text = plaintextOf(ev);
    if (!text) return;

    const trimmed = text.trim();
    if (trimmed.startsWith('/')) {
      await handleCommand(trimmed, ev);
      return;
    }

    const current = getCurrentSession();
    if (!current) {
      if (activeSessions.size === 0) {
        await sendText(ev.chat_id, `No active sessions. Start one with:\n${startCommandHint}`, ev.message_id);
      } else {
        const list = Array.from(activeSessions.values())
          .map((s) => `- ${s.sessionName}`)
          .join('\n');
        await sendText(ev.chat_id, `Multiple sessions. Select with /switch <name>:\n${list}`, ev.message_id);
      }
      return;
    }

    // Stick this session's outbound to the chat that just messaged us — so the
    // assistant reply goes back to the same chat (DM or group, doesn't matter).
    current.outboundChatId = ev.chat_id;
    current.outboundReplyTo = ev.message_id;
    current.firstReplyThreaded = false;

    feishuSentMessages.add(trimmed);
    const sent = sessionManager.sendInput(current.sessionId, text);
    if (!sent) {
      feishuSentMessages.delete(trimmed);
      await sendText(ev.chat_id, 'Failed to send input - session not connected.', ev.message_id);
    }
  }

  async function handleCommand(text: string, ev: FeishuEvent) {
    const [command, ...args] = text.split(' ');
    const sessionArg = args[0];

    let target: SessionTracking | null = null;
    if (sessionArg && !sessionArg.startsWith('/')) {
      target = getSessionByName(sessionArg);
    }
    if (!target) target = getMostRecentSession();

    const replyChat = ev.chat_id;
    const replyTo = ev.message_id;

    switch (command.toLowerCase()) {
      case '/sessions': {
        if (activeSessions.size === 0) {
          await sendText(replyChat, `No active sessions. Start one with: ${startCommandHint}`, replyTo);
          return;
        }
        const current = getCurrentSession();
        const list = Array.from(activeSessions.values())
          .map((s) => {
            const isCurrent = current && s.sessionId === current.sessionId;
            const display = `${s.projectName}/${s.sessionName}`;
            return isCurrent ? `- ${display} <- current` : `- ${display}`;
          })
          .join('\n');
        await sendMarkdown(replyChat, `**Active Sessions:**\n${list}\n\nSwitch with /switch <name>`, replyTo);
        return;
      }
      case '/switch':
      case '/select': {
        if (!sessionArg) {
          await sendText(replyChat, 'Usage: /switch <name>', replyTo);
          return;
        }
        const found = getSessionByName(sessionArg);
        if (found) {
          currentSessionId = found.sessionId;
          await sendText(replyChat, `Switched to: ${found.sessionName}`, replyTo);
        } else {
          await sendText(replyChat, `Session not found: ${sessionArg}`, replyTo);
        }
        return;
      }
      case '/background':
      case '/bg': {
        if (!target) { await sendText(replyChat, 'No active session.', replyTo); return; }
        const sent = sessionManager.sendInput(target.sessionId, '\x02');
        await sendText(replyChat, sent ? 'Sent Ctrl+B' : 'Failed - session not connected.', replyTo);
        return;
      }
      case '/interrupt':
      case '/stop': {
        if (!target) { await sendText(replyChat, 'No active session.', replyTo); return; }
        const sent = sessionManager.sendInput(target.sessionId, '\x1b');
        await sendText(replyChat, sent ? 'Sent Escape' : 'Failed - session not connected.', replyTo);
        return;
      }
      case '/mode': {
        if (!target) { await sendText(replyChat, 'No active session.', replyTo); return; }
        const sent = sessionManager.sendInput(target.sessionId, '\x1b[Z');
        await sendText(replyChat, sent ? 'Sent Shift+Tab' : 'Failed - session not connected.', replyTo);
        return;
      }
      case '/compact': {
        if (!target) { await sendText(replyChat, 'No active session.', replyTo); return; }
        const sent = sessionManager.sendInput(target.sessionId, '/compact\n');
        await sendText(replyChat, sent ? 'Sent /compact' : 'Failed - session not connected.', replyTo);
        return;
      }
      case '/model': {
        if (!target) { await sendText(replyChat, 'No active session.', replyTo); return; }
        const modelArg = args.slice(target === getSessionByName(args[0] || '') ? 1 : 0).join(' ');
        if (!modelArg) { await sendText(replyChat, 'Usage: /model <opus|sonnet|haiku>', replyTo); return; }
        const sent = sessionManager.sendInput(target.sessionId, `/model ${modelArg}\n`);
        await sendText(replyChat, sent ? `Sent /model ${modelArg}` : 'Failed - session not connected.', replyTo);
        return;
      }
      case '/help': {
        await sendMarkdown(
          replyChat,
          '**AFK Code (Feishu) commands:**\n' +
          '`/sessions` — list active sessions\n' +
          '`/switch <name>` — switch session\n' +
          '`/model <name>` — switch model\n' +
          '`/compact` — /compact\n' +
          '`/background` — Ctrl+B\n' +
          '`/interrupt` — Escape\n' +
          '`/mode` — Shift+Tab\n' +
          '`/help` — this message\n' +
          '\nAny non-/ message is forwarded to the current session.\n' +
          'Group chats: @mention the bot or reply to one of its messages to address it.',
          replyTo,
        );
        return;
      }
      default:
        return;
    }
  }

  let consumer: ChildProcess | null = null;
  let historyPoller: ReturnType<typeof setInterval> | null = null;
  let shuttingDown = false;

  function startConsumer() {
    consumer = spawn(LARK_CLI, [
      '--profile', config.larkProfile,
      'event', 'consume', 'im.message.receive_v1',
      '--as', 'bot',
    ], { stdio: ['pipe', 'pipe', 'pipe'] });

    let buf = '';
    consumer.stdout?.on('data', (chunk: Buffer) => {
      buf += chunk.toString();
      let nl: number;
      while ((nl = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, nl).trim();
        buf = buf.slice(nl + 1);
        if (!line) continue;
        try {
          const ev = JSON.parse(line);
          if (ev?.chat_id && ev?.sender_id) {
            handleInbound(ev).catch((e) => console.error('[Feishu] handleInbound:', e));
          }
        } catch (err) {
          console.error('[Feishu] bad event JSON:', err, 'line:', line.slice(0, 200));
        }
      }
    });

    consumer.stderr?.on('data', (d: Buffer) => {
      process.stderr.write(`[lark-cli event] ${d.toString()}`);
    });

    consumer.on('exit', (code, sig) => {
      console.error(`[Feishu] consumer exited code=${code} sig=${sig}`);
      consumer = null;
      if (!shuttingDown) {
        console.error('[Feishu] restarting consumer in 3s...');
        setTimeout(startConsumer, 3000);
      }
    });
  }

  async function pollHistory() {
    // History fallback only works for the legacy bound chat — we don't have
    // a way to poll history for "every group the bot might be in". Group msgs
    // missed during downtime stay missed; the live event consumer handles all
    // current traffic. (Acceptable trade-off; groups are best-effort.)
    if (!legacyBoundChatId) return;

    const r = await runLark(buildFeishuHistoryListArgs(legacyBoundChatId));
    if (!r.ok) {
      console.error(`[Feishu] history poll failed: ${r.stderr || r.stdout}`);
      return;
    }

    let parsed: any;
    try {
      parsed = JSON.parse(r.stdout);
    } catch (err) {
      console.error('[Feishu] history poll bad JSON:', err);
      return;
    }

    const messages = Array.isArray(parsed?.data?.messages) ? parsed.data.messages : [];
    if (!historySeeded) {
      for (const message of messages) {
        const position = Number(message?.message_position ?? 0);
        if (position > historyWatermarkPosition) historyWatermarkPosition = position;
      }
      historySeeded = true;
      console.error(`[Feishu] history fallback seeded at position ${historyWatermarkPosition}`);
      return;
    }

    for (const message of messages.reverse()) {
      const position = Number(message?.message_position ?? 0);
      if (position && position <= historyWatermarkPosition) continue;
      const ev = feishuHistoryMessageToReceiveEvent(message);
      if (ev) {
        await handleInbound(ev, 'history');
      }
      if (position > historyWatermarkPosition) historyWatermarkPosition = position;
    }
  }

  function startHistoryPoller() {
    if (historyPoller) return;
    historyPoller = setInterval(() => {
      pollHistory().catch((err) => console.error('[Feishu] history poll:', err));
    }, 5000);
    void pollHistory().catch((err) => console.error('[Feishu] history poll:', err));
  }

  function shutdown() {
    shuttingDown = true;
    if (historyPoller) {
      clearInterval(historyPoller);
      historyPoller = null;
    }
    if (consumer) {
      try { consumer.stdin?.end(); } catch {}
      try { consumer.kill('SIGTERM'); } catch {}
    }
  }

  return { sessionManager, startConsumer, startHistoryPoller, shutdown, access };
}

// Re-export so `chunkMessage` consumers in tests still work
export { FEISHU_MAX_MESSAGE_LENGTH };
