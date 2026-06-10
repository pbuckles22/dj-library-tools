#!/usr/bin/env python3
"""Bitrate distribution report for Master (flat root)."""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib import config as cfg
from lib.dedup import AUDIO_EXTENSIONS, get_bitrate


def _bucket(kbps: int) -> str:
    if kbps <= 96:
        return "<=96"
    if kbps <= 128:
        return "128"
    if kbps <= 160:
        return "160"
    if kbps <= 192:
        return "192"
    if kbps <= 256:
        return "256"
    if kbps <= 320:
        return "320"
    return ">320"


def main():
    master = cfg.require_master()
    files = sorted(
        p for p in master.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    )
    total = len(files)
    print(f"Master: {master}")
    print(f"Audio files: {total}\n")

    buckets: Counter[str] = Counter()
    unknown = 0
    low_128_or_less: list[tuple[str, int]] = []
    bitrates: list[int] = []

    for i, path in enumerate(files, 1):
        if i == 1 or i % 1000 == 0 or i == total:
            print(f"  Scanning {i}/{total}...", flush=True)

        br = get_bitrate(str(path))
        if not br:
            unknown += 1
            buckets["unknown"] += 1
            continue
        kbps = br // 1000
        bitrates.append(kbps)
        buckets[_bucket(kbps)] += 1
        if kbps <= 128:
            low_128_or_less.append((path.name, kbps))

    print()
    print("=== Bitrate buckets (kbps) ===")
    for key in ["<=96", "128", "160", "192", "256", "320", ">320", "unknown"]:
        n = buckets.get(key, 0)
        if n:
            pct = 100 * n / total
            print(f"  {key:>8}: {n:5}  ({pct:.1f}%)")

    if bitrates:
        bitrates.sort()
        print(f"\nMedian: {bitrates[len(bitrates)//2]} kbps")
        print(f"Mean:   {sum(bitrates)//len(bitrates)} kbps")

    low_n = len(low_128_or_less)
    print(f"\n<=128 kbps: {low_n} ({100*low_n/total:.1f}%)")
    print(f"Unknown bitrate: {unknown}")

    report = master / "_meta" / "bitrate_report.txt"
    report.parent.mkdir(exist_ok=True)
    with open(report, "w", encoding="utf-8") as fh:
        fh.write(f"Master bitrate report — {total} files\n\n")
        for key in ["<=96", "128", "160", "192", "256", "320", ">320", "unknown"]:
            n = buckets.get(key, 0)
            if n:
                fh.write(f"{key}: {n} ({100*n/total:.1f}%)\n")
        fh.write(f"\n<=128 kbps files ({low_n}):\n")
        for name, kbps in sorted(low_128_or_less, key=lambda x: (x[1], x[0])):
            fh.write(f"  {kbps:3} kbps  {name}\n")
    print(f"\nFull <=128 list: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
