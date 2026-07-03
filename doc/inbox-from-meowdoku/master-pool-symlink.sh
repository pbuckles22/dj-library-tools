#!/bin/bash

# Target destination where Lexicon/Serato will look for files
STATIC_LINK="$HOME/Music/DJ_Master_Link"

# Find the active mount point (Replace 'MasterPool' with CLI config variable)
CURRENT_MOUNT=$(df | grep -E "/Volumes/MasterPool(_[0-9]|\s[0-9])?" | awk '{for(i=6;i<=NF;i++) printf "%s ", $i; print ""}' | xargs)

if [ -z "$CURRENT_MOUNT" ]; then
    echo "External drive not connected."
    exit 1
fi

# Remove old link and create new static link
if [ -L "$STATIC_LINK" ] || [ -e "$STATIC_LINK" ]; then
    rm -f "$STATIC_LINK"
fi

ln -s "$CURRENT_MOUNT" "$STATIC_LINK"
