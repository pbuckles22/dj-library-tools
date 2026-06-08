"""
Move non-audio files from Master root into Master/_meta.
"""

import time
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav", ".aac", ".ogg", ".alac", ".aiff"}
SKIP_FILES = {"Thumbs.db", "Desktop.ini", ".DS_Store"}


def organize(master: Path, days: float | None = None) -> int:
    """
    Move non-audio files in master root to master/_meta.
    Returns count of files moved.
    """
    meta = master / "_meta"
    meta.mkdir(exist_ok=True)

    cutoff = None
    if days and days > 0:
        cutoff = time.time() - (days * 86400)
        print(f"Organizing (last {days} day(s))...")
    else:
        print("Organizing...")

    moved = 0
    for f in master.iterdir():
        if not f.is_file() or f.parent == meta:
            continue
        if cutoff and f.stat().st_mtime < cutoff:
            continue
        if f.suffix.lower() in AUDIO_EXTENSIONS:
            continue
        if f.name in SKIP_FILES:
            continue
        dest = meta / f.name
        n = 1
        while dest.exists():
            dest = meta / f"{f.stem} ({n}){f.suffix}"
            n += 1
        try:
            f.rename(dest)
            print(f"  {f.name} -> _meta/")
            moved += 1
        except OSError as e:
            print(f"  ERROR moving {f.name}: {e}")

    print(f"Moved {moved} file(s) to _meta/")
    return moved
