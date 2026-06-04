/*
 * wxkey - WeChat SQLCipher key candidate extractor (clean reimplementation, no WeFlow code).
 *
 * Mirrors the documented technique: get a Mach task port for the running WeChat process
 * (task_for_pid), walk its readable private memory regions (mach_vm_region_recurse),
 * copy them (mach_vm_read_overwrite), and emit 32-byte high-entropy candidates as hex on
 * stdout. The Python side (wechat_db.py) VALIDATES each candidate by trying to open the DB,
 * so this binary needs no SQLCipher and no DB access — only the debugger entitlement to read
 * another process's memory (see wxkey_entitlements.plist + build-and-sign.sh).
 *
 *   usage:  wxkey <pid>
 *   output: one 64-hex-char candidate key per line
 *
 * Requires macOS (Mach VM APIs). Build:  ./build-and-sign.sh
 *
 * Tuning note: this emits every 8-byte-aligned 32-byte window in writable-private regions that
 * passes an entropy gate — correct but broad. To narrow (fewer candidates, faster validation),
 * restrict to regions near WeChat's key structures once a signature is known on your version.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <mach/mach.h>
#include <mach/mach_vm.h>

#define KEYLEN 32
#define ALIGN 8
#define MAX_REGION (64u * 1024 * 1024)   /* skip/chunk regions larger than 64MB */
#define MAX_CANDS 200000                 /* safety cap on emitted candidates */

static int looks_like_key(const uint8_t *p) {
    /* binary, high-entropy 32 bytes: not all-zero, decent byte diversity, not plain ASCII text */
    int seen[256] = {0}, distinct = 0, ascii = 0, zero = 0;
    for (int i = 0; i < KEYLEN; i++) {
        uint8_t b = p[i];
        if (!seen[b]) { seen[b] = 1; distinct++; }
        if (b == 0) zero++;
        if (b >= 0x20 && b < 0x7f) ascii++;
    }
    if (zero > 4) return 0;          /* keys rarely have many zero bytes */
    if (distinct < 16) return 0;     /* low entropy -> not a key */
    if (ascii >= KEYLEN - 2) return 0; /* looks like printable text, not a raw key */
    return 1;
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "usage: %s <pid>\n", argv[0]); return 2; }
    pid_t pid = (pid_t)atoi(argv[1]);
    if (pid <= 0) { fprintf(stderr, "bad pid\n"); return 2; }

    task_t task;
    kern_return_t kr = task_for_pid(mach_task_self(), pid, &task);
    if (kr != KERN_SUCCESS) {
        fprintf(stderr, "task_for_pid failed (%d): need the debugger entitlement or SIP off\n", kr);
        return 1;
    }

    mach_vm_address_t addr = 0;
    long emitted = 0;
    uint8_t *buf = malloc(MAX_REGION);
    if (!buf) { fprintf(stderr, "oom\n"); return 1; }

    while (emitted < MAX_CANDS) {
        mach_vm_size_t size = 0;
        vm_region_submap_info_data_64_t info;
        mach_msg_type_number_t count = VM_REGION_SUBMAP_INFO_COUNT_64;
        natural_t depth = 0;
        kr = mach_vm_region_recurse(task, &addr, &size, &depth,
                                    (vm_region_recurse_info_t)&info, &count);
        if (kr != KERN_SUCCESS) break;            /* no more regions */

        /* only readable, private (anonymous heap) regions are worth scanning for the key */
        int readable = (info.protection & VM_PROT_READ);
        int priv = (info.share_mode == SM_PRIVATE || info.share_mode == SM_COW);
        if (readable && priv && size > 0) {
            mach_vm_size_t off = 0;
            while (off < size && emitted < MAX_CANDS) {
                mach_vm_size_t chunk = size - off;
                if (chunk > MAX_REGION) chunk = MAX_REGION;
                mach_vm_size_t got = 0;
                kr = mach_vm_read_overwrite(task, addr + off, chunk,
                                            (mach_vm_address_t)buf, &got);
                if (kr == KERN_SUCCESS && got >= KEYLEN) {
                    for (mach_vm_size_t i = 0; i + KEYLEN <= got && emitted < MAX_CANDS; i += ALIGN) {
                        if (looks_like_key(buf + i)) {
                            char hex[KEYLEN * 2 + 1];
                            for (int k = 0; k < KEYLEN; k++)
                                snprintf(hex + k * 2, 3, "%02x", buf[i + k]);
                            puts(hex);
                            emitted++;
                        }
                    }
                }
                off += chunk;
            }
        }
        addr += size;
    }

    free(buf);
    fprintf(stderr, "[wxkey] emitted %ld candidate(s)\n", emitted);
    return emitted > 0 ? 0 : 1;
}
