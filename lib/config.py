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
import subprocess
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
    if not value:
        return Path()
    return Path(os.path.expanduser(str(value))).resolve()


def load() -> dict:
    """Return resolved config dict with Path values."""
    base  = _load_json(_ROOT / "config.json")
    local = _load_json(_ROOT / "config.local.json")

    merged = {**base, **local}
    merged.pop("_comment", None)

    master = _resolve(merged.get("master", ""))
    new_music_cfg = merged.get("new_music")
    if new_music_cfg:
        new_music = _resolve(new_music_cfg)
    else:
        new_music = master.parent / "NewMusic"

    gig_usb_cfg = merged.get("gig_usb", {})
    gig_usb = _resolve(gig_usb_cfg) if gig_usb_cfg else Path()

    return {
        "master":               master,
        "new_music":            new_music,
        "serato_latest_import": _resolve(merged.get("serato_latest_import", "")),
        "rekordbox_music":      _resolve(merged.get("rekordbox_music", "")),
        "gig_usb":              gig_usb,
        "lexicon_root":         _resolve(merged.get("lexicon_root", master)),
        "nas_volume":           merged.get("nas_volume", "buckles"),
        "nas_link":             _resolve(merged.get("nas_link", "")),
    }


def get_master() -> Path:
    return load()["master"]


def get_new_music() -> Path:
    return load()["new_music"]


def get_serato() -> Path:
    return load()["serato_latest_import"]


def get_rekordbox() -> Path:
    return load()["rekordbox_music"]


def get_gig_usb() -> Path:
    return load()["gig_usb"]


def get_nas_volume() -> str:
    return load()["nas_volume"]


def ensure_nas_link() -> None:
    """Refresh ~/Music/DJ_Master_Link on macOS before NAS paths are used."""
    if platform.system() != "Darwin":
        return
    script = _ROOT / "scripts" / "update-nas-link.sh"
    if not script.is_file():
        return
    env = {**os.environ, "NAS_VOLUME": get_nas_volume()}
    result = subprocess.run(["bash", str(script)], env=env)
    if result.returncode != 0:
        sys.exit(result.returncode)


def require_master() -> Path:
    ensure_nas_link()
    p = get_master()
    if not p.is_dir():
        print(f"Error: Master not found at {p}")
        print(f"  Mount NAS volume '{get_nas_volume()}' in Finder, then retry.")
        print("  Windows: map the NAS share or update config.local.json")
        sys.exit(1)
    return p
