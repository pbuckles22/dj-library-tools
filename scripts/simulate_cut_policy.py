"""Simulate cut standardization and one-cut-per-song deletion policy."""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import config as cfg
from lib.dedup import AUDIO_EXTENSIONS

# Canonical cut names (filename suffix after base title)
CANONICAL = {
    "intro_clean": "Intro Clean",
    "clean": "Clean",
    "clean_extended": "Clean Extended",
    "dirty": "Dirty",
    "intro_dirty": "Intro Dirty",
    "acapella": "Acapella",
    "remix_edit": "Remix",
    "other": "Other",
    "plain": "",  # no parenthetical cut tag
}

# Map raw last-paren text -> family (order = keep preference, best first)
INTRO_CLEAN_ALIASES = (
    "intro clean",
    "intro - clean",
    "djcity intro - clean",
    "hook first - clean",
    "djcity hook first - clean",
    "short edit - clean",  # still an edit; lower priority intro-ish
)


def parse_name(name: str):
    stem = Path(name).stem
    stem = re.sub(r"\s+\(\d+\)$", "", stem)
    if " - " not in stem:
        return None
    artist, title = stem.split(" - ", 1)
    parens = re.findall(r"\(([^)]*)\)", title)
    base = re.sub(r"\s*\([^)]*\)", "", title).strip()
    base = re.sub(r"\s+", " ", base)
    return artist.strip(), base, parens


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def classify_cut(parens: list[str]) -> str:
    if not parens:
        return "plain"
    last = parens[-1].lower().strip()
    if last in INTRO_CLEAN_ALIASES or (
        "intro" in last and "clean" in last and "dirty" not in last
    ):
        return "intro_clean"
    if last == "clean":
        return "clean"
    if "clean extended" in last or (
        "extended" in last and "clean" in last and "intro" not in last
    ):
        return "clean_extended"
    if "intro" in last and "dirty" in last:
        return "intro_dirty"
    if last == "dirty" or ("dirty" in last and "acap" not in last):
        return "dirty"
    if "acap" in last:
        return "acapella"
    if any(w in last for w in ("remix", "edit", "bootleg", "mashup", "rework", "segue")):
        return "remix_edit"
    return "other"


def intro_clean_rank(parens: list[str]) -> int:
    """Lower = better keeper among intro_clean family."""
    if not parens:
        return 99
    last = parens[-1].lower().strip()
    for i, alias in enumerate(INTRO_CLEAN_ALIASES):
        if last == alias:
            return i
    if "intro clean" in last:
        return 0
    if "intro" in last and "clean" in last:
        return 5
    return 50


# Global keep preference across families
FAMILY_RANK = {
    "intro_clean": 0,
    "clean": 1,
    "clean_extended": 2,
    "dirty": 3,
    "intro_dirty": 4,
    "acapella": 5,
    "remix_edit": 6,
    "other": 7,
    "plain": 8,
}


def pick_keeper(files: list[dict]) -> dict:
    def sort_key(f):
        fam = f["family"]
        rank = FAMILY_RANK.get(fam, 99)
        intro_rank = intro_clean_rank(f["parens"]) if fam == "intro_clean" else 0
        return (rank, intro_rank, f["path"].name.lower())

    return sorted(files, key=sort_key)[0]


def canonical_suffix(family: str) -> str:
    return CANONICAL.get(family, "Other")


def standardized_name(artist: str, base: str, family: str, ext: str) -> str:
    cut = canonical_suffix(family)
    if cut:
        return f"{artist} - {base} ({cut}){ext}"
    return f"{artist} - {base}{ext}"


def main():
    master = cfg.get_master()
    groups: dict[tuple[str, str], list] = defaultdict(list)

    for p in master.iterdir():
        if not p.is_file() or p.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        parsed = parse_name(p.name)
        if not parsed:
            continue
        artist, base, parens = parsed
        fam = classify_cut(parens)
        groups[(norm(artist), norm(base))].append(
            {
                "path": p,
                "artist": artist,
                "base": base,
                "parens": parens,
                "family": fam,
            }
        )

    to_delete = []
    to_rename = []
    songs_affected = 0
    delete_by_family = Counter()
    rename_map = Counter()  # old last-paren -> canonical

    for key, files in groups.items():
        if len(files) < 2:
            # still standardize single-file intro aliases
            f = files[0]
            if f["family"] == "intro_clean" and f["parens"]:
                last = f["parens"][-1]
                if last != CANONICAL["intro_clean"]:
                    new = standardized_name(
                        f["artist"], f["base"], f["family"], f["path"].suffix
                    )
                    if new != f["path"].name:
                        to_rename.append((f["path"].name, new, last))
                        rename_map[last] += 1
            continue

        keeper = pick_keeper(files)
        songs_affected += 1
        for f in files:
            if f["path"] != keeper["path"]:
                to_delete.append(f)
                delete_by_family[f["family"]] += 1
            elif f["family"] == "intro_clean" and f["parens"]:
                last = f["parens"][-1]
                if last != CANONICAL["intro_clean"]:
                    new = standardized_name(
                        f["artist"], f["base"], f["family"], f["path"].suffix
                    )
                    if new != f["path"].name:
                        to_rename.append((f["path"].name, new, last))
                        rename_map[last] += 1

    # Narrow policy: only delete non-intro when intro_clean exists in group
    delete_if_intro = []
    for key, files in groups.items():
        if len(files) < 2:
            continue
        has_intro = any(f["family"] == "intro_clean" for f in files)
        if not has_intro:
            continue
        keeper = pick_keeper([f for f in files if f["family"] == "intro_clean"])
        for f in files:
            if f["path"] != keeper["path"]:
                delete_if_intro.append(f)

    lines = [
        "=== CUT POLICY SIMULATION ===",
        "Preference: Intro Clean > Clean > Clean Extended > Dirty > Acapella > Remix/Edit > Other",
        "",
        f"Total tracks now: {sum(len(v) for v in groups.values())}",
        f"Unique songs: {len(groups)}",
        "",
        "--- ONE CUT PER SONG (strict) ---",
        f"Songs with 2+ files affected: {songs_affected}",
        f"Files DELETED: {len(to_delete)}",
        f"Master after: {sum(len(v) for v in groups.values()) - len(to_delete)}",
        "",
        "Deletions by cut family:",
    ]
    for fam, n in delete_by_family.most_common():
        lines.append(f"  {n:4d}  {fam}")

    lines += [
        "",
        "--- NARROW: drop extras only when Intro Clean family exists ---",
        f"Files DELETED: {len(delete_if_intro)}",
        f"Master after: {sum(len(v) for v in groups.values()) - len(delete_if_intro)}",
        "",
        "--- RENAME standardization (intro aliases -> 'Intro Clean') ---",
        f"Files renamed: {len(to_rename)}",
        "Alias mappings:",
    ]
    for old, n in rename_map.most_common():
        lines.append(f"  {n:4d}  ({old}) -> (Intro Clean)")

    out = master / "_meta" / "cut_policy_simulation.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
