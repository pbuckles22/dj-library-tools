"""Tests for lib.compare helpers."""

import pytest

from lib.compare import _key_from_file, _normalize, collect_audio_files


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
