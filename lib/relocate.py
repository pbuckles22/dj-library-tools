"""
Move non-DJ Master files to parent folder (My Music).

Used for WAV, Persian/regional, and comedy/sketch content that should not
live in the flat DJ Master library.
"""

import shutil
from pathlib import Path

from lib.dedup import AUDIO_EXTENSIONS

PERSIAN_KEYWORDS = (
    "persian", "iran", "farsi", "yazd", "tarane", "bhangra", "shadmehr",
    "black cats", "ay yar", "arash", "abdolmaleki", "folad", "mokhte",
    "kermani", "ey iran", "shade irany", "bir mu", "iran-tarane",
    "mohsen chavoshi", "mohsen yegane", "reza yazdani", "dj mansour",
    "maziar falahi", "shahram shabpareh", "tataloo", "mehran modiri",
    "dokhtare rashti", "ba man beemone",
)
COMEDY_KEYWORDS = (
    "chappelle", "chapelle", "comedy central", "family guy",
    "pablo francisco", "elmo,shut", "titty bar", "sesame street",
    "answering machine messa", "peanut butter jelly",
    "south park", "disney", "lion king", "willy wonka",
    "tv show friends", "tv show quotes - friends", "friends - whoopa",
    "friends - joey",
)


def _matches_keywords(name: str, keywords: tuple[str, ...]) -> bool:
    low = name.lower()
    return any(k in low for k in keywords)


def classify_for_relocate(path: Path) -> str | None:
    """Return relocate reason or None if file should stay in Master."""
    name = path.name
    if path.suffix.lower() == ".wav":
        return "wav"
    if _matches_keywords(name, PERSIAN_KEYWORDS):
        return "persian"
    if _matches_keywords(name, COMEDY_KEYWORDS):
        return "comedy"
    return None


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


def relocate_from_master(
    master: Path,
    dest: Path | None = None,
    *,
    dry_run: bool = False,
) -> tuple[list[tuple[Path, Path, str]], list[str]]:
    """
    Move WAV / Persian / comedy files from Master root to dest (default: parent).
    Returns (moved_list, errors).
    """
    if dest is None:
        dest = master.parent
    dest.mkdir(parents=True, exist_ok=True)

    moved: list[tuple[Path, Path, str]] = []
    errors: list[str] = []

    for path in sorted(master.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in AUDIO_EXTENSIONS and path.suffix.lower() != ".wav":
            continue
        reason = classify_for_relocate(path)
        if not reason:
            continue

        target = _unique_dest(dest, path.name)
        if dry_run:
            print(f"  WOULD MOVE [{reason}]: {path.name} -> {target}")
            moved.append((path, target, reason))
            continue

        try:
            shutil.move(str(path), str(target))
            print(f"  MOVED [{reason}]: {path.name} -> {target.name}")
            moved.append((path, target, reason))
        except OSError as exc:
            msg = f"{path.name}: {exc}"
            errors.append(msg)
            print(f"  ERROR: {msg}")

    return moved, errors
