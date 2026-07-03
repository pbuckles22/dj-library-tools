"""
Sync Master → Serato / Rekordbox.

Uses rsync on macOS/Linux, robocopy on Windows.
Both exclude _meta and junk files.
"""

import os
import platform
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

EXCLUDE = ["_meta", "Thumbs.db", "Desktop.ini", ".DS_Store"]
AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".flac", ".aiff", ".aif", ".ogg"}

# macOS ships "openrsync" (reports as 2.6.9) which lacks --iconv and mishandles
# accented filenames over SMB. Prefer a real GNU rsync 3.x if one is installed.
_GNU_RSYNC_CANDIDATES = [
    "/opt/homebrew/bin/rsync",
    "/usr/local/bin/rsync",
    "/opt/homebrew/opt/rsync/bin/rsync",
]


def _rsync_bin() -> str:
    for path in _GNU_RSYNC_CANDIDATES:
        if Path(path).is_file():
            return path
    return shutil.which("rsync") or "rsync"


def _rsync_supports_iconv(binary: str) -> bool:
    try:
        out = subprocess.run([binary, "--version"], capture_output=True,
                             text=True).stdout
    except OSError:
        return False
    return "no iconv" not in out and "version 3" in out


def _rsync_base() -> list:
    """rsync command prefix with macOS Unicode normalization when supported."""
    binary = _rsync_bin()
    cmd = [binary, "-av", "--modify-window=2"]
    if platform.system() == "Darwin" and _rsync_supports_iconv(binary):
        # Normalize NFD (local APFS) <-> NFC so accented names match the NAS.
        cmd.append("--iconv=utf-8-mac")
    return cmd


def _excludes() -> list:
    out = []
    for ex in EXCLUDE:
        out += ["--exclude", ex]
    return out


def _rsync(src: Path, dst: Path) -> int:
    cmd = _rsync_base() + ["--delete"] + _excludes() + [f"{src}/", str(dst) + "/"]
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


def _rsync_pull(src: Path, dst: Path, prune: bool, dry_run: bool,
                quiet: bool = False) -> int:
    # --modify-window (in _rsync_base) guards against SMB/exFAT timestamp
    # rounding so we don't re-copy unchanged files on every run.
    cmd = _rsync_base() + ["--itemize-changes"]
    if prune:
        cmd.append("--delete")
    if dry_run:
        cmd.append("--dry-run")
    cmd += _excludes() + [f"{src}/", str(dst) + "/"]
    result = subprocess.run(cmd, capture_output=quiet, text=quiet)
    if quiet and result.stdout:
        changed = [ln for ln in result.stdout.splitlines()
                   if ln and not ln.startswith("sending ")]
        if changed:
            print(f"  {len(changed)} file(s) updated")
    return result.returncode


def _robocopy_pull(src: Path, dst: Path, prune: bool, dry_run: bool) -> int:
    mode = "/MIR" if prune else "/E"
    cmd = ["robocopy", str(src), str(dst), mode, "/NFL", "/NDL", "/NJH", "/NJS"]
    if dry_run:
        cmd.append("/L")
    cmd += ["/XD"] + EXCLUDE + ["/XF", "Thumbs.db", "Desktop.ini", ".DS_Store"]
    result = subprocess.run(cmd)
    return 0 if result.returncode < 8 else result.returncode


def pull_new(master: Path, rekordbox: Path, prune: bool = False,
             dry_run: bool = False) -> None:
    """
    Pull new/changed files from NAS Master into the local Rekordbox folder.

    Additive by default (never deletes), so Rekordbox keeps pointing at a stable
    local path. Pass prune=True for a true mirror, dry_run=True to preview.
    """
    if not master.is_dir():
        print(f"Error: Master not found: {master}")
        print("  Mount the NAS (buckles) or update config.local.json.")
        sys.exit(1)
    rekordbox.mkdir(parents=True, exist_ok=True)

    label = "mirror" if prune else "additive"
    preview = " [DRY RUN]" if dry_run else ""
    print(f"Pulling new/changed files ({label}){preview}")
    print(f"  from: {master}")
    print(f"  to:   {rekordbox}")

    if platform.system() == "Windows":
        rc = _robocopy_pull(master, rekordbox, prune, dry_run)
    else:
        rc = _rsync_pull(master, rekordbox, prune, dry_run)

    if rc != 0:
        print(f"Warning: pull exited with code {rc}")
    elif dry_run:
        print("Dry run complete — no files changed.")
    else:
        print("Pull complete. In Rekordbox, add the new files and analyze.")


def _is_audio(name: str) -> bool:
    return Path(name).suffix.lower() in AUDIO_EXTS


def _list_audio(dir_path: Path) -> list[str]:
    if not dir_path.is_dir():
        return []
    return sorted(n for n in os.listdir(dir_path) if _is_audio(n))


def _nfc(name: str) -> str:
    return unicodedata.normalize("NFC", name)


def _local_audio_nfc(dir_path: Path) -> set[str]:
    return {_nfc(n) for n in _list_audio(dir_path)}


def _missing_on_local(master: Path, rekordbox: Path) -> list[str]:
    local = _local_audio_nfc(rekordbox)
    return [n for n in _list_audio(master) if _nfc(n) not in local]


def _file_openable(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            f.read(1)
        return True
    except OSError:
        return False


def _name_variants(name: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for cand in (name, unicodedata.normalize("NFC", name),
                 unicodedata.normalize("NFD", name)):
        if cand not in seen:
            seen.add(cand)
            out.append(cand)
    return out


def _copy_one(master: Path, rekordbox: Path, name: str) -> bool:
    for cand in _name_variants(name):
        src = master / cand
        if not _file_openable(src):
            continue
        dst = rekordbox / cand
        try:
            shutil.copy2(src, dst)
            return True
        except OSError:
            continue
    return False


def _find_ghosts(master: Path, names: list[str]) -> list[str]:
    ghosts = []
    for name in names:
        if any(_file_openable(master / cand) for cand in _name_variants(name)):
            continue
        ghosts.append(name)
    return ghosts


def refresh_local(master: Path, rekordbox: Path, retries: int = 3) -> int:
    """
    Pull NAS Master into the local Rekordbox folder before opening Rekordbox.

    Retries rsync over flaky SMB, then copies any stragglers directly.
    Returns exit code (0 = ready, 1 = NAS not mounted, 2 = ghost files remain).
    """
    if not master.is_dir():
        print(f"Error: Master not found: {master}")
        print("  Mount the NAS (buckles) or update config.local.json.")
        return 1

    rekordbox.mkdir(parents=True, exist_ok=True)
    before = len(_local_audio_nfc(rekordbox))

    print("=" * 50)
    print("  Refresh local Rekordbox library")
    print("=" * 50)
    print(f"  from: {master}")
    print(f"  to:   {rekordbox}")
    print(f"  local tracks now: {before}")
    print()

    for attempt in range(1, retries + 1):
        print(f"Pull attempt {attempt}/{retries}...")
        if platform.system() == "Windows":
            rc = _robocopy_pull(master, rekordbox, prune=False, dry_run=False)
        else:
            rc = _rsync_pull(master, rekordbox, prune=False, dry_run=False, quiet=True)
        if rc == 0:
            print("  up to date")
            break
        print(f"  rsync exit {rc}, retrying...")

    missing = _missing_on_local(master, rekordbox)
    if missing:
        print(f"\nCopying {len(missing)} straggler(s) directly...")
        copied = 0
        still_missing = []
        for name in missing:
            if _copy_one(master, rekordbox, name):
                copied += 1
                print(f"  copied: {name}")
            else:
                still_missing.append(name)
        missing = still_missing
        if copied:
            print(f"  {copied} file(s) copied.")

    after = len(_local_audio_nfc(rekordbox))
    added = after - before
    ghosts = _find_ghosts(master, missing) if missing else []

    print()
    print("=" * 50)
    print("  Refresh complete")
    print("=" * 50)
    print(f"  Local tracks: {before} → {after}" + (f" (+{added} new)" if added else ""))

    if ghosts:
        print(f"\n  WARNING: {len(ghosts)} file(s) on NAS are unreadable (ghost entries).")
        print("  Re-download or re-copy these into Master, then run refresh again:")
        for name in ghosts:
            print(f"    - {name}")
        print("\n  Open Rekordbox — most tracks should load. Fix ghosts on the NAS.")
        return 2

    if missing:
        print(f"\n  {len(missing)} file(s) still missing — SMB may be flaky. Try again.")
        for name in missing:
            print(f"    - {name}")
        return 2

    print("\n  Ready. Open Rekordbox (collection: ~/Music/RekordboxMusic).")
    if added:
        print("  New files were added — in Rekordbox: File → Reload, then analyze new tracks.")
    return 0
