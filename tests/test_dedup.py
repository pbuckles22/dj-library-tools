"""Tests for lib.dedup hashing and hash library cache."""

from lib.dedup import get_md5, load_hash_lib, save_hash_lib


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
