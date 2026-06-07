#!/usr/bin/env python3
"""Native Windows WeChat 4.0 reader — the engine that replaces WeFlow on Windows.

Drop-in backend for wechat_bridge.py: implements the same surface the mac wechat_db.py exposes
(`sessions`, `messages`, `find_message_dbs`) so the existing bridge serves WeFlow's API unchanged.

Mechanism (no Electron, no WeFlow):
  - DB discovery under  <xwechat_files>/<acct>/db_storage/{session,message,contact}/*.db
  - per-DB raw enc_key scanned out of a live WeChat/WeFlow process (poc_decrypt.scan_process_for_key)
  - pure-Python SQLCipher-4 page decrypt (poc_decrypt.decrypt_db) -> plaintext SQLite in a cache dir
  - WeChat 4.0 schema: session.SessionTable ; per-chat Msg_<md5(talker)> across message_*.db shards ;
    contact.contact for display names ; message_content is plain utf-8 OR zstd (magic 28 b5 2f fd)

Env:
  WECHAT_DB_DIR   override the db_storage path (else auto-discover under %USERPROFILE%/.. and D:/)
  WECHAT_KEY_PROCS  comma list of processes to scan for keys (default Weixin.exe,WeFlow.exe)
Read-only on WeChat. Decrypted copies live in a cache dir (sensitive — see CACHE).
"""
import os, sys, glob, hashlib, sqlite3, shutil, tempfile, time, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poc_decrypt import decrypt_db, scan_process_for_key, pids_for, SALTSZ

try:
    import zstandard
    _zd = zstandard.ZstdDecompressor()
except Exception:
    _zd = None

CACHE = os.path.join(tempfile.gettempdir(), "wxbridge_cache")
os.makedirs(CACHE, exist_ok=True)
KEY_PROCS = [p.strip() for p in os.environ.get("WECHAT_KEY_PROCS", "Weixin.exe,WeFlow.exe").split(",") if p.strip()]
_key_cache = {}   # salt_hex -> enc_key bytes
_plain_cache = {} # src_path -> (src_mtime, plain_path)


def _db_root():
    # WECHAT_DB_DIR  = exact db_storage path (skip discovery).
    # WECHAT_FILES_ROOT = the xwechat_files dir if relocated off the default (e.g. another drive);
    #                     the <acct> subdir is globbed. Set either in windows/wechat/config.ps1.
    if os.environ.get("WECHAT_DB_DIR"):
        return os.environ["WECHAT_DB_DIR"]
    roots = [os.environ["WECHAT_FILES_ROOT"]] if os.environ.get("WECHAT_FILES_ROOT") else []
    roots += [os.path.expandvars(r"%USERPROFILE%\Documents\xwechat_files"),
              os.path.expanduser(r"~/Documents/xwechat_files")]
    for r in roots:
        g = glob.glob(os.path.join(r, "*", "db_storage"))
        if g:
            return g[0]
    raise RuntimeError("WeChat db_storage not found; set WECHAT_DB_DIR or WECHAT_FILES_ROOT")

ROOT = _db_root()
SELF = os.path.basename(os.path.dirname(ROOT)).rsplit("_", 1)[0]  # acct dir <wxid>_<hex> -> wxid


def find_message_dbs():
    return sorted(glob.glob(os.path.join(ROOT, "message", "message_*.db")))

def _session_db():  return os.path.join(ROOT, "session", "session.db")
def _contact_db():  return os.path.join(ROOT, "contact", "contact.db")


def _key_for(db):
    salt = open(db, "rb").read(SALTSZ)
    sh = salt.hex()
    if sh in _key_cache:
        return _key_cache[sh]
    for _, pid in pids_for(KEY_PROCS):
        for k in (scan_process_for_key(pid, salt) or []):
            # validate cheaply by trying a one-page decrypt
            tmp = os.path.join(CACHE, "_probe.enc")
            shutil.copy2(db, tmp)
            ok, _ = decrypt_db(tmp, k, tmp + ".plain")
            if ok:
                _key_cache[sh] = k
                return k
    raise RuntimeError(f"no key found for {os.path.basename(db)} (is WeChat or WeFlow running?)")


def _plain(db):
    """Decrypt `db` to the cache (re-using if source unchanged); return plaintext path."""
    mtime = os.path.getmtime(db)
    cached = _plain_cache.get(db)
    if cached and cached[0] == mtime and os.path.exists(cached[1]):
        return cached[1]
    key = _key_for(db)
    enc = os.path.join(CACHE, os.path.basename(db) + ".enc")
    out = os.path.join(CACHE, os.path.basename(db) + ".plain")
    shutil.copy2(db, enc)  # copy so we never lock WeChat's live file
    ok, _ = decrypt_db(enc, key, out)
    if not ok:
        raise RuntimeError(f"decrypt failed for {db}")
    _plain_cache[db] = (mtime, out)
    return out


def _conn(db):
    c = sqlite3.connect(_plain(db)); c.text_factory = bytes; return c


def _decode(v):
    if v is None: return ""
    if isinstance(v, bytes):
        if v[:4] == b"\x28\xb5\x2f\xfd" and _zd:
            try: return _zd.decompress(v).decode("utf-8", "replace")
            except Exception: return ""
        return v.decode("utf-8", "replace")
    return str(v)


# ---- display-name map (username -> remark|nick_name) ----
_names = None
def _name_map():
    global _names
    if _names is not None: return _names
    _names = {}
    try:
        con = _conn(_contact_db()); cur = con.cursor()
        for uname, remark, nick in cur.execute("SELECT username, remark, nick_name FROM contact"):
            u = _decode(uname); _names[u] = _decode(remark) or _decode(nick) or u
        con.close()
    except Exception:
        pass
    return _names


# ---- shard index: md5(talker) table -> message_N.db ----
_shard_idx = None
def _shard_index():
    global _shard_idx
    if _shard_idx is not None: return _shard_idx
    _shard_idx = {}
    for db in find_message_dbs():
        try:
            con = _conn(db); cur = con.cursor()
            for (name,) in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Msg\\_%' ESCAPE '\\'"):
                _shard_idx[name.decode() if isinstance(name, bytes) else name] = db
            con.close()
        except Exception:
            pass
    return _shard_idx


def sessions(limit=2000):
    con = _conn(_session_db()); cur = con.cursor()
    names = _name_map()
    rows = cur.execute(
        "SELECT username, type, unread_count, summary, last_timestamp "
        "FROM SessionTable ORDER BY sort_timestamp DESC LIMIT ?", (limit,)).fetchall()
    con.close()
    out = []
    for uname, typ, unread, summary, last_ts in rows:
        u = _decode(uname)
        if u.startswith("@"):  # placeholder/fold pseudo-rows
            continue
        out.append({
            "username": u,
            "displayName": names.get(u, u),
            "type": typ or 0,
            "sessionType": "group" if u.endswith("@chatroom") else "private",
            "lastTimestamp": last_ts or 0,
            "unreadCount": unread or 0,
            "summary": _decode(summary)[:200],
        })
    return out


def messages(talker, limit=200):
    tbl = "Msg_" + hashlib.md5(talker.encode()).hexdigest()
    db = _shard_index().get(tbl)
    if not db:
        return []
    con = _conn(db); cur = con.cursor()
    # message db's own Name2Id resolves real_sender_id -> username
    id2name = {rid: _decode(un) for rid, un in cur.execute("SELECT rowid, user_name FROM Name2Id")}
    rows = cur.execute(
        f'SELECT local_id, server_id, local_type, sort_seq, real_sender_id, create_time, message_content '
        f'FROM "{tbl}" ORDER BY create_time DESC LIMIT ?', (limit,)).fetchall()
    con.close()
    out = []
    for lid, sid, ltype, seq, sender_id, ctime, content in rows:
        sender = id2name.get(sender_id, "")
        is_send = 1 if sender == SELF else 0
        out.append({
            "localId": lid, "serverId": str(sid) if sid is not None else "",
            "localType": ltype, "sortSeq": seq, "createTime": ctime,
            "isSend": is_send,
            "senderUsername": SELF if is_send else (talker if not talker.endswith("@chatroom") else sender),
            "content": _decode(content),
        })
    out.reverse()  # oldest-first, matching WeFlow
    return out


if __name__ == "__main__":
    print(f"db_root: {ROOT}\nself: {SELF}\nmessage shards: {len(find_message_dbs())}")
    s = sessions(limit=5)
    print(f"\nsessions (top 5):")
    for x in s: print("  ", x["sessionType"], x["displayName"][:18], "| last", x["lastTimestamp"], "| unread", x["unreadCount"])
