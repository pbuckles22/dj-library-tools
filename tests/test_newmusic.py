"""Tests for lib.newmusic ingest and staging clear."""

import shutil

from lib.dedup import get_md5, load_hash_lib, save_hash_lib
from lib.newmusic import clear_staging, ingest, iter_audio_files


def test_iter_audio_files_skips_meta(tmp_path):
    newmusic = tmp_path / "NewMusic"
    newmusic.mkdir()
    (newmusic / "_meta").mkdir()
    (newmusic / "track.mp3").write_bytes(b"audio")
    (newmusic / "_meta" / "hidden.mp3").write_bytes(b"hidden")
    sub = newmusic / "sub"
    sub.mkdir()
    (sub / "nested.flac").write_bytes(b"nested")

    paths = list(iter_audio_files(newmusic))
    assert len(paths) == 2
    names = {p.name for p in paths}
    assert names == {"track.mp3", "nested.flac"}


def test_ingest_copies_new_files(tmp_path):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    newmusic.mkdir()
    (master / "_meta").mkdir()

    src = newmusic / "fresh.mp3"
    src.write_bytes(b"new track bytes")

    copied, skipped = ingest(master, newmusic)

    assert copied == 1
    assert skipped == 0
    assert (master / "fresh.mp3").read_bytes() == b"new track bytes"
    assert src.exists()


def test_ingest_skips_when_master_has_same_content(tmp_path):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    newmusic.mkdir()

    content = b"duplicate content"
    (master / "already.mp3").write_bytes(content)
    (newmusic / "staging.mp3").write_bytes(content)

    copied, skipped = ingest(master, newmusic)

    assert copied == 0
    assert skipped == 1
    assert len(list(master.iterdir())) == 1


def test_clear_staging_deletes_validated_files(tmp_path):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    meta = master / "_meta"
    master.mkdir()
    meta.mkdir()
    newmusic.mkdir()

    content = b"shared track"
    master_file = master / "Artist - Title.mp3"
    master_file.write_bytes(content)
    staging = newmusic / "download.mp3"
    staging.write_bytes(content)

    md5 = get_md5(str(master_file))
    save_hash_lib(meta, {md5: {"path": str(master_file), "bitrate": 320000}})

    deleted, kept, failures = clear_staging(master, newmusic)

    assert deleted == 1
    assert kept == 0
    assert failures == []
    assert not staging.exists()
    assert master_file.exists()


def test_clear_staging_keeps_unmatched_files(tmp_path):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    meta = master / "_meta"
    master.mkdir()
    meta.mkdir()
    newmusic.mkdir()

    (master / "in-master.mp3").write_bytes(b"master only")
    orphan = newmusic / "not-ingested.mp3"
    orphan.write_bytes(b"never copied")

    deleted, kept, failures = clear_staging(master, newmusic)

    assert deleted == 0
    assert kept == 1
    assert failures == []
    assert orphan.exists()


def test_ingest_skips_via_hash_lib_without_scanning_master(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    meta = master / "_meta"
    master.mkdir()
    meta.mkdir()
    newmusic.mkdir()

    content = b"library hit"
    (master / "On Disk.mp3").write_bytes(content)
    (newmusic / "staging.mp3").write_bytes(content)

    md5 = get_md5(str(master / "On Disk.mp3"))
    save_hash_lib(meta, {md5: {"path": str(master / "On Disk.mp3"), "bitrate": 320000}})

    scanned: list[str] = []
    real_md5 = get_md5

    def track_md5(path):
        scanned.append(path)
        return real_md5(path)

    monkeypatch.setattr("lib.newmusic.get_md5", track_md5)

    copied, skipped = ingest(master, newmusic)

    assert copied == 0
    assert skipped == 1
    assert str(master / "On Disk.mp3") not in scanned


def test_ingest_unique_dest_on_name_collision(tmp_path):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    newmusic.mkdir()
    (master / "track.mp3").write_bytes(b"existing")
    (newmusic / "track.mp3").write_bytes(b"incoming-different")

    copied, skipped = ingest(master, newmusic)

    assert copied == 1
    assert skipped == 0
    assert (master / "track (1).mp3").read_bytes() == b"incoming-different"


def test_clear_staging_prunes_empty_subdirs(tmp_path):
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    (master / "_meta").mkdir()
    sub = newmusic / "empty-nested"
    sub.mkdir(parents=True)
    content = b"shared"
    master_file = master / "a.mp3"
    master_file.write_bytes(content)
    staging = newmusic / "a.mp3"
    staging.write_bytes(content)
    md5 = get_md5(str(master_file))
    save_hash_lib(master / "_meta", {md5: {"path": str(master_file), "bitrate": 320000}})

    clear_staging(master, newmusic)
    assert not sub.exists()


def test_clear_staging_uses_hash_lib_then_falls_back_to_master_scan(tmp_path):

    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    newmusic.mkdir()

    content = b"renamed but same bytes"
    master_file = master / "Renamed - Track.mp3"
    master_file.write_bytes(content)
    staging = newmusic / "original.mp3"
    staging.write_bytes(content)

    deleted, kept, failures = clear_staging(master, newmusic, hash_lib={})

    assert deleted == 1
    assert kept == 0
    assert failures == []
    assert not staging.exists()
