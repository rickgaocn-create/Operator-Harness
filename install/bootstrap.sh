#!/usr/bin/env bash
# macOS installer for the operator harness — the bash counterpart to bootstrap.ps1.
# Copies the vault framework + ~/.claude machinery into place, substitutes machine
# placeholders, ports the hooks to python3, and registers the 38 routines as launchd
# agents (via taskxml_to_launchd.py). Idempotent-ish; re-runnable.
#
# Usage:
#   bash install/bootstrap.sh --vault-root "$HOME/Documents/RG" [--python /opt/homebrew/bin/python3]
#                             [--register-agents] [--install-daemons] [--dry-run]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VAULT_ROOT=""
PYTHON=""
USER_HOME="$HOME"
REGISTER_AGENTS=0
INSTALL_DAEMONS=0
DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --vault-root) VAULT_ROOT="$2"; shift 2;;
    --python) PYTHON="$2"; shift 2;;
    --user-home) USER_HOME="$2"; shift 2;;
    --register-agents) REGISTER_AGENTS=1; shift;;
    --install-daemons) INSTALL_DAEMONS=1; shift;;
    --dry-run) DRY=1; shift;;
    *) echo "unknown arg: $1"; exit 1;;
  esac
done

info(){ printf '\033[36m[*]\033[0m %s\n' "$*"; }
ok(){   printf '\033[32m[+]\033[0m %s\n' "$*"; }
warn(){ printf '\033[33m[!]\033[0m %s\n' "$*"; }

[[ "$(uname)" == "Darwin" ]] || warn "Not macOS (uname=$(uname)). This installer targets macOS; on Windows use bootstrap.ps1."
[[ -n "$VAULT_ROOT" ]] || { echo "ERROR: --vault-root is required"; exit 1; }
VAULT_ROOT="${VAULT_ROOT/#\~/$HOME}"
[[ -n "$PYTHON" ]] || PYTHON="$(command -v python3 || true)"
[[ -n "$PYTHON" ]] || { echo "ERROR: python3 not found; pass --python"; exit 1; }
HOSTNAME_VAL="$(hostname -s 2>/dev/null || echo mac)"
TASK_USER="$(id -un)"
CLAUDE_HOME="$USER_HOME/.claude"

info "vault-root = $VAULT_ROOT"
info "python     = $PYTHON  ($("$PYTHON" --version 2>&1))"
info "claude home= $CLAUDE_HOME"
[[ $DRY -eq 1 ]] && warn "DRY RUN — no files written."

# --- placeholder substitution helper (text files only) ---
substitute_tree() {
  local root="$1"
  [[ $DRY -eq 1 ]] && return 0
  "$PYTHON" - "$root" "$VAULT_ROOT" "$USER_HOME" "$PYTHON" "$TASK_USER" "$HOSTNAME_VAL" <<'PY'
import os, sys
root, vault, home, py, tuser, host = sys.argv[1:7]
EXT={'.md','.py','.sh','.json','.toml','.txt','.yml','.yaml','.plist','.cjs','.mjs','.js','.ts'}
sub={'{{VAULT_ROOT}}':vault,'{{USER_HOME}}':home,'{{PYTHON_EXE}}':py,'{{TASK_USER}}':tuser,'{{HOSTNAME}}':host}
for dp,_,fns in os.walk(root):
    if '/.git' in dp: continue
    for fn in fns:
        if os.path.splitext(fn)[1].lower() not in EXT: continue
        p=os.path.join(dp,fn)
        try: t=open(p,encoding='utf-8').read()
        except: continue
        o=t
        for k,v in sub.items(): t=t.replace(k,v)
        if t!=o: open(p,'w',encoding='utf-8').write(t)
PY
}

copy_tree() {
  local src="$1" dst="$2"
  [[ -d "$src" ]] || return 0
  if [[ $DRY -eq 1 ]]; then info "would copy $src -> $dst"; return 0; fi
  mkdir -p "$dst"
  cp -R "$src/." "$dst/"
  info "copied $src -> $dst"
}

# --- 1. vault framework + global machinery ---
copy_tree "$REPO_ROOT/vault" "$VAULT_ROOT"
copy_tree "$REPO_ROOT/claude-global" "$CLAUDE_HOME"

# --- 2. macOS hook ports overlay (python hooks replace the .ps1 ones on mac) ---
if [[ -d "$REPO_ROOT/macos/hooks" ]]; then
  copy_tree "$REPO_ROOT/macos/hooks" "$CLAUDE_HOME/hooks"
  ok "installed macOS python hook ports"
fi

# --- 3. substitute placeholders in the installed trees ---
if [[ $DRY -eq 0 ]]; then
  info "substituting machine placeholders..."
  substitute_tree "$VAULT_ROOT"
  substitute_tree "$CLAUDE_HOME"
  ok "placeholders substituted"
fi

# --- 4. settings.local.json for macOS (wires the python hooks with python3) ---
DARWIN_SETTINGS="$REPO_ROOT/macos/settings.local.darwin.json"
if [[ -f "$DARWIN_SETTINGS" && $DRY -eq 0 ]]; then
  mkdir -p "$CLAUDE_HOME"
  sed -e "s#{{PYTHON_EXE}}#$PYTHON#g" -e "s#{{VAULT_ROOT}}#$VAULT_ROOT#g" -e "s#{{USER_HOME}}#$USER_HOME#g" \
      "$DARWIN_SETTINGS" > "$CLAUDE_HOME/settings.local.json"
  ok "wrote $CLAUDE_HOME/settings.local.json (macOS hook wiring)"
fi

# --- 5. launchd agents from the 38 task XMLs ---
LA="$USER_HOME/Library/LaunchAgents"
GEN="$REPO_ROOT/install/macos/taskxml_to_launchd.py"
if [[ $REGISTER_AGENTS -eq 1 ]]; then
  info "generating launchd plists from runtime/scheduled-tasks ..."
  "$PYTHON" "$GEN" --tasks-dir "$REPO_ROOT/runtime/scheduled-tasks" --out-dir "$LA" \
      --python "$PYTHON" --vault-root "$VAULT_ROOT" --user-home "$USER_HOME" $([[ $DRY -eq 1 ]] && echo --dry-run)
  if [[ $DRY -eq 0 ]]; then
    mkdir -p "$USER_HOME/Library/Logs/operator-harness"
    loaded=0
    for plist in "$LA"/com.operator-harness.*.plist; do
      [[ -e "$plist" ]] || continue
      launchctl unload "$plist" 2>/dev/null || true
      if launchctl load "$plist" 2>/dev/null; then loaded=$((loaded+1)); fi
    done
    ok "loaded $loaded launchd agents"
  fi
else
  warn "--register-agents not set; skipping launchd registration. Re-run with it to enable the 38 routines."
fi

# --- 6. daemon launchers (optional) ---
if [[ $INSTALL_DAEMONS -eq 1 && -d "$REPO_ROOT/macos/daemons" && $DRY -eq 0 ]]; then
  for d in "$REPO_ROOT/macos/daemons"/*/; do
    [[ -d "$d" ]] || continue
    name="$(basename "$d")"; dest="$USER_HOME/.$name"
    mkdir -p "$dest"; cp -R "$d." "$dest/"; chmod +x "$dest"/*.sh 2>/dev/null || true
  done
  warn "daemon launchers installed; supply tokens (.env / access.json) before they will run."
fi

# make hook + extra scripts executable
[[ $DRY -eq 0 ]] && { chmod +x "$CLAUDE_HOME/hooks"/*.py "$CLAUDE_HOME/hooks"/*.sh 2>/dev/null || true; }

echo
ok "macOS install complete."
cat <<EONEXT

NEXT STEPS (manual):
  1. Personalize $VAULT_ROOT/me.md , /CLAUDE.md , /MEMORY.md (replace {{USER_NAME}} etc.).
  2. Channel secrets: create the gitignored .env / access.json the daemons expect.
  3. Open the vault in Obsidian; install the community plugins in .obsidian.
  4. Verify launchd: launchctl list | grep operator-harness
  5. Mac-only extras: see macos/mac-extras/ (native notifications, clipboard capture).
EONEXT
