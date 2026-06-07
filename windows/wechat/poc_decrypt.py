#!/usr/bin/env python3
"""PoC: native Windows WeChat 4.0 reader — no WeFlow, no Electron.

Proves the full pipeline on this machine:
  1. read a target DB's salt (first 16 bytes)
  2. scan a live process's memory (ctypes ReadProcessMemory) for that DB's raw enc_key
     (WCDB caches it; format is enc_key(32B) || salt(16B), stored either raw or as x'<hex>' text)
  3. validate the candidate by HMAC-SHA512 over page 1 (definitive, no full decrypt needed)
  4. pure-Python SQLCipher-4 page decrypt -> plaintext SQLite -> open with stdlib sqlite3

WeChat 4.0 / SQLCipher-4 constants (sourced from ylytdeng/wechat-decrypt + SQLCipher v4 defaults):
  PAGE=4096  RESERVE=80 (IV16 + HMAC-SHA512 64)  KEY=32  AES-256-CBC  mac_key=PBKDF2-SHA512(enc_key, salt^0x3a, 2)

Usage:  python poc_decrypt.py <encrypted_db_path> [--procs Weixin.exe,WeFlow.exe]
Read-only on the DB (operates on a copy). READ-only on process memory.
"""
import ctypes, ctypes.wintypes as wt, sys, os, re, hmac, hashlib, struct, shutil, sqlite3, tempfile, argparse

PAGE, RESERVE, KEYSZ, IVSZ, HMACSZ, SALTSZ = 4096, 80, 32, 16, 64, 16
SQLITE_HDR = b"SQLite format 3\x00"

# ---------- pure-Python SQLCipher-4 decrypt ----------
from Crypto.Cipher import AES

def derive_mac_key(enc_key, salt):
    mac_salt = bytes(b ^ 0x3a for b in salt)
    return hashlib.pbkdf2_hmac('sha512', enc_key, mac_salt, 2, dklen=KEYSZ)

def page_hmac_ok(page, idx, enc_key, salt, mac_key):
    start = SALTSZ if idx == 0 else 0
    data_end = PAGE - RESERVE          # 4016
    iv_end = data_end + IVSZ           # 4032
    mac = hmac.new(mac_key, page[start:iv_end] + struct.pack('<I', idx + 1), hashlib.sha512).digest()
    return mac == page[iv_end:iv_end + HMACSZ]

def decrypt_db(src, enc_key, out):
    with open(src, 'rb') as f:
        blob = f.read()
    if len(blob) < PAGE:
        raise ValueError("db smaller than one page")
    salt = blob[:SALTSZ]
    mac_key = derive_mac_key(enc_key, salt)
    # validate on page 1 before committing to a full decrypt
    if not page_hmac_ok(blob[:PAGE], 0, enc_key, salt, mac_key):
        return False, salt
    npages = len(blob) // PAGE
    out_buf = bytearray()
    for i in range(npages):
        page = blob[i * PAGE:(i + 1) * PAGE]
        start = SALTSZ if i == 0 else 0
        iv = page[PAGE - RESERVE:PAGE - RESERVE + IVSZ]
        enc = page[start:PAGE - RESERVE]
        dec = AES.new(enc_key, AES.MODE_CBC, iv).decrypt(enc)
        if i == 0:
            out_buf += SQLITE_HDR + dec + page[PAGE - RESERVE:]
        else:
            out_buf += dec + page[PAGE - RESERVE:]
    with open(out, 'wb') as f:
        f.write(out_buf)
    return True, salt

# ---------- ctypes process-memory scan ----------
k32 = ctypes.WinDLL('kernel32', use_last_error=True)
PROCESS_VM_READ, PROCESS_QUERY_INFORMATION = 0x0010, 0x0400
MEM_COMMIT = 0x1000
READABLE = {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("RegionSize", ctypes.c_size_t),
                ("State", wt.DWORD), ("Protect", wt.DWORD), ("Type", wt.DWORD)]

def pids_for(names):
    import subprocess
    out = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
    res = []
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) >= 2 and parts[0] and parts[0].lower() in {n.lower() for n in names}:
            try: res.append((parts[0], int(parts[1].replace('"', ''))))
            except ValueError: pass
    return res

def scan_process_for_key(pid, salt):
    """Find a 32-byte enc_key in this pid whose (enc||salt) or hex form sits next to `salt`."""
    h = k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        return None
    salt_hex = salt.hex().encode()           # 32 ascii hex chars
    candidates = []
    addr, mbi = 0, MBI()
    try:
        while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            base, size = mbi.BaseAddress or 0, mbi.RegionSize
            if mbi.State == MEM_COMMIT and mbi.Protect in READABLE and 0 < size <= 500 * 1024 * 1024:
                buf = ctypes.create_string_buffer(size)
                read = ctypes.c_size_t(0)
                if k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, size, ctypes.byref(read)):
                    data = buf.raw[:read.value]
                    # (a) raw form: enc_key(32) || salt(16)
                    pos = data.find(salt)
                    while pos != -1:
                        if pos >= KEYSZ:
                            candidates.append(data[pos - KEYSZ:pos])
                        pos = data.find(salt, pos + 1)
                    # (b) text form: x'<64hex enc><32hex salt>'  -> find salt_hex, take 64 hex before
                    pos = data.find(salt_hex)
                    while pos != -1:
                        if pos >= 64:
                            try: candidates.append(bytes.fromhex(data[pos - 64:pos].decode('ascii')))
                            except Exception: pass
                        pos = data.find(salt_hex, pos + 1)
            nxt = base + size
            if nxt <= addr:
                break
            addr = nxt
    finally:
        k32.CloseHandle(h)
    # dedupe preserving order
    seen, uniq = set(), []
    for c in candidates:
        if len(c) == KEYSZ and c not in seen:
            seen.add(c); uniq.append(c)
    return uniq

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('db')
    ap.add_argument('--procs', default='Weixin.exe,WeFlow.exe,WeChatAppEx.exe')
    args = ap.parse_args()
    db = args.db
    salt = open(db, 'rb').read(SALTSZ)
    print(f"target: {db}\nsalt:   {salt.hex()}")
    names = [s.strip() for s in args.procs.split(',') if s.strip()]
    procs = pids_for(names)
    print(f"scanning {len(procs)} process(es): {procs}")
    for pname, pid in procs:
        cands = scan_process_for_key(pid, salt) or []
        print(f"  {pname} pid={pid}: {len(cands)} candidate key(s)")
        for key in cands:
            tmp = os.path.join(tempfile.gettempdir(), 'wxpoc_' + os.path.basename(db))
            shutil.copy2(db, tmp + '.enc')
            ok, _ = decrypt_db(tmp + '.enc', key, tmp + '.plain')
            if ok:
                print(f"  >>> KEY FOUND in {pname}: {key.hex()}")
                con = sqlite3.connect(tmp + '.plain'); cur = con.cursor()
                tbls = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
                print(f"  decrypted OK. {len(tbls)} tables: {tbls[:12]}")
                for t in tbls[:3]:
                    try:
                        n = cur.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
                        print(f"     {t}: {n} rows")
                    except Exception: pass
                con.close()
                print("\nPoC SUCCESS — native decrypt works, no WeFlow needed.")
                return 0
    print("\nNo valid key found in scanned processes. If personal WeChat (微信) is closed, open it and rescan Weixin.exe.")
    return 1

if __name__ == '__main__':
    sys.exit(main())
