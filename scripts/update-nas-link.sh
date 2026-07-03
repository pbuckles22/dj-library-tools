#!/bin/bash
# Stable NAS path for Lexicon, Serato config, and dj.py pipeline.
# Creates ~/Music/DJ_Master_Link -> /Volumes/buckles (or buckles-1, etc.)

set -euo pipefail

NAS_VOLUME="${NAS_VOLUME:-buckles}"
STATIC_LINK="${HOME}/Music/DJ_Master_Link"
LOG_DIR="${HOME}/Library/Logs/dj-tools"
mkdir -p "$LOG_DIR" "$HOME/Music"
LOG="${LOG_DIR}/nas-link.log"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

CURRENT_MOUNT=""
for candidate in "/Volumes/${NAS_VOLUME}" /Volumes/${NAS_VOLUME}*; do
    if [ -d "$candidate" ] && mount | grep -q " on ${candidate} "; then
        CURRENT_MOUNT="$candidate"
        break
    fi
done

if [ -z "$CURRENT_MOUNT" ]; then
    echo "$(ts) ERROR: NAS volume '${NAS_VOLUME}' not mounted" >> "$LOG"
    echo "NAS not mounted. Mount '${NAS_VOLUME}' in Finder, then retry." >&2
    exit 1
fi

if [ -L "$STATIC_LINK" ] || [ -e "$STATIC_LINK" ]; then
    rm -f "$STATIC_LINK"
fi

ln -s "$CURRENT_MOUNT" "$STATIC_LINK"
echo "$(ts) OK: ${STATIC_LINK} -> ${CURRENT_MOUNT}" >> "$LOG"
echo "NAS link: ${STATIC_LINK} -> ${CURRENT_MOUNT}"
