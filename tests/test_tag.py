"""Tests for lib.tag AcoustID tagging helpers."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lib.tag import (
    TagMatch,
    iter_untagged,
    needs_tags,
    pick_best_match,
    tag_files,
    write_tags,
)


def test_needs_tags_when_both_missing():
    assert needs_tags(None, None) is True


def test_needs_tags_when_partial():
    assert needs_tags("Artist", None) is True
    assert needs_tags(None, "Title") is True


def test_needs_tags_when_complete():
    assert needs_tags("Artist", "Title") is False


def test_pick_best_match_chooses_highest_score():
    results = [
        (0.55, "mbid-a", "Low", "Artist A"),
        (0.92, "mbid-b", "High", "Artist B"),
        (0.80, "mbid-c", "Mid", "Artist C"),
    ]
    match = pick_best_match(results)
    assert match is not None
    assert match.score == 0.92
    assert match.title == "High"
    assert match.artist == "Artist B"
    assert match.recording_id == "mbid-b"


def test_pick_best_match_rejects_below_threshold():
    results = [(0.40, "mbid-a", "Guess", "Artist")]
    assert pick_best_match(results) is None


def test_pick_best_match_requires_artist_and_title():
    results = [(0.95, "mbid-a", "", "Artist")]
    assert pick_best_match(results) is None


def test_iter_untagged_finds_files_without_tags(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    track = master / "mystery.mp3"
    track.write_bytes(b"fake")

    monkeypatch.setattr("lib.tag.read_tags", lambda _p: (None, None))

    found = list(iter_untagged(master))
    assert found == [track]


def test_iter_untagged_skips_tagged_files(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    tagged = master / "Artist - Title.mp3"
    tagged.write_bytes(b"fake")

    monkeypatch.setattr("lib.tag.read_tags", lambda p: ("Artist", "Title") if p == tagged else (None, None))

    assert list(iter_untagged(master)) == []


def test_write_tags_calls_mutagen(monkeypatch):
    captured = {}

    class FakeAudio:
        def __init__(self):
            self.data = {}

        def __setitem__(self, key, value):
            self.data[key] = value

        def save(self):
            captured["saved"] = True

    monkeypatch.setattr("lib.tag.MutagenFile", lambda _path, easy=True: FakeAudio())

    track = Path("track.mp3")
    assert write_tags(track, "Daft Punk", "Around the World") is True
    assert captured["saved"] is True


def test_tag_files_dry_run_does_not_write(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    track = master / "mystery.mp3"
    track.write_bytes(b"fake")

    monkeypatch.setattr("lib.tag.read_tags", lambda _p: (None, None))
    monkeypatch.setattr(
        "lib.tag.lookup_match",
        lambda _p, _k: TagMatch(0.95, "mbid", "Real Title", "Real Artist"),
    )

    write_mock = MagicMock(return_value=True)
    monkeypatch.setattr("lib.tag.write_tags", write_mock)

    tagged, skipped, failed = tag_files(
        master,
        api_key="test-key",
        dry_run=True,
    )

    assert tagged == 1
    assert skipped == 0
    assert failed == 0
    write_mock.assert_not_called()


def test_tag_files_writes_when_not_dry_run(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    track = master / "mystery.mp3"
    track.write_bytes(b"fake")

    monkeypatch.setattr("lib.tag.read_tags", lambda _p: (None, None))
    monkeypatch.setattr(
        "lib.tag.lookup_match",
        lambda _p, _k: TagMatch(0.95, "mbid", "Real Title", "Real Artist"),
    )

    write_mock = MagicMock(return_value=True)
    monkeypatch.setattr("lib.tag.write_tags", write_mock)

    tagged, skipped, failed = tag_files(
        master,
        api_key="test-key",
        dry_run=False,
    )

    assert tagged == 1
    write_mock.assert_called_once_with(track, "Real Artist", "Real Title")
