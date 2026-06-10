"""
Stage untagged Shazam-queue files out of Master for manual tagging.
"""

import shutil
from pathlib import Path

from lib.rename import AUDIO_EXTENSIONS
from lib.tag import iter_untagged


def default_shazam_dir(master: Path) -> Path:
    """Shazam staging folder: sibling of Master under My Music."""
    return (master.parent / "Shazam").resolve()


def read_queue_names(master: Path) -> list[str]:
    """Read filenames from Master/_meta/shazam_queue.txt, or scan untagged."""
    queue_file = master / "_meta" / "shazam_queue.txt"
    names: list[str] = []

    if queue_file.exists():
        for line in queue_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(("Shazam queue", "Policy:", "Total:")):
                continue
            names.append(line)

    if names:
        return names

    return [p.name for p in iter_untagged(master)]


def _unique_dest(dest_dir: Path, name: str) -> Path:
    dest = dest_dir / name
    if not dest.exists():
        return dest
    stem = Path(name).stem
    suffix = Path(name).suffix
    n = 1
    while True:
        candidate = dest_dir / f"{stem} ({n}){suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def stage_shazam_queue(
    master: Path,
    dest: Path | None = None,
    *,
    dry_run: bool = False,
) -> tuple[list[tuple[Path, Path]], list[str]]:
    """
    Move Shazam-queue files from Master to dest (default: ../Shazam).
    Returns (moved_pairs, errors).
    """
    if dest is None:
        dest = default_shazam_dir(master)
    dest.mkdir(parents=True, exist_ok=True)

    names = read_queue_names(master)
    moved: list[tuple[Path, Path]] = []
    errors: list[str] = []
    missing: list[str] = []

    print(f"Staging {len(names)} file(s) from Master -> {dest}")
    if dry_run:
        print("  DRY RUN — no files will be moved.")

    for name in names:
        src = master / name
        if not src.is_file():
            missing.append(name)
            continue

        target = _unique_dest(dest, name)
        if dry_run:
            print(f"  WOULD MOVE: {name}")
            moved.append((src, target))
            continue

        try:
            shutil.move(str(src), str(target))
            print(f"  MOVED: {name}")
            moved.append((src, target))
        except OSError as exc:
            msg = f"{name}: {exc}"
            errors.append(msg)
            print(f"  ERROR: {msg}")

    if missing:
        print(f"  {len(missing)} listed file(s) not found in Master (skipped).")

    if not dry_run and moved:
        note = master / "_meta" / "shazam_queue.txt"
        lines = [
            "Shazam queue — files staged for manual tagging.",
            f"Location: {dest}",
            f"Staged: {len(moved)}",
            "",
            "When tagged, move back to Master and run:",
            "  python dj.py rename --full",
            "  python dj.py sync rekordbox",
            "",
        ]
        for _, dst in moved:
            lines.append(dst.name)
        note.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{'Would stage' if dry_run else 'Staged'}: {len(moved)}  Errors: {len(errors)}")
    return moved, errors
