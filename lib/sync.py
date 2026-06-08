"""
Sync Master → Serato / Rekordbox.

Uses rsync on macOS/Linux, robocopy on Windows.
Both exclude _meta and junk files.
"""

import platform
import subprocess
import sys
from pathlib import Path

EXCLUDE = ["_meta", "Thumbs.db", "Desktop.ini", ".DS_Store"]


def _rsync(src: Path, dst: Path) -> int:
    excludes = []
    for ex in EXCLUDE:
        excludes += ["--exclude", ex]
    cmd = ["rsync", "-av", "--delete"] + excludes + [f"{src}/", str(dst) + "/"]
    result = subprocess.run(cmd)
    return result.returncode


def _robocopy(src: Path, dst: Path) -> int:
    excludes_dirs  = ["/XD"] + EXCLUDE
    excludes_files = ["/XF", "Thumbs.db", "Desktop.ini", ".DS_Store"]
    cmd = (
        ["robocopy", str(src), str(dst), "/MIR", "/NFL", "/NDL", "/NJH", "/NJS"]
        + excludes_dirs + excludes_files
    )
    result = subprocess.run(cmd)
    # robocopy exit codes < 8 are success/partial success
    return 0 if result.returncode < 8 else result.returncode


def sync(src: Path, dst: Path, label: str = "") -> None:
    if not src.is_dir():
        print(f"Error: source not found: {src}")
        sys.exit(1)
    dst.mkdir(parents=True, exist_ok=True)

    tag = f" ({label})" if label else ""
    print(f"Syncing{tag}: {src} → {dst}")

    if platform.system() == "Windows":
        rc = _robocopy(src, dst)
    else:
        rc = _rsync(src, dst)

    if rc != 0:
        print(f"Warning: sync exited with code {rc}")
    else:
        print("Sync complete.")


def sync_serato(master: Path, serato: Path) -> None:
    sync(master, serato, label="Serato")
    print("Restart Serato to pick up changes.")


def sync_rekordbox(master: Path, rekordbox: Path) -> None:
    sync(master, rekordbox, label="Rekordbox")
    print("Restart Rekordbox to pick up changes.")
