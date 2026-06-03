// Global error handlers for the afk-claude2 daemon.
// Logged but NEVER allowed to terminate the process — any async bug that escapes
// upstream try/catch (e.g. discord.js channel ops on a deleted channel, network
// blips, etc.) gets swallowed here instead of killing the daemon.
//
// Loaded by launch-daemon.ps1 via `node --import file:///.../shield.mjs`.
// Lives outside node_modules so npm install / upgrade does NOT clobber it.

const ts = () => new Date().toISOString();

// --- Broken-pipe immunity (added 2026-05-27) ---
// Root cause of the 2026-05-21→27 silent outage: the launcher powershell that
// owns the `*>> daemon.log` stdout redirection died, ORPHANING the daemon. Its
// inherited stdout/stderr pipe broke, so the next console.log() inside session
// handling threw EPIPE and aborted channel creation — while the process and the
// named pipe stayed alive, so the pipe-only healthcheck never noticed.
// Fix: a broken stdout/stderr must NEVER throw or crash the daemon. Writes
// silently no-op when the pipe is gone, so an orphaned daemon keeps creating
// channels. Lives in the shield (survives `npm install`).
for (const stream of [process.stdout, process.stderr]) {
  stream.on('error', () => {});               // EPIPE -> no uncaughtException
  const origWrite = stream.write.bind(stream);
  stream.write = (...args) => {
    try { return origWrite(...args); }
    catch {                                    // ERR_STREAM_DESTROYED / EPIPE
      const cb = args[args.length - 1];
      if (typeof cb === 'function') { try { cb(); } catch {} }
      return true;
    }
  };
}

process.on('unhandledRejection', (reason) => {
  const msg = reason?.stack ?? reason?.message ?? String(reason);
  console.error(`[shield ${ts()}] unhandledRejection swallowed:\n${msg}`);
});

process.on('uncaughtException', (err) => {
  const msg = err?.stack ?? err?.message ?? String(err);
  console.error(`[shield ${ts()}] uncaughtException swallowed:\n${msg}`);
});

console.error(`[shield ${ts()}] global error handlers installed (stdout/stderr broken-pipe hardened)`);
