"""
Cross-platform config loader.

Reads config.json (committed defaults) and merges config.local.json
(gitignored, machine-specific overrides).

On Mac/Linux, uses the "mac" key. On Windows, uses "windows" key.
Expands ~ in paths.
"""

import json
import os
import platform
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent


def _load_json(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _get_platform_key() -> str:
    return "windows" if platform.system() == "Windows" else "mac"


def _resolve(value) -> Path:
    """Resolve a path string or {mac, windows} dict to an absolute Path."""
    if isinstance(value, dict):
        key = _get_platform_key()
        value = value.get(key, value.get("mac", ""))
    return Path(os.path.expanduser(str(value))).resolve()


def load() -> dict:
    """Return resolved config dict with Path values."""
    base  = _load_json(_ROOT / "config.json")
    local = _load_json(_ROOT / "config.local.json")

    # Deep merge: local overrides base at the key level
    merged = {**base, **local}
    # Remove comment key
    merged.pop("_comment", None)

    return {
        "master":               _resolve(merged.get("master", "")),
        "serato_latest_import": _resolve(merged.get("serato_latest_import", "")),
        "rekordbox_music":      _resolve(merged.get("rekordbox_music", "")),
    }


def get_master() -> Path:
    return load()["master"]


def get_serato() -> Path:
    return load()["serato_latest_import"]


def get_rekordbox() -> Path:
    return load()["rekordbox_music"]


def require_master() -> Path:
    p = get_master()
    if not p.is_dir():
        print(f"Error: Master not found at {p}")
        print("  Mac: mount buckles volume")
        print("  Windows: map the NAS share or update config.local.json")
        sys.exit(1)
    return p
