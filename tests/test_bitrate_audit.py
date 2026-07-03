"""Tests for lib.bitrate_audit tier logic."""

from lib.bitrate_audit import _tier


def test_tier_le96():
    assert _tier(64) == "<=96"
    assert _tier(96) == "<=96"


def test_tier_128():
    assert _tier(128) == "<=128"
    assert _tier(100) == "<=128"


def test_tier_above_not_flagged():
    assert _tier(192) is None
    assert _tier(320) is None


def test_quality_label_buckets():
    from lib.bitrate_audit import _quality_label

    assert _quality_label(160) == "160"
    assert _quality_label(192) == "192"
    assert _quality_label(256) == "256"


def test_apply_quality_tiers(tmp_path, monkeypatch):
    from lib.bitrate_audit import apply_quality_tiers

    master = tmp_path / "Master"
    low = tmp_path / "LowQuality"
    master.mkdir()

    delete_me = master / "low.mp3"
    move_me = master / "mid.mp3"
    keep_me = master / "high.mp3"
    delete_me.write_bytes(b"a")
    move_me.write_bytes(b"b")
    keep_me.write_bytes(b"c")

    kbps = {str(delete_me): 160, str(move_me): 192, str(keep_me): 320}
    monkeypatch.setattr("lib.bitrate_audit.get_bitrate", lambda p: kbps[str(p)] * 1000)

    deleted, moved, kept, errors = apply_quality_tiers(
        master, low_quality_dir=low, dry_run=False
    )

    assert errors == []
    assert deleted == 1
    assert moved == 1
    assert kept == 1
    assert not delete_me.exists()
    assert (low / "mid.mp3").exists()
    assert keep_me.exists()


def test_us_qual_01_audit_bitrates_tier_cleanup(tmp_path, monkeypatch):
    """US-QUAL-01: audit_bitrates --tier-cleanup applies quality tiers."""
    from lib.bitrate_audit import audit_bitrates

    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    low = master / "low.mp3"
    mid = master / "mid.mp3"
    high = master / "high.mp3"
    low.write_bytes(b"a")
    mid.write_bytes(b"b")
    high.write_bytes(b"c")

    kbps = {str(low): 128, str(mid): 192, str(high): 320}
    monkeypatch.setattr("lib.bitrate_audit.get_bitrate", lambda p: kbps[str(p)] * 1000)

    report = audit_bitrates(master, tier_cleanup=True, dry_run=False)

    assert report.is_file()
    assert not low.exists()
    assert (tmp_path / "LowQuality" / "mid.mp3").exists()
    assert high.exists()


def test_us_qual_01_move_low_bitrate_to_shazam(tmp_path, monkeypatch):
    """US-QUAL-01: <=128 kbps can move to Shazam."""
    from lib.bitrate_audit import BitrateEntry, move_low_bitrate_to_shazam

    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    track = master / "weak.mp3"
    track.write_bytes(b"x")

    flagged = [BitrateEntry(path=track, kbps=128, tier="<=128")]
    moved, errors = move_low_bitrate_to_shazam(master, flagged, dry_run=False)

    assert errors == []
    assert len(moved) == 1
    assert (tmp_path / "Shazam" / "weak.mp3").exists()
    assert not track.exists()
