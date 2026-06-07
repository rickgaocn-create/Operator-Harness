# Native WeChat reader — Windows (replaces WeFlow)

A native, stdlib-light replacement for WeFlow on Windows. WeFlow's actual capability is a memory
key-scan + SQLCipher-4 queries; its 184MB Electron bundle is bloat — and it crashes WeChat. This
keeps the capability, drops the app, and is a **drop-in**: point `WEFLOW_BASE` at this bridge and the
harness (`daily-wechat-ingest`, `wechat_schedule_capture`) works unchanged. Verified 2026-06-05.

## How WeChat-Windows reading works (the mechanism)

WeChat 4.0 stores messages in **SQLCipher-4** SQLite under
`D:\…\xwechat_files\<acct>\db_storage\{session,message,contact}\*.db`. The per-DB raw `enc_key`
lives in the running WeChat process's memory (WCDB caches `enc_key‖salt`). So:

1. `OpenProcess(PROCESS_VM_READ|QUERY)` on `Weixin.exe` → `VirtualQueryEx`/`ReadProcessMemory` →
   find the 32-byte `enc_key` sitting next to the target DB's 16-byte salt. **No admin entitlement
   like macOS `task_for_pid` — same-user `ReadProcessMemory` is enough** (run elevated if a region
   is denied).
2. Pure-Python SQLCipher-4 decrypt: page 4096, reserve 80 (IV 16 + HMAC-SHA512 64), AES-256-CBC,
   `mac_key = PBKDF2-SHA512(enc_key, salt⊕0x3a, 2)`. HMAC-verify page 1, decrypt to plaintext SQLite.
3. Query: `session.SessionTable` (sessions) · per-chat `Msg_<md5(talker)>` across `message_*.db`
   shards (messages) · `contact.contact` (display names). `message_content` is plain utf-8 **or**
   zstd (magic `28 b5 2f fd`).

## Components

| File | Role |
|---|---|
| `poc_decrypt.py` | the engine: ctypes memory key-scan + pure-Python SQLCipher-4 page decrypt (standalone, proves a DB) |
| `wechat_db_win.py` | DB discovery + key cache + decrypt cache + `sessions()` / `messages()` (WeFlow JSON shapes) |
| `wechat_bridge.py` | localhost HTTP server: `/health`, `/api/v1/sessions`, `/api/v1/messages` + Bearer auth |

## Deps

```
pip install pycryptodome zstandard      # AES + zstd; ctypes/sqlite3/hashlib are stdlib
```

## Run (drop-in for WeFlow)

```bat
:: 1. make sure WeChat (微信 / Weixin.exe) is running — it's the key source
:: 2. start the native bridge (default port 5031, same as WeFlow)
set WECHAT_BRIDGE_TOKEN=<your-token>
python wechat_bridge.py --port 5031
:: 3. point the harness at it (ingest.py / wechat_schedule_capture.py unchanged):
set WEFLOW_BASE=http://127.0.0.1:5031
set WEFLOW_TOKEN=<your-token>
:: 4. stop WeFlow.exe — no longer needed.
```

Wrap `wechat_bridge.py` in a Task Scheduler entry (mirror `runtime/scheduled-tasks/*`) to keep it up.

## Key source — the one operational note

The `enc_key` is read from a live process's memory. Default scan order is `Weixin.exe,WeFlow.exe`
(`WECHAT_KEY_PROCS`). **In normal use 微信 is open, so the bridge reads `Weixin.exe` and WeFlow is not
needed at all.** During the 2026-06-05 build 微信 was closed, so the key was validated from
`WeFlow.exe`'s memory — same key value, proving the pipeline. Cut over with 微信 open.

## Security

Decrypted copies land in `%TEMP%\wxbridge_cache` (whole WeChat history in cleartext). Lock down or
point at a private dir; the build wipes it on exit. Read-only on WeChat's live files (always operates
on a copy — never locks the DB the way WeFlow does).

## Not yet wired

- `/api/v1/media/*` (images/voice) — same key decrypts WeChat's `.dat` media; port the mac decryptor.
- Group-message sender names resolve via each shard's `Name2Id`; 1-on-1 `isSend` via self wxid.
