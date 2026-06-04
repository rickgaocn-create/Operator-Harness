#!/usr/bin/env python3
"""Direct SQLCipher reader for the macOS WeChat client DB — the engine that replaces WeFlow.

WeFlow's actual WeChat-reading capability is ~3 native files (a memory key-scanner + SQLCipher
queries); everything else in its 184MB Electron bundle is irrelevant. This module reimplements
that capability cleanly:

  1. KEY ACQUISITION (pluggable, in priority order):
       a. $WECHAT_DB_KEY   — explicit 64-hex-char raw key (skip extraction entirely)
       b. WeFlow's signed helper ($WXKEY_HELPER = path to xkey_helper)  [Option A bootstrap]
       c. our own extractor ($WXKEY = path to the wxkey binary, see keyscan/)  [Option B]
     The extractor reads WeChat's process memory (task_for_pid) and emits candidate keys; we
     VALIDATE each by trying to open the DB — so no entitlement is needed on the Python side.
  2. SQLCipher OPEN with WeChat's params — supports both 3.x and 4.0 cipher profiles.
  3. QUERIES for sessions / messages, matching the shapes daily-wechat-ingest expects.

NOTE: schema + cipher params are WeChat-version-specific. The 3.x/4.0 profiles below are the
documented values; verify against your installed WeChat on first run (`--probe`). Marked TODO
where a live target is needed to pin exact table/column names.
"""
import glob, hashlib, json, os, subprocess, sys

CONTAINER = os.path.expanduser("~/Library/Containers/com.tencent.xinWeChat/Data")

# SQLCipher cipher profiles. WeChat-mac 3.x ~ SQLCipher v3; WeChat 4.0 (2024+) ~ SQLCipher v4.
CIPHER_PROFILES = {
    "3": ["PRAGMA cipher_compatibility = 3", "PRAGMA kdf_iter = 64000",
          "PRAGMA cipher_page_size = 4096", "PRAGMA cipher_hmac_algorithm = HMAC_SHA1",
          "PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1"],
    "4": ["PRAGMA cipher_compatibility = 4", "PRAGMA kdf_iter = 256000",
          "PRAGMA cipher_page_size = 4096", "PRAGMA cipher_hmac_algorithm = HMAC_SHA512",
          "PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512"],
}


# ---------- DB discovery ----------
def find_message_dbs():
    """All message DB shards. 3.x: .../Message/msg_*.db ; 4.0: .../db_storage/message/*.db."""
    pats = [
        os.path.join(CONTAINER, "Documents", "*", "Message", "msg_*.db"),
        os.path.join(CONTAINER, "Documents", "*", "Message", "MSG*.db"),
        os.path.join(CONTAINER, "Documents", "*", "db_storage", "message", "*.db"),
    ]
    out = []
    for p in pats:
        out += glob.glob(p)
    return sorted(set(out))


def find_session_db():
    for p in [os.path.join(CONTAINER, "Documents", "*", "session", "session.db"),
              os.path.join(CONTAINER, "Documents", "*", "Contact", "wccontact_new2.db"),
              os.path.join(CONTAINER, "Documents", "*", "db_storage", "session", "*.db"),
              os.path.join(CONTAINER, "Documents", "*", "Contact", "*.db")]:
        g = glob.glob(p)
        if g:
            return g[0]
    return None


# ---------- key acquisition ----------
def _wechat_pid():
    try:
        out = subprocess.run(["pgrep", "-x", "WeChat"], capture_output=True, text=True, timeout=5).stdout
        pids = [int(x) for x in out.split()]
        return pids[0] if pids else None
    except Exception:
        return None


def candidate_keys():
    """Yield candidate raw keys (hex) from the configured source. The DB-open step validates them."""
    env = os.environ.get("WECHAT_DB_KEY", "").strip()
    if env:
        yield env
        return
    pid = _wechat_pid()
    if not pid:
        raise RuntimeError("WeChat is not running — start it so its key is in memory")
    # Option A: WeFlow's signed helper (xkey_helper <pid> <ciphertext_hex>) -> JSON {aesKey}
    helper = os.environ.get("WXKEY_HELPER")
    if helper and os.path.exists(helper):
        db = find_message_dbs()
        ct = ""
        if db:
            with open(db[0], "rb") as fh:
                ct = fh.read(64).hex()  # first page bytes as the validation ciphertext sample
        try:
            r = subprocess.run([helper, str(pid), ct], capture_output=True, text=True, timeout=30)
            data = json.loads(r.stdout.strip() or "{}")
            if data.get("success") and data.get("aesKey"):
                yield data["aesKey"]
        except Exception:
            pass
    # Option B: our extractor — emits newline-separated hex candidates
    wxkey = os.environ.get("WXKEY")
    if wxkey and os.path.exists(wxkey):
        try:
            r = subprocess.run([wxkey, str(pid)], capture_output=True, text=True, timeout=60)
            for line in r.stdout.splitlines():
                line = line.strip()
                if len(line) == 64 and all(c in "0123456789abcdefABCDEF" for c in line):
                    yield line
        except Exception:
            pass


# ---------- SQLCipher open ----------
def _connect(path, key_hex):
    """Open a SQLCipher DB with WeChat params; return (conn, profile) or raise. Tries 3.x then 4.x."""
    try:
        from pysqlcipher3 import dbapi2 as sqlcipher
    except ImportError:
        raise RuntimeError("pip3 install pysqlcipher3  (or use the sqlcipher CLI fallback)")
    last = None
    for profile, pragmas in CIPHER_PROFILES.items():
        try:
            con = sqlcipher.connect(f"file:{path}?mode=ro", uri=True)
            cur = con.cursor()
            cur.execute(f"PRAGMA key = \"x'{key_hex}'\"")
            for p in pragmas:
                cur.execute(p)
            cur.execute("SELECT count(*) FROM sqlite_master")  # validates key+params
            cur.fetchone()
            return con, profile
        except Exception as e:
            last = e
            try:
                con.close()
            except Exception:
                pass
    raise RuntimeError(f"could not open {os.path.basename(path)} with any profile: {last}")


def open_db(path):
    """Find a working key from the configured source and open the DB. Returns (conn, key_hex, profile)."""
    errs = []
    for key in candidate_keys():
        try:
            con, profile = _connect(path, key)
            return con, key, profile
        except Exception as e:
            errs.append(str(e)[:80])
    raise RuntimeError(f"no candidate key opened the DB (tried {len(errs)})")


# ---------- queries ----------
def talker_table(talker):
    """WeChat-mac per-chat message table name: Chat_<md5hex(talker)>."""
    return "Chat_" + hashlib.md5(talker.encode("utf-8")).hexdigest()


def sessions(limit=2000):
    """Return [{username, name, lastTimestamp}] — matches WeFlow's /api/v1/sessions."""
    sdb = find_session_db()
    if not sdb:
        return []
    con, _key, _prof = open_db(sdb)
    cur = con.cursor()
    # discover the session table + columns (schema varies by version) — TODO verify names on-device
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    out = []
    cand = [t for t in tables if t.lower() in ("session", "sessionabstract", "chat_session")]
    if cand:
        t = cand[0]
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})")]
        ucol = next((c for c in cols if c.lower() in ("username", "strusrname", "userid")), cols[0])
        tcol = next((c for c in cols if "time" in c.lower()), None)
        ncol = next((c for c in cols if c.lower() in ("strnickname", "nickname", "name")), ucol)
        q = f"SELECT {ucol}, {ncol}" + (f", {tcol}" if tcol else "") + f" FROM {t} LIMIT {int(limit)}"
        for row in cur.execute(q):
            out.append({"username": row[0], "name": row[1] if len(row) > 1 else row[0],
                        "lastTimestamp": int(row[2]) if tcol and len(row) > 2 and row[2] else 0})
    con.close()
    return out


def messages(talker, limit=200):
    """Return [{content, createTime, senderUsername, mediaType}] — matches /api/v1/messages."""
    table = talker_table(talker)
    for db in find_message_dbs():
        try:
            con, _key, _prof = open_db(db)
        except Exception:
            continue
        cur = con.cursor()
        has = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                          (table,)).fetchone()
        if not has:
            con.close()
            continue
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info({table})")]
        ccol = next((c for c in cols if c.lower() in ("msgcontent", "strcontent", "content")), None)
        tcol = next((c for c in cols if c.lower() in ("msgcreatetime", "createtime", "mescreatetime")), None)
        dcol = next((c for c in cols if c.lower() in ("mesdes", "isdes", "des")), None)  # 0=sent 1=recv
        out = []
        q = f"SELECT {ccol}, {tcol}" + (f", {dcol}" if dcol else "") + \
            f" FROM {table} ORDER BY {tcol} DESC LIMIT {int(limit)}"
        for row in cur.execute(q):
            content = row[0] or ""
            sender = talker
            # group messages prefix the sender wxid: "wxid_x:\n<content>"
            if "@chatroom" in talker and ":\n" in content[:64]:
                sender, content = content.split(":\n", 1)
            out.append({"content": content, "createTime": int(row[1] or 0),
                        "senderUsername": sender,
                        "mediaType": "text"})  # TODO: classify media via messageType column
        con.close()
        return out
    return []


def probe():
    print("container:", CONTAINER, "exists:", os.path.isdir(CONTAINER))
    print("message dbs:", len(find_message_dbs()))
    print("session db:", find_session_db())
    print("WeChat pid:", _wechat_pid())
    print("key sources: WECHAT_DB_KEY=%s WXKEY_HELPER=%s WXKEY=%s" %
          (bool(os.environ.get("WECHAT_DB_KEY")), os.environ.get("WXKEY_HELPER"), os.environ.get("WXKEY")))


if __name__ == "__main__":
    if "--probe" in sys.argv:
        probe()
    elif "--sessions" in sys.argv:
        print(json.dumps({"sessions": sessions()}, ensure_ascii=False))
    elif "--messages" in sys.argv:
        t = sys.argv[sys.argv.index("--messages") + 1]
        print(json.dumps({"messages": messages(t)}, ensure_ascii=False))
