"""US-PIPE-01 / US-SYNC-02 — CLI flags and defaults (blackbox via argparse)."""

from types import SimpleNamespace

import dj


def test_us_sync_02_refresh_defaults_to_serato():
    """US-SYNC-02: refresh --target defaults to serato."""
    parser = dj.build_parser()
    args = parser.parse_args(["refresh"])
    assert args.target == "serato"


def test_us_pipe_01_pipeline_flags_default_include_both_syncs():
    """US-PIPE-01: pipeline defaults include Serato and Rekordbox unless skipped."""
    parser = dj.build_parser()
    args = parser.parse_args(["pipeline", "--no-tag"])
    assert args.no_serato is False
    assert args.no_rekordbox is False


def test_us_pipe_01_pipeline_no_rekordbox_flag():
    """US-PIPE-01: --no-rekordbox skips Rekordbox only."""
    parser = dj.build_parser()
    args = parser.parse_args(["pipeline", "--no-rekordbox"])
    assert args.no_rekordbox is True
    assert args.no_serato is False


def test_us_pipe_01_pipeline_no_serato_flag():
    """US-PIPE-01: --no-serato skips Serato."""
    parser = dj.build_parser()
    args = parser.parse_args(["pipeline", "--no-serato"])
    assert args.no_serato is True


def test_us_pipe_01_pipeline_skips_sync_targets(tmp_path, monkeypatch, capsys):
    """US-PIPE-01: pipeline honors --no-serato and --no-rekordbox."""
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    (master / "_meta").mkdir()
    newmusic.mkdir()

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)
    monkeypatch.setattr(dj.cfg, "get_newmusic", lambda: newmusic)
    monkeypatch.setattr(dj.cfg, "get_acoustid_key", lambda: "")
    monkeypatch.setattr(dj.cfg, "get_serato", lambda: tmp_path / "serato")
    monkeypatch.setattr(dj.cfg, "get_rekordbox", lambda: tmp_path / "rb")

    calls = []
    monkeypatch.setattr(dj.staging_mod, "import_new_music", lambda *a: 0)
    monkeypatch.setattr(dj.newmusic_mod, "ingest", lambda *a, **k: (0, 0))
    monkeypatch.setattr(dj.organize_mod, "organize", lambda *a, **k: 0)
    monkeypatch.setattr(dj.rename_mod, "rename_by_tags", lambda *a, **k: (0, 0))
    monkeypatch.setattr(dj.dedup_mod, "dedup", lambda *a, **k: [])
    monkeypatch.setattr(dj.dedup_mod, "load_hash_lib", lambda *a, **k: {})
    monkeypatch.setattr(dj.newmusic_mod, "clear_staging", lambda *a, **k: (0, 0, []))
    monkeypatch.setattr(
        dj.sync_mod, "sync_serato", lambda *a, **k: calls.append("serato")
    )
    monkeypatch.setattr(
        dj.sync_mod, "sync_rekordbox", lambda *a, **k: calls.append("rekordbox")
    )

    args = SimpleNamespace(
        full=True,
        days=1,
        from_step="import",
        no_serato=True,
        no_rekordbox=True,
        no_newmusic=False,
        no_tag=True,
    )
    dj.cmd_pipeline(args)

    assert calls == []
    out = capsys.readouterr().out
    assert "Serato sync skipped" in out
    assert "Rekordbox sync skipped" in out


def test_us_sync_02_pipeline_runs_serato_by_default(tmp_path, monkeypatch):
    """US-SYNC-02: pipeline includes Serato unless --no-serato."""
    master = tmp_path / "Master"
    newmusic = tmp_path / "NewMusic"
    master.mkdir()
    (master / "_meta").mkdir()
    newmusic.mkdir()

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)
    monkeypatch.setattr(dj.cfg, "get_newmusic", lambda: newmusic)
    monkeypatch.setattr(dj.cfg, "get_acoustid_key", lambda: "")
    monkeypatch.setattr(dj.cfg, "get_serato", lambda: tmp_path / "serato")
    monkeypatch.setattr(dj.cfg, "get_rekordbox", lambda: tmp_path / "rb")

    calls = []
    monkeypatch.setattr(dj.staging_mod, "import_new_music", lambda *a: 0)
    monkeypatch.setattr(dj.newmusic_mod, "ingest", lambda *a, **k: (0, 0))
    monkeypatch.setattr(dj.organize_mod, "organize", lambda *a, **k: 0)
    monkeypatch.setattr(dj.rename_mod, "rename_by_tags", lambda *a, **k: (0, 0))
    monkeypatch.setattr(dj.dedup_mod, "dedup", lambda *a, **k: [])
    monkeypatch.setattr(dj.dedup_mod, "load_hash_lib", lambda *a, **k: {})
    monkeypatch.setattr(dj.newmusic_mod, "clear_staging", lambda *a, **k: (0, 0, []))
    monkeypatch.setattr(
        dj.sync_mod, "sync_serato", lambda *a, **k: calls.append("serato")
    )
    monkeypatch.setattr(
        dj.sync_mod, "sync_rekordbox", lambda *a, **k: calls.append("rekordbox")
    )

    args = SimpleNamespace(
        full=True,
        days=1,
        from_step="sync",
        no_serato=False,
        no_rekordbox=True,
        no_newmusic=True,
        no_tag=True,
    )
    dj.cmd_pipeline(args)

    assert calls == ["serato"]
