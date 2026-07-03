"""US-FREEZE-01 / US-CUT-01 — CLI freeze and cuts commands."""

from types import SimpleNamespace

import dj
from lib.cuts import CANONICAL_INTRO_CLEAN


def test_us_freeze_01_cli_status(tmp_path, monkeypatch, capsys):
    """US-FREEZE-01: freeze status prints frozen / total."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    track = master / "a.mp3"
    track.write_bytes(b"a")

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)

    from lib.freeze import mark_done

    mark_done(track, master)
    dj.cmd_freeze(SimpleNamespace(freeze_action="status", paths=None))
    out = capsys.readouterr().out
    assert "Frozen: 1 / 1" in out


def test_us_freeze_01_cli_mark_and_unmark(tmp_path, monkeypatch, capsys):
    """US-FREEZE-01: freeze mark / unmark via CLI."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / "_meta").mkdir()
    track = master / "a.mp3"
    track.write_bytes(b"a")

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)

    dj.cmd_freeze(SimpleNamespace(freeze_action="mark", paths=[str(track)]))
    assert "frozen:" in capsys.readouterr().out

    dj.cmd_freeze(SimpleNamespace(freeze_action="unmark", paths=[str(track)]))
    assert "unfrozen:" in capsys.readouterr().out


def test_us_cut_01_cli_standardize_dry_run(tmp_path, monkeypatch, capsys):
    """US-CUT-01: cuts standardize --dry-run via CLI."""
    master = tmp_path / "Master"
    master.mkdir()
    src = master / "Artist - Song (Intro - Clean).mp3"
    src.write_bytes(b"x")

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)

    dj.cmd_cuts(
        SimpleNamespace(
            action="standardize",
            full=True,
            days=1,
            dry_run=True,
        )
    )
    out = capsys.readouterr().out
    assert "would rename" in out
    assert src.exists()
    assert not (master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3").exists()


def test_us_cut_02_cli_dedupe_dry_run(tmp_path, monkeypatch):
    """US-CUT-02: cuts dedupe dry-run via CLI writes report."""
    master = tmp_path / "Master"
    master.mkdir()
    (master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3").write_bytes(b"a")
    (master / "Artist - Song (Clean).mp3").write_bytes(b"b")

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)

    dj.cmd_cuts(
        SimpleNamespace(
            action="dedupe",
            full=True,
            days=1,
            mode="narrow",
            apply=False,
        )
    )
    assert (master / "_meta" / "cut_dedup_report.txt").is_file()


def test_us_cut_02_cli_dedupe_apply(tmp_path, monkeypatch):
    """US-CUT-02: cuts dedupe --apply deletes extras."""
    master = tmp_path / "Master"
    master.mkdir()
    keeper = master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3"
    extra = master / "Artist - Song (Clean).mp3"
    keeper.write_bytes(b"a")
    extra.write_bytes(b"b")

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)

    dj.cmd_cuts(
        SimpleNamespace(
            action="dedupe",
            full=True,
            days=1,
            mode="narrow",
            apply=True,
        )
    )
    assert keeper.exists()
    assert not extra.exists()


def test_us_cut_01_cli_standardize_apply(tmp_path, monkeypatch):
    master = tmp_path / "Master"
    master.mkdir()
    src = master / "Artist - Song (Intro - Clean).mp3"
    src.write_bytes(b"x")

    monkeypatch.setattr(dj.cfg, "require_master", lambda: master)
    dj.cmd_cuts(
        SimpleNamespace(action="standardize", full=True, days=1, dry_run=False)
    )
    assert (master / f"Artist - Song ({CANONICAL_INTRO_CLEAN}).mp3").exists()
    assert not src.exists()


def test_cmd_cuts_unknown_action(tmp_path, monkeypatch):
    monkeypatch.setattr(dj.cfg, "require_master", lambda: tmp_path)
    with __import__("pytest").raises(SystemExit):
        dj.cmd_cuts(SimpleNamespace(action="nope"))

