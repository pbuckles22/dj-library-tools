"""US-NAS-01 / US-USB-01 — config path resolution and stable NAS access."""

import platform
from pathlib import Path

import pytest

from lib.config import _get_platform_key, _resolve, load, require_master


def test_resolve_uses_mac_key(monkeypatch):
    monkeypatch.setattr("lib.config._get_platform_key", lambda: "mac")
    result = _resolve({"mac": "/tmp/master", "windows": "/tmp/windows-master"})
    assert result == Path("/tmp/master").resolve()


def test_resolve_uses_windows_key(monkeypatch):
    monkeypatch.setattr("lib.config._get_platform_key", lambda: "windows")
    result = _resolve({"mac": "/tmp/master", "windows": "/tmp/windows-master"})
    assert result == Path("/tmp/windows-master").resolve()


def test_resolve_plain_string(monkeypatch, tmp_path):
    p = tmp_path / "plain"
    monkeypatch.setattr("lib.config._get_platform_key", lambda: "mac")
    result = _resolve(str(p))
    assert result == p.resolve()


def test_resolve_expands_tilde(monkeypatch, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    result = _resolve("~/Music/Master")
    assert result == (home / "Music" / "Master").resolve()


def test_get_platform_key(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    assert _get_platform_key() == "windows"
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    assert _get_platform_key() == "mac"


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows path parsing")
def test_resolve_windows_drive_path():
    result = _resolve({"mac": "/tmp/master", "windows": "C:\\Music\\Master"})
    assert result.name == "Master"
    assert result.drive == "C:"


def test_us_nas_01_load_resolves_core_paths():
    """US-NAS-01: config resolves nas_link, master, newmusic, lexicon, serato, gig_usb."""
    import json

    from lib import config as cfg_mod

    raw = json.loads((cfg_mod._ROOT / "config.json").read_text(encoding="utf-8"))
    assert "DJ_Master_Link" in raw["nas_link"]["mac"]
    assert "DJ_Master_Link" in raw["master"]["mac"]
    assert "DJ_Master_Link" in raw["lexicon_root"]["mac"]

    cfg = load()
    for key in (
        "nas_link",
        "master",
        "newmusic",
        "lexicon_root",
        "serato_latest_import",
        "gig_usb",
        "nas_volume",
    ):
        assert key in cfg
    assert cfg["nas_volume"] == "buckles"
    assert cfg["master"].name == "Master"


def test_us_nas_01_require_master_refreshes_nas_link(tmp_path, monkeypatch):
    """US-NAS-01: require_master invokes NAS link refresh before path checks."""
    master = tmp_path / "Master"
    master.mkdir()
    called = []

    monkeypatch.setattr("lib.config.ensure_nas_link", lambda: called.append(True))
    monkeypatch.setattr("lib.config.get_master", lambda: master)

    assert require_master() == master
    assert called == [True]


def test_us_nas_01_require_master_missing_exits(tmp_path, monkeypatch):
    """US-NAS-01: missing Master exits non-zero."""
    monkeypatch.setattr("lib.config.ensure_nas_link", lambda: None)
    monkeypatch.setattr("lib.config.get_master", lambda: tmp_path / "missing")
    monkeypatch.setattr("lib.config.get_nas_volume", lambda: "buckles")

    with pytest.raises(SystemExit) as exc:
        require_master()
    assert exc.value.code == 1


def test_us_usb_01_gig_usb_is_not_serato_library():
    """US-USB-01: Serato library path is local Latest Import, not gig_usb."""
    cfg = load()
    serato = cfg["serato_latest_import"]
    gig = cfg["gig_usb"]
    assert serato != gig
    assert "Latest Import" in str(serato) or "_Serato_" in str(serato)
    if platform.system() != "Windows":
        assert "DJ_USB" in str(gig)


def test_us_nas_01_getters_match_load():
    """US-NAS-01: public getters return load() paths."""
    from lib import config as cfg

    data = load()
    assert cfg.get_master() == data["master"]
    assert cfg.get_newmusic() == data["newmusic"]
    assert cfg.get_new_music() == data["newmusic"]
    assert cfg.get_serato() == data["serato_latest_import"]
    assert cfg.get_rekordbox() == data["rekordbox_music"]
    assert cfg.get_gig_usb() == data["gig_usb"]
    assert cfg.get_nas_volume() == data["nas_volume"]
    assert cfg.get_acoustid_key() == data["acoustid_api_key"]
    assert cfg.get_musicbrainz_app() == data["musicbrainz_app"]


def test_require_acoustid_key_missing_exits(monkeypatch):
    from lib.config import require_acoustid_key

    monkeypatch.setattr("lib.config.get_acoustid_key", lambda: "")
    with pytest.raises(SystemExit) as exc:
        require_acoustid_key()
    assert exc.value.code == 1


def test_ensure_nas_link_noop_on_non_darwin(monkeypatch):
    from lib.config import ensure_nas_link

    monkeypatch.setattr(platform, "system", lambda: "Linux")
    ensure_nas_link()  # no raise


def test_require_acoustid_key_returns_key(monkeypatch):
    from lib.config import require_acoustid_key

    monkeypatch.setattr("lib.config.get_acoustid_key", lambda: "abc")
    assert require_acoustid_key() == "abc"


