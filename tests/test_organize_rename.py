"""US-PIPE-01 / US-FREEZE-02 — organize and rename public behavior."""

from lib.organize import organize
from lib.rename import rename_by_tags


def test_us_pipe_01_organize_moves_non_audio(tmp_path):
    """US-PIPE-01: organize moves non-audio from Master root to _meta."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / "track.mp3").write_bytes(b"audio")
    junk = master / "notes.txt"
    junk.write_text("x", encoding="utf-8")

    moved = organize(master)

    assert moved == 1
    assert (master / "track.mp3").exists()
    assert (master / "_meta" / "notes.txt").exists()
    assert not junk.exists()


def test_us_pipe_01_rename_unfrozen_track(tmp_path, monkeypatch):
    """US-PIPE-01: rename renames unfrozen files from tags and freezes result."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    track = master / "raw.mp3"
    track.write_bytes(b"audio")

    monkeypatch.setattr("lib.rename._get_tags", lambda _p: ("Artist", "Title"))

    renamed, skipped = rename_by_tags(master)

    assert renamed == 1
    assert skipped == 0
    dest = master / "Artist - Title.mp3"
    assert dest.exists()
    assert not track.exists()


def test_rename_skips_untagged(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    track = master / "raw.mp3"
    track.write_bytes(b"audio")

    monkeypatch.setattr("lib.rename._get_tags", lambda _p: (None, None))
    renamed, skipped = rename_by_tags(master)
    assert renamed == 0
    assert skipped == 1
    assert track.exists()


def test_rename_skips_when_dest_exists(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    track = master / "raw.mp3"
    track.write_bytes(b"audio")
    (master / "Artist - Title.mp3").write_bytes(b"other")

    monkeypatch.setattr("lib.rename._get_tags", lambda _p: ("Artist", "Title"))
    renamed, skipped = rename_by_tags(master)
    assert renamed == 0
    assert skipped >= 1
    assert track.exists()


def test_organize_days_filter(tmp_path):
    import os
    import time

    master = tmp_path / "Master"
    master.mkdir()
    old = master / "old.txt"
    old.write_text("old", encoding="utf-8")
    old_mtime = time.time() - 10 * 86400
    os.utime(old, (old_mtime, old_mtime))

    moved = organize(master, days=1)
    assert moved == 0
    assert old.exists()

