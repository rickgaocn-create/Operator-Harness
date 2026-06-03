/**
 * Feishu access policy + inbound gate for the codex bridge.
 *
 * Ported from the fs-claude MCP plugin (~/.claude/plugins/marketplaces/local/feishu/server.ts).
 * Same access.json shape so the two bridges stay conceptually aligned. Lives at
 * ~/.afk-code/feishu-access.json (separate from fs-claude's
 * ~/.claude/channels/feishu/access.json — different bot, different tenant).
 */

import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'fs';
import { homedir } from 'os';
import { join, dirname } from 'path';
import { randomBytes } from 'crypto';
import spawn from 'cross-spawn';

export type DmPolicy = 'pairing' | 'allowlist' | 'disabled';

export interface PendingEntry {
  senderId: string;   // ou_xxx
  chatId: string;     // oc_xxx
  createdAt: number;
  expiresAt: number;
  replies: number;
}

export interface GroupPolicy {
  requireMention: boolean;
  allowFrom: string[];
}

export interface Access {
  dmPolicy: DmPolicy;
  allowFrom: string[];
  groups: Record<string, GroupPolicy>;
  pending: Record<string, PendingEntry>;
  mentionPatterns?: string[];
  textChunkLimit?: number;
  chunkMode?: 'length' | 'newline';
  groupOpenForAllowedSenders?: boolean;
}

export interface FeishuEvent {
  chat_id: string;
  chat_type: 'p2p' | 'group';
  content: string;
  message_id: string;
  sender_id: string;
  message_type: string;
  create_time?: string;
  event_id?: string;
}

export type GateResult =
  | { action: 'deliver'; access: Access }
  | { action: 'drop'; reason: string }
  | { action: 'pair'; code: string; isResend: boolean };

export interface AccessStoreOptions {
  larkProfile: string;
  larkCli: string;
  filePath?: string;
}

export class AccessStore {
  readonly filePath: string;
  readonly larkProfile: string;
  readonly larkCli: string;
  private cachedBotOpenId: string | null | undefined = undefined;
  private readonly sentIdsFile: string;
  private readonly sentIds = new Set<string>();
  private sentIdsDirty = false;

  constructor(opts: AccessStoreOptions) {
    this.larkProfile = opts.larkProfile;
    this.larkCli = opts.larkCli;
    this.filePath = opts.filePath ?? join(homedir(), '.afk-code', 'feishu-access.json');
    this.sentIdsFile = join(dirname(this.filePath), 'feishu-sent-ids.json');
    this.loadSentIds();
    setInterval(() => this.persistSentIds(), 2000).unref();
  }

  load(): Access {
    try {
      const raw = readFileSync(this.filePath, 'utf8');
      const parsed = JSON.parse(raw) as Partial<Access>;
      return {
        dmPolicy: parsed.dmPolicy ?? 'allowlist',
        allowFrom: parsed.allowFrom ?? [],
        groups: parsed.groups ?? {},
        pending: parsed.pending ?? {},
        mentionPatterns: parsed.mentionPatterns,
        textChunkLimit: parsed.textChunkLimit,
        chunkMode: parsed.chunkMode,
        groupOpenForAllowedSenders: parsed.groupOpenForAllowedSenders ?? true,
      };
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === 'ENOENT') return defaultAccess();
      try { renameSync(this.filePath, `${this.filePath}.corrupt-${Date.now()}`); } catch {}
      process.stderr.write(`[Feishu access] ${this.filePath} corrupt, moved aside\n`);
      return defaultAccess();
    }
  }

  save(a: Access): void {
    mkdirSync(dirname(this.filePath), { recursive: true });
    const tmp = this.filePath + '.tmp';
    writeFileSync(tmp, JSON.stringify(a, null, 2) + '\n');
    renameSync(tmp, this.filePath);
  }

  pruneExpired(a: Access): boolean {
    const now = Date.now();
    let changed = false;
    for (const [code, p] of Object.entries(a.pending)) {
      if (p.expiresAt < now) {
        delete a.pending[code];
        changed = true;
      }
    }
    return changed;
  }

  async gate(ev: FeishuEvent): Promise<GateResult> {
    const access = this.load();
    if (this.pruneExpired(access)) this.save(access);

    if (access.dmPolicy === 'disabled') return { action: 'drop', reason: 'policy-disabled' };

    const isDM = ev.chat_type === 'p2p';
    const senderId = ev.sender_id;

    if (isDM) {
      if (access.allowFrom.includes(senderId)) return { action: 'deliver', access };
      if (access.dmPolicy === 'allowlist') return { action: 'drop', reason: 'sender-not-allowlisted' };

      // pairing mode
      for (const [code, p] of Object.entries(access.pending)) {
        if (p.senderId === senderId) {
          if ((p.replies ?? 1) >= 2) return { action: 'drop', reason: 'pair-resend-limit' };
          p.replies = (p.replies ?? 1) + 1;
          this.save(access);
          return { action: 'pair', code, isResend: true };
        }
      }
      if (Object.keys(access.pending).length >= 3) return { action: 'drop', reason: 'pair-queue-full' };

      const code = randomBytes(3).toString('hex');
      const now = Date.now();
      access.pending[code] = {
        senderId,
        chatId: ev.chat_id,
        createdAt: now,
        expiresAt: now + 60 * 60 * 1000,
        replies: 1,
      };
      this.save(access);
      return { action: 'pair', code, isResend: false };
    }

    // group chat
    const policy = access.groups[ev.chat_id];
    if (policy) {
      const groupAllowFrom = policy.allowFrom ?? [];
      if (groupAllowFrom.length > 0 && !groupAllowFrom.includes(senderId)) {
        return { action: 'drop', reason: 'group-sender-not-allowed' };
      }
      if (policy.requireMention) {
        const ctx = await this.fetchMessageContext(ev.message_id);
        const botId = await this.botOpenId();
        const mentioned = ctx && botId ? ctx.mentionedOpenIds.has(botId) : false;
        const repliedToBot = ctx?.parentId ? this.sentIds.has(ctx.parentId) : false;
        if (!mentioned && !repliedToBot) return { action: 'drop', reason: 'group-mention-required' };
      }
      return { action: 'deliver', access };
    }

    // permissive: allowFrom sender + (bot @mentioned OR replying to bot's prior message)
    if (access.groupOpenForAllowedSenders === false) return { action: 'drop', reason: 'group-not-configured' };
    if (!access.allowFrom.includes(senderId)) return { action: 'drop', reason: 'group-sender-not-allowlisted' };

    const ctx = await this.fetchMessageContext(ev.message_id);
    if (!ctx) return { action: 'drop', reason: 'group-ctx-fetch-failed' };
    const botId = await this.botOpenId();
    const mentioned = botId ? ctx.mentionedOpenIds.has(botId) : false;
    const repliedToBot = ctx.parentId ? this.sentIds.has(ctx.parentId) : false;
    if (mentioned || repliedToBot) return { action: 'deliver', access };
    return { action: 'drop', reason: 'group-not-addressed-to-bot' };
  }

  // --- bot identity ---
  async botOpenId(): Promise<string | undefined> {
    if (this.cachedBotOpenId !== undefined) return this.cachedBotOpenId ?? undefined;
    const r = await this.runLark(['auth', 'status', '--verify']);
    if (!r.ok) {
      process.stderr.write(`[Feishu access] bot openId probe failed (${r.code}): ${r.stderr.slice(0, 200)}\n`);
      this.cachedBotOpenId = null;
      return undefined;
    }
    try {
      const parsed = JSON.parse(r.stdout);
      const id = parsed?.identities?.bot?.openId;
      if (typeof id === 'string' && id.startsWith('ou_')) {
        this.cachedBotOpenId = id;
        process.stderr.write(`[Feishu access] bot openId → ${id}\n`);
        return id;
      }
    } catch (err) {
      process.stderr.write(`[Feishu access] bot openId parse failed: ${err}\n`);
    }
    this.cachedBotOpenId = null;
    return undefined;
  }

  async fetchMessageContext(messageId: string): Promise<{ parentId?: string; mentionedOpenIds: Set<string> } | null> {
    const r = await this.runLark(['api', 'GET', `im/v1/messages/${messageId}`, '--as', 'bot']);
    if (!r.ok) {
      process.stderr.write(`[Feishu access] fetchMessageContext failed for ${messageId} (${r.code}): ${r.stderr.slice(0, 200)}\n`);
      return null;
    }
    try {
      const parsed = JSON.parse(r.stdout);
      const msg = parsed?.data?.items?.[0];
      if (!msg) return null;
      const out = {
        parentId: typeof msg.parent_id === 'string' && msg.parent_id ? msg.parent_id : undefined,
        mentionedOpenIds: new Set<string>(),
      };
      const mentions = msg.mentions;
      if (Array.isArray(mentions)) {
        for (const m of mentions) {
          const id = m?.id;
          if (typeof id === 'string' && id.startsWith('ou_')) out.mentionedOpenIds.add(id);
        }
      }
      return out;
    } catch (err) {
      process.stderr.write(`[Feishu access] fetchMessageContext parse failed: ${err}\n`);
      return null;
    }
  }

  // --- sent ids (persistent, used for "user replied to bot" detection in groups) ---
  noteSent(id: string): void {
    if (!id || this.sentIds.has(id)) return;
    this.sentIds.add(id);
    this.sentIdsDirty = true;
    if (this.sentIds.size > 1000) {
      const first = this.sentIds.values().next().value;
      if (first) this.sentIds.delete(first);
    }
  }

  hasSent(id: string): boolean {
    return this.sentIds.has(id);
  }

  private loadSentIds(): void {
    if (!existsSync(this.sentIdsFile)) return;
    try {
      const arr = JSON.parse(readFileSync(this.sentIdsFile, 'utf8')) as string[];
      if (Array.isArray(arr)) for (const id of arr) this.sentIds.add(id);
    } catch (err) {
      process.stderr.write(`[Feishu access] load sent-ids failed: ${err}\n`);
    }
  }

  private persistSentIds(): void {
    if (!this.sentIdsDirty) return;
    this.sentIdsDirty = false;
    try {
      mkdirSync(dirname(this.sentIdsFile), { recursive: true });
      const tmp = this.sentIdsFile + '.tmp';
      writeFileSync(tmp, JSON.stringify(Array.from(this.sentIds)) + '\n');
      renameSync(tmp, this.sentIdsFile);
    } catch (err) {
      process.stderr.write(`[Feishu access] persist sent-ids failed: ${err}\n`);
      this.sentIdsDirty = true;
    }
  }

  // --- helpers ---
  runLark(args: string[]): Promise<{ ok: boolean; stdout: string; stderr: string; code: number }> {
    return new Promise(resolve => {
      const p = spawn(this.larkCli, ['--profile', this.larkProfile, ...args], { stdio: ['ignore', 'pipe', 'pipe'] });
      let stdout = '';
      let stderr = '';
      p.stdout?.on('data', d => { stdout += d.toString(); });
      p.stderr?.on('data', d => { stderr += d.toString(); });
      p.on('exit', code => resolve({ ok: code === 0, stdout, stderr, code: code ?? -1 }));
      p.on('error', err => resolve({ ok: false, stdout, stderr: stderr + String(err), code: -1 }));
    });
  }
}

export function defaultAccess(): Access {
  return {
    dmPolicy: 'allowlist',
    allowFrom: [],
    groups: {},
    pending: {},
    groupOpenForAllowedSenders: true,
  };
}
