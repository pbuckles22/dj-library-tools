"""Analyze Master for same-song multiple cuts (Clean, Intro Clean, etc.)."""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import config as cfg
from lib.dedup import AUDIO_EXTENSIONS


def parse_name(name: str):
    stem = Path(name).stem
    stem = re.sub(r"\s+\(\d+\)$", "", stem)
    if " - " not in stem:
        return None
    artist, title = stem.split(" - ", 1)
    parens = re.findall(r"\(([^)]*)\)", title)
    base = re.sub(r"\s*\([^)]*\)", "", title).strip()
    base = re.sub(r"\s+", " ", base)
    return artist.strip(), base, parens, title.strip()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def variant_label(parens: list[str]) -> str:
    if not parens:
        return "(no tag)"
    return " | ".join(parens)


def last_cut_tag(parens: list[str]) -> str | None:
    return parens[-1].strip() if parens else None


def main():
    master = cfg.get_master()
    groups: dict[tuple[str, str], list] = defaultdict(list)
    parse_fail = 0
    all_parens: Counter = Counter()

    for p in master.iterdir():
        if not p.is_file() or p.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        parsed = parse_name(p.name)
        if not parsed:
            parse_fail += 1
            continue
        artist, base, parens, full_title = parsed
        key = (norm(artist), norm(base))
        groups[key].append(
            {
                "file": p.name,
                "artist": artist,
                "base": base,
                "parens": parens,
                "variant": variant_label(parens),
                "full_title": full_title,
            }
        )
        for par in parens:
            all_parens[par.lower().strip()] += 1

    multi = {k: v for k, v in groups.items() if len(v) >= 2}
    multi_diff = {
        k: v for k, v in multi.items() if len({x["variant"] for x in v}) >= 2
    }

    intro_vs_clean = []
    for k, files in multi_diff.items():
        last_tags = [last_cut_tag(f["parens"]) for f in files]
        last_lower = [(t or "").lower() for t in last_tags]
        if "intro clean" in last_lower and "clean" in last_lower:
            intro_vs_clean.append((k, files))

    total_tracks = sum(len(v) for v in groups.values()) + parse_fail
    last_paren: Counter = Counter()
    for files in groups.values():
        for f in files:
            if f["parens"]:
                last_paren[f["parens"][-1]] += 1

    perm_counter: Counter = Counter()
    for files in multi_diff.values():
        perm = tuple(sorted({f["variant"] for f in files}))
        perm_counter[perm] += 1

    out = master / "_meta" / "cut_analysis.txt"
    lines = [
        "=== MASTER CUT ANALYSIS ===",
        f"Total tracks: {total_tracks}",
        f"Unique songs (artist + base title): {len(groups)}",
        f"Songs with 2+ files (any reason): {len(multi)}",
        f"Songs with 2+ different cuts/tags: {len(multi_diff)}",
        f"Songs with both Intro Clean and Clean: {len(intro_vs_clean)}",
        f"Unparsed filenames: {parse_fail}",
        "",
        "Terminology: DJ pools call these 'versions', 'edits', or 'cuts'.",
        "Common tags: Clean, Intro Clean, Extended, Dirty, Remix, Acapella, etc.",
        "",
        "=== TOP CUT TAGS (last parenthetical) ===",
    ]
    for tag, n in last_paren.most_common(30):
        lines.append(f"  {n:4d}  {tag}")

    lines += ["", "=== TOP VARIANT COMBINATIONS (same base song) ==="]
    for perm, n in perm_counter.most_common(25):
        lines.append(f"  {n:3d}x  ({len(perm)} variants)")
        for v in perm:
            lines.append(f"        - {v}")

    lines += ["", "=== INTRO CLEAN + CLEAN PAIRS (all) ==="]
    for (artist, base), files in sorted(intro_vs_clean, key=lambda x: x[0][1]):
        lines.append(f"  {files[0]['artist']} - {files[0]['base']}")
        for f in sorted(files, key=lambda x: x["variant"]):
            lines.append(f"    [{f['variant']}]")

    text = "\n".join(lines)
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8")

    print(text[:4000])
    if len(text) > 4000:
        print(f"\n... full report ({len(lines)} lines) -> {out}")


if __name__ == "__main__":
    main()
