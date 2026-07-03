"""CLI command coverage for requirement-mapped entry points."""

from types import SimpleNamespace

import pytest

import dj


@pytest.fixture
def master_env(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    (master / "track.mp3").write_bytes(b"audio")
    newmusic = tmp_path / "NewMusic"
    newmusic.mkdir()
    serato = tmp_path / "serato"
    rb = tmp_path / "rb"

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)
    monkeypatch.setattr(dj.cfg, "get_newmusic", lambda: newmusic)
    monkeypatch.setattr(dj.cfg, "get_serato", lambda: serato)
    monkeypatch.setattr(dj.cfg, "get_rekordbox", lambda: rb)
    monkeypatch.setattr(dj.cfg, "get_acoustid_key", lambda: "")
    monkeypatch.setattr(dj.cfg, "require_acoustid_key", lambda: "key")

    return master, newmusic, serato, rb


def test_cmd_organize(master_env):
    master, *_ = master_env
    (master / "notes.txt").write_text("x", encoding="utf-8")
    dj.cmd_organize(SimpleNamespace(full=True, days=1))
    assert (master / "_meta" / "notes.txt").exists()


def test_cmd_rename(master_env, monkeypatch):
    master, *_ = master_env
    monkeypatch.setattr(dj.rename_mod, "rename_by_tags", lambda *a, **k: (0, 0))
    dj.cmd_rename(SimpleNamespace(full=True, days=1))


def test_cmd_dedup(master_env, monkeypatch):
    monkeypatch.setattr(dj.dedup_mod, "dedup", lambda *a, **k: [])
    dj.cmd_dedup(SimpleNamespace(full=True, days=1))


def test_cmd_sync_serato(master_env, monkeypatch):
    calls = []
    monkeypatch.setattr(dj.sync_mod, "sync_serato", lambda *a: calls.append("s"))
    monkeypatch.setattr(dj.sync_mod, "sync_rekordbox", lambda *a: calls.append("r"))
    dj.cmd_sync(SimpleNamespace(target="serato"))
    assert calls == ["s"]


def test_cmd_sync_rekordbox(master_env, monkeypatch):
    calls = []
    monkeypatch.setattr(dj.sync_mod, "sync_serato", lambda *a: calls.append("s"))
    monkeypatch.setattr(dj.sync_mod, "sync_rekordbox", lambda *a: calls.append("r"))
    dj.cmd_sync(SimpleNamespace(target="rekordbox"))
    assert calls == ["r"]


def test_cmd_sync_all(master_env, monkeypatch):
    calls = []
    monkeypatch.setattr(dj.sync_mod, "sync_serato", lambda *a: calls.append("s"))
    monkeypatch.setattr(dj.sync_mod, "sync_rekordbox", lambda *a: calls.append("r"))
    dj.cmd_sync(SimpleNamespace(target="all"))
    assert calls == ["s", "r"]


def test_cmd_sync_unknown_exits(master_env):
    with pytest.raises(SystemExit) as exc:
        dj.cmd_sync(SimpleNamespace(target="nope"))
    assert exc.value.code == 1


def test_cmd_pull(master_env, monkeypatch):
    called = {}
    monkeypatch.setattr(
        dj.sync_mod,
        "pull_new",
        lambda m, r, prune=False, dry_run=False: called.update(
            prune=prune, dry_run=dry_run
        ),
    )
    dj.cmd_pull(SimpleNamespace(prune=True, dry_run=True))
    assert called == {"prune": True, "dry_run": True}


def test_cmd_refresh(master_env, monkeypatch):
    monkeypatch.setattr(dj.sync_mod, "refresh_local", lambda *a, **k: 0)
    with pytest.raises(SystemExit) as exc:
        dj.cmd_refresh(SimpleNamespace(target="serato", retries=1))
    assert exc.value.code == 0


def test_cmd_freeze_mark_all(master_env, capsys):
    dj.cmd_freeze(SimpleNamespace(freeze_action="mark-all", paths=None))
    assert "Marked" in capsys.readouterr().out


def test_cmd_audit(master_env, monkeypatch):
    monkeypatch.setattr(dj.bitrate_mod, "audit_bitrates", lambda *a, **k: None)
    dj.cmd_audit(
        SimpleNamespace(move_shazam=False, tier_cleanup=False, dry_run=True)
    )


def test_cmd_cleanup(master_env, monkeypatch):
    monkeypatch.setattr(dj.cleanup_mod, "clean_my_music", lambda *a, **k: {})
    dj.cmd_cleanup(SimpleNamespace(dry_run=True))


def test_cmd_shazam_stage(master_env, monkeypatch):
    monkeypatch.setattr(dj.shazam_mod, "stage_shazam_queue", lambda *a, **k: (0, 0))
    monkeypatch.setattr(dj.shazam_mod, "default_shazam_dir", lambda m: m.parent / "Shazam")
    dj.cmd_shazam(SimpleNamespace(action="stage", dry_run=True))


def test_cmd_shazam_unknown(master_env):
    with pytest.raises(SystemExit):
        dj.cmd_shazam(SimpleNamespace(action="nope", dry_run=False))


def test_cmd_relocate(master_env, monkeypatch, capsys):
    monkeypatch.setattr(
        dj.relocate_mod, "relocate_from_master", lambda *a, **k: ([], [])
    )
    dj.cmd_relocate(SimpleNamespace(dry_run=True))
    assert "DRY RUN" in capsys.readouterr().out


def test_cmd_tag(master_env, monkeypatch):
    monkeypatch.setattr(dj.tag_mod, "tag_files", lambda *a, **k: (0, 0, 0))
    dj.cmd_tag(SimpleNamespace(full=True, days=1, dry_run=True, limit=None))


def test_cmd_compare_tags(master_env, monkeypatch, capsys):
    monkeypatch.setattr(
        dj.compare_mod, "compare_tags", lambda *a, **k: ([(1, 2)], [])
    )
    dj.cmd_compare(SimpleNamespace(dirs=["/old"], md5=False))
    assert "In Master" in capsys.readouterr().out


def test_cmd_compare_md5(master_env, monkeypatch):
    monkeypatch.setattr(dj.compare_mod, "compare_md5", lambda *a, **k: ([], []))
    dj.cmd_compare(SimpleNamespace(dirs=["/old"], md5=True))


def test_cmd_compare_no_dirs(master_env):
    with pytest.raises(SystemExit):
        dj.cmd_compare(SimpleNamespace(dirs=[], md5=False))
