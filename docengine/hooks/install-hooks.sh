#!/usr/bin/env bash
set -e
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_SRC="$REPO_ROOT/docengine/hooks/pre-commit"
HOOK_DEST="$REPO_ROOT/.git/hooks/pre-commit"

if [ -f "$HOOK_DEST" ] || [ -L "$HOOK_DEST" ]; then
    rm "$HOOK_DEST"
fi

ln -s "$HOOK_SRC" "$HOOK_DEST"
chmod +x "$HOOK_DEST"
echo "[OK] Hook local de pre-commit enlazado correctamente en .git/hooks/pre-commit"
