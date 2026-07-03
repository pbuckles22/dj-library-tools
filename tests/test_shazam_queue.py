"""Tests for lib.shazam_queue staging."""

from pathlib import Path

from lib.shazam_queue import read_queue_names, stage_shazam_queue


def test_read_queue_names_from_file(tmp_path):
    master = tmp_path / "Master"
    meta = master / "_meta"
    meta.mkdir(parents=True)
    (meta / "shazam_queue.txt").write_text(
        "Shazam queue — test\nTotal: 2\n\nTrack A.mp3\nTrack B.mp3\n",
        encoding="utf-8",
    )
    assert read_queue_names(master) == ["Track A.mp3", "Track B.mp3"]


def test_stage_moves_queue_files(tmp_path):
    music = tmp_path / "My Music"
    master = music / "Master"
    shazam = music / "Shazam"
    meta = master / "_meta"
    meta.mkdir(parents=True)

    (meta / "shazam_queue.txt").write_text("Total: 1\n\nneeds-tag.mp3\n", encoding="utf-8")
    track = master / "needs-tag.mp3"
    track.write_bytes(b"mp3")
    (master / "keep.mp3").write_bytes(b"other")

    moved, errors = stage_shazam_queue(master, dest=shazam)

    assert errors == []
    assert len(moved) == 1
    assert (shazam / "needs-tag.mp3").exists()
    assert not track.exists()
    assert (master / "keep.mp3").exists()


def test_stage_dry_run_and_missing(tmp_path):
    master = tmp_path / "Master"
    meta = master / "_meta"
    meta.mkdir(parents=True)
    (meta / "shazam_queue.txt").write_text(
        "Total: 2\n\nneeds-tag.mp3\nmissing.mp3\n", encoding="utf-8"
    )
    track = master / "needs-tag.mp3"
    track.write_bytes(b"mp3")

    moved, errors = stage_shazam_queue(master, dry_run=True)

    assert errors == []
    assert len(moved) == 1
    assert track.exists()


def test_stage_unique_dest(tmp_path):
    master = tmp_path / "Master"
    dest = tmp_path / "Shazam"
    meta = master / "_meta"
    meta.mkdir(parents=True)
    dest.mkdir()
    (meta / "shazam_queue.txt").write_text("Total: 1\n\nsong.mp3\n", encoding="utf-8")
    (master / "song.mp3").write_bytes(b"new")
    (dest / "song.mp3").write_bytes(b"old")

    moved, errors = stage_shazam_queue(master, dest=dest)
    assert errors == []
    assert (dest / "song (1).mp3").exists()

