# Native WeChat reader (replaces WeFlow)

A ~400-line native replacement for WeFlow's WeChat ingest. WeFlow's actual capability is a memory
key-scanner + SQLCipher queries; its 184MB is Electron/ffmpeg/fonts bloat. This module keeps the
capability, drops the app, and is a **drop-in**: `daily-wechat-ingest/ingest.py` works unchanged.

## How WeChat reading works (the mechanism)

WeChat-mac stores messages in **SQLCipher-encrypted** SQLite (`com.tencent.xinWeChat/.../Message/msg_*.db`).
The 32-byte AES key is **not on disk** — it lives in the running WeChat process's memory. So:

1. `task_for_pid(WeChat)` → read its memory → find the key. (Needs the `com.apple.security.cs.debugger`
   entitlement — this is the only hard part.)
2. Open the DB with `PRAGMA key = x'<hex>'` + WeChat's cipher params.
3. Query the per-chat `Chat_<md5(talker)>` tables + the session DB.

## Components

| File | Role |
|---|---|
| `wechat_db.py` | SQLCipher reader: DB discovery, key acquisition (3 sources), open (3.x/4.0 profiles), sessions/messages queries |
| `wechat_bridge.py` | localhost HTTP server exposing WeFlow's exact 3 endpoints + Bearer auth — the drop-in |
| `keyscan/wxkey.c` | our own key-candidate extractor (task_for_pid + memory scan); validation stays in Python |
| `keyscan/build-and-sign.sh` | compile + self-sign with the debugger entitlement |

## Key acquisition — pick one (in priority order)

`wechat_db.py` tries these in order; the DB-open step validates whichever it gets:

1. **`WECHAT_DB_KEY`** — if you already know the 64-hex key, set it and skip extraction entirely.
2. **`WXKEY_HELPER`** — path to WeFlow's signed `xkey_helper` (Option A bootstrap: reuse the
   already-signed extractor to prove the pipeline today; you keep ~3 small files, drop the Electron app).
3. **`WXKEY`** — path to our own `wxkey` (Option B: fully ours, no WeFlow code). Build it:
   ```bash
   cd keyscan && ./build-and-sign.sh && export WXKEY="$PWD/wxkey"
   ```

## Run (drop-in)

```bash
pip3 install pysqlcipher3
export WECHAT_BRIDGE_TOKEN=$(openssl rand -hex 16)
python3 wechat_db.py --probe              # sanity: dbs found? WeChat running? key source set?
python3 wechat_bridge.py --port 5031 &    # the localhost server
# point the harness at our bridge instead of WeFlow — ingest.py unchanged:
export WEFLOW_BASE=http://127.0.0.1:5031  WEFLOW_TOKEN=$WECHAT_BRIDGE_TOKEN
python3 ../../vault/.claude/skills/daily-wechat-ingest/scripts/ingest.py
```

Wrap `wechat_bridge.py` in a launchd agent (use the `taskxml_to_launchd.py` pattern) to keep it up.

## WeChat-version handling

Cipher params + schema differ by version. `wechat_db.py` ships both profiles and tries each:
- **3.x** — SQLCipher v3: `kdf_iter 64000`, HMAC-SHA1, page 4096.
- **4.0 (2024+)** — SQLCipher v4: `kdf_iter 256000`, HMAC-SHA512, page 4096.

Table/column names are discovered via `sqlite_master` + `PRAGMA table_info`, but the exact
session/message schema is version-specific — the spots marked `TODO verify on-device` need one
look at your installed WeChat's DB to pin names. Run `wechat_db.py --probe` first.

## Honest caveats

- **The entitlement is the real work**, not the SQL. `task_for_pid` on a non-child needs the signed
  debugger entitlement, and on some setups SIP off (`csrutil`) and `DevToolsSecurity -enable`.
  WeFlow ships a pre-signed helper to dodge this; ours self-signs (local-only) — see build-and-sign.sh.
- **Version-fragile.** WeChat updates change the DB format/params and can break this — exactly the
  fragility WeFlow itself has.
- **ToS / personal use.** Reading your own messages locally is legitimate personal tooling; automated
  extraction is against WeChat's ToS. Keep it to your own machine/data.
- **Untested from Windows.** This was written by construction on a non-Mac box. The Python/SQL logic
  is structured + validated for syntax; the `task_for_pid` path and exact schema must be exercised on
  a real Apple-Silicon Mac with WeChat installed. Start with `--probe`, then Option A (WeFlow's helper)
  to confirm the SQLCipher→endpoints pipeline before switching to our `wxkey`.
- **`media` endpoint is stubbed** — image/voice are encrypted `.dat` files (same key, AES); wiring the
  decryptor is the one remaining piece for full parity with WeFlow's media support.
