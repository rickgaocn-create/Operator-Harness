import net from 'net';
const PIPE = ['', '', '.', 'pipe', 'afk-code-claude2-daemon'].join('\\');
const id = "diagverify-0529b";
const sock = net.createConnection(PIPE, () => {
  console.log("connected to daemon pipe:", PIPE);
  sock.write(JSON.stringify({ type: "session_start", id, name: "diag-verify (channel-creation test)", cwd: "C:\\diagverify", projectDir: "C:\\diagverify" }) + "\n");
  setTimeout(() => {
    sock.write(JSON.stringify({ type: "session_end", sessionId: id }) + "\n");
    setTimeout(() => { sock.end(); process.exit(0); }, 1500);
  }, 2500);
});
sock.on('error', e => { console.error("PIPE ERROR:", e.message); process.exit(1); });
