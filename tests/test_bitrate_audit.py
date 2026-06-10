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
