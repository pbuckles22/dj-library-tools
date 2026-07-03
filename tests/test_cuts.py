"""US-CUT-01 / US-CUT-02 — standardize intro aliases and narrow cut dedupe."""

from pathlib import Path

import pytest

from lib.cuts import (
    CANONICAL_INTRO_CLEAN,
    build_canonical_filename,
    classify_cut,
    dedupe_cuts,
    is_intro_clean_alias,
    parse_track_filename,
    standardize_cuts,
)
from lib.dedup import AUDIO_EXTENSIONS


def test_is_intro_clean_alias():
    assert is_intro_clean_alias("Intro - Clean") is True
    assert is_intro_clean_alias("DJcity Intro - Clean") is True
    assert is_intro_clean_alias("Intro Clean") is False
    assert is_intro_clean_alias("Clean") is False


def test_build_canonical_filename_intro():
    name = build_canonical_filename(
        "2Pac", "California Love", ["Intro - Clean"], ".mp3"
    )
    assert name == f"2Pac - California Love ({CANONICAL_INTRO_CLEAN}).mp3"


def test_classify_cut_families():
    assert classify_cut(["Intro - Clean"]) == "intro_clean"
    assert classify_cut(["Clean"]) == "clean"
    assert classify_cut([]) == "plain"


def test_standardize_renames_intro_alias(tmp_path):
    """US-CUT-01: apply renames intro aliases to (Intro Clean)."""
    master = tmp_path / "Master"
    master.mkdir()
    src = master / "Artist - Song (Intro - Clean).mp3"
    src.write_bytes(b"fake")

    renamed, skipped = standardize_cuts(master, dry_run=False)

    assert renamed == 1
    assert skipped == 0
    dest = master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3"
    assert dest.exists()
    assert not src.exists()


def test_standardize_skips_already_canonical(tmp_path):
    """US-CUT-01: already-canonical names are skipped."""
    master = tmp_path / "Master"
    master.mkdir()
    f = master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3"
    f.write_bytes(b"fake")

    renamed, skipped = standardize_cuts(master, dry_run=False)

    assert renamed == 0
    assert skipped == 1


def test_standardize_dry_run_no_change(tmp_path):
    """US-CUT-01: dry-run reports renames without changing files."""
    master = tmp_path / "Master"
    master.mkdir()
    src = master / "Artist - Song (DJcity Intro - Clean).mp3"
    src.write_bytes(b"fake")

    renamed, skipped = standardize_cuts(master, dry_run=True)

    assert renamed == 1
    assert skipped == 0
    assert src.exists()


def test_dedupe_narrow_dry_run_keeps_files(tmp_path):
    """US-CUT-02: dry-run writes report and keeps files."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3").write_bytes(b"a")
    (master / "Artist - Song (Clean).mp3").write_bytes(b"b")

    deleted, kept, report = dedupe_cuts(master, mode="narrow", dry_run=True)

    assert deleted == 1
    assert kept == 0  # failed deletes
    audio = [p for p in master.iterdir() if p.suffix.lower() in AUDIO_EXTENSIONS]
    assert len(audio) == 2
    assert report.exists()
    assert report.name == "cut_dedup_report.txt"
    assert report.parent.name == "_meta"


def test_dedupe_narrow_apply_deletes_extras(tmp_path):
    """US-CUT-02: apply deletes extras when Intro Clean family exists."""
    master = tmp_path / "Master"
    master.mkdir()
    keeper = master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3"
    extra = master / "Artist - Song (Clean).mp3"
    keeper.write_bytes(b"a")
    extra.write_bytes(b"b")

    deleted, kept, _ = dedupe_cuts(master, mode="narrow", dry_run=False)

    assert deleted == 1
    assert kept == 0
    assert keeper.exists()
    assert not extra.exists()


def test_dedupe_narrow_no_intro_skips_group(tmp_path):
    """US-CUT-02: groups without Intro Clean are left alone."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / "Artist - Song (Clean).mp3").write_bytes(b"a")
    (master / "Artist - Song (Clean Extended).mp3").write_bytes(b"b")

    deleted, kept, _ = dedupe_cuts(master, mode="narrow", dry_run=False)

    assert deleted == 0
    assert kept == 0
    assert len([p for p in master.iterdir() if p.suffix in AUDIO_EXTENSIONS]) == 2
