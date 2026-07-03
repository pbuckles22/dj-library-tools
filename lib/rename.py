"""
Rename audio files to "Artist - Title.ext" using ID3/metadata tags.
Skips frozen (done) tracks.
"""

import re
import time
from pathlib import Path

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

from .freeze import is_done, mark_done

AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav", ".aac", ".ogg", ".alac", ".aiff"}


def _safe_filename(s: str) -> str:
    if not s or not s.strip():
        return "Unknown"
    s = re.sub(r"[\uf00a\r\n\t]", " ", s)
    s = re.sub(r'[<>:"/\\|?*]', "", s)
    s = re.sub(r"\s+", " ", s)
    s = s.strip().strip(".")
    return s or "Unknown"


def _get_tags(filepath: Path):
    if MutagenFile is None:
        return None, None
    f = None
    try:
        f = MutagenFile(str(filepath), easy=True)
        if f is None:
            return None, None
        artist = f.get("artist")
        title  = f.get("title")
        if isinstance(artist, (list, tuple)):
            artist = artist[0] if artist else None
        if isinstance(title, (list, tuple)):
            title = title[0] if title else None
        return artist, title
    except Exception:
        return None, None
    finally:
        if f is not None:
            try:
                f.close()
            except Exception:
                pass


def rename_by_tags(master: Path, days: float | None = None) -> tuple[int, int]:
    """
    Rename files in master to "Artist - Title.ext".
    Returns (renamed, skipped).
    """
    if MutagenFile is None:
        print("Error: mutagen not installed. Run: pip install mutagen")
        return 0, 0

    cutoff = None
    if days and days > 0:
        cutoff = time.time() - (days * 86400)
        print(f"Renaming files (last {days} day(s))...")
    else:
        print("Renaming files...")

    renamed = skipped = frozen_skip = 0
    for f in sorted(master.iterdir()):
        if not f.is_file() or f.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        if is_done(f, master):
            frozen_skip += 1
            continue
        if cutoff and f.stat().st_mtime < cutoff:
            continue
        artist, title = _get_tags(f)
        if not artist and not title:
            skipped += 1
            continue
        artist = _safe_filename(str(artist)) if artist else "Unknown"
        title  = _safe_filename(str(title))  if title  else "Unknown"
        new_name = f"{artist} - {title}{f.suffix}"
        new_path = f.parent / new_name
        if new_path == f or (new_path.exists() and new_path != f):
            skipped += 1
            continue
        try:
            f.rename(new_path)
            mark_done(new_path, master)
            print(f"  {f.name} -> {new_name}")
            renamed += 1
        except OSError as e:
            print(f"  ERROR renaming file: {e}")

    print(f"Renamed: {renamed}  Skipped: {skipped}  Frozen (untouched): {frozen_skip}")
    return renamed, skipped
