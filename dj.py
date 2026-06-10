#!/usr/bin/env python3
"""
DJ Library Tools — cross-platform CLI.

Usage:
  python dj.py pipeline              # organize → rename → dedup → sync (last 24h)
  python dj.py pipeline --full       # full library scan
  python dj.py pipeline --days 3     # last 3 days
  python dj.py pipeline --no-serato
  python dj.py pipeline --no-rekordbox

  python dj.py organize              # move non-audio files to _meta
  python dj.py rename                # rename to "Artist - Title.ext"
  python dj.py dedup                 # dedup within Master (incremental)
  python dj.py dedup --full          # dedup within Master (full scan)

  python dj.py sync serato           # rsync/robocopy Master → Serato
  python dj.py sync rekordbox        # rsync/robocopy Master → Rekordbox
  python dj.py sync all              # both

  python dj.py compare <dir> [dir2 ...]          # tag-based compare (default)
  python dj.py compare --md5 <dir> [dir2 ...]    # MD5-based compare
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import config as cfg
from lib import dedup as dedup_mod
from lib import organize as organize_mod
from lib import rename as rename_mod
from lib import sync as sync_mod
from lib import compare as compare_mod


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_pipeline(args):
    master = cfg.require_master()
    meta   = master / "_meta"
    meta.mkdir(exist_ok=True)

    days  = None if args.full else args.days
    full  = args.full

    print("=" * 50)
    print(f"  DJ Pipeline {'(FULL)' if full else f'(last {days} day(s))'}")
    print("=" * 50)

    print("\n[1/5] Organizing...")
    organize_mod.organize(master, days=None if full else days)

    print("\n[2/5] Renaming...")
    rename_mod.rename_by_tags(master, days=None if full else days)

    print("\n[3/5] Deduplicating...")
    to_delete = dedup_mod.dedup(master, full=full, days=days)
    if to_delete:
        del_script = meta / "delete_duplicates.sh"
        print(f"  Running delete script ({len(to_delete)} files)...")
        import subprocess, platform
        if platform.system() == "Windows":
            # On Windows, delete directly
            for p in to_delete:
                try:
                    Path(p).unlink(missing_ok=True)
                except OSError as e:
                    print(f"  Could not delete {p}: {e}")
        else:
            subprocess.run(["bash", str(del_script)])

    if not args.no_serato:
        print("\n[4/5] Syncing → Serato...")
        sync_mod.sync_serato(master, cfg.get_serato())
    else:
        print("\n[4/5] Serato sync skipped.")

    if not args.no_rekordbox:
        print("\n[5/5] Syncing → Rekordbox...")
        sync_mod.sync_rekordbox(master, cfg.get_rekordbox())
    else:
        print("\n[5/5] Rekordbox sync skipped.")

    print("\n" + "=" * 50)
    parts = []
    if not args.no_serato:   parts.append("Serato")
    if not args.no_rekordbox: parts.append("Rekordbox")
    if parts:
        print(f"  Done. Restart {' and '.join(parts)}.")
    else:
        print("  Done. No DJ app sync requested.")
    print("=" * 50)


def cmd_organize(args):
    master = cfg.require_master()
    days   = args.days if not args.full else None
    organize_mod.organize(master, days=days)


def cmd_rename(args):
    master = cfg.require_master()
    days   = args.days if not args.full else None
    rename_mod.rename_by_tags(master, days=days)


def cmd_dedup(args):
    master = cfg.require_master()
    dedup_mod.dedup(master, full=args.full, days=args.days)


def cmd_sync(args):
    master = cfg.require_master()
    target = args.target.lower()
    if target in ("serato", "all"):
        sync_mod.sync_serato(master, cfg.get_serato())
    if target in ("rekordbox", "all"):
        sync_mod.sync_rekordbox(master, cfg.get_rekordbox())
    if target not in ("serato", "rekordbox", "all"):
        print(f"Unknown sync target: {args.target}. Use: serato, rekordbox, all")
        sys.exit(1)


def cmd_compare(args):
    master = cfg.require_master()
    if not args.dirs:
        print("Error: provide at least one directory to compare.")
        sys.exit(1)
    if args.md5:
        in_m, not_in_m = compare_mod.compare_md5(master, args.dirs)
        mode = "MD5"
    else:
        in_m, not_in_m = compare_mod.compare_tags(master, args.dirs)
        mode = "tag"

    print(f"""
========================================
  Compare ({mode}) complete
========================================
  In Master:      {len(in_m)}   (safe to delete from OLD folders)
  Not in Master:  {len(not_in_m)}   (REVIEW)

Reports written to project folder.
Run the generated delete script when ready.
""")


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _add_days_full(p):
    g = p.add_mutually_exclusive_group()
    g.add_argument("--days", type=float, default=1,
                   help="Process files modified in last N days (default: 1)")
    g.add_argument("--full", action="store_true",
                   help="Full library scan")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="dj",
        description="DJ Library Tools — manage Master, dedup, sync to Serato/Rekordbox.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # pipeline
    p_pipe = sub.add_parser("pipeline", help="Full pipeline: organize→rename→dedup→sync")
    _add_days_full(p_pipe)
    p_pipe.add_argument("--no-serato",    action="store_true")
    p_pipe.add_argument("--no-rekordbox", action="store_true")
    p_pipe.set_defaults(func=cmd_pipeline)

    # organize
    p_org = sub.add_parser("organize", help="Move non-audio files to _meta")
    _add_days_full(p_org)
    p_org.set_defaults(func=cmd_organize)

    # rename
    p_ren = sub.add_parser("rename", help="Rename files to Artist - Title.ext")
    _add_days_full(p_ren)
    p_ren.set_defaults(func=cmd_rename)

    # dedup
    p_dd = sub.add_parser("dedup", help="Deduplicate files in Master")
    _add_days_full(p_dd)
    p_dd.set_defaults(func=cmd_dedup)

    # sync
    p_sync = sub.add_parser("sync", help="Sync Master to DJ apps")
    p_sync.add_argument("target", choices=["serato", "rekordbox", "all"])
    p_sync.set_defaults(func=cmd_sync)

    # compare
    p_cmp = sub.add_parser("compare", help="Compare old folders to Master")
    p_cmp.add_argument("dirs", nargs="*", help="Old directories to scan")
    p_cmp.add_argument("--md5", action="store_true",
                       help="Use MD5 hash instead of tag matching")
    p_cmp.set_defaults(func=cmd_compare)

    return parser


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = build_parser()
    args   = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
