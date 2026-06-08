"""
Deduplicate audio files in a directory by MD5 hash.
Keeps the highest bitrate version of each duplicate group.
Supports incremental mode via a hash library cache.
"""

import hashlib
import json
import os
import time
from pathlib import Path

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav", ".aac", ".ogg", ".alac", ".aiff"}


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def get_md5(filepath: str, chunk_size: int = 65536) -> str:
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Bitrate — uses mutagen (cross-platform) with afinfo fallback on macOS
# ---------------------------------------------------------------------------

def _bitrate_mutagen(filepath: str) -> int:
    if MutagenFile is None:
        return 0
    try:
        f = MutagenFile(filepath)
        if f is None:
            return 0
        info = getattr(f, "info", None)
        if info is None:
            return 0
        br = getattr(info, "bitrate", 0)
        return int(br) if br else 0
    except Exception:
        return 0


def _bitrate_afinfo(filepath: str) -> int:
    """macOS-only fallback."""
    import subprocess
    try:
        result = subprocess.run(
            ["afinfo", filepath], capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return 0
        for line in result.stdout.splitlines():
            if line.strip().startswith("bit rate:"):
                parts = line.split(":")
                if len(parts) >= 2:
                    return int(parts[1].strip().split()[0])
    except Exception:
        pass
    return 0


def get_bitrate(filepath: str) -> int:
    br = _bitrate_mutagen(filepath)
    if br > 0:
        return br
    import platform
    if platform.system() == "Darwin":
        return _bitrate_afinfo(filepath)
    return 0


# ---------------------------------------------------------------------------
# Hash library
# ---------------------------------------------------------------------------

def load_hash_lib(meta: Path) -> dict:
    path = meta / "hash_library.json"
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_hash_lib(meta: Path, lib: dict) -> None:
    path = meta / "hash_library.json"
    with open(path, "w") as f:
        json.dump(lib, f, indent=2)


# ---------------------------------------------------------------------------
# Delete script writer
# ---------------------------------------------------------------------------

def _write_delete_script(meta: Path, to_delete: list) -> None:
    report_path = meta / "duplicate_report.txt"
    script_path = meta / "delete_duplicates.sh"

    with open(report_path, "w") as f:
        f.write("Duplicates to remove (lower bit rate).\n" + "=" * 80 + "\n\n")
        f.write("\n".join(f"DELETE: {Path(p).name}" for p in to_delete))
        f.write(f"\n\nTotal: {len(to_delete)}\n")

    with open(script_path, "w") as f:
        f.write("#!/bin/bash\n\n")
        for p in to_delete:
            escaped = str(p).replace("'", "'\"'\"'")
            f.write(f"rm -f '{escaped}'\n")

    script_path.chmod(0o755)


# ---------------------------------------------------------------------------
# Full scan
# ---------------------------------------------------------------------------

def run_full(root: Path, meta: Path) -> list:
    files = [f for f in root.iterdir()
             if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS]
    total = len(files)
    print(f"Full scan: {total} files")
    print("Phase 1: Computing MD5 hashes...")

    hash_to_files: dict = {}
    for i, f in enumerate(files):
        if (i + 1) % 500 == 0 or i == 0:
            print(f"  {i + 1}/{total}...", end="\r", flush=True)
        try:
            md5 = get_md5(str(f))
            hash_to_files.setdefault(md5, []).append(f)
        except (OSError, PermissionError) as e:
            print(f"\n  Skipped {f.name}: {e}")
    print(f"  {total}/{total} done.          ")

    to_delete = []
    lib = {}
    for md5, paths in hash_to_files.items():
        if len(paths) == 1:
            p = paths[0]
            if p.exists():
                lib[md5] = {"path": str(p), "bitrate": get_bitrate(str(p))}
            continue
        file_rates = []
        for p in paths:
            if p.exists():
                file_rates.append((p, get_bitrate(str(p))))
        if not file_rates:
            continue
        file_rates.sort(key=lambda x: (-x[1], str(x[0])))
        keeper = file_rates[0]
        lib[md5] = {"path": str(keeper[0]), "bitrate": keeper[1]}
        for p, _ in file_rates[1:]:
            to_delete.append(p)

    _write_delete_script(meta, to_delete)
    save_hash_lib(meta, lib)
    msg = f"{len(to_delete)} to delete" if to_delete else "No duplicates"
    print(f"\n{msg}. Hash library updated ({len(lib)} tracks).")
    return to_delete


# ---------------------------------------------------------------------------
# Incremental scan
# ---------------------------------------------------------------------------

def run_incremental(root: Path, meta: Path, days: float) -> list:
    cutoff = time.time() - (days * 86400)
    new_files = [
        f for f in root.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
        and f.stat().st_mtime >= cutoff
    ]
    lib = load_hash_lib(meta)

    if not new_files:
        print(f"Incremental: no files modified in last {days} day(s)")
        return []

    total = len(new_files)
    print(f"Incremental: {total} new/modified file(s) (last {days} day(s))")

    new_by_md5: dict = {}
    for i, f in enumerate(new_files):
        if (i + 1) % 100 == 0 or i == 0:
            print(f"  Hashing {i + 1}/{total}...", end="\r", flush=True)
        try:
            new_by_md5.setdefault(get_md5(str(f)), []).append(f)
        except (OSError, PermissionError):
            pass
    print(f"  Hashing {total}/{total} done.          ")

    to_delete = []
    new_keepers: dict = {}

    for md5, paths in new_by_md5.items():
        if len(paths) == 1:
            p = paths[0]
            if p.exists():
                new_keepers[md5] = (str(p), get_bitrate(str(p)))
            continue
        file_rates = [(p, get_bitrate(str(p))) for p in paths if p.exists()]
        if not file_rates:
            continue
        file_rates.sort(key=lambda x: (-x[1], str(x[0])))
        new_keepers[md5] = (str(file_rates[0][0]), file_rates[0][1])
        for p, _ in file_rates[1:]:
            to_delete.append(p)

    for md5, (path, bitrate) in new_keepers.items():
        if md5 in lib:
            existing = lib[md5]
            if bitrate > existing["bitrate"]:
                old_path = Path(existing["path"])
                if old_path.exists() and old_path != Path(path):
                    to_delete.append(old_path)
                lib[md5] = {"path": path, "bitrate": bitrate}
            else:
                p = Path(path)
                if p.exists():
                    to_delete.append(p)
        else:
            lib[md5] = {"path": path, "bitrate": bitrate}

    to_del_paths = {str(Path(p).resolve()) for p in to_delete}
    lib = {m: v for m, v in lib.items()
           if v["path"] not in to_del_paths and Path(v["path"]).exists()}
    save_hash_lib(meta, lib)
    _write_delete_script(meta, to_delete)

    msg = f"{len(to_delete)} to delete" if to_delete else "No duplicates"
    print(f"\n{msg}. Hash library updated.")
    return to_delete


def dedup(root: Path, full: bool = False, days: float | None = None) -> list:
    """Entry point for dedup. Returns list of files to delete."""
    meta = root / "_meta"
    meta.mkdir(exist_ok=True)
    if full or not days or days <= 0:
        return run_full(root, meta)
    return run_incremental(root, meta, days)
