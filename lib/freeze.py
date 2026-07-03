"""
Freeze lock — mark processed tracks as done so the pipeline never touches them.

macOS: xattr user.djtools.status=done
All platforms: Master/_meta/frozen.json (path + sha256)
"""

import hashlib
import json
import platform
import subprocess
from pathlib import Path

XATTR_KEY = "user.djtools.status"
XATTR_VAL = "done"
AUDIO_EXTENSIONS = {".mp3", ".flac", ".m4a", ".wav", ".aac", ".ogg", ".alac", ".aiff"}


def _manifest_path(master: Path) -> Path:
    return master / "_meta" / "frozen.json"


def _sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest(master: Path) -> dict:
    path = _manifest_path(master)
    if not path.exists():
        return {"files": {}, "hashes": {}}
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"files": {}, "hashes": {}}
    data.setdefault("files", {})
    data.setdefault("hashes", {})
    return data


def _save_manifest(master: Path, data: dict) -> None:
    meta = master / "_meta"
    meta.mkdir(exist_ok=True)
    with open(_manifest_path(master), "w") as f:
        json.dump(data, f, indent=2)


def _xattr_get(path: Path) -> str | None:
    if platform.system() != "Darwin":
        return None
    try:
        out = subprocess.run(
            ["xattr", "-p", XATTR_KEY, str(path)],
            capture_output=True, text=True,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except OSError:
        pass
    return None


def _xattr_set(path: Path, value: str) -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        subprocess.run(["xattr", "-w", XATTR_KEY, value, str(path)], check=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _xattr_remove(path: Path) -> None:
    if platform.system() != "Darwin":
        return
    try:
        subprocess.run(["xattr", "-d", XATTR_KEY, str(path)], capture_output=True)
    except OSError:
        pass


def is_done(path: Path, master: Path | None = None) -> bool:
    if not path.is_file():
        return False
    if master is None:
        master = path.parent
    manifest = _load_manifest(master)
    key = str(path.resolve())
    if key in manifest["files"]:
        return True
    if _xattr_get(path) == XATTR_VAL:
        return True
    try:
        digest = _sha256(path)
        if digest in manifest["hashes"]:
            return True
    except OSError:
        pass
    return False


def mark_done(path: Path, master: Path | None = None) -> bool:
    if not path.is_file():
        return False
    if master is None:
        master = path.parent
    try:
        digest = _sha256(path)
    except OSError:
        return False
    _xattr_set(path, XATTR_VAL)
    manifest = _load_manifest(master)
    key = str(path.resolve())
    manifest["files"][key] = {"sha256": digest, "name": path.name}
    manifest["hashes"][digest] = key
    _save_manifest(master, manifest)
    return True


def unmark(path: Path, master: Path | None = None) -> bool:
    if master is None:
        master = path.parent
    _xattr_remove(path)
    manifest = _load_manifest(master)
    key = str(path.resolve())
    entry = manifest["files"].pop(key, None)
    if entry and entry.get("sha256") in manifest["hashes"]:
        manifest["hashes"].pop(entry["sha256"], None)
    _save_manifest(master, manifest)
    return True


def list_audio(master: Path) -> list[Path]:
    return sorted(
        p for p in master.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    )


def status(master: Path) -> tuple[int, int]:
    files = list_audio(master)
    manifest = _load_manifest(master)
    manifest_paths = {Path(k).resolve() for k in manifest["files"]}
    frozen = sum(1 for p in files if p.resolve() in manifest_paths or _xattr_get(p) == XATTR_VAL)
    return frozen, len(files)


def mark_all(master: Path) -> int:
    count = 0
    for p in list_audio(master):
        if mark_done(p, master):
            count += 1
            if count % 500 == 0:
                print(f"  frozen {count}...", flush=True)
    return count


def frozen_paths(master: Path) -> list[Path]:
    return [p for p in list_audio(master) if is_done(p, master)]
