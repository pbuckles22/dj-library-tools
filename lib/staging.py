"""
Move new music from the staging folder into Master.

Clash policy: Master always wins. On conflict, delete the incoming NewMusic file.
"""

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .dedup import get_md5
from .freeze import frozen_paths, is_done
from .organize import SKIP_FILES
from .rename import _get_tags

AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav", ".aac", ".ogg", ".alac", ".aiff"}


def _log_reject(master: Path, name: str, reason: str) -> None:
    meta = master / "_meta"
    meta.mkdir(exist_ok=True)
    log = meta / "rejected_imports.log"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(log, "a") as f:
        f.write(f"{ts}  REJECT  {name}  ({reason})\n")


def _norm_tag(s: str | None) -> str:
    return (s or "").strip().lower()


def _frozen_tag_index(master: Path) -> dict[tuple[str, str], Path]:
    index: dict[tuple[str, str], Path] = {}
    for p in frozen_paths(master):
        artist, title = _get_tags(p)
        key = (_norm_tag(artist), _norm_tag(title))
        if key != ("", ""):
            index[key] = p
    return index


def _reject_incoming(f: Path, master: Path, reason: str) -> None:
    print(f"  CLASH ({reason}): deleted incoming {f.name}")
    _log_reject(master, f.name, reason)
    try:
        f.unlink()
    except OSError as e:
        print(f"  ERROR deleting incoming {f.name}: {e}")


def import_new_music(new_music: Path, master: Path) -> int:
    """
    Move files from NewMusic into Master (flat, root-level only).
    On clash with existing Master file: delete incoming, keep Master.
    Returns count of files moved.
    """
    if not new_music.is_dir():
        print(f"  NewMusic not found at {new_music}, skipping.")
        return 0

    entries = [f for f in new_music.iterdir() if f.is_file() and f.name not in SKIP_FILES]
    if not entries:
        print("  NewMusic is empty, nothing to import.")
        return 0

    print(f"Importing from {new_music}...")
    tag_index = _frozen_tag_index(master)

    moved = rejected = 0
    for f in sorted(entries):
        dest = master / f.name

        if dest.exists():
            _reject_incoming(f, master, "filename exists in Master")
            rejected += 1
            continue

        artist, title = _get_tags(f)
        tag_key = (_norm_tag(artist), _norm_tag(title))
        if tag_key != ("", "") and tag_key in tag_index:
            _reject_incoming(f, master, "Artist+Title matches frozen Master track")
            rejected += 1
            continue

        try:
            rejected_md5 = False
            incoming_md5 = get_md5(str(f))
            for frozen in frozen_paths(master):
                try:
                    if get_md5(str(frozen)) == incoming_md5:
                        _reject_incoming(f, master, "MD5 matches frozen Master track")
                        rejected += 1
                        rejected_md5 = True
                        break
                except OSError:
                    continue
            if rejected_md5 or not f.exists():
                continue

            shutil.move(str(f), str(dest))
            os.utime(dest, None)
            print(f"  {f.name}")
            moved += 1
        except OSError as e:
            print(f"  ERROR moving {f.name}: {e}")

    for f in sorted(new_music.iterdir()):
        if f.is_dir() and f.name != "_meta":
            print(f"  Note: subfolder left in NewMusic: {f.name}/")

    print(f"Moved {moved} file(s) NewMusic → Master  |  rejected {rejected}")
    return moved
