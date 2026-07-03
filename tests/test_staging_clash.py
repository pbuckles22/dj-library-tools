"""US-CLASH-01 — incoming NewMusic loses on clash; Master stays sacred."""

from lib.freeze import mark_done
from lib.staging import import_new_music


def _setup(tmp_path):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    (master / "_meta").mkdir()
    newmusic.mkdir()
    return master, newmusic


def test_us_clash_01_filename_exists_deletes_incoming(tmp_path):
    """US-CLASH-01: filename in Master → delete incoming, keep Master."""
    master, newmusic = _setup(tmp_path)
    master_file = master / "same-name.mp3"
    master_file.write_bytes(b"master-content")
    incoming = newmusic / "same-name.mp3"
    incoming.write_bytes(b"incoming-content")

    moved = import_new_music(newmusic, master)

    assert moved == 0
    assert master_file.read_bytes() == b"master-content"
    assert not incoming.exists()
    log = (master / "_meta" / "rejected_imports.log").read_text(encoding="utf-8")
    assert "same-name.mp3" in log
    assert "filename exists" in log


def test_us_clash_01_md5_matches_frozen_deletes_incoming(tmp_path):
    """US-CLASH-01: MD5 matches frozen Master track → delete incoming."""
    master, newmusic = _setup(tmp_path)
    content = b"identical-audio-payload"
    frozen = master / "published.mp3"
    frozen.write_bytes(content)
    mark_done(frozen, master)
    incoming = newmusic / "different-name.mp3"
    incoming.write_bytes(content)

    moved = import_new_music(newmusic, master)

    assert moved == 0
    assert frozen.exists()
    assert frozen.read_bytes() == content
    assert not incoming.exists()
    log = (master / "_meta" / "rejected_imports.log").read_text(encoding="utf-8")
    assert "MD5 matches frozen" in log


def test_us_clash_01_tag_matches_frozen_deletes_incoming(tmp_path, monkeypatch):
    """US-CLASH-01: Artist+Title matches frozen Master track → delete incoming."""
    master, newmusic = _setup(tmp_path)
    frozen = master / "old-name.mp3"
    frozen.write_bytes(b"frozen-bytes")
    mark_done(frozen, master)
    incoming = newmusic / "new-name.mp3"
    incoming.write_bytes(b"incoming-bytes")

    def fake_tags(path):
        if path.name == "old-name.mp3":
            return ("Artist", "Title")
        if path.name == "new-name.mp3":
            return ("Artist", "Title")
        return (None, None)

    monkeypatch.setattr("lib.staging._get_tags", fake_tags)

    moved = import_new_music(newmusic, master)

    assert moved == 0
    assert frozen.exists()
    assert not incoming.exists()
    log = (master / "_meta" / "rejected_imports.log").read_text(encoding="utf-8")
    assert "Artist+Title matches frozen" in log


def test_us_clash_01_non_clash_moves_into_master(tmp_path):
    """US-CLASH-01: non-clashing files move into Master."""
    master, newmusic = _setup(tmp_path)
    incoming = newmusic / "fresh.mp3"
    incoming.write_bytes(b"brand-new")

    moved = import_new_music(newmusic, master)

    assert moved == 1
    dest = master / "fresh.mp3"
    assert dest.exists()
    assert dest.read_bytes() == b"brand-new"
    assert not incoming.exists()
    assert not (master / "_meta" / "rejected_imports.log").exists()
