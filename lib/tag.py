"""
Tag untagged Master files via AcoustID fingerprint lookup.

Flow: fingerprint → AcoustID match → write Artist/Title with mutagen.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from lib.rename import AUDIO_EXTENSIONS, _get_tags

try:
    import acoustid
except ImportError:
    acoustid = None

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None

MIN_MATCH_SCORE = 0.80


@dataclass(frozen=True)
class TagMatch:
    score: float
    recording_id: str
    title: str
    artist: str


def read_tags(filepath: Path) -> tuple[str | None, str | None]:
    """Public wrapper for tag reads (testable)."""
    return _get_tags(filepath)


def needs_tags(artist: str | None, title: str | None) -> bool:
    """True when Artist or Title is missing (same rule as rename skip)."""
    if not artist or not str(artist).strip():
        return True
    if not title or not str(title).strip():
        return True
    return False


def pick_best_match(results) -> TagMatch | None:
    """Return the highest-scoring AcoustID match above threshold."""
    best: TagMatch | None = None
    for score, recording_id, title, artist in results:
        if score < MIN_MATCH_SCORE:
            continue
        if not artist or not str(artist).strip():
            continue
        if not title or not str(title).strip():
            continue
        match = TagMatch(
            score=float(score),
            recording_id=str(recording_id or ""),
            title=str(title).strip(),
            artist=str(artist).strip(),
        )
        if best is None or match.score > best.score:
            best = match
    return best


def lookup_match(filepath: Path, api_key: str) -> TagMatch | None:
    """Fingerprint file and lookup best AcoustID match."""
    if acoustid is None:
        raise RuntimeError("pyacoustid not installed. Run: pip install pyacoustid")

    try:
        results = list(acoustid.match(api_key, str(filepath)))
    except acoustid.NoBackendError:
        raise RuntimeError(
            "Chromaprint fpcalc not found. Install Chromaprint and ensure fpcalc is on PATH."
        ) from None
    except acoustid.FingerprintGenerationError:
        return None
    except acoustid.AcoustidError:
        return None

    return pick_best_match(results)


def write_tags(filepath: Path, artist: str, title: str) -> bool:
    """Write easy-mode Artist/Title tags. Returns True on success."""
    if MutagenFile is None:
        raise RuntimeError("mutagen not installed. Run: pip install mutagen")

    audio = MutagenFile(str(filepath), easy=True)
    if audio is None:
        return False
    audio["artist"] = artist
    audio["title"] = title
    audio.save()
    return True


def iter_untagged(master: Path, days: float | None = None):
    """Yield untagged audio files in Master root."""
    cutoff = None
    if days and days > 0:
        cutoff = time.time() - (days * 86400)

    for path in sorted(master.iterdir()):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        if cutoff and path.stat().st_mtime < cutoff:
            continue
        artist, title = read_tags(path)
        if needs_tags(artist, title):
            yield path


def _write_report(meta: Path, lines: list[str]) -> None:
    meta.mkdir(exist_ok=True)
    report = meta / "tag_report.txt"
    with open(report, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
        if lines:
            fh.write("\n")


def tag_files(
    master: Path,
    api_key: str,
    *,
    days: float | None = None,
    dry_run: bool = False,
    limit: int | None = None,
) -> tuple[int, int, int]:
    """
    Tag untagged files in Master via AcoustID.
    Returns (tagged, skipped, failed).
    """
    if acoustid is None:
        print("Error: pyacoustid not installed. Run: pip install pyacoustid")
        return 0, 0, 0
    if MutagenFile is None:
        print("Error: mutagen not installed. Run: pip install mutagen")
        return 0, 0, 0

    if days and days > 0:
        print(f"Tagging untagged files (last {days} day(s))...")
    else:
        print("Tagging untagged files...")

    if dry_run:
        print("  DRY RUN — no files will be modified.")

    candidates = []
    for path in iter_untagged(master, days=days):
        candidates.append(path)
        if limit is not None and len(candidates) >= limit:
            break

    total = len(candidates)
    print(f"  {total} untagged file(s) to process.")

    tagged = skipped = failed = 0
    report_lines: list[str] = []

    for i, path in enumerate(candidates, start=1):
        if i == 1 or i % 25 == 0 or i == total:
            print(f"  {i}/{total}...", flush=True)

        try:
            match = lookup_match(path, api_key)
        except RuntimeError as exc:
            print(f"Error: {exc}")
            return tagged, skipped, failed + (total - i + 1)

        if match is None:
            skipped += 1
            report_lines.append(f"SKIP  {path.name}")
            continue

        label = f"{match.artist} - {match.title} ({match.score:.0%})"
        if dry_run:
            print(f"  WOULD TAG: {path.name} -> {label}")
            tagged += 1
            report_lines.append(f"DRY   {path.name} -> {label}")
            continue

        try:
            if write_tags(path, match.artist, match.title):
                print(f"  TAGGED: {path.name} -> {label}")
                tagged += 1
                report_lines.append(f"OK    {path.name} -> {label}")
            else:
                failed += 1
                report_lines.append(f"FAIL  {path.name} (could not write tags)")
        except OSError as exc:
            failed += 1
            report_lines.append(f"FAIL  {path.name} ({exc})")

    _write_report(master / "_meta", report_lines)
    print(f"\nTagged: {tagged}  Skipped (no match): {skipped}  Failed: {failed}")
    print(f"Report: {master / '_meta' / 'tag_report.txt'}")
    return tagged, skipped, failed
