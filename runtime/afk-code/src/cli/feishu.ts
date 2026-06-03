import { homedir } from 'os';
import { mkdir, writeFile, readFile, access } from 'fs/promises';
import * as readline from 'readline';
import { join } from 'path';
import { AccessStore, defaultAccess, type Access } from '../feishu/access.js';
import { resolveLarkCli } from '../feishu/feishu-app.js';

const CONFIG_DIR = `${homedir()}/.afk-code`;

function getFeishuConfigFile(): string {
  return process.env.AFK_FEISHU_CONFIG_FILE || `${CONFIG_DIR}/feishu.env`;
}

function getStartCommandHint(): string {
  return process.env.AFK_FEISHU_START_COMMAND || 'afk-code run -- claude';
}

function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

async function fileExists(path: string): Promise<boolean> {
  try { await access(path); return true; } catch { return false; }
}

export async function feishuSetup(): Promise<void> {
  const feishuConfigFile = getFeishuConfigFile();
  console.log(`
AFK Code Feishu Setup

This will configure a Feishu (Lark) bridge for monitoring Claude
Code sessions. Unlike Discord/Telegram, this uses lark-cli, which
must already be installed and authenticated.

Step 1: lark-cli must be on PATH and bound to a Feishu app.
        Check with: lark-cli --profile <name> config show

Step 2: You need the chat_id (oc_xxx) of the DM you want messages
        sent to. The easiest way: send your bot any DM, then check
        ~/.claude/channels/feishu/access.json - the chat_id is on
        the pairing entry, or in the MCP plugin's log file.
`);

  const larkProfile = (await prompt('lark-cli profile name [morty]: ')) || 'morty';
  if (!/^[a-zA-Z0-9_-]+$/.test(larkProfile)) {
    console.error('Invalid profile name.');
    process.exit(1);
  }

  const chatId = await prompt('Chat ID (oc_xxx): ');
  if (!chatId.startsWith('oc_')) {
    console.error('Chat ID must start with "oc_".');
    process.exit(1);
  }

  await mkdir(CONFIG_DIR, { recursive: true });
  const envContent = `# AFK Code Feishu Configuration
FEISHU_LARK_PROFILE=${larkProfile}
FEISHU_CHAT_ID=${chatId}
`;
  await writeFile(feishuConfigFile, envContent);
  console.log(`
Configuration saved to ${feishuConfigFile}

To start the Feishu bridge daemon, run:
  afk-code feishu

Then start a Claude Code session (in another terminal) with:
  afk-feishu        # if you've installed the PowerShell function
  # or:
  afk-code run -- claude
`);
}

async function loadEnvFile(path: string): Promise<Record<string, string>> {
  if (!(await fileExists(path))) return {};
  const content = await readFile(path, 'utf-8');
  const config: Record<string, string> = {};
  for (const line of content.split('\n')) {
    if (line.startsWith('#') || !line.includes('=')) continue;
    const [key, ...rest] = line.split('=');
    config[key.trim()] = rest.join('=').trim();
  }
  return config;
}

export async function feishuRun(): Promise<void> {
  const feishuConfigFile = getFeishuConfigFile();
  const globalConfig = await loadEnvFile(feishuConfigFile);
  const localConfig = await loadEnvFile(`${process.cwd()}/.env`);
  const config: Record<string, string> = { ...globalConfig, ...localConfig };

  if (process.env.FEISHU_LARK_PROFILE) config.FEISHU_LARK_PROFILE = process.env.FEISHU_LARK_PROFILE;
  if (process.env.FEISHU_CHAT_ID) config.FEISHU_CHAT_ID = process.env.FEISHU_CHAT_ID;

  const required = ['FEISHU_LARK_PROFILE'];
  const missing = required.filter((k) => !config[k]);
  if (missing.length > 0) {
    console.error(`Missing config: ${missing.join(', ')}`);
    console.error('Run "afk-code feishu setup" for guided configuration.');
    process.exit(1);
  }

  console.log('[AFK Code] Starting Feishu bridge...');
  console.log(`[AFK Code] Lark profile: ${config.FEISHU_LARK_PROFILE}`);
  if (config.FEISHU_CHAT_ID) {
    console.log(`[AFK Code] Chat: ${config.FEISHU_CHAT_ID}`);
  } else {
    console.log('[AFK Code] Chat: waiting for the first DM to bind this bridge');
  }
  console.log(`[AFK Code] Daemon socket: ${process.env.AFK_DAEMON_SOCKET ?? '/tmp/afk-code-daemon.sock'}`);

  const { createFeishuApp } = await import('../feishu/feishu-app.js');
  const { sessionManager, startConsumer, startHistoryPoller, shutdown } = createFeishuApp({
    larkProfile: config.FEISHU_LARK_PROFILE,
    chatId: config.FEISHU_CHAT_ID,
    configFilePath: feishuConfigFile,
    startCommandHint: getStartCommandHint(),
  });

  try {
    await sessionManager.start();
    console.log('[AFK Code] Session manager listening');
  } catch (err) {
    console.error('[AFK Code] Failed to start session manager:', err);
    process.exit(1);
  }

  startConsumer();
  startHistoryPoller();
  console.log('[AFK Code] Feishu consumer started');
  console.log('[AFK Code] Feishu history fallback started');
  console.log('');
  console.log(`Start a monitored session with: ${getStartCommandHint()}`);
  console.log('(set AFK_DAEMON_SOCKET to the same value used here)');

  const onSignal = () => {
    console.error('[AFK Code] shutting down');
    shutdown();
    setTimeout(() => process.exit(0), 1000);
  };
  process.on('SIGTERM', onSignal);
  process.on('SIGINT', onSignal);
}

// ---------------------------------------------------------------------------
// `afk-code feishu access` — manage access.json for the codex bridge.
// Mirrors fs-claude's /feishu:access skill: show/allow/deny/group-add/
// group-rm/policy/pair. Edits ~/.afk-code/feishu-access.json by default
// (overridable via AFK_FEISHU_ACCESS_FILE).
// ---------------------------------------------------------------------------

function getAccessFile(): string {
  return process.env.AFK_FEISHU_ACCESS_FILE || join(CONFIG_DIR, 'feishu-access.json');
}

function getAccessStoreFromEnv(): AccessStore {
  const profile = process.env.FEISHU_LARK_PROFILE || 'codex-afk-feishu';
  return new AccessStore({
    larkProfile: profile,
    larkCli: resolveLarkCli(),
    filePath: getAccessFile(),
  });
}

function printAccess(a: Access): void {
  console.log(`dmPolicy: ${a.dmPolicy}`);
  console.log(`groupOpenForAllowedSenders: ${a.groupOpenForAllowedSenders ?? true}`);
  console.log(`allowFrom (${a.allowFrom.length}):`);
  for (const ou of a.allowFrom) console.log(`  - ${ou}`);
  const groups = Object.keys(a.groups);
  console.log(`groups (${groups.length}):`);
  for (const oc of groups) {
    const g = a.groups[oc];
    console.log(`  - ${oc}  requireMention=${g.requireMention} allowFrom=[${g.allowFrom.join(', ')}]`);
  }
  const pending = Object.keys(a.pending);
  if (pending.length > 0) {
    console.log(`pending (${pending.length}):`);
    for (const code of pending) {
      const p = a.pending[code];
      const left = Math.max(0, Math.floor((p.expiresAt - Date.now()) / 60_000));
      console.log(`  - code=${code} sender=${p.senderId} chat=${p.chatId} expires in ${left}m`);
    }
  }
}

export async function feishuAccess(args: string[]): Promise<void> {
  const sub = (args[0] || '').toLowerCase();
  const store = getAccessStoreFromEnv();

  switch (sub) {
    case '':
    case 'show': {
      const a = store.load();
      if (store.pruneExpired(a)) store.save(a);
      console.log(`# Access file: ${store.filePath}`);
      printAccess(a);
      return;
    }
    case 'allow': {
      const ou = args[1];
      if (!ou || !ou.startsWith('ou_')) {
        console.error('Usage: afk-code feishu access allow <ou_xxx>');
        process.exit(1);
      }
      const a = store.load();
      if (!a.allowFrom.includes(ou)) a.allowFrom.push(ou);
      // Promote pairing → allowlist once we have at least one allowed sender.
      if (a.dmPolicy === 'pairing') a.dmPolicy = 'allowlist';
      store.save(a);
      console.log(`Allowed sender ${ou}. dmPolicy=${a.dmPolicy}`);
      return;
    }
    case 'deny':
    case 'remove': {
      const ou = args[1];
      if (!ou) {
        console.error('Usage: afk-code feishu access deny <ou_xxx>');
        process.exit(1);
      }
      const a = store.load();
      const before = a.allowFrom.length;
      a.allowFrom = a.allowFrom.filter((x) => x !== ou);
      store.save(a);
      console.log(before === a.allowFrom.length ? `${ou} was not allowed` : `Removed ${ou}`);
      return;
    }
    case 'group-add': {
      const oc = args[1];
      if (!oc || !oc.startsWith('oc_')) {
        console.error('Usage: afk-code feishu access group-add <oc_xxx> [--no-mention] [--allow ou_xxx,...]');
        process.exit(1);
      }
      const requireMention = !args.includes('--no-mention');
      const allowIdx = args.indexOf('--allow');
      const groupAllow = allowIdx >= 0 && args[allowIdx + 1] ? args[allowIdx + 1].split(',') : [];
      const a = store.load();
      a.groups[oc] = { requireMention, allowFrom: groupAllow };
      store.save(a);
      console.log(`Group ${oc} added (requireMention=${requireMention}, allowFrom=[${groupAllow.join(', ')}])`);
      return;
    }
    case 'group-rm':
    case 'group-remove': {
      const oc = args[1];
      if (!oc) {
        console.error('Usage: afk-code feishu access group-rm <oc_xxx>');
        process.exit(1);
      }
      const a = store.load();
      const existed = oc in a.groups;
      delete a.groups[oc];
      store.save(a);
      console.log(existed ? `Removed group ${oc}` : `${oc} was not configured`);
      return;
    }
    case 'policy': {
      const p = (args[1] || '').toLowerCase();
      if (!['pairing', 'allowlist', 'disabled'].includes(p)) {
        console.error('Usage: afk-code feishu access policy <pairing|allowlist|disabled>');
        process.exit(1);
      }
      const a = store.load();
      a.dmPolicy = p as Access['dmPolicy'];
      store.save(a);
      console.log(`dmPolicy set to ${p}`);
      return;
    }
    case 'pair': {
      const code = args[1];
      if (!code) {
        console.error('Usage: afk-code feishu access pair <code>');
        console.error('       (use the code the bot sent when an unallowed user DMed)');
        process.exit(1);
      }
      const a = store.load();
      const entry = a.pending[code];
      if (!entry) {
        console.error(`No pending pair for code "${code}". Try: afk-code feishu access show`);
        process.exit(1);
      }
      if (!a.allowFrom.includes(entry.senderId)) a.allowFrom.push(entry.senderId);
      delete a.pending[code];
      if (a.dmPolicy === 'pairing') a.dmPolicy = 'allowlist';
      store.save(a);
      console.log(`Paired sender ${entry.senderId} from chat ${entry.chatId}. dmPolicy=${a.dmPolicy}`);
      return;
    }
    case 'init': {
      // Idempotent bootstrap — writes a fresh access.json if none exists.
      const a = defaultAccess();
      store.save(a);
      console.log(`Initialized ${store.filePath} with defaults.`);
      printAccess(a);
      return;
    }
    case 'help':
    case '--help':
    case '-h':
      console.log(`
afk-code feishu access <subcommand> [args]

Subcommands:
  show                          Print current access state
  allow <ou_xxx>                Allowlist a sender (DMs accepted from them)
  deny <ou_xxx>                 Remove from allowlist
  group-add <oc_xxx>            Add a group; default requires @mention
      [--no-mention] [--allow ou_a,ou_b]
  group-rm <oc_xxx>             Remove an explicit group policy
  policy <pairing|allowlist|disabled>
                                Set DM policy
  pair <code>                   Accept a pending pairing code (from the bot's DM)
  init                          Write a fresh access.json with defaults

Env:
  FEISHU_LARK_PROFILE           lark-cli profile (default: codex-afk-feishu)
  AFK_FEISHU_ACCESS_FILE        Access file path (default: ~/.afk-code/feishu-access.json)
`);
      return;
    default:
      console.error(`Unknown subcommand: ${sub}. Try: afk-code feishu access help`);
      process.exit(1);
  }
}
