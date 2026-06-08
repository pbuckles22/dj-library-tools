"""Tests for lib.config path resolution."""

import platform
from pathlib import Path

import pytest

from lib.config import _get_platform_key, _resolve


@pytest.mark.parametrize(
    "value, platform_name, expected_suffix",
    [
        ({"mac": "/tmp/master", "windows": "C:\\Music\\Master"}, "Windows", "Master"),
        ({"mac": "/tmp/master", "windows": "C:\\Music\\Master"}, "Darwin", "master"),
        ("/tmp/plain", "Windows", "plain"),
    ],
)
def test_resolve_platform_paths(monkeypatch, value, platform_name, expected_suffix):
    monkeypatch.setattr(platform, "system", lambda: platform_name)
    result = _resolve(value)
    assert result.is_absolute()
    assert result.name == expected_suffix


def test_resolve_expands_tilde(monkeypatch, tmp_path):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("USERPROFILE", str(home))
    result = _resolve("~/Music/Master")
    assert result == (home / "Music" / "Master").resolve()


def test_get_platform_key(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    assert _get_platform_key() == "windows"
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    assert _get_platform_key() == "mac"
