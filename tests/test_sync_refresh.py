"""US-SYNC-01 / US-SYNC-02 — Serato primary sync and refresh behavior."""

from pathlib import Path

import pytest

from lib.sync import refresh_local, sync


def test_us_sync_02_sync_copies_master_to_destination(tmp_path, monkeypatch):
    """US-SYNC-02: sync copies Master audio into local mirror."""
    master = tmp_path / "Master"
    dest = tmp_path / "Serato"
    master.mkdir()
    track = master / "Artist - Title.mp3"
    track.write_bytes(b"track-bytes")

    # Avoid real rsync/robocopy; exercise public sync() with a direct copy shim.
    def fake_rsync(src, dst):
        for f in src.iterdir():
            if f.is_file():
                (dst / f.name).write_bytes(f.read_bytes())
        return 0

    monkeypatch.setattr("lib.sync._rsync", fake_rsync)
    monkeypatch.setattr("lib.sync._robocopy", fake_rsync)

    sync(master, dest, label="Serato")

    assert (dest / "Artist - Title.mp3").read_bytes() == b"track-bytes"


def test_us_sync_01_sync_rekordbox_path_same_behavior(tmp_path, monkeypatch):
    """US-SYNC-01: Rekordbox sync uses same copy path (opt-in target)."""
    master = tmp_path / "Master"
    dest = tmp_path / "Rekordbox"
    master.mkdir()
    (master / "a.mp3").write_bytes(b"a")

    def fake_rsync(src, dst):
        for f in src.iterdir():
            if f.is_file():
                (dst / f.name).write_bytes(f.read_bytes())
        return 0

    monkeypatch.setattr("lib.sync._rsync", fake_rsync)
    monkeypatch.setattr("lib.sync._robocopy", fake_rsync)

    sync(master, dest, label="Rekordbox")
    assert (dest / "a.mp3").exists()


def test_us_sync_02_refresh_copies_missing_tracks(tmp_path, monkeypatch):
    """US-SYNC-02: refresh copies missing tracks into local mirror."""
    master = tmp_path / "Master"
    local = tmp_path / "Latest Import"
    master.mkdir()
    local.mkdir()
    (master / "only-on-master.mp3").write_bytes(b"payload")
    (master / "already-local.mp3").write_bytes(b"shared")
    (local / "already-local.mp3").write_bytes(b"shared")

    # Skip rsync; exercise straggler copy path.
    monkeypatch.setattr(
        "lib.sync._rsync_pull",
        lambda *a, **k: 0,
    )
    monkeypatch.setattr(
        "lib.sync._robocopy_pull",
        lambda *a, **k: 0,
    )

    rc = refresh_local(master, local, retries=1)

    assert rc == 0
    assert (local / "only-on-master.mp3").read_bytes() == b"payload"
    assert (local / "already-local.mp3").exists()


def test_us_sync_02_refresh_missing_master_returns_1(tmp_path):
    """US-SYNC-02: refresh exits 1 when Master path missing."""
    rc = refresh_local(tmp_path / "nope", tmp_path / "local", retries=1)
    assert rc == 1


def test_us_sync_02_sync_serato_wrapper(tmp_path, monkeypatch, capsys):
    """US-SYNC-02: sync_serato labels destination."""
    from lib.sync import sync_serato

    master = tmp_path / "Master"
    serato = tmp_path / "Serato"
    master.mkdir()
    (master / "a.mp3").write_bytes(b"a")

    monkeypatch.setattr(
        "lib.sync._rsync",
        lambda src, dst: (dst.mkdir(parents=True, exist_ok=True) or 0),
    )
    monkeypatch.setattr("lib.sync._robocopy", lambda src, dst: 0)

    sync_serato(master, serato)
    assert "Serato" in capsys.readouterr().out


def test_us_sync_01_sync_rekordbox_wrapper(tmp_path, monkeypatch, capsys):
    """US-SYNC-01: sync_rekordbox labels destination."""
    from lib.sync import sync_rekordbox

    master = tmp_path / "Master"
    rb = tmp_path / "RB"
    master.mkdir()

    monkeypatch.setattr("lib.sync._rsync", lambda src, dst: 0)
    monkeypatch.setattr("lib.sync._robocopy", lambda src, dst: 0)

    sync_rekordbox(master, rb)
    assert "Rekordbox" in capsys.readouterr().out


def test_pull_new_dry_run(tmp_path, monkeypatch):
    from lib.sync import pull_new

    master = tmp_path / "Master"
    local = tmp_path / "local"
    master.mkdir()
    (master / "a.mp3").write_bytes(b"a")

    monkeypatch.setattr("lib.sync._rsync_pull", lambda *a, **k: 0)
    monkeypatch.setattr("lib.sync._robocopy_pull", lambda *a, **k: 0)

    pull_new(master, local, dry_run=True)
    assert not (local / "a.mp3").exists()


@pytest.mark.skipif(
    __import__("platform").system() == "Windows",
    reason="rsync path",
)
def test_rsync_pull_copies_audio(tmp_path):
    from lib.sync import _rsync_pull

    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "track.mp3").write_bytes(b"payload")

    rc = _rsync_pull(src, dst, prune=False, dry_run=False, quiet=True)
    assert rc == 0
    assert (dst / "track.mp3").read_bytes() == b"payload"


@pytest.mark.skipif(
    __import__("platform").system() == "Windows",
    reason="rsync path",
)
def test_pull_new_real_rsync(tmp_path):
    from lib.sync import pull_new

    master = tmp_path / "Master"
    local = tmp_path / "local"
    master.mkdir()
    (master / "a.mp3").write_bytes(b"a")

    pull_new(master, local, dry_run=False)
    assert (local / "a.mp3").read_bytes() == b"a"


def test_pull_new_missing_master_exits(tmp_path):
    from lib.sync import pull_new

    with pytest.raises(SystemExit) as exc:
        pull_new(tmp_path / "missing", tmp_path / "local")
    assert exc.value.code == 1


def test_refresh_reports_ghosts(tmp_path, monkeypatch):
    """Refresh returns 2 when master file is unreadable."""
    master = tmp_path / "Master"
    local = tmp_path / "local"
    master.mkdir()
    local.mkdir()
    ghost = master / "ghost.mp3"
    ghost.write_bytes(b"x")

    monkeypatch.setattr("lib.sync._rsync_pull", lambda *a, **k: 0)
    monkeypatch.setattr("lib.sync._robocopy_pull", lambda *a, **k: 0)
    monkeypatch.setattr("lib.sync._file_openable", lambda p: False)

    rc = refresh_local(master, local, retries=1)
    assert rc == 2


@pytest.mark.skipif(
    __import__("platform").system() == "Windows",
    reason="rsync path",
)
def test_sync_uses_rsync(tmp_path):
    master = tmp_path / "Master"
    dest = tmp_path / "dest"
    master.mkdir()
    (master / "a.mp3").write_bytes(b"a")

    sync(master, dest, label="test")
    assert (dest / "a.mp3").exists()


def test_sync_missing_source_exits(tmp_path):
    with pytest.raises(SystemExit) as exc:
        sync(tmp_path / "missing", tmp_path / "dest")
    assert exc.value.code == 1


@pytest.mark.skipif(
    __import__("platform").system() == "Windows",
    reason="rsync path",
)
def test_rsync_pull_dry_run(tmp_path):
    from lib.sync import _rsync_pull

    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "track.mp3").write_bytes(b"payload")

    rc = _rsync_pull(src, dst, prune=False, dry_run=True, quiet=False)
    assert rc == 0
    assert not (dst / "track.mp3").exists()



