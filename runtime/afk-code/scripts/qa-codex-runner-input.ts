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
const tmpRoot = join(tmpdir(), `afk-codex-runner-qa-${runId}`);
const fakeCodex = join(tmpRoot, 'fake-codex.cjs');
const inputLog = join(tmpRoot, 'input.jsonl');
const codexHome = join(tmpRoot, 'codex-home');
const pipeName = process.platform === 'win32'
  ? `\\\\.\\pipe\\afk-codex-runner-qa-${runId}`
  : join(tmpRoot, 'daemon.sock');

await mkdir(tmpRoot, { recursive: true });
await mkdir(codexHome, { recursive: true });

await writeFile(fakeCodex, `
const fs = require('node:fs');
const log = process.argv[2];
let buffer = '';
let submissions = 0;

function prompt() {
  process.stdout.write('\\n\\u203a\\n  gpt-5.5 high - qa\\n');
}

fs.writeFileSync(log, '');
if (process.stdin.isTTY && process.stdin.setRawMode) process.stdin.setRawMode(true);
process.stdin.resume();
prompt();

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
  process.stdout.write('\\n• processed ' + submissions + '\\n');
  if (submissions >= 2) {
    setTimeout(() => process.exit(0), 250);
  } else {
    setTimeout(prompt, 100);
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
        }, 2200);
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

      if (Date.now() - started > 15_000) {
        clearInterval(interval);
        rejectSubmissions(new Error(`runner did not submit two prompts\nstdout:\n${stdout}\nstderr:\n${stderr}`));
      }
    }, 250);
  });

  assert.ok(sessionStart, 'daemon received session_start');
  assert.equal(sessionStart.transcriptBackend, 'codex');
  assert.equal(sessionStart.projectDir, join(codexHome, 'sessions'));

  const log = await readFile(inputLog, 'utf8');
  const entries = log.trim().split('\n').map((line) => JSON.parse(line));
  const submissions = entries.filter((entry) => entry.kind === 'submission');
  assert.equal(submissions.length, 2, log);
  assert.match(submissions[0].cleaned, /AFK_QA_FIRST_INPUT/);
  assert.match(submissions[1].cleaned, /AFK_QA_SECOND_INPUT/);

  runner.kill();
  console.log('codex runner input qa ok');
} finally {
  sessionSocket?.destroy();
  server.close();
  if (runner && runner.exitCode === null) runner.kill();
  await rm(tmpRoot, { recursive: true, force: true });
}
