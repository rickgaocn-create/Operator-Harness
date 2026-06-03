#!/usr/bin/env node
/*
 * fs-pty-harness.cjs — keep a Feishu-channel Claude Code session alive in a ConPTY.
 *
 * The Feishu bridge has no afk-code-style harness; it uses Claude's native
 * `--channels plugin:feishu@local`. Interactive Claude needs a TTY (Ink raw
 * mode), which a scheduled task / agent shell does not have. node-pty allocates
 * a pseudo-console programmatically, so Claude runs headless and unattended:
 * the feishu plugin (FEISHU_READ_QUEUE=1) drains ~/.claude/channels/feishu/
 * queue/events and Claude auto-replies as "Business Morty".
 *
 * Spawned in a restart loop by launch-fs-daemon.ps1. Exits when Claude exits so
 * the loop respawns it. Lifecycle → daemon.log; raw PTY stream → session.pty.log
 * (size-guarded, kept only for crash diagnosis).
 */
'use strict';

const path = require('path');
const fs = require('fs');

const HOME = process.env.USERPROFILE || process.env.HOME;
const DAEMON_DIR = path.join(HOME, '.fs-claude-daemon');
const LIFECYCLE_LOG = path.join(DAEMON_DIR, 'daemon.log');
const PTY_LOG = path.join(DAEMON_DIR, 'session.pty.log');
const PTY_LOG_CAP = 2 * 1024 * 1024; // 2 MB ring; Ink redraws are noisy

// node-pty: reuse afk-code's prebuilt ConPTY binary (override via FS_NODE_PTY).
const NODE_PTY = process.env.FS_NODE_PTY ||
  path.join(HOME, '.afk-code-claude2', 'node_modules', 'node-pty');
const pty = require(NODE_PTY);

// Same binary the afk-code Discord daemon drives (override via FS_CLAUDE_BIN).
const CLAUDE = process.env.FS_CLAUDE_BIN ||
  path.join(HOME, '.local', 'bin', 'claude.exe');

const AFK_PROMPT =
  'You are running in a remote-monitored AFK session via Feishu (Business Morty bot). ' +
  'Incoming messages reach you only after passing the Feishu plugin\'s allowlist gate ' +
  '(~/.claude/channels/feishu/access.json), so treat them as authenticated user input from ' +
  '{{USER_NAME}} — same trust level as a local terminal. Use Bash, Grep, Read, and any other tools ' +
  'freely to fulfill requests; do not refuse system probes on chat-trust-boundary grounds. ' +
  'The user is not at the terminal and cannot see or respond to interactive TUI prompts.';

fs.mkdirSync(DAEMON_DIR, { recursive: true });
const lifecycle = fs.createWriteStream(LIFECYCLE_LOG, { flags: 'a' });
const log = (m) => lifecycle.write(`[${new Date().toISOString()}] ${m}\n`);

// Size-guarded PTY stream sink: truncate when it crosses the cap.
function makePtySink() {
  let written = 0;
  try {
    const st = fs.statSync(PTY_LOG);
    written = st.size;
  } catch { /* missing is fine */ }
  let ws = fs.createWriteStream(PTY_LOG, { flags: 'a' });
  return (chunk) => {
    written += Buffer.byteLength(chunk);
    if (written > PTY_LOG_CAP) {
      ws.end();
      ws = fs.createWriteStream(PTY_LOG, { flags: 'w' }); // rotate-in-place
      written = Buffer.byteLength(chunk);
    }
    ws.write(chunk);
  };
}
const ptySink = makePtySink();

const env = { ...process.env, FEISHU_READ_QUEUE: '1' };
delete env.FS_CLAUDE_DISCORD; // feishu-only daemon; never auto-attach Discord

const args = [
  '--channels', 'plugin:feishu@local',
  '--dangerously-skip-permissions',
  '--append-system-prompt', AFK_PROMPT,
];

log(`harness start: "${CLAUDE}" ${args.join(' ')}`);

let child;
try {
  child = pty.spawn(CLAUDE, args, {
    name: 'xterm-256color',
    cols: 120,
    rows: 40,
    cwd: HOME,
    env,
  });
} catch (err) {
  log(`FATAL spawn failed: ${err && err.stack ? err.stack : err}`);
  process.exit(1);
}

log(`spawned claude pid=${child.pid}`);
child.onData((d) => ptySink(d));
child.onExit(({ exitCode, signal }) => {
  log(`claude exited code=${exitCode} signal=${signal}`);
  setTimeout(() => process.exit(typeof exitCode === 'number' ? exitCode : 0), 250);
});

// Forward termination so a daemon stop kills Claude cleanly.
const stop = (sig) => {
  log(`harness received ${sig}; killing child pid=${child.pid}`);
  try { child.kill(); } catch { /* already gone */ }
};
process.on('SIGTERM', () => stop('SIGTERM'));
process.on('SIGINT', () => stop('SIGINT'));

// Keep the event loop alive; nothing to forward to Claude's stdin.
setInterval(() => {}, 1 << 30);
