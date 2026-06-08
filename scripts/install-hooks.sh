#!/bin/bash
# Install git hooks that strip Cursor attribution from commit messages.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS="$ROOT/.git/hooks"

mkdir -p "$HOOKS"
cp "$ROOT/scripts/prepare-commit-msg" "$HOOKS/prepare-commit-msg"
chmod +x "$HOOKS/prepare-commit-msg"
echo "Installed prepare-commit-msg hook in $HOOKS"
