// Global error handlers for the fs-claude (Feishu/Business Morty) daemon.
// Logged but NEVER allowed to terminate the harness — any async bug that
// escapes try/catch (node-pty hiccup, write-stream EPIPE, etc.) gets swallowed
// here instead of killing the supervisor. Mirrors the afk-code-claude2 shield.
//
// Loaded by launch-fs-daemon.ps1 via `node --import file:///.../shield.mjs`.
// Lives outside node_modules so npm install / upgrade does NOT clobber it.

const ts = () => new Date().toISOString();

process.on('unhandledRejection', (reason) => {
  const msg = reason?.stack ?? reason?.message ?? String(reason);
  console.error(`[shield ${ts()}] unhandledRejection swallowed:\n${msg}`);
});

process.on('uncaughtException', (err) => {
  const msg = err?.stack ?? err?.message ?? String(err);
  console.error(`[shield ${ts()}] uncaughtException swallowed:\n${msg}`);
});

console.error(`[shield ${ts()}] global error handlers installed`);
