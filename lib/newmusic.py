"""
Ingest audio from NewMusic staging into Master and clear validated copies.

Copy new files at pipeline start; after organize/rename/dedup/sync, remove
NewMusic files whose content (MD5) is confirmed present in Master.
"""

import shutil
from pathlib import Path

from lib.dedup import AUDIO_EXTENSIONS, get_md5, load_hash_lib

SKIP_DIR_NAMES = {"_meta", ".DS_Store"}


def iter_audio_files(root: Path):
    """Yield audio files under root, recursively; skip _meta and junk dirs."""
    if not root.is_dir():
        return
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        yield path


def _unique_dest(master: Path, name: str) -> Path:
    dest = master / name
    if not dest.exists():
        return dest
    stem = Path(name).stem
    suffix = Path(name).suffix
    n = 1
    while True:
        candidate = master / f"{stem} ({n}){suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def _count_master_audio(master: Path) -> int:
    return sum(
        1
        for f in master.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    )


def _master_md5_set(master: Path, hash_lib: dict | None) -> set[str]:
    """All MD5s present in Master (hash_lib when complete, else one-time flat scan)."""
    md5s = set(hash_lib.keys()) if hash_lib else set()
    on_disk = _count_master_audio(master)
    if hash_lib and len(md5s) >= on_disk:
        return md5s

    for f in master.iterdir():
        if not f.is_file() or f.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        try:
            md5s.add(get_md5(str(f)))
        except OSError:
            pass
    return md5s


def _prune_empty_dirs(root: Path) -> int:
    removed = 0
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path == root:
            continue
        if path.is_dir() and not any(path.iterdir()):
            try:
                path.rmdir()
                removed += 1
            except OSError:
                pass
    return removed


def ingest(
    master: Path,
    newmusic: Path,
) -> tuple[int, int]:
    """
    Copy audio from NewMusic into Master flat root when content is not already present.
    Always scans all of NewMusic (staging folder, not day-filtered).
    Returns (copied, skipped_already_in_master).
    """
    if not newmusic.is_dir():
        print(f"NewMusic not found at {newmusic} — skipping ingest.")
        return 0, 0

    meta = master / "_meta"
    hash_lib = load_hash_lib(meta)
    print("Indexing Master content hashes...")
    known_md5s = _master_md5_set(master, hash_lib)
    print(f"  {len(known_md5s)} unique hash(es) in Master.")

    print("Ingesting NewMusic...")

    copied = 0
    skipped = 0

    for src in iter_audio_files(newmusic):
        try:
            md5 = get_md5(str(src))
        except OSError as e:
            print(f"  SKIP hash {src.name}: {e}")
            continue

        if md5 in known_md5s:
            skipped += 1
            continue

        dest = _unique_dest(master, src.name)
        try:
            shutil.copy2(src, dest)
            known_md5s.add(md5)
            print(f"  {src.relative_to(newmusic)} -> Master/{dest.name}")
            copied += 1
        except OSError as e:
            print(f"  ERROR copying {src.name}: {e}")

    print(f"Ingested {copied} file(s); {skipped} already in Master.")
    return copied, skipped


def clear_staging(
    master: Path,
    newmusic: Path,
    hash_lib: dict | None = None,
) -> tuple[int, int, list[str]]:
    """
    Delete NewMusic files whose MD5 matches content in Master.
    Returns (deleted, kept, failure_messages).
    """
    if not newmusic.is_dir():
        print(f"NewMusic not found at {newmusic} — skipping clear.")
        return 0, 0, []

    if hash_lib is None:
        hash_lib = load_hash_lib(master / "_meta")
    known_md5s = _master_md5_set(master, hash_lib)

    print("Clearing NewMusic staging (validate MD5, then delete)...")

    deleted = 0
    kept = 0
    failures: list[str] = []

    for src in list(iter_audio_files(newmusic)):
        try:
            md5 = get_md5(str(src))
        except OSError as e:
            failures.append(f"{src}: hash failed: {e}")
            kept += 1
            continue

        if md5 not in known_md5s:
            print(f"  KEEP (not in Master): {src.relative_to(newmusic)}")
            kept += 1
            continue

        try:
            src.unlink()
            print(f"  Removed {src.relative_to(newmusic)}")
            deleted += 1
        except OSError as e:
            failures.append(f"{src}: delete failed: {e}")
            kept += 1

    pruned = _prune_empty_dirs(newmusic)
    if pruned:
        print(f"  Removed {pruned} empty folder(s).")

    print(f"Cleared {deleted} file(s); {kept} kept (not validated).")
    if failures:
        print(f"  {len(failures)} error(s) — see above.")
    return deleted, kept, failures
