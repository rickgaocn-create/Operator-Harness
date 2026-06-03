/**
 * Session manager for chat bridges. Watches Claude or Codex JSONL transcripts
 * and relays messages back through the active channel.
 */

import { watch, type FSWatcher } from 'fs';
import { readdir, readFile, stat, unlink, mkdir } from 'fs/promises';
import { createServer, type Server, type Socket } from 'net';
import { createHash } from 'crypto';
import { join } from 'path';
import type { TodoItem } from '../types.js';

const DAEMON_SOCKET = process.env.AFK_DAEMON_SOCKET ?? '/tmp/afk-code-daemon.sock';
const CODEX_SESSION_LOOKBACK_MS = 60 * 1000;
const CODEX_SESSION_FUTURE_SKEW_MS = 2 * 60 * 1000;
type TranscriptBackend = 'claude' | 'codex';

export function acceptsDaemonSessionToken(expected: string | undefined, actual: unknown): boolean {
  return !expected || (typeof actual === 'string' && actual.length > 0 && actual === expected);
}

export function codexSessionTimestampMatchesStart(startedAt: Date, metaTimestamp: number | undefined): boolean {
  if (typeof metaTimestamp !== 'number') return true;
  const start = startedAt.getTime();
  return (
    metaTimestamp >= start - CODEX_SESSION_LOOKBACK_MS &&
    metaTimestamp <= start + CODEX_SESSION_FUTURE_SKEW_MS
  );
}

export interface SessionInfo {
  id: string;
  name: string;
  cwd: string;
  projectDir: string;
  transcriptBackend: TranscriptBackend;
  status: 'running' | 'idle' | 'ended';
  startedAt: Date;
}

type SessionIdentityInfo = Pick<
  SessionInfo,
  'name' | 'cwd' | 'projectDir' | 'transcriptBackend'
>;

export interface SessionManagerOptions {
  replaceDuplicateSessions?: boolean;
}

interface InternalSession extends SessionInfo {
  socket: Socket;
  watcher?: FSWatcher;
  watchedFile?: string;
  seenMessages: Set<string>;
  slugFound: boolean;
  lastTodosHash: string;
  inPlanMode: boolean;
  initialFileStats: Map<string, number>;
  locatingFile: boolean;
  pollInterval?: ReturnType<typeof setInterval>;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ToolCallInfo {
  id: string;
  name: string;
  input: any;
}

export interface ToolResultInfo {
  toolUseId: string;
  content: string;
  isError: boolean;
}

export interface SessionEvents {
  onSessionStart: (session: SessionInfo) => void;
  onSessionEnd: (sessionId: string) => void;
  onSessionUpdate: (sessionId: string, name: string) => void;
  onSessionStatus: (sessionId: string, status: 'running' | 'idle' | 'ended') => void;
  onMessage: (sessionId: string, role: 'user' | 'assistant', content: string) => void;
  onTodos: (sessionId: string, todos: TodoItem[]) => void;
  onToolCall: (sessionId: string, tool: ToolCallInfo) => void;
  onToolResult: (sessionId: string, result: ToolResultInfo) => void;
  onPlanModeChange: (sessionId: string, inPlanMode: boolean) => void;
}

function normalizePathForIdentity(path: string): string {
  const normalized = path.replace(/\\/g, '/').replace(/\/+$/g, '');
  return process.platform === 'win32' ? normalized.toLowerCase() : normalized;
}

function normalizeNameForIdentity(name: string): string {
  return name.trim().replace(/\s+/g, ' ');
}

export function sessionIdentityKey(session: SessionIdentityInfo): string {
  if (session.transcriptBackend === 'codex') {
    return [
      session.transcriptBackend,
      normalizePathForIdentity(session.cwd),
      normalizePathForIdentity(session.projectDir),
    ].join('\0');
  }

  return [
    session.transcriptBackend,
    normalizePathForIdentity(session.cwd),
    normalizePathForIdentity(session.projectDir),
    normalizeNameForIdentity(session.name),
  ].join('\0');
}

export function sessionsHaveSameIdentity(
  left: SessionIdentityInfo,
  right: SessionIdentityInfo
): boolean {
  return sessionIdentityKey(left) === sessionIdentityKey(right);
}

export function buildSessionInputPayloads(
  transcriptBackend: TranscriptBackend,
  text: string
): Array<{ text?: string; submitText?: string }> {
  if (transcriptBackend !== 'codex' || isRawTerminalInput(text)) {
    return [{ text }];
  }

  const prompt = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  return [{ submitText: prompt }];
}

function isRawTerminalInput(text: string): boolean {
  if (text.startsWith('\x1b') || text.startsWith('\x02')) return true;
  return text.length === 1 && text.charCodeAt(0) < 0x20;
}

function hash(data: string): string {
  return createHash('md5').update(data).digest('hex');
}

export class SessionManager {
  private sessions = new Map<string, InternalSession>();
  private claimedFiles = new Set<string>();
  private events: SessionEvents;
  private options: SessionManagerOptions;
  private server: Server | null = null;

  constructor(events: SessionEvents, options: SessionManagerOptions = {}) {
    this.events = events;
    this.options = options;
  }

  async start(): Promise<void> {
    try {
      await unlink(DAEMON_SOCKET);
    } catch {}

    this.server = createServer((socket) => {
      let messageBuffer = '';

      socket.on('data', (data) => {
        messageBuffer += data.toString();
        const lines = messageBuffer.split('\n');
        messageBuffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const parsed = JSON.parse(line);
            void this.handleSessionMessage(socket, parsed);
          } catch (error) {
            console.error('[SessionManager] Error parsing message:', error);
          }
        }
      });

      socket.on('error', (error) => {
        console.error('[SessionManager] Socket error:', error);
      });

      socket.on('close', () => {
        for (const [id, session] of this.sessions) {
          if (session.socket === socket) {
            console.log(`[SessionManager] Session disconnected: ${id}`);
            this.stopWatching(session);
            this.sessions.delete(id);
            this.events.onSessionEnd(id);
            break;
          }
        }
      });
    });

    this.server.listen(DAEMON_SOCKET, () => {
      console.log(`[SessionManager] Listening on ${DAEMON_SOCKET}`);
    });
  }

  stop(): void {
    for (const session of this.sessions.values()) {
      this.stopWatching(session);
    }
    this.sessions.clear();
    if (this.server) {
      this.server.close();
    }
  }

  sendInput(sessionId: string, text: string): boolean {
    const session = this.sessions.get(sessionId);
    if (!session) {
      console.error(`[SessionManager] Session not found: ${sessionId}`);
      return false;
    }

    const payloads = buildSessionInputPayloads(session.transcriptBackend, text);

    try {
      for (const payload of payloads) {
        session.socket.write(JSON.stringify({ type: 'input', ...payload }) + '\n');
      }
    } catch (err) {
      console.error(`[SessionManager] Failed to send input to ${sessionId}:`, err);
      this.stopWatching(session);
      this.sessions.delete(sessionId);
      this.events.onSessionEnd(sessionId);
      return false;
    }

    return true;
  }

  getSession(sessionId: string): SessionInfo | undefined {
    const session = this.sessions.get(sessionId);
    return session ? this.toSessionInfo(session) : undefined;
  }

  getAllSessions(): SessionInfo[] {
    return Array.from(this.sessions.values()).map((session) => this.toSessionInfo(session));
  }

  private toSessionInfo(session: InternalSession): SessionInfo {
    return {
      id: session.id,
      name: session.name,
      cwd: session.cwd,
      projectDir: session.projectDir,
      transcriptBackend: session.transcriptBackend,
      status: session.status,
      startedAt: session.startedAt,
    };
  }

  private async handleSessionMessage(socket: Socket, message: any): Promise<void> {
    switch (message.type) {
      case 'session_start': {
        if (!acceptsDaemonSessionToken(process.env.AFK_DAEMON_TOKEN, message.sessionToken)) {
          console.error(`[SessionManager] Rejected session without matching token: ${message.name || message.command?.join(' ') || message.id}`);
          try {
            socket.write(JSON.stringify({ type: 'session_rejected', reason: 'invalid_session_token' }) + '\n');
            socket.end();
          } catch {}
          break;
        }

        const transcriptBackend: TranscriptBackend = message.transcriptBackend === 'codex' ? 'codex' : 'claude';
        const startedAt = message.startedAt ? new Date(message.startedAt) : new Date();
        const initialFileStats = await this.snapshotJsonlFiles(message.projectDir, transcriptBackend);

        const session: InternalSession = {
          id: message.id,
          name: message.name || message.command?.join(' ') || 'Session',
          cwd: message.cwd,
          projectDir: message.projectDir,
          transcriptBackend,
          socket,
          status: 'running',
          seenMessages: new Set(),
          startedAt,
          slugFound: false,
          lastTodosHash: '',
          inPlanMode: false,
          initialFileStats,
          locatingFile: false,
        };

        if (this.options.replaceDuplicateSessions) {
          this.replaceDuplicateSessions(session);
        }

        this.sessions.set(message.id, session);
        console.log(
          `[SessionManager] Session started: ${message.id} (${session.transcriptBackend}) - ${session.name}`
        );
        console.log(`[SessionManager] Snapshot: ${initialFileStats.size} existing JSONL files`);

        this.events.onSessionStart(this.toSessionInfo(session));
        await this.startWatching(session);
        break;
      }

      case 'session_end': {
        const session = this.sessions.get(message.sessionId);
        if (session) {
          console.log(`[SessionManager] Session ended: ${message.sessionId}`);
          this.stopWatching(session);
          this.sessions.delete(message.sessionId);
          this.events.onSessionEnd(message.sessionId);
        }
        break;
      }
    }
  }

  private replaceDuplicateSessions(newSession: InternalSession): void {
    for (const [id, existing] of Array.from(this.sessions)) {
      if (id === newSession.id) continue;
      if (!sessionsHaveSameIdentity(existing, newSession)) continue;

      console.log(
        `[SessionManager] Replacing duplicate session ${existing.id} with ${newSession.id}`
      );
      this.stopWatching(existing);
      this.sessions.delete(id);
      try {
        existing.socket.write(JSON.stringify({
          type: 'session_replaced',
          sessionId: existing.id,
          replacedBy: newSession.id,
        }) + '\n');
        existing.socket.end();
      } catch {}
      this.events.onSessionEnd(id);
    }
  }

  private async snapshotJsonlFiles(
    projectDir: string,
    transcriptBackend: TranscriptBackend
  ): Promise<Map<string, number>> {
    const stats = new Map<string, number>();
    try {
      const files = await this.listJsonlFiles(projectDir, transcriptBackend);
      for (const path of files) {
        const fileStat = await stat(path);
        stats.set(path, fileStat.mtimeMs);
      }
    } catch {}
    return stats;
  }

  private async listJsonlFiles(
    projectDir: string,
    transcriptBackend: TranscriptBackend
  ): Promise<string[]> {
    if (transcriptBackend === 'claude') {
      const files = await readdir(projectDir);
      return files
        .filter((name) => name.endsWith('.jsonl') && !name.startsWith('agent-'))
        .map((name) => join(projectDir, name));
    }

    return this.collectCodexRolloutFiles(projectDir);
  }

  private async collectCodexRolloutFiles(dir: string, files: string[] = []): Promise<string[]> {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) {
        await this.collectCodexRolloutFiles(path, files);
      } else if (entry.isFile() && entry.name.startsWith('rollout-') && entry.name.endsWith('.jsonl')) {
        files.push(path);
      }
    }
    return files;
  }

  private async hasConversationMessages(
    path: string,
    transcriptBackend: TranscriptBackend,
    session?: InternalSession
  ): Promise<boolean> {
    try {
      const content = await readFile(path, 'utf-8');
      if (transcriptBackend === 'claude') {
        return content.includes('"type":"user"') || content.includes('"type":"assistant"');
      }

      return this.codexFileMatchesSession(content, session).matched;
    } catch {
      return false;
    }
  }

  private codexFileMatchesSession(
    content: string,
    session?: InternalSession
  ): { matched: boolean; hasMessages: boolean; metaTimestamp?: number } {
    let metaCwd: string | undefined;
    let metaTimestamp: number | undefined;
    let hasMessages = false;

    for (const line of content.split('\n')) {
      if (!line.trim()) continue;
      try {
        const data = JSON.parse(line);

        if (data.type === 'session_meta' && data.payload) {
          metaCwd = data.payload.cwd;
          const rawTimestamp = data.payload.timestamp || data.timestamp;
          const parsedTimestamp = typeof rawTimestamp === 'string' ? Date.parse(rawTimestamp) : NaN;
          if (!Number.isNaN(parsedTimestamp)) {
            metaTimestamp = parsedTimestamp;
          }
          continue;
        }

        if (
          data.type === 'response_item' &&
          data.payload?.type === 'message' &&
          (data.payload.role === 'assistant' || data.payload.role === 'user')
        ) {
          hasMessages = true;
        }
      } catch {}
    }

    if (!session) {
      return { matched: Boolean(metaCwd), hasMessages, metaTimestamp };
    }

    if (!metaCwd || metaCwd !== session.cwd) {
      return { matched: false, hasMessages, metaTimestamp };
    }

    if (!codexSessionTimestampMatchesStart(session.startedAt, metaTimestamp)) {
      return { matched: false, hasMessages, metaTimestamp };
    }

    return { matched: true, hasMessages, metaTimestamp };
  }

  private async findActiveJsonlFile(session: InternalSession): Promise<string | null> {
    try {
      const allPaths = (await this.listJsonlFiles(session.projectDir, session.transcriptBackend))
        .filter((path) => !this.claimedFiles.has(path));

      if (allPaths.length === 0) return null;

      const fileStats = await Promise.all(
        allPaths.map(async (path) => {
          const fileStat = await stat(path);
          return { path, mtime: fileStat.mtimeMs };
        })
      );

      fileStats.sort((a, b) => b.mtime - a.mtime);

      if (session.transcriptBackend === 'codex') {
        let best: { path: string; score: number } | null = null;

        for (const { path, mtime } of fileStats) {
          const content = await readFile(path, 'utf-8');
          const match = this.codexFileMatchesSession(content, session);
          if (!match.matched) continue;

          const initialMtime = session.initialFileStats.get(path);
          if (
            initialMtime !== undefined &&
            mtime <= initialMtime &&
            mtime < session.startedAt.getTime() - 1000
          ) {
            continue;
          }

          const createdAfterStart = initialMtime === undefined ? 300_000 : 0;
          const modifiedAfterStart = initialMtime !== undefined && mtime > initialMtime ? 150_000 : 0;
          const recentWrite = mtime >= session.startedAt.getTime() ? 75_000 : 0;
          const messageBonus = match.hasMessages ? 10_000 : 0;
          const timeBonus = typeof match.metaTimestamp === 'number'
            ? Math.max(0, 600_000 - Math.abs(match.metaTimestamp - session.startedAt.getTime()))
            : 0;

          const score = createdAfterStart + modifiedAfterStart + recentWrite + messageBonus + timeBonus;
          if (!best || score > best.score) {
            best = { path, score };
          }
        }

        if (best) {
          console.log(`[SessionManager] Matched Codex transcript: ${best.path}`);
          return best.path;
        }

        return null;
      }

      for (const { path, mtime } of fileStats) {
        const initialMtime = session.initialFileStats.get(path);
        if (initialMtime !== undefined && mtime > initialMtime) {
          if (await this.hasConversationMessages(path, session.transcriptBackend, session)) {
            console.log(`[SessionManager] Found modified JSONL (--continue): ${path}`);
            return path;
          }
        }
      }

      for (const { path } of fileStats) {
        const initialMtime = session.initialFileStats.get(path);
        if (initialMtime === undefined) {
          if (await this.hasConversationMessages(path, session.transcriptBackend, session)) {
            console.log(`[SessionManager] Found new JSONL: ${path}`);
            return path;
          }
        }
      }

      return null;
    } catch {
      return null;
    }
  }

  private async processJsonlUpdates(session: InternalSession): Promise<void> {
    if (!session.watchedFile) return;

    try {
      const content = await readFile(session.watchedFile, 'utf-8');
      const lines = content.split('\n').filter(Boolean);

      for (const line of lines) {
        const lineHash = hash(line);
        if (session.seenMessages.has(lineHash)) continue;
        session.seenMessages.add(lineHash);

        if (!session.slugFound) {
          const slug = this.extractSlug(line);
          if (slug) {
            session.slugFound = true;
            session.name = slug;
            console.log(`[SessionManager] Session ${session.id} name: ${slug}`);
            this.events.onSessionUpdate(session.id, slug);
          }
        }

        const todos = this.extractTodos(line);
        if (todos) {
          const todosHash = hash(JSON.stringify(todos));
          if (todosHash !== session.lastTodosHash) {
            session.lastTodosHash = todosHash;
            this.events.onTodos(session.id, todos);
          }
        }

        const planModeStatus = this.detectPlanMode(line);
        if (planModeStatus !== null && planModeStatus !== session.inPlanMode) {
          session.inPlanMode = planModeStatus;
          console.log(`[SessionManager] Session ${session.id} plan mode: ${planModeStatus}`);
          this.events.onPlanModeChange(session.id, planModeStatus);
        }

        const toolCalls = this.extractToolCalls(line);
        for (const tool of toolCalls) {
          this.events.onToolCall(session.id, tool);
        }

        const toolResults = this.extractToolResults(line);
        for (const result of toolResults) {
          this.events.onToolResult(session.id, result);
        }

        const parsed = this.parseJsonlLine(line);
        if (parsed) {
          const messageTime = new Date(parsed.timestamp);
          if (messageTime < session.startedAt) continue;
          this.events.onMessage(session.id, parsed.role, parsed.content);
          this.events.onSessionStatus(session.id, session.status);
        }
      }
    } catch (err) {
      console.error('[SessionManager] Error processing JSONL:', err);
    }
  }

  private async startWatching(session: InternalSession): Promise<void> {
    await this.attachActiveJsonlFile(session);

    if (session.watchedFile) {
      await this.processJsonlUpdates(session);
    } else {
      console.log(`[SessionManager] Waiting for JSONL changes in ${session.projectDir}`);
    }

    try {
      await mkdir(session.projectDir, { recursive: true });
      session.watcher = watch(
        session.projectDir,
        { recursive: session.transcriptBackend === 'codex' },
        async (_, filename) => {
          const changedPath = filename ? join(session.projectDir, filename.toString()) : '';

          await this.attachActiveJsonlFile(session);

          if (!session.watchedFile) return;
          if (session.transcriptBackend === 'claude' && changedPath && changedPath !== session.watchedFile) {
            return;
          }

          await this.processJsonlUpdates(session);
        }
      );
    } catch (err) {
      console.error('[SessionManager] Error setting up watcher:', err);
    }

    session.pollInterval = setInterval(async () => {
      if (!this.sessions.has(session.id)) {
        if (session.pollInterval) clearInterval(session.pollInterval);
        return;
      }

      if (!session.watchedFile) {
        await this.attachActiveJsonlFile(session);
      }

      if (session.watchedFile) {
        await this.processJsonlUpdates(session);
      }
    }, 1000);
  }

  private async attachActiveJsonlFile(session: InternalSession): Promise<void> {
    if (session.watchedFile || session.locatingFile) return;

    session.locatingFile = true;
    try {
      if (session.watchedFile) return;
      const jsonlFile = await this.findActiveJsonlFile(session);
      if (!jsonlFile || session.watchedFile) return;

      session.watchedFile = jsonlFile;
      this.claimedFiles.add(jsonlFile);
      console.log(`[SessionManager] Watching: ${jsonlFile}`);
    } finally {
      session.locatingFile = false;
    }
  }

  private stopWatching(session: InternalSession): void {
    if (session.watcher) {
      session.watcher.close();
    }
    if (session.pollInterval) {
      clearInterval(session.pollInterval);
    }
    if (session.watchedFile) {
      this.claimedFiles.delete(session.watchedFile);
    }
  }

  private detectPlanMode(line: string): boolean | null {
    try {
      const data = JSON.parse(line);
      let content = '';

      if (data.type === 'user') {
        content = this.extractClaudeText(data.message?.content);
      } else if (data.type === 'response_item' && data.payload?.type === 'message') {
        content = this.extractCodexText(data.payload.content, data.payload.role);
      }

      if (!content) return null;
      if (content.includes('<system-reminder>') && content.includes('Plan mode is active')) return true;
      if (content.includes('Exited Plan Mode') || content.includes('exited plan mode')) return false;
      return null;
    } catch {
      return null;
    }
  }

  private extractToolCalls(line: string): ToolCallInfo[] {
    try {
      const data = JSON.parse(line);

      if (data.type === 'assistant') {
        const content = data.message?.content;
        if (!Array.isArray(content)) return [];

        return content
          .filter((block: any) => block.type === 'tool_use' && block.id && block.name)
          .map((block: any) => ({
            id: block.id,
            name: block.name,
            input: block.input || {},
          }));
      }

      if (data.type === 'response_item' && data.payload?.type === 'function_call' && data.payload.call_id) {
        let input: any = {};
        if (typeof data.payload.arguments === 'string' && data.payload.arguments.trim()) {
          try {
            input = JSON.parse(data.payload.arguments);
          } catch {
            input = { raw: data.payload.arguments };
          }
        }

        return [{
          id: data.payload.call_id,
          name: data.payload.name || 'function_call',
          input,
        }];
      }

      return [];
    } catch {
      return [];
    }
  }

  private extractToolResults(line: string): ToolResultInfo[] {
    try {
      const data = JSON.parse(line);

      if (data.type === 'user') {
        const content = data.message?.content;
        if (!Array.isArray(content)) return [];

        return content
          .filter((block: any) => block.type === 'tool_result' && block.tool_use_id)
          .map((block: any) => ({
            toolUseId: block.tool_use_id,
            content: typeof block.content === 'string'
              ? block.content
              : Array.isArray(block.content)
                ? block.content
                    .filter((entry: any) => entry.type === 'text')
                    .map((entry: any) => entry.text)
                    .join('\n')
                : '',
            isError: block.is_error === true,
          }));
      }

      if (data.type === 'response_item' && data.payload?.type === 'function_call_output' && data.payload.call_id) {
        return [{
          toolUseId: data.payload.call_id,
          content: typeof data.payload.output === 'string'
            ? data.payload.output
            : JSON.stringify(data.payload.output ?? ''),
          isError: data.payload.is_error === true,
        }];
      }

      return [];
    } catch {
      return [];
    }
  }

  private extractSlug(line: string): string | null {
    try {
      const data = JSON.parse(line);
      return typeof data.slug === 'string' ? data.slug : null;
    } catch {
      return null;
    }
  }

  private extractTodos(line: string): TodoItem[] | null {
    try {
      const data = JSON.parse(line);
      if (data.todos && Array.isArray(data.todos) && data.todos.length > 0) {
        return data.todos.map((todo: any) => ({
          content: todo.content || '',
          status: todo.status || 'pending',
          activeForm: todo.activeForm,
        }));
      }
      return null;
    } catch {
      return null;
    }
  }

  private parseJsonlLine(line: string): ChatMessage | null {
    try {
      const data = JSON.parse(line);

      if (data.type === 'user' || data.type === 'assistant') {
        if (data.isMeta || data.subtype) return null;
        const message = data.message;
        if (!message || !message.role) return null;

        const content = this.extractClaudeText(message.content).trim();
        if (!content) return null;

        return {
          role: message.role as 'user' | 'assistant',
          content,
          timestamp: data.timestamp || new Date().toISOString(),
        };
      }

      if (data.type === 'response_item' && data.payload?.type === 'message') {
        const role = data.payload.role;
        if (role !== 'assistant') return null;

        const content = this.extractCodexText(data.payload.content, role).trim();
        if (!content) return null;

        return {
          role,
          content,
          timestamp: data.timestamp || new Date().toISOString(),
        };
      }

      return null;
    } catch {
      return null;
    }
  }

  private extractClaudeText(content: unknown): string {
    if (typeof content === 'string') return content;
    if (!Array.isArray(content)) return '';

    return content
      .filter((block: any) => block.type === 'text' && block.text)
      .map((block: any) => block.text)
      .join('');
  }

  private extractCodexText(content: unknown, role: 'user' | 'assistant'): string {
    if (typeof content === 'string') return content;
    if (!Array.isArray(content)) return '';

    return content
      .filter((block: any) => {
        if (!block || typeof block !== 'object') return false;
        if (role === 'assistant') {
          return (block.type === 'output_text' || block.type === 'text') && block.text;
        }
        return (block.type === 'input_text' || block.type === 'text') && block.text;
      })
      .map((block: any) => block.text)
      .join('');
  }
}
