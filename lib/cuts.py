"""
Standardize DJ pool cut tags in filenames and dedupe same-song alternate cuts.

Intro aliases (Intro - Clean, DJcity Intro - Clean, …) → canonical Intro Clean.
Narrow dedupe: when an intro-clean cut exists, drop other cuts for that song.
"""

import re
import time
from collections import defaultdict
from pathlib import Path

from lib.dedup import AUDIO_EXTENSIONS
from lib.rename import _safe_filename
from lib.tag import write_tags

CANONICAL_INTRO_CLEAN = "Intro Clean"

INTRO_CLEAN_ALIASES = frozenset(
    {
        "intro clean",
        "intro - clean",
        "djcity intro - clean",
        "hook first - clean",
        "djcity hook first - clean",
        "short edit - clean",
    }
)

FAMILY_RANK = {
    "intro_clean": 0,
    "clean": 1,
    "clean_extended": 2,
    "dirty": 3,
    "intro_dirty": 4,
    "acapella": 5,
    "remix_edit": 6,
    "other": 7,
    "plain": 8,
}


def parse_track_filename(name: str) -> tuple[str, str, list[str]] | None:
    stem = Path(name).stem
    stem = re.sub(r"\s+\(\d+\)$", "", stem)
    if " - " not in stem:
        return None
    artist, title = stem.split(" - ", 1)
    parens = re.findall(r"\(([^)]*)\)", title)
    base = re.sub(r"\s*\([^)]*\)", "", title).strip()
    base = re.sub(r"\s+", " ", base)
    return artist.strip(), base, parens


def norm_key(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def is_intro_clean_alias(tag: str) -> bool:
    t = tag.lower().strip()
    if t == CANONICAL_INTRO_CLEAN.lower():
        return False
    if t in INTRO_CLEAN_ALIASES:
        return True
    return "intro" in t and "clean" in t and "dirty" not in t


def classify_cut(parens: list[str]) -> str:
    if not parens:
        return "plain"
    last = parens[-1].lower().strip()
    if last in INTRO_CLEAN_ALIASES or (
        "intro" in last and "clean" in last and "dirty" not in last
    ):
        return "intro_clean"
    if last == "clean":
        return "clean"
    if "clean extended" in last or (
        "extended" in last and "clean" in last and "intro" not in last
    ):
        return "clean_extended"
    if "intro" in last and "dirty" in last:
        return "intro_dirty"
    if last == "dirty" or ("dirty" in last and "acap" not in last):
        return "dirty"
    if "acap" in last:
        return "acapella"
    if any(w in last for w in ("remix", "edit", "bootleg", "mashup", "rework", "segue")):
        return "remix_edit"
    return "other"


def intro_clean_rank(parens: list[str]) -> int:
    if not parens:
        return 99
    last = parens[-1].lower().strip()
    order = list(INTRO_CLEAN_ALIASES) + [CANONICAL_INTRO_CLEAN.lower()]
    for i, alias in enumerate(order):
        if last == alias:
            return i
    if "intro" in last and "clean" in last:
        return 50
    return 99


def build_canonical_filename(
    artist: str, base: str, parens: list[str], ext: str
) -> str | None:
    if not parens or not is_intro_clean_alias(parens[-1]):
        return None
    new_parens = parens[:-1] + [CANONICAL_INTRO_CLEAN]
    suffix = "".join(f" ({p})" for p in new_parens)
    artist = _safe_filename(artist)
    base = _safe_filename(base)
    return f"{artist} - {base}{suffix}{ext}"


def _title_from_parts(base: str, parens: list[str]) -> str:
    if not parens:
        return base
    return base + "".join(f" ({p})" for p in parens)


def _iter_master_audio(master: Path, days: float | None):
    cutoff = None
    if days and days > 0:
        cutoff = time.time() - (days * 86400)
    for path in sorted(master.iterdir()):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        if cutoff and path.stat().st_mtime < cutoff:
            continue
        yield path


def standardize_cuts(
    master: Path,
    days: float | None = None,
    dry_run: bool = False,
) -> tuple[int, int]:
    """
    Rename intro-clean aliases to canonical (Intro Clean) in filename and ID3 title.
    Returns (renamed, skipped).
    """
    if days and days > 0:
        print(f"Standardizing intro cut names (last {days} day(s))...")
    else:
        print("Standardizing intro cut names...")

    renamed = skipped = 0
    for path in _iter_master_audio(master, days):
        parsed = parse_track_filename(path.name)
        if not parsed:
            skipped += 1
            continue
        artist, base, parens = parsed
        new_name = build_canonical_filename(artist, base, parens, path.suffix)
        if not new_name:
            skipped += 1
            continue
        if new_name == path.name:
            skipped += 1
            continue

        new_path = path.parent / new_name
        if new_path.exists() and new_path != path:
            print(f"  SKIP collision: {path.name} -> {new_name}")
            skipped += 1
            continue

        new_parens = parens[:-1] + [CANONICAL_INTRO_CLEAN]
        new_title = _title_from_parts(base, new_parens)

        if dry_run:
            print(f"  would rename -> {new_name}")
            renamed += 1
            continue

        try:
            write_tags(path, artist, new_title)
        except Exception as e:
            print(f"  WARN tags {path.name}: {e}")

        try:
            path.rename(new_path)
            print(f"  renamed -> {new_name}")
            renamed += 1
        except OSError as e:
            print(f"  ERROR {path.name}: {e}")
            skipped += 1

    print(f"Standardized: {renamed}  Skipped: {skipped}")
    return renamed, skipped


def _pick_keeper(files: list[dict]) -> dict:
    def sort_key(f):
        fam = f["family"]
        rank = FAMILY_RANK.get(fam, 99)
        intro_rank = intro_clean_rank(f["parens"]) if fam == "intro_clean" else 0
        return (rank, intro_rank, f["path"].name.lower())

    return sorted(files, key=sort_key)[0]


def _pick_intro_keeper(files: list[dict]) -> dict:
    intro_files = [f for f in files if f["family"] == "intro_clean"]
    return _pick_keeper(intro_files)


def _group_tracks(master: Path, days: float | None) -> dict[tuple[str, str], list]:
    groups: dict[tuple[str, str], list] = defaultdict(list)
    for path in _iter_master_audio(master, days):
        parsed = parse_track_filename(path.name)
        if not parsed:
            continue
        artist, base, parens = parsed
        groups[(norm_key(artist), norm_key(base))].append(
            {
                "path": path,
                "artist": artist,
                "base": base,
                "parens": parens,
                "family": classify_cut(parens),
            }
        )
    return groups


def dedupe_cuts(
    master: Path,
    mode: str = "narrow",
    days: float | None = None,
    dry_run: bool = True,
) -> tuple[int, int, Path]:
    """
    Remove alternate cuts when a preferred copy exists.
    narrow: only when intro_clean family exists in the group.
    strict: one file per song (intro_clean > clean > …).
    Returns (deleted_count, kept_count, report_path).
    """
    meta = master / "_meta"
    meta.mkdir(exist_ok=True)
    report_path = meta / "cut_dedup_report.txt"

    label = "DRY-RUN" if dry_run else "APPLY"
    print(f"Deduping cuts [{mode}] ({label})...")

    groups = _group_tracks(master, days)
    to_delete: list[Path] = []
    lines = [
        f"Cut dedupe report ({mode}, {label})",
        f"Policy: narrow = drop extras when Intro Clean family exists",
        "",
    ]

    for key, files in sorted(groups.items()):
        if len(files) < 2:
            continue

        if mode == "narrow":
            if not any(f["family"] == "intro_clean" for f in files):
                continue
            keeper = _pick_intro_keeper(files)
        elif mode == "strict":
            keeper = _pick_keeper(files)
        else:
            raise ValueError(f"Unknown mode: {mode}")

        extras = [f for f in files if f["path"] != keeper["path"]]
        if not extras:
            continue

        artist, base = files[0]["artist"], files[0]["base"]
        lines.append(f"KEEP: {keeper['path'].name}")
        for f in extras:
            to_delete.append(f["path"])
            lines.append(f"  DELETE: {f['path'].name}  [{f['family']}]")
        lines.append("")

    deleted = kept = 0
    for path in to_delete:
        if dry_run:
            deleted += 1
            continue
        try:
            path.unlink()
            print(f"  deleted {path.name}")
            deleted += 1
        except OSError as e:
            print(f"  ERROR delete {path.name}: {e}")
            kept += 1

    lines.insert(2, f"Would delete: {len(to_delete)} files" if dry_run else f"Deleted: {deleted}")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report: {report_path}")
    if dry_run:
        print(f"Would delete {len(to_delete)} file(s). Use --apply to execute.")
    else:
        print(f"Deleted {deleted} file(s); {kept} failed.")
    return len(to_delete) if dry_run else deleted, kept, report_path
