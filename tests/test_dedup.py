"""Tests for lib.dedup hashing and hash library cache."""

from pathlib import Path

from lib.dedup import dedup, get_md5, load_hash_lib, save_hash_lib


def test_get_md5_known_content(tmp_path):
    f = tmp_path / "track.bin"
    f.write_bytes(b"hello world")
    assert get_md5(str(f)) == "5eb63bbbe01eeed093cb22bb8f5acdc3"


def test_hash_lib_round_trip(tmp_path):
    meta = tmp_path / "_meta"
    meta.mkdir()
    lib = {"abc123": {"path": "/music/track.mp3", "bitrate": 320000}}

    save_hash_lib(meta, lib)
    loaded = load_hash_lib(meta)

    assert loaded == lib


def test_load_hash_lib_missing_file(tmp_path):
    assert load_hash_lib(tmp_path / "_meta") == {}


def test_dedup_full_flags_duplicate(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    content = b"dup-bytes"
    a = master / "a.mp3"
    b = master / "b.mp3"
    a.write_bytes(content)
    b.write_bytes(content)

    monkeypatch.setattr("lib.dedup.get_bitrate", lambda _p: 320000)
    to_delete = dedup(master, full=True)

    assert len(to_delete) == 1
    assert Path(to_delete[0]).name in {"a.mp3", "b.mp3"}
    assert (master / "_meta" / "hash_library.json").is_file()


def test_dedup_incremental_no_recent_files(tmp_path):
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    (master / "old.mp3").write_bytes(b"x")

    to_delete = dedup(master, full=False, days=0.000001)
    assert to_delete == []


def test_dedup_incremental_flags_recent_dupes(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    content = b"recent-dup"
    (master / "a.mp3").write_bytes(content)
    (master / "b.mp3").write_bytes(content)

    monkeypatch.setattr("lib.dedup.get_bitrate", lambda _p: 256000)
    to_delete = dedup(master, full=False, days=1)

    assert len(to_delete) == 1

