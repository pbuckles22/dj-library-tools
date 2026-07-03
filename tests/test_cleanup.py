"""US-CLEAN-01 — junk and empty dir cleanup under My Music."""

from lib.cleanup import clean_my_music


def test_us_clean_01_deletes_junk_and_empty_legacy_folder(tmp_path):
    """US-CLEAN-01: junk/artwork removed; empty legacy folder removed."""
    music = tmp_path / "My Music"
    master = music / "Master"
    meta = master / "_meta"
    legacy = music / "iTunes"
    master.mkdir(parents=True)
    meta.mkdir()
    legacy.mkdir()
    (legacy / "cover.jpg").write_bytes(b"img")
    (legacy / "readme.txt").write_text("junk", encoding="utf-8")
    (music / "NewMusic").mkdir()
    (music / "Shazam").mkdir()

    result = clean_my_music(music, dry_run=False)

    assert not legacy.exists()
    assert any("cover.jpg" in p for p in result["deleted_files"])
    assert "Master" in result["remaining"]
    assert "NewMusic" in result["remaining"]
    assert "Shazam" in result["remaining"]
    assert (meta / "cleanup_report.txt").is_file()


def test_us_clean_01_dry_run_keeps_files(tmp_path):
    """US-CLEAN-01: dry-run reports deletes without removing files."""
    music = tmp_path / "My Music"
    master = music / "Master"
    master.mkdir(parents=True)
    (master / "_meta").mkdir()
    legacy = music / "OldStuff"
    legacy.mkdir()
    junk = legacy / "notes.nfo"
    junk.write_text("x", encoding="utf-8")

    result = clean_my_music(music, dry_run=True)

    assert junk.exists()
    assert any("notes.nfo" in p for p in result["deleted_files"])
    assert not (master / "_meta" / "cleanup_report.txt").exists()


def test_us_clean_01_flags_legacy_with_audio(tmp_path):
    """US-CLEAN-01: legacy folders with audio are fishy, not auto-deleted."""
    music = tmp_path / "My Music"
    master = music / "Master"
    master.mkdir(parents=True)
    (master / "_meta").mkdir()
    legacy = music / "Personal"
    legacy.mkdir()
    (legacy / "keep.mp3").write_bytes(b"audio")

    result = clean_my_music(music, dry_run=False)

    assert legacy.exists()
    assert any("Personal" in f for f in result["fishy_dirs"])


def test_us_clean_01_cleans_master_subdirs(tmp_path):
    """US-CLEAN-01: junk inside Master subfolders is removed."""
    music = tmp_path / "My Music"
    master = music / "Master"
    album = master / "Album"
    album.mkdir(parents=True)
    (master / "_meta").mkdir()
    (album / "folder.jpg").write_bytes(b"img")
    (album / "track.mp3").write_bytes(b"audio")
    (music / "NewMusic").mkdir()
    (music / "Shazam").mkdir()

    result = clean_my_music(music, dry_run=False)

    assert not (album / "folder.jpg").exists()
    assert (album / "track.mp3").exists()
    assert any("Album" in f for f in result["fishy_dirs"])

