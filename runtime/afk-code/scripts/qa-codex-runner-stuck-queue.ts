// Regression test for the Open Morty / codex-feishu bug where only the first
// inbound message reached codex per session. The original terminalLooksReady
// required a `gpt-.*(badge)` line in the slice-after-latest-prompt of the
// pty's screenTail. Real codex re-renders its input area on subsequent turns
// in a way that often leaves the badge above the latest prompt line, so the
// regex never matches and the second message stays queued forever.
//
// This QA spins up a fake codex that:
//   1. Emits a normal prompt+badge on startup (so message 1 submits).
//   2. After receiving the first submission, emits ONLY a fresh prompt char
//      (no badge afterwards) — this is the failure shape we observed in the
//      real codex daemon log.
// The test then sends a second submission via the daemon socket and asserts
// the runner injects it into the fake codex's stdin within 6s.

import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { existsSync } from 'node:fs';
import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { createServer, type Socket } from 'node:net';

const repoRoot = resolve(import.meta.dirname, '..');
const distCli = join(repoRoot, 'dist', 'cli', 'index.js');
assert.equal(existsSync(distCli), true, 'run npm run build before this QA');

const runId = randomUUID().slice(0, 8);
const tmpRoot = join(tmpdir(), `afk-codex-stuck-queue-qa-${runId}`);
const fakeCodex = join(tmpRoot, 'fake-codex.cjs');
const inputLog = join(tmpRoot, 'input.jsonl');
const codexHome = join(tmpRoot, 'codex-home');
const pipeName = process.platform === 'win32'
  ? `\\\\.\\pipe\\afk-codex-stuck-queue-qa-${runId}`
  : join(tmpRoot, 'daemon.sock');

await mkdir(tmpRoot, { recursive: true });
await mkdir(codexHome, { recursive: true });

await writeFile(fakeCodex, `
const fs = require('node:fs');
const log = process.argv[2];
let buffer = '';
let submissions = 0;

function initialPromptWithBadge() {
  process.stdout.write('\\n\\u203a\\n  gpt-5.5 high - qa\\n');
}

function laterPromptNoBadge() {
  // Mimics codex re-rendering its input area after a turn without putting
  // the model badge after the prompt line (the bug shape).
  process.stdout.write('\\n\\u203a\\n');
}

fs.writeFileSync(log, '');
if (process.stdin.isTTY && process.stdin.setRawMode) process.stdin.setRawMode(true);
process.stdin.resume();
initialPromptWithBadge();

process.stdin.on('data', (chunk) => {
  const text = chunk.toString('utf8');
  fs.appendFileSync(log, JSON.stringify({ kind: 'chunk', hex: chunk.toString('hex'), text }) + '\\n');
  buffer += text;
  if (!text.includes('\\r')) return;

  submissions += 1;
  const cleaned = buffer
    .replace(/\\x15/g, '')
    .replace(/\\x1b\\[200~/g, '')
    .replace(/\\x1b\\[201~/g, '')
    .replace(/\\r/g, '');
  fs.appendFileSync(log, JSON.stringify({ kind: 'submission', submissions, cleaned }) + '\\n');
  buffer = '';
  process.stdout.write('\\n\\u2022 processed ' + submissions + '\\n');
  if (submissions >= 2) {
    setTimeout(() => process.exit(0), 250);
  } else {
    // Emit a brief 'Working' line then go quiet for >1500ms with a bare
    // prompt and NO badge. The runner's old regex-based readiness check
    // would never reopen the gate; the new quiet-force-flush fallback
    // should drain the queue after the silence.
    process.stdout.write('Working (' + submissions + 's)\\n');
    setTimeout(() => {
      laterPromptNoBadge();
    }, 200);
  }
});
`, 'utf8');

let runner: ReturnType<typeof spawn> | null = null;
let sessionSocket: Socket | null = null;
let sessionStart: any = null;
let stdout = '';
let stderr = '';

const server = createServer((socket) => {
  sessionSocket = socket;
  let buffer = '';
  socket.on('data', (chunk) => {
    buffer += chunk.toString('utf8');
    let newline: number;
    while ((newline = buffer.indexOf('\n')) >= 0) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      if (!line) continue;
      const message = JSON.parse(line);
      if (message.type === 'session_start') {
        sessionStart = message;
        socket.write(JSON.stringify({ type: 'input', submitText: 'AFK_QA_FIRST_INPUT' }) + '\n');
        setTimeout(() => {
          socket.write(JSON.stringify({ type: 'input', submitText: 'AFK_QA_SECOND_INPUT' }) + '\n');
        }, 1500);
      }
    }
  });
});

try {
  await new Promise<void>((resolveListen, rejectListen) => {
    server.once('error', rejectListen);
    server.listen(pipeName, resolveListen);
  });

  runner = spawn(process.execPath, [
    distCli,
    process.execPath,
    fakeCodex,
    inputLog,
  ], {
    cwd: repoRoot,
    env: {
      ...process.env,
      AFK_DAEMON_SOCKET: pipeName,
      AFK_TRANSCRIPT_BACKEND: 'codex',
      AFK_DAEMON_TOKEN: 'qa-token',
      CODEX_HOME: codexHome,
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  runner.stdout.on('data', (chunk) => { stdout += chunk.toString('utf8'); });
  runner.stderr.on('data', (chunk) => { stderr += chunk.toString('utf8'); });

  await new Promise<void>((resolveSubmissions, rejectSubmissions) => {
    const started = Date.now();
    const interval = setInterval(async () => {
      try {
        const log = await readFile(inputLog, 'utf8');
        const count = log
          .trim()
          .split('\n')
          .filter((line) => line.includes('"kind":"submission"'))
          .length;
        if (count >= 2) {
          clearInterval(interval);
          resolveSubmissions();
          return;
        }
      } catch {}

      if (Date.now() - started > 8_000) {
        clearInterval(interval);
        rejectSubmissions(new Error(`runner did not submit two prompts within 8s — the stuck-queue regression is back\nstdout:\n${stdout}\nstderr:\n${stderr}`));
      }
    }, 250);
  });

  assert.ok(sessionStart, 'daemon received session_start');
  assert.equal(sessionStart.transcriptBackend, 'codex');

  const log = await readFile(inputLog, 'utf8');
  const entries = log.trim().split('\n').map((line) => JSON.parse(line));
  const submissions = entries.filter((entry) => entry.kind === 'submission');
  assert.equal(submissions.length, 2, log);
  assert.match(submissions[0].cleaned, /AFK_QA_FIRST_INPUT/);
  assert.match(submissions[1].cleaned, /AFK_QA_SECOND_INPUT/);

  runner.kill();
  console.log('codex runner stuck-queue qa ok');
} finally {
  sessionSocket?.destroy();
  server.close();
  if (runner && runner.exitCode === null) runner.kill();
  await rm(tmpRoot, { recursive: true, force: true });
}
