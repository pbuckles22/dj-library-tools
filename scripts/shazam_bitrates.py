#!/usr/bin/env python3
"""List bitrates for files in My Music/Shazam."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import config as cfg
from lib.dedup import AUDIO_EXTENSIONS, get_bitrate


def main():
    shazam = cfg.get_master().parent / "Shazam"
    if not shazam.is_dir():
        print(f"Shazam folder not found: {shazam}")
        return 1

    files = sorted(
        p for p in shazam.iterdir()
        if p.is_file()
        and (p.suffix.lower() in AUDIO_EXTENSIONS or p.suffix.lower() == ".wav")
    )

    print(f"Shazam folder: {shazam}")
    print(f"Files: {len(files)}\n")
    print(f"{'Bitrate':>10}  File")
    print("-" * 90)

    unknown = 0
    for path in files:
        br = get_bitrate(str(path))
        if br:
            label = f"{br // 1000} kbps"
        else:
            label = "unknown"
            unknown += 1
        print(f"{label:>10}  {path.name}")

    print("-" * 90)
    print(f"Unknown bitrate: {unknown}/{len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
