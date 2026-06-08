"""Tests for lib.rename helpers."""

import pytest

from lib.rename import _safe_filename


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Normal Title", "Normal Title"),
        ('Bad:Name/Here?', "BadNameHere"),
        ("  spaced  ", "spaced"),
        ("trailing dots...", "trailing dots"),
        ("", "Unknown"),
        ("   ", "Unknown"),
        ('<>:"/\\|?*', "Unknown"),
    ],
)
def test_safe_filename(raw, expected):
    assert _safe_filename(raw) == expected
