"""Tests for lib.config path resolution."""

import platform
from pathlib import Path

import pytest

from lib.config import _get_platform_key, _resolve


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
