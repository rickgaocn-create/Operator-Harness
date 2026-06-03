# Tunnel Runbook · Phone Preview Workflow

For when user says "can I check on phone" / "share to phone" / "preview elsewhere".

## Decision Tree

```
User asks phone access?
  ├─ HTML already in cloud / Obsidian Sync? → just sync, no tunnel needed
  ├─ HTML lives locally only? → tunnel path
  └─ Loss-of-interactivity acceptable? → PDF export path (Ctrl+P)
```

## Tunnel Path (recommended · full interactivity)

### Step 1 · Verify toolchain

```bash
python --version   # need 3.x
cloudflared --version   # may not be installed
```

If `cloudflared` not in PATH:
```bash
powershell.exe -Command "winget install --id Cloudflare.cloudflared --silent --accept-source-agreements --accept-package-agreements"
```
Installs to `C:\Program Files (x86)\cloudflared\cloudflared.exe`. PATH refresh needed for new shells — current shell uses full path.

### Step 2 · Scoped serve directory

```bash
mkdir -p "{{USER_HOME}}/AppData/Local/Temp/{artifact-name}-preview"
cp "{{VAULT_ROOT}}/.../source.html" "{{USER_HOME}}/AppData/Local/Temp/{artifact-name}-preview/index.html"
```

Use **scoped temp dir** so server doesn't expose other files. Naming the file `index.html` makes URL root serve it directly.

### Step 3 · Start Python HTTP server in background

```bash
cd "{{USER_HOME}}/AppData/Local/Temp/{artifact-name}-preview" && \
  python -m http.server 8765 > /tmp/httpserv.log 2>&1 &
sleep 1
curl -s -o /dev/null -w "Local check: %{http_code}\n" http://localhost:8765/
```

Port 8765 chosen to avoid conflicts with common dev ports (3000/5173/8000/8080). Confirm HTTP 200 before tunneling.

### Step 4 · Cloudflare quick tunnel

```bash
"/c/Program Files (x86)/cloudflared/cloudflared.exe" tunnel --url http://localhost:8765 > /tmp/tunnel.log 2>&1 &
```

Wait ~8 sec for URL assignment. Parse from log:
```bash
sleep 8 && cat /tmp/tunnel.log | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com'
```

URL format: `https://[random-words].trycloudflare.com`. Random, unguessable, no auth required. Expires when process dies.

### Step 5 · Verify public side

```bash
curl -s -o /dev/null -w "Public tunnel HTTP %{http_code} · %{size_download} bytes\n" https://[random].trycloudflare.com/
```

Confirm both `200` status + size matches local file.

### Step 6 · Give user the URL

Format response:
```
# 📱 Open on phone

**https://[random].trycloudflare.com**

**QR code** (scan from phone via desktop browser):
https://api.qrserver.com/v1/create-qr-code/?size=400x400&data=https%3A%2F%2F[random].trycloudflare.com
```

Use `api.qrserver.com` for QR generation — public free API, no auth, returns PNG. URL-encode the target.

### Step 7 · Re-sync on edits

When user requests changes to HTML and you edit the vault file, **re-cp** to the serve dir:

```bash
cp "{{VAULT_ROOT}}/.../source.html" "{{USER_HOME}}/AppData/Local/Temp/{artifact-name}-preview/index.html"
```

Tell user: "refresh phone browser to see changes."

Phone refresh: Safari pull-down or Chrome refresh icon. Should pick up new version immediately (no cache concern with single-shot tunnel sessions).

### Step 8 · Kill on demand

When user says "kill tunnel" / "stop sharing":

```bash
# Find PIDs
tasklist //FI "IMAGENAME eq python.exe"
tasklist //FI "IMAGENAME eq cloudflared.exe"

# Kill both
powershell.exe -Command "Stop-Process -Name python -Force; Stop-Process -Name cloudflared -Force"
```

Tell user: "tunnel killed · URL no longer reachable."

## Trycloudflare Caveats

- **No uptime guarantee** — Cloudflare reserves the right to investigate misuse
- **No HTTPS auth** — URL is technically public; rely on random subdomain being unguessable
- **Session-bound** — process dies = URL dies (no persistence)
- **Latency** — typically 2-4s first byte (routed via nearest edge — likely Singapore SIN15 from CN)
- **Account-less rate limits** — heavy traffic may throttle; OK for single-user phone preview

For production / repeated use: user should create a Cloudflare account + named tunnel. Skip for v0.x prototypes.

## Alternative Tunnels (fallbacks)

If cloudflared install fails:

| Tool | Pros | Cons | Install |
|---|---|---|---|
| **localtunnel** (Node) | npx, no install needed | Shows "password page" first visit (uses your public IP) | `npx localtunnel --port 8765` |
| **serveo.net** (SSH-based) | Works with Windows built-in SSH | Subdomain not random unless you reserve | `ssh -R 80:localhost:8765 serveo.net` |
| **ngrok** | Stable, well-known | Requires free account + auth token | Manual signup + `ngrok http 8765` |

Recommend cloudflared first; fall back to localtunnel if winget install fails.

## PDF Path (loss of interactivity, but offline-readable)

If user wants to view without internet OR send via WeChat 文件传输助手:

```bash
# Using Chrome headless to convert HTML → PDF
chrome.exe --headless --print-to-pdf="{{USER_HOME}}/.../output.pdf" "file://{{USER_HOME}}/.../source.html"
```

Or in Edge:
```bash
msedge.exe --headless --print-to-pdf="..." "file:///..."
```

PDF preserves:
- Layout, color, SVG charts, images
- Section anchors as bookmarks
- Print-friendly CSS (dark sections → white-bg)

PDF loses:
- 演示模式 toggle
- Scroll-spy nav highlight
- Interactive hover states
- External image links if not embedded

For a leadership forward where they'll skim once and archive — PDF is often the better artifact.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `cloudflared: command not found` after winget install | Use full path `/c/Program Files (x86)/cloudflared/cloudflared.exe` — PATH not refreshed in current shell |
| Tunnel says "Connection failed" | Check Python http.server alive: `curl http://localhost:8765/` |
| Phone shows blank page | Check public side: `curl -I https://[url]/` — if 200 + correct content-length, phone may have cache; force-refresh |
| Phone shows "Tunnel Password" page (using localtunnel) | Visit `https://loca.lt/mytunnelpassword` once from same IP to register; or switch to cloudflared |
| Hot-linked Wikipedia images don't load on phone | Verify CN access to upload.wikimedia.org — sometimes ISP-throttled, may need to inline base64 critical images |
| HTTPS-only image loaded over HTTP tunnel | Cloudflare quick tunnel is HTTPS by default. Mixed content shouldn't be an issue. |

## Anti-pattern

- **Don't serve the entire vault dir** — only the scoped temp dir. Exposes biz docs / wiki / etc.
- **Don't loop sleep + recheck tunnel** — process is up or it isn't. Single check, move on.
- **Don't reuse tunnels across artifacts** — each artifact gets its own scoped temp dir. Otherwise stale content leaks.
