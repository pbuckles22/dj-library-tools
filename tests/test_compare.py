"""US-OLD-02 — compare old folders to Master."""

import pytest

from lib.compare import (
    _key_from_file,
    _normalize,
    collect_audio_files,
    compare_md5,
    compare_tags,
)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Daft Punk", "daft punk"),
        ("  Around   The   World  ", "around the world"),
        ("Rock & Roll (Live)", "rock roll live"),
        ("AC/DC - T.N.T.", "ac dc t n t"),
    ],
)
def test_normalize(raw, expected):
    assert _normalize(raw) == expected


def test_collect_audio_files_finds_supported_extensions(tmp_path):
    music = tmp_path / "music"
    music.mkdir()
    (music / "track.mp3").write_bytes(b"mp3")
    (music / "nested" / "track.flac").parent.mkdir()
    (music / "nested" / "track.flac").write_bytes(b"flac")
    (music / "readme.txt").write_text("skip")
    (music / "cover.jpg").write_bytes(b"jpg")

    found = collect_audio_files([music])
    assert sorted(p.name for p in found) == ["track.flac", "track.mp3"]


def test_collect_audio_files_skips_missing_directories(tmp_path, capsys):
    found = collect_audio_files([tmp_path / "missing"])
    assert found == []
    assert "not a directory" in capsys.readouterr().out


def test_key_from_file_parses_filename_when_no_tags(tmp_path):
    track = tmp_path / "Daft Punk - Around the World.mp3"
    track.write_bytes(b"fake")

    artist, title = _key_from_file(track)
    assert artist == "daft punk"
    assert title == "around the world"


def test_key_from_file_strips_leading_track_number(tmp_path):
    track = tmp_path / "01 - Artist - Title.mp3"
    track.write_bytes(b"fake")

    artist, title = _key_from_file(track)
    assert artist == "artist"
    assert title == "title"


def test_us_old_02_compare_tags_splits_in_and_not_in_master(tmp_path, monkeypatch):
    """US-OLD-02: tag compare reports in-Master vs not-in-Master."""
    master = tmp_path / "Master"
    old = tmp_path / "Old"
    out = tmp_path / "out"
    master.mkdir()
    old.mkdir()
    out.mkdir()
    (master / "Artist - Known.mp3").write_bytes(b"m")
    (old / "Artist - Known.mp3").write_bytes(b"o1")
    (old / "Artist - Unique.mp3").write_bytes(b"o2")

    monkeypatch.setattr("lib.compare._OUT_DIR", out)

    in_m, not_in = compare_tags(master, [old])

    assert len(in_m) == 1
    assert len(not_in) == 1
    assert not_in[0].name == "Artist - Unique.mp3"
    assert (out / "tag_compare_in_master.txt").is_file()
    assert (out / "tag_compare_not_in_master.txt").is_file()
    assert (out / "tag_compare_delete.sh").is_file()


def test_us_old_02_compare_md5_uses_content(tmp_path, monkeypatch):
    """US-OLD-02: MD5 compare matches by content hash."""
    master = tmp_path / "Master"
    old = tmp_path / "Old"
    out = tmp_path / "out"
    master.mkdir()
    (master / "_meta").mkdir()
    old.mkdir()
    out.mkdir()
    shared = b"same-bytes"
    (master / "a.mp3").write_bytes(shared)
    (old / "copy.mp3").write_bytes(shared)
    (old / "other.mp3").write_bytes(b"different")

    monkeypatch.setattr("lib.compare._OUT_DIR", out)

    in_m, not_in = compare_md5(master, [old])

    assert len(in_m) == 1
    assert in_m[0].name == "copy.mp3"
    assert len(not_in) == 1
    assert not_in[0].name == "other.mp3"

