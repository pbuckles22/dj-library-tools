"""
Bitrate audit for Master — report and move low-bitrate files to Shazam staging.
"""

from __future__ import annotations

import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from lib.dedup import AUDIO_EXTENSIONS, get_bitrate
from lib.shazam_queue import _unique_dest, default_shazam_dir


@dataclass(frozen=True)
class BitrateEntry:
    path: Path
    kbps: int
    tier: str  # "<=96" or "<=128"


def _tier(kbps: int) -> str | None:
    if kbps <= 96:
        return "<=96"
    if kbps <= 128:
        return "<=128"
    return None


def scan_master_bitrates(master: Path) -> tuple[list[BitrateEntry], Counter[str], int]:
    """Scan flat Master root. Returns (flagged, all_buckets, total_audio)."""
    buckets: Counter[str] = Counter()
    flagged: list[BitrateEntry] = []
    total = 0

    for path in sorted(master.iterdir()):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        total += 1
        br = get_bitrate(str(path))
        if not br:
            buckets["unknown"] += 1
            continue
        kbps = br // 1000
        tier = _tier(kbps)
        if tier:
            flagged.append(BitrateEntry(path, kbps, tier))
        if kbps <= 96:
            buckets["<=96"] += 1
        elif kbps <= 128:
            buckets["128"] += 1
        elif kbps <= 160:
            buckets["160"] += 1
        elif kbps <= 192:
            buckets["192"] += 1
        elif kbps <= 256:
            buckets["256"] += 1
        elif kbps <= 320:
            buckets["320"] += 1
        else:
            buckets[">320"] += 1

    return flagged, buckets, total


def write_bitrate_report(master: Path, flagged: list[BitrateEntry], buckets: Counter[str], total: int) -> Path:
    meta = master / "_meta"
    meta.mkdir(exist_ok=True)
    report = meta / "bitrate_report.txt"

    lines = [
        f"Master bitrate report — {total} audio files in flat root",
        "",
        "=== Distribution (kbps) ===",
    ]
    for key in ["<=96", "128", "160", "192", "256", "320", ">320", "unknown"]:
        n = buckets.get(key, 0)
        if n:
            lines.append(f"  {key:>6}: {n:5}  ({100 * n / total:.1f}%)")

    le128 = [e for e in flagged]
    lines.extend([
        "",
        f"Flagged <=128 kbps: {len(le128)} ({100 * len(le128) / total:.1f}%)",
        f"  <=96 kbps: {sum(1 for e in le128 if e.tier == '<=96')}",
        f"  128 kbps:  {sum(1 for e in le128 if e.tier == '<=128')}",
        "",
        "=== Files <=128 kbps ===",
    ])
    for entry in sorted(le128, key=lambda e: (e.kbps, e.path.name.lower())):
        lines.append(f"  {entry.kbps:3} kbps  [{entry.tier}]  {entry.path.name}")

    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def move_low_bitrate_to_shazam(
    master: Path,
    flagged: list[BitrateEntry],
    *,
    dry_run: bool = False,
) -> tuple[list[tuple[Path, Path]], list[str]]:
    """Move flagged files from Master to Shazam folder; update queue list."""
    dest = default_shazam_dir(master)
    dest.mkdir(parents=True, exist_ok=True)

    moved: list[tuple[Path, Path]] = []
    errors: list[str] = []

    print(f"Moving {len(flagged)} low-bitrate file(s) Master -> {dest}")
    if dry_run:
        print("  DRY RUN — no files will be moved.")

    for entry in flagged:
        src = entry.path
        if not src.is_file():
            continue
        target = _unique_dest(dest, src.name)
        label = f"{entry.kbps} kbps [{entry.tier}]"
        if dry_run:
            print(f"  WOULD MOVE {label}: {src.name}")
            moved.append((src, target))
            continue
        try:
            shutil.move(str(src), str(target))
            print(f"  MOVED {label}: {src.name}")
            moved.append((src, target))
        except OSError as exc:
            msg = f"{src.name}: {exc}"
            errors.append(msg)
            print(f"  ERROR: {msg}")

    if not dry_run:
        queue = dest / "shazam_queue.txt"
        existing: list[str] = []
        if queue.exists():
            for line in queue.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line and not line.startswith(("Shazam", "Policy", "Total", "Location", "When", "python")):
                    existing.append(line)
        names = sorted(set(existing + [dst.name for _, dst in moved]))
        lines = [
            "Shazam queue — manual tagging (untagged + low bitrate <=128 kbps).",
            f"Location: {dest}",
            f"Total: {len(names)}",
            "",
            "When tagged, move back to Master and run:",
            "  python dj.py rename --full",
            "  python dj.py sync rekordbox",
            "",
        ] + names
        queue.write_text("\n".join(lines) + "\n", encoding="utf-8")

        (master / "_meta").mkdir(exist_ok=True)
        (master / "_meta" / "shazam_queue.txt").write_text(
            f"Low-bitrate files moved to: {dest}\nSee: {queue}\n",
            encoding="utf-8",
        )

    print(f"\n{'Would move' if dry_run else 'Moved'}: {len(moved)}  Errors: {len(errors)}")
    return moved, errors


def default_low_quality_dir(master: Path) -> Path:
    return (master.parent / "LowQuality").resolve()


def scan_all_entries(master: Path) -> list[BitrateEntry]:
    """All audio files in Master flat root with measured kbps."""
    entries: list[BitrateEntry] = []
    for path in sorted(master.iterdir()):
        if not path.is_file() or path.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        br = get_bitrate(str(path))
        if not br:
            continue
        kbps = br // 1000
        entries.append(BitrateEntry(path, kbps, _quality_label(kbps)))
    return entries


def _quality_label(kbps: int) -> str:
    if kbps <= 96:
        return "<=96"
    if kbps <= 128:
        return "128"
    if kbps <= 160:
        return "160"
    if kbps <= 192:
        return "192"
    if kbps <= 256:
        return "256"
    return "320+"


def apply_quality_tiers(
    master: Path,
    *,
    delete_max_kbps: int = 160,
    move_max_kbps: int = 192,
    low_quality_dir: Path | None = None,
    dry_run: bool = False,
) -> tuple[int, int, int, list[str]]:
    """
    Delete files <= delete_max_kbps; move (delete_max, move_max] to LowQuality.
    Returns (deleted, moved, kept, errors).
    """
    if low_quality_dir is None:
        low_quality_dir = default_low_quality_dir(master)
    low_quality_dir.mkdir(parents=True, exist_ok=True)

    entries = scan_all_entries(master)
    to_delete = [e for e in entries if e.kbps <= delete_max_kbps]
    to_move = [e for e in entries if delete_max_kbps < e.kbps <= move_max_kbps]
    kept = len(entries) - len(to_delete) - len(to_move)

    print(f"Quality tiers: delete <= {delete_max_kbps} kbps, move <= {move_max_kbps} kbps")
    print(f"  Delete: {len(to_delete)}  Move -> LowQuality: {len(to_move)}  Keep in Master: {kept}")
    if dry_run:
        print("  DRY RUN — no changes.")

    errors: list[str] = []
    deleted = moved = 0

    for entry in to_delete:
        if dry_run:
            print(f"  WOULD DELETE [{entry.kbps} kbps]: {entry.path.name}")
            deleted += 1
            continue
        try:
            entry.path.unlink()
            print(f"  DELETED [{entry.kbps} kbps]: {entry.path.name}")
            deleted += 1
        except OSError as exc:
            errors.append(f"{entry.path.name}: {exc}")
            print(f"  ERROR delete: {entry.path.name}: {exc}")

    for entry in to_move:
        target = _unique_dest(low_quality_dir, entry.path.name)
        if dry_run:
            print(f"  WOULD MOVE [{entry.kbps} kbps]: {entry.path.name}")
            moved += 1
            continue
        try:
            shutil.move(str(entry.path), str(target))
            print(f"  MOVED [{entry.kbps} kbps]: {entry.path.name}")
            moved += 1
        except OSError as exc:
            errors.append(f"{entry.path.name}: {exc}")
            print(f"  ERROR move: {entry.path.name}: {exc}")

    if not dry_run and moved:
        names = sorted(p.name for p in low_quality_dir.iterdir() if p.is_file())
        manifest = low_quality_dir / "low_quality_manifest.txt"
        lines = [
            "LowQuality — 192 kbps tier moved from Master (club floor >=256 preferred).",
            f"Location: {low_quality_dir}",
            f"Total: {len(names)}",
            "",
        ] + names
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Manifest: {manifest}")

    meta = master / "_meta"
    meta.mkdir(exist_ok=True)
    summary = meta / "quality_tier_cleanup.txt"
    if not dry_run:
        summary.write_text(
            "\n".join([
                f"Deleted (<= {delete_max_kbps} kbps): {deleted}",
                f"Moved to {low_quality_dir} (<= {move_max_kbps} kbps): {moved}",
                f"Remaining in Master: {kept}",
                f"Errors: {len(errors)}",
            ]) + "\n",
            encoding="utf-8",
        )

    print(f"\nDeleted: {deleted}  Moved: {moved}  Kept: {kept}  Errors: {len(errors)}")
    return deleted, moved, kept, errors


def audit_bitrates(
    master: Path,
    *,
    move_shazam: bool = False,
    tier_cleanup: bool = False,
    dry_run: bool = False,
) -> Path:
    """Run scan, write report, optionally move <=128 or apply quality tiers."""
    print("Scanning Master bitrates...")
    flagged, buckets, total = scan_master_bitrates(master)
    report = write_bitrate_report(master, flagged, buckets, total)
    print(f"Report: {report}")
    print(f"Flagged <=128 kbps: {len(flagged)} / {total}")

    if move_shazam:
        move_low_bitrate_to_shazam(master, flagged, dry_run=dry_run)
    if tier_cleanup:
        apply_quality_tiers(master, dry_run=dry_run)

    return report
