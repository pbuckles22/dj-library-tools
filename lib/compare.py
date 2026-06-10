"""
Compare old music folders to Master.

Two modes:
  md5   — byte-for-byte comparison (fast but fails when files were re-tagged)
  tags  — Artist+Title tag comparison (handles re-tagged files; default)

Outputs written to the project root:
  tag_compare_in_master.txt
  tag_compare_not_in_master.txt
  tag_compare_no_tags.txt
  tag_compare_delete.sh
"""

import hashlib
import json
import re
from pathlib import Path

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav", ".aac", ".ogg", ".alac", ".aiff"}
_OUT_DIR = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def collect_audio_files(directories: list) -> list:
    files = []
    for d in directories:
        p = Path(d)
        if not p.is_dir():
            print(f"Warning: {d} is not a directory, skipping")
            continue
        for f in p.rglob("*"):
            if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS:
                files.append(f)
    return files


def _write_outputs(prefix: str, in_master, not_in_master, no_tags=None, paired=False):
    """
    Write result files. If paired=True, in_master is list of (old, master) tuples.
    """
    in_path  = _OUT_DIR / f"{prefix}_in_master.txt"
    not_path = _OUT_DIR / f"{prefix}_not_in_master.txt"
    del_path = _OUT_DIR / f"{prefix}_delete.sh"

    with open(in_path, "w", encoding="utf-8") as fh:
        fh.write(f"Files whose content/title match Master ({len(in_master)} files).\n")
        fh.write("Safe to delete from the old folder.\n")
        fh.write("=" * 80 + "\n\n")
        for item in sorted(in_master, key=lambda x: str(x[0] if paired else x)):
            if paired:
                old, mst = item
                fh.write(f"OLD:    {old}\nMASTER: {mst}\n\n")
            else:
                fh.write(str(item) + "\n")

    with open(not_path, "w", encoding="utf-8") as fh:
        fh.write(f"Files NOT found in Master ({len(not_in_master)} files).\n")
        fh.write("REVIEW before deleting. May be personal tracks.\n")
        fh.write("=" * 80 + "\n\n")
        for p in sorted(not_in_master):
            fh.write(str(p) + "\n")

    with open(del_path, "w", encoding="utf-8") as fh:
        fh.write("#!/bin/bash\n")
        fh.write(f"# Delete {len(in_master)} files already confirmed in Master.\n\n")
        items = [x[0] if paired else x for x in in_master]
        for p in sorted(items, key=str):
            escaped = str(p).replace("'", "'\"'\"'")
            fh.write(f"rm -f '{escaped}'\n")
    del_path.chmod(0o755)

    if no_tags is not None:
        nt_path = _OUT_DIR / f"{prefix}_no_tags.txt"
        with open(nt_path, "w", encoding="utf-8") as fh:
            fh.write(f"Files with no readable tags ({len(no_tags)} files). Manual review.\n")
            fh.write("=" * 80 + "\n\n")
            for p in sorted(no_tags):
                fh.write(str(p) + "\n")

    return in_path, not_path, del_path


# ---------------------------------------------------------------------------
# MD5 compare
# ---------------------------------------------------------------------------

def _get_md5(filepath, chunk_size=65536):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_hash_lib(meta: Path) -> set:
    path = meta / "hash_library.json"
    if path.exists():
        try:
            with open(path) as f:
                return set(json.load(f).keys())
        except Exception:
            pass
    return set()


def compare_md5(master: Path, old_dirs: list) -> tuple:
    meta = master / "_meta"
    known = _load_hash_lib(meta)
    if known:
        print(f"Loaded {len(known)} hashes from hash library.")
    else:
        print("No hash library found — hashing Master directly (slow)...")
        files = [f for f in master.rglob("*")
                 if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
                 and not str(f).startswith(str(meta))]
        for i, f in enumerate(files):
            if (i + 1) % 500 == 0:
                print(f"  {i + 1}/{len(files)}...", end="\r", flush=True)
            try:
                known.add(_get_md5(str(f)))
            except (OSError, PermissionError):
                pass
        print(f"  {len(files)} done.          ")

    old_files = collect_audio_files(old_dirs)
    total = len(old_files)
    print(f"Checking {total} files by MD5...")

    in_master, not_in_master = [], []
    for i, f in enumerate(old_files):
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{total}...", end="\r", flush=True)
        try:
            md5 = _get_md5(str(f))
            (in_master if md5 in known else not_in_master).append(f)
        except (OSError, PermissionError) as e:
            print(f"\n  Skipped {f.name}: {e}")
    print(f"  {total}/{total} done.          ")

    _write_outputs("md5_compare", in_master, not_in_master, paired=False)
    return in_master, not_in_master


# ---------------------------------------------------------------------------
# Tag-based compare
# ---------------------------------------------------------------------------

def _normalize(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _key_from_file(filepath: Path) -> tuple:
    artist, title = None, None
    if MutagenFile:
        try:
            f = MutagenFile(str(filepath), easy=True)
            if f:
                a = f.get("artist") or f.get("albumartist")
                t = f.get("title")
                artist = (a[0] if isinstance(a, (list, tuple)) else a) if a else None
                title  = (t[0] if isinstance(t, (list, tuple)) else t) if t else None
                artist = str(artist).strip() if artist else None
                title  = str(title).strip()  if title  else None
        except Exception:
            pass
    if not title:
        stem = re.sub(r"^\d+[\s\-\.]+", "", filepath.stem).strip()
        if " - " in stem:
            parts = stem.split(" - ", 1)
            artist, title = parts[0].strip(), parts[1].strip()
        else:
            title = stem
    return _normalize(artist or ""), _normalize(title or "")


def _build_master_index(master: Path) -> dict:
    meta = master / "_meta"
    files = [f for f in master.rglob("*")
             if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
             and not str(f).startswith(str(meta))]
    total = len(files)
    print(f"Indexing Master by tags ({total} files)...")
    index = {}
    for i, f in enumerate(files):
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{total}...", end="\r", flush=True)
        k = _key_from_file(f)
        if k[1]:
            index[k] = f
    print(f"  {total}/{total} done. {len(index)} title keys.")
    return index


def compare_tags(master: Path, old_dirs: list) -> tuple:
    if MutagenFile is None:
        print("Error: mutagen not installed. Run: pip install mutagen")
        return [], []

    index = _build_master_index(master)

    old_files = collect_audio_files(old_dirs)
    total = len(old_files)
    print(f"\nChecking {total} files by tags...")

    in_master, not_in_master, no_tags = [], [], []
    for i, f in enumerate(old_files):
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{total}...", end="\r", flush=True)
        k = _key_from_file(f)
        if not k[1]:
            no_tags.append(f)
            continue
        if k in index:
            in_master.append((f, index[k]))
        else:
            not_in_master.append(f)
    print(f"  {total}/{total} done.          ")

    _write_outputs("tag_compare", in_master, not_in_master, no_tags=no_tags, paired=True)
    return in_master, not_in_master
