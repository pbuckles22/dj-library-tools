"""Tests for lib.relocate classification and move."""

from pathlib import Path

from lib.relocate import classify_for_relocate, relocate_from_master


def test_classify_wav():
    assert classify_for_relocate(Path("track.wav")) == "wav"


def test_classify_persian():
    assert classify_for_relocate(Path("Ashkin (www.Yazd-Music3.com) - Unknown.mp3")) == "persian"


def test_classify_comedy():
    assert classify_for_relocate(Path("Dave Chappelle - Titty Bar.mp3")) == "comedy"


def test_classify_dj_track_stays():
    assert classify_for_relocate(Path("50 Cent - Candy Shop.mp3")) is None


def test_classify_slipped_through_persian():
    assert classify_for_relocate(Path("Maziar Falahi - Unknown.mp3")) == "persian"
    assert classify_for_relocate(Path("Tataloo Ft. Tomeh - Dokhtare Rashti.mp3")) == "persian"


def test_classify_slipped_through_comedy():
    assert classify_for_relocate(Path("Disney - Unknown.mp3")) == "comedy"
    assert classify_for_relocate(Path("South Park - Timmy Rap.mp3")) == "comedy"
    assert classify_for_relocate(Path("Tv Show Friends - Joey Imitating Cha.mp3")) == "comedy"


def test_relocate_moves_matching_files(tmp_path):
    master = tmp_path / "Master"
    parent = tmp_path / "My Music"
    master.mkdir()
    parent.mkdir()

    wav = master / "mix.wav"
    wav.write_bytes(b"wav")
    dj = master / "Artist - Title.mp3"
    dj.write_bytes(b"mp3")

    moved, errors = relocate_from_master(master, dest=parent)

    assert errors == []
    assert len(moved) == 1
    assert (parent / "mix.wav").exists()
    assert not wav.exists()
    assert dj.parent == master


def test_relocate_dry_run_no_move(tmp_path):
    master = tmp_path / "Master"
    dest = tmp_path / "My Music"
    master.mkdir()
    f = master / "Ey IRAN.mp3"
    f.write_bytes(b"x")

    moved, _ = relocate_from_master(master, dest=dest, dry_run=True)

    assert len(moved) == 1
    assert f.exists()
    assert not (dest / f.name).exists()
