#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="${REPO_ROOT}/scripts/launchd/local.dj.nas-link.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/local.dj.nas-link.plist"
USERNAME="$(whoami)"

sed -e "s|REPO_ROOT|${REPO_ROOT}|g" \
    -e "s|USERNAME|${USERNAME}|g" \
    "$PLIST_SRC" > "$PLIST_DST"

launchctl bootout "gui/${UID}/local.dj.nas-link" 2>/dev/null || true
launchctl bootstrap "gui/${UID}" "$PLIST_DST"
launchctl enable "gui/${UID}/local.dj.nas-link" 2>/dev/null || true

bash "${REPO_ROOT}/scripts/update-nas-link.sh"
echo "Installed launchd agent: ${PLIST_DST}"
