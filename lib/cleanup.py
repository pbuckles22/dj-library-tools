"""
Clean leftover sorting folders under My Music and inside Master.

Removes empty directories, album artwork, and non-audio junk.
Keeps operational folders: Master, NewMusic, Shazam.
"""

from __future__ import annotations

from pathlib import Path

from lib.dedup import AUDIO_EXTENSIONS
from lib.organize import SKIP_FILES

ARTWORK_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}
ARTWORK_NAMES = {"folder.jpg", "folder.png", "cover.jpg", "cover.png", "albumart", "albumartsmall"}
JUNK_EXTENSIONS = {".txt", ".nfo", ".m3u", ".m3u8", ".cue", ".log", ".sfv", ".url", ".ini", ".db"}

KEEP_TOP_LEVEL = {"master", "newmusic", "shazam"}


def _is_artwork(path: Path) -> bool:
    if path.suffix.lower() in ARTWORK_EXTENSIONS:
        return True
    return path.name.lower() in ARTWORK_NAMES


def _is_junk_file(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return True
    if path.suffix.lower() in JUNK_EXTENSIONS:
        return True
    return _is_artwork(path)


def _is_audio(path: Path) -> bool:
    return path.suffix.lower() in AUDIO_EXTENSIONS or path.suffix.lower() == ".wav"


def _count_audio(root: Path) -> int:
    n = 0
    try:
        for p in root.rglob("*"):
            if p.is_file() and _is_audio(p):
                n += 1
    except OSError:
        pass
    return n


def clean_my_music(music_root: Path, *, dry_run: bool = False) -> dict:
    """Delete junk/artwork and empty dirs; report folders that still contain audio."""
    print(f"Cleaning under: {music_root}")
    if dry_run:
        print("  DRY RUN — no changes.")

    deleted_files: list[str] = []
    deleted_dirs: list[str] = []
    fishy_dirs: list[str] = []

    # Clean inside Master subdirs (except _meta and flat root)
    master = music_root / "Master"
    if master.is_dir():
        for sub in master.iterdir():
            if not sub.is_dir() or sub.name == "_meta":
                continue
            for path in sorted(sub.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if path.is_file() and _is_junk_file(path):
                    if dry_run:
                        deleted_files.append(str(path))
                    else:
                        try:
                            path.unlink()
                            deleted_files.append(str(path))
                        except OSError:
                            fishy_dirs.append(str(path))
                elif path.is_dir():
                    try:
                        if not any(path.iterdir()):
                            if dry_run:
                                deleted_dirs.append(str(path))
                            else:
                                path.rmdir()
                                deleted_dirs.append(str(path))
                    except OSError:
                        pass
            if sub.is_dir():
                audio_n = _count_audio(sub)
                if audio_n:
                    fishy_dirs.append(f"{sub.name}/ ({audio_n} audio files)")
                elif not dry_run:
                    try:
                        sub.rmdir()
                        deleted_dirs.append(str(sub))
                    except OSError:
                        pass
                elif dry_run and not any(sub.iterdir()):
                    deleted_dirs.append(str(sub))

    # Clean legacy top-level folders (not Master/NewMusic/Shazam)
    for top in sorted(music_root.iterdir()):
        if not top.is_dir():
            continue
        if top.name.lower() in KEEP_TOP_LEVEL:
            continue

        for path in sorted(top.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if path.is_file() and _is_junk_file(path):
                if dry_run:
                    deleted_files.append(str(path))
                else:
                    try:
                        path.unlink()
                        deleted_files.append(str(path))
                    except OSError:
                        fishy_dirs.append(str(path))

        for path in sorted(top.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            if not path.is_dir() or path == top:
                continue
            try:
                if not any(path.iterdir()):
                    if dry_run:
                        deleted_dirs.append(str(path))
                    else:
                        path.rmdir()
                        deleted_dirs.append(str(path))
            except OSError:
                pass

        if top.is_dir():
            audio_n = _count_audio(top)
            if audio_n:
                fishy_dirs.append(f"{top.name}/ ({audio_n} audio files — review before delete)")
            else:
                try:
                    if not any(top.iterdir()):
                        if dry_run:
                            deleted_dirs.append(str(top))
                        else:
                            top.rmdir()
                            deleted_dirs.append(str(top))
                except OSError:
                    pass

    remaining = sorted(p.name for p in music_root.iterdir() if p.is_dir())

    print(f"\nDeleted junk/artwork files: {len(deleted_files)}")
    print(f"Deleted empty dirs: {len(deleted_dirs)}")
    print(f"Folders still with audio (fishy): {len(fishy_dirs)}")
    print(f"\nTop-level folders remaining ({len(remaining)}):")
    for name in remaining:
        print(f"  {name}/")

    report = music_root / "Master" / "_meta" / "cleanup_report.txt"
    try:
        report.parent.mkdir(exist_ok=True)
        lines = [
            f"Cleanup under {music_root}",
            f"Dry run: {dry_run}",
            "",
            f"Deleted junk files: {len(deleted_files)}",
            f"Deleted empty dirs: {len(deleted_dirs)}",
            "",
            "=== Top-level folders remaining ===",
        ] + [f"  {n}/" for n in remaining]
        if fishy_dirs:
            lines.extend(["", "=== Still contain audio (needs review) ==="] + fishy_dirs[:100])
        if not dry_run:
            report.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"\nReport: {report}")
    except OSError as exc:
        print(f"Could not write report: {exc}")

    return {
        "deleted_files": deleted_files,
        "deleted_dirs": deleted_dirs,
        "fishy_dirs": fishy_dirs,
        "remaining": remaining,
    }
