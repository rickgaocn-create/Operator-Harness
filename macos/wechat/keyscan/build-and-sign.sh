#!/usr/bin/env bash
# Compile wxkey and code-sign it with the debugger entitlement so task_for_pid() works.
#
# The entitlement is the only hard part of the whole WeChat-reader. macOS won't let an
# unsigned/unentitled binary read another process's memory. Two paths:
#   (1) self-signed cert (this script) — no Apple Developer account needed, but you must create a
#       local code-signing cert once and the binary only runs on THIS Mac.
#   (2) a real Developer ID cert with the entitlement — redistributable.
# Either way you may still need to grant the Terminal/binary "Developer Tools" rights, and on some
# setups disable SIP (csrutil) for task_for_pid on non-children. See README.md.
set -euo pipefail
cd "$(dirname "$0")"

CERT="${WXKEY_SIGN_IDENTITY:-wxkey-local}"   # name of a code-signing identity in your keychain
OUT="wxkey"

echo "[1/3] compile (arm64 + x86_64 universal)"
clang -O2 -arch arm64 -arch x86_64 -o "$OUT" wxkey.c

# create a self-signed code-signing cert if the named identity doesn't exist yet
if ! security find-identity -v -p codesigning | grep -q "$CERT"; then
  cat <<EOF

  No code-signing identity named "$CERT" found. Create one ONCE:
    1. Open  Keychain Access  ->  Keychain Access menu  ->  Certificate Assistant
       ->  Create a Certificate…
    2. Name: $CERT   Identity Type: Self Signed Root   Certificate Type: Code Signing
    3. Create, then set it to "Always Trust" for code signing.
  Then re-run this script.  (Or use a real Developer ID and set WXKEY_SIGN_IDENTITY.)

EOF
  exit 1
fi

echo "[2/3] codesign with entitlements"
codesign --force --options runtime \
  --entitlements wxkey_entitlements.plist \
  --sign "$CERT" "$OUT"

echo "[3/3] verify"
codesign -d --entitlements - "$OUT" 2>/dev/null | grep -q debugger \
  && echo "  ✅ debugger entitlement present" || { echo "  ❌ entitlement missing"; exit 1; }

echo
echo "Built ./wxkey . Point the reader at it:  export WXKEY=\"$(pwd)/wxkey\""
echo "If task_for_pid still returns (5) KERN_FAILURE, you likely need: csrutil status / disable,"
echo "or grant your terminal Developer Tools rights (DevToolsSecurity -enable; sudo)."
