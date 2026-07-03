"""US-FREEZE-01 / US-FREEZE-02 — freeze lock and pipeline respect."""

from pathlib import Path

from lib.dedup import dedup
from lib.freeze import is_done, mark_all, mark_done, status, unmark
from lib.organize import organize
from lib.rename import rename_by_tags


def _master_with_track(tmp_path, name="track.mp3", data=b"audio-bytes"):
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    track = master / name
    track.write_bytes(data)
    return master, track


def test_us_freeze_01_mark_writes_manifest(tmp_path):
    """US-FREEZE-01: mark records path + sha256 in frozen.json."""
    master, track = _master_with_track(tmp_path)

    assert mark_done(track, master) is True
    assert is_done(track, master) is True

    manifest = master / "_meta" / "frozen.json"
    assert manifest.is_file()
    text = manifest.read_text(encoding="utf-8")
    assert track.name in text
    assert "sha256" in text


def test_us_freeze_01_unmark_removes_lock(tmp_path):
    """US-FREEZE-01: unmark clears freeze."""
    master, track = _master_with_track(tmp_path)
    mark_done(track, master)

    assert unmark(track, master) is True
    assert is_done(track, master) is False


def test_us_freeze_01_status_counts(tmp_path):
    """US-FREEZE-01: status reports frozen / total."""
    master, track = _master_with_track(tmp_path)
    (master / "other.mp3").write_bytes(b"other")

    assert status(master) == (0, 2)
    mark_done(track, master)
    assert status(master) == (1, 2)


def test_us_freeze_01_mark_all(tmp_path):
    """US-FREEZE-01: mark-all freezes every audio file in Master root."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / "a.mp3").write_bytes(b"a")
    (master / "b.flac").write_bytes(b"b")
    (master / "notes.txt").write_text("skip", encoding="utf-8")

    n = mark_all(master)
    assert n == 2
    frozen, total = status(master)
    assert frozen == 2
    assert total == 2


def test_us_freeze_02_rename_skips_frozen(tmp_path, monkeypatch):
    """US-FREEZE-02: rename leaves frozen files untouched."""
    master, track = _master_with_track(tmp_path, name="raw.mp3")
    mark_done(track, master)

    monkeypatch.setattr("lib.rename._get_tags", lambda _p: ("Artist", "Title"))
    renamed, skipped = rename_by_tags(master)

    assert renamed == 0
    assert track.exists()
    assert track.name == "raw.mp3"
    assert not (master / "Artist - Title.mp3").exists()


def test_us_freeze_02_organize_skips_frozen(tmp_path):
    """US-FREEZE-02: organize leaves frozen non-audio untouched."""
    master = tmp_path / "Master"
    master.mkdir()
    junk = master / "cover.jpg"
    junk.write_bytes(b"img")
    mark_done(junk, master)

    moved = organize(master)

    assert moved == 0
    assert junk.exists()
    assert not (master / "_meta" / "cover.jpg").exists()


def test_us_freeze_02_dedup_never_deletes_frozen(tmp_path, monkeypatch):
    """US-FREEZE-02: dedup never deletes a path-frozen track; unfrozen dupe is candidate."""
    import json

    master = tmp_path / "Master"
    master.mkdir()
    meta = master / "_meta"
    meta.mkdir()
    content = b"same-audio-content"
    frozen = master / "keeper.mp3"
    dupe = master / "dupe.mp3"
    frozen.write_bytes(content)
    dupe.write_bytes(content)
    # Path-only freeze (no content hash) so same-bytes dupe is not auto-frozen.
    (meta / "frozen.json").write_text(
        json.dumps(
            {
                "files": {
                    str(frozen.resolve()): {"sha256": "path-only", "name": frozen.name}
                },
                "hashes": {},
            }
        ),
        encoding="utf-8",
    )
    assert is_done(frozen, master)
    assert not is_done(dupe, master)

    monkeypatch.setattr("lib.dedup.get_bitrate", lambda _p: 320000)
    to_delete = dedup(master, full=True)

    assert frozen.exists()
    assert dupe.exists()  # delete script not auto-run by lib.dedup
    resolved = {Path(p).resolve() for p in to_delete}
    assert frozen.resolve() not in resolved
    assert dupe.resolve() in resolved
