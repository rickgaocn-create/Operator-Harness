import { randomUUID } from 'crypto';
import { homedir } from 'os';
import { createConnection, type Socket } from 'net';
import { basename, join, resolve } from 'path';
import * as pty from 'node-pty';

const DAEMON_SOCKET = process.env.AFK_DAEMON_SOCKET ?? '/tmp/afk-code-daemon.sock';
type TranscriptBackend = 'claude' | 'codex';
type RemoteInputMessage = { text?: string; submitText?: string };

export function getEffectiveCwd(baseCwd: string, command: string[]): string {
  for (let i = 1; i < command.length - 1; i++) {
    if (command[i] === '-C' || command[i] === '--cwd') {
      return resolve(baseCwd, command[i + 1]);
    }
  }
  return baseCwd;
}

// Get Claude's project directory for the current working directory
function getClaudeProjectDir(cwd: string): string {
  // Claude encodes paths by replacing / and . with -
  const encodedPath = cwd.replace(/[/.\\:]/g, '-');
  return `${homedir()}/.claude/projects/${encodedPath}`;
}

export function getCodexHome(): string {
  const override = process.env.CODEX_HOME?.trim();
  return override ? resolve(override) : join(homedir(), '.codex');
}

function getCodexSessionsDir(): string {
  return join(getCodexHome(), 'sessions');
}

export function getTranscriptConfig(cwd: string, command: string[]): { backend: TranscriptBackend; projectDir: string } {
  const override = (process.env.AFK_TRANSCRIPT_BACKEND ?? '').toLowerCase();
  if (override === 'codex') {
    return { backend: 'codex', projectDir: getCodexSessionsDir() };
  }
  if (override === 'claude') {
    return { backend: 'claude', projectDir: getClaudeProjectDir(cwd) };
  }

  const executable = basename(command[0] ?? '').toLowerCase();
  const backend: TranscriptBackend = executable.startsWith('codex') ? 'codex' : 'claude';
  return {
    backend,
    projectDir: backend === 'codex'
      ? getCodexSessionsDir()
      : getClaudeProjectDir(cwd),
  };
}

// Connect to daemon and maintain bidirectional communication
function connectToDaemon(
  sessionId: string,
  projectDir: string,
  transcriptBackend: TranscriptBackend,
  cwd: string,
  command: string[],
  startedAt: string,
  onInput: (message: RemoteInputMessage) => void,
  onDisconnect?: () => void,
  onReplaced?: () => void
): Promise<{ close: () => void } | null> {
  return new Promise((resolve) => {
    const socket = createConnection(DAEMON_SOCKET);
    let messageBuffer = '';
    let settled = false;
    let connected = false;
    let intentionallyClosed = false;
    let rejected = false;

    socket.on('connect', () => {
      connected = true;
      // Tell daemon about this session
      socket.write(JSON.stringify({
        type: 'session_start',
        id: sessionId,
        projectDir,
        transcriptBackend,
        cwd,
        command,
        name: command.join(' '),
        startedAt,
        sessionToken: process.env.AFK_DAEMON_TOKEN,
      }) + '\n');

      const connection = {
        close: () => {
          intentionallyClosed = true;
          try {
            socket.write(JSON.stringify({ type: 'session_end', sessionId }) + '\n');
            socket.end();
          } catch {}
        },
      };
      settled = true;
      resolve(connection);
    });

    socket.on('data', (data) => {
      messageBuffer += data.toString();

      const lines = messageBuffer.split('\n');
      messageBuffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const msg = JSON.parse(line);
          if (msg.type === 'session_rejected') {
            rejected = true;
            try { socket.end(); } catch {}
          } else if (msg.type === 'session_replaced') {
            rejected = true;
            try { socket.end(); } catch {}
            onReplaced?.();
          } else if (msg.type === 'input') {
            if (typeof msg.submitText === 'string') {
              onInput({ submitText: msg.submitText });
            } else if (typeof msg.text === 'string' && msg.text.length > 0) {
              onInput({ text: msg.text });
            }
          }
        } catch {}
      }
    });

    socket.on('close', () => {
      if (!settled) {
        settled = true;
        resolve(null);
      } else if (connected && !intentionallyClosed && !rejected) {
        onDisconnect?.();
      }
    });

    socket.on('error', () => {
      // Daemon not running - that's okay, run without it
      if (!settled) {
        settled = true;
        resolve(null);
      }
    });
  });
}

function maintainDaemonConnection(
  sessionId: string,
  projectDir: string,
  transcriptBackend: TranscriptBackend,
  cwd: string,
  command: string[],
  startedAt: string,
  onInput: (message: RemoteInputMessage) => void,
  onReplaced?: () => void
): { close: () => void } {
  let current: { close: () => void } | null = null;
  let closed = false;
  let reconnecting = false;

  const reconnect = async () => {
    if (closed || reconnecting || current) return;
    reconnecting = true;
    while (!closed && !current) {
      current = await connectToDaemon(
        sessionId,
        projectDir,
        transcriptBackend,
        cwd,
        command,
        startedAt,
        onInput,
        () => {
          current = null;
          void reconnect();
        },
        onReplaced
      );
      if (!current && !closed) {
        await new Promise((r) => setTimeout(r, 1000));
      }
    }
    reconnecting = false;
  };

  const interval = setInterval(() => {
    void reconnect();
  }, 1000);

  void reconnect();

  return {
    close: () => {
      closed = true;
      clearInterval(interval);
      current?.close();
      current = null;
    },
  };
}

function normalizeTerminalText(data: string): string {
  return data
    .replace(/\x1b\][^\x07]*(\x07|\x1b\\)/g, '')
    .replace(/\x1b\[[0-9;?]*[ -/]*[@-~]/g, '')
    .replace(/\x1b[()][A-Za-z0-9]/g, '')
    .replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g, '');
}

export function terminalLooksReady(screenText: string): boolean {
  const text = normalizeTerminalText(screenText).replace(/\r/g, '\n');
  const lines = text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
  const recentLines = lines.slice(-20);
  const recentTail = recentLines.join('\n');
  if (/Do you trust the contents of this directory\?/i.test(recentTail)) return false;
  if (/\bWorking \(/i.test(recentTail)) return false;
  if (/Running .*hook/i.test(recentTail)) return false;
  if (/press enter to continue|press any key|continue\?/i.test(recentTail)) return false;

  const promptPattern = /^(?:\u203a|>)(?:\s|$)/;
  return recentLines.some((line) => promptPattern.test(line));
}

class RemoteInputQueue {
  private queue: RemoteInputMessage[] = [];
  private screenTail = '';
  private submitting = false;
  private lastOutputAt = Date.now();
  private retryTimer: ReturnType<typeof setInterval> | null = null;

  constructor(private ptyProcess: pty.IPty) {}

  observeOutput(data: string): void {
    this.screenTail = (this.screenTail + data).slice(-30_000);
    this.lastOutputAt = Date.now();
    this.flush();
  }

  enqueue(message: RemoteInputMessage): void {
    this.queue.push(message);
    this.flush();
    this.ensureRetryTimer();
  }

  private ensureRetryTimer(): void {
    if (this.retryTimer || this.queue.length === 0) return;
    this.retryTimer = setInterval(() => {
      if (this.queue.length === 0) {
        if (this.retryTimer) {
          clearInterval(this.retryTimer);
          this.retryTimer = null;
        }
        return;
      }
      this.flush();
    }, 500);
  }

  private flush(): void {
    if (this.submitting || this.queue.length === 0) return;
    const ready = terminalLooksReady(this.screenTail);
    // Fallback: the readiness probe is brittle because screenTail strips
    // ANSI but doesn't simulate cursor-overwrites, so stale text like
    // "Working (3s)" keeps the gate closed long after codex has redrawn
    // over it. Force-flush after 1500ms of pty silence — the pty going
    // quiet with a queued message is the most reliable cross-version
    // signal that codex is idle and accepting input again.
    const quietForceFlush = !ready && Date.now() - this.lastOutputAt > 1500;
    if (!ready && !quietForceFlush) return;

    const message = this.queue.shift();
    if (!message) return;
    this.submitting = true;

    if (typeof message.submitText === 'string') {
      this.submitPrompt(message.submitText);
    } else if (typeof message.text === 'string') {
      this.ptyProcess.write(message.text);
      this.finishSubmission();
      return;
    }

    setTimeout(() => this.finishSubmission(), 1200);
  }

  private finishSubmission(): void {
    this.submitting = false;
    this.flush();
  }

  private submitPrompt(text: string): void {
    const normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').replace(/\n+$/g, '');

    // Ctrl+U clears any suggestion or stale text before injecting the remote prompt.
    this.ptyProcess.write('\x15');
    setTimeout(() => {
      this.ptyProcess.write(`\x1b[200~${normalized}\x1b[201~`);
    }, 120);
    setTimeout(() => this.ptyProcess.write('\r'), normalized.includes('\n') ? 700 : 500);
  }
}

export async function run(command: string[]): Promise<void> {
  const sessionId = randomUUID().slice(0, 8);
  const cwd = getEffectiveCwd(process.cwd(), command);
  const { backend: transcriptBackend, projectDir } = getTranscriptConfig(cwd, command);
  const startedAt = new Date().toISOString();

  // Show loading spinner while starting
  const spinnerFrames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
  let spinnerIndex = 0;
  let spinnerInterval: ReturnType<typeof setInterval> | null = setInterval(() => {
    process.stdout.write(`\r${spinnerFrames[spinnerIndex]} Starting...`);
    spinnerIndex = (spinnerIndex + 1) % spinnerFrames.length;
  }, 80);

  const stopSpinner = () => {
    if (spinnerInterval) {
      clearInterval(spinnerInterval);
      spinnerInterval = null;
      // Clear the spinner line
      process.stdout.write('\r\x1b[K');
    }
  };

  // Use node-pty for full terminal features + remote input
  const cols = process.stdout.columns || 80;
  const rows = process.stdout.rows || 24;

  const ptyProcess = pty.spawn(command[0], command.slice(1), {
    name: process.env.TERM || 'xterm-256color',
    cols,
    rows,
    cwd,
    env: process.env as Record<string, string>,
  });
  const remoteInputQueue = new RemoteInputQueue(ptyProcess);
  let replacedByNewerSession = false;

  const daemon = maintainDaemonConnection(
    sessionId,
    projectDir,
    transcriptBackend,
    cwd,
    command,
    startedAt,
    (message) => remoteInputQueue.enqueue(message),
    () => {
      replacedByNewerSession = true;
      process.stdout.write('\r\x1b[K[afk-code] Replaced by a newer identical session. Closing this monitored session.\n');
      try { ptyProcess.kill(); } catch {}
    }
  );

  if (process.stdin.isTTY) {
    process.stdin.setRawMode(true);
  }

  ptyProcess.onData((data: string) => {
    stopSpinner();
    remoteInputQueue.observeOutput(data);
    process.stdout.write(data);
  });

  const onStdinData = (data: Buffer) => {
    ptyProcess.write(data.toString());
  };
  process.stdin.on('data', onStdinData);

  process.stdout.on('resize', () => {
    ptyProcess.resize(process.stdout.columns || 80, process.stdout.rows || 24);
  });

  await new Promise<void>((resolve) => {
    ptyProcess.onExit(() => {
      // Clean up stdin
      process.stdin.removeListener('data', onStdinData);
      if (process.stdin.isTTY) {
        process.stdin.setRawMode(false);
      }
      if (typeof process.stdin.unref === 'function') {
        process.stdin.unref();
      }

      daemon?.close();
      resolve();
    });
  });
}
