#!/usr/bin/env python3
"""
DJ Library Tools — cross-platform CLI.

Usage:
  python dj.py pipeline              # newmusic → organize → rename → dedup → sync → clear NewMusic
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

  python dj.py tag                   # AcoustID tag untagged files (last 24h)
  python dj.py tag --full            # tag all untagged in Master
  python dj.py tag --dry-run         # preview matches without writing

  python dj.py shazam stage          # move Shazam-queue files to My Music/Shazam

  python dj.py cuts standardize --full   # intro aliases -> Intro Clean
  python dj.py cuts dedupe --full          # dry-run narrow dedupe report
  python dj.py cuts dedupe --full --apply  # delete extras (after review)
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
from lib import newmusic as newmusic_mod
from lib import tag as tag_mod
from lib import relocate as relocate_mod
from lib import shazam_queue as shazam_mod
from lib import bitrate_audit as bitrate_mod
from lib import cleanup as cleanup_mod
from lib import cuts as cuts_mod


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

    newmusic = cfg.get_newmusic()
    steps = 8
    if args.no_newmusic:
        steps -= 1
    if args.no_tag:
        steps -= 1
    step = 0

    if not args.no_newmusic:
        step += 1
        print(f"\n[{step}/{steps}] Ingesting NewMusic → Master...")
        newmusic_mod.ingest(master, newmusic)

    step += 1
    print(f"\n[{step}/{steps}] Organizing...")
    organize_mod.organize(master, days=None if full else days)

    if not args.no_tag:
        step += 1
        print(f"\n[{step}/{steps}] Tagging (AcoustID)...")
        api_key = cfg.get_acoustid_key()
        if api_key:
            tag_mod.tag_files(
                master,
                api_key,
                days=None if full else days,
            )
        else:
            print("  Skipped — acoustid_api_key not set in config.local.json")

    step += 1
    print(f"\n[{step}/{steps}] Renaming...")
    rename_mod.rename_by_tags(master, days=None if full else days)

    step += 1
    print(f"\n[{step}/{steps}] Deduplicating...")
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
        step += 1
        print(f"\n[{step}/{steps}] Syncing → Serato...")
        sync_mod.sync_serato(master, cfg.get_serato())
    else:
        step += 1
        print(f"\n[{step}/{steps}] Serato sync skipped.")

    if not args.no_rekordbox:
        step += 1
        print(f"\n[{step}/{steps}] Syncing → Rekordbox...")
        sync_mod.sync_rekordbox(master, cfg.get_rekordbox())
    else:
        step += 1
        print(f"\n[{step}/{steps}] Rekordbox sync skipped.")

    if not args.no_newmusic:
        step += 1
        print(f"\n[{step}/{steps}] Clearing NewMusic staging...")
        hash_lib = dedup_mod.load_hash_lib(meta)
        newmusic_mod.clear_staging(master, newmusic, hash_lib=hash_lib)

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


def cmd_audit(args):
    master = cfg.require_master()
    bitrate_mod.audit_bitrates(
        master,
        move_shazam=args.move_shazam,
        tier_cleanup=args.tier_cleanup,
        dry_run=args.dry_run,
    )


def cmd_cleanup(args):
    music = cfg.get_master().parent
    cleanup_mod.clean_my_music(music, dry_run=args.dry_run)


def cmd_shazam(args):
    master = cfg.require_master()
    if args.action == "stage":
        dest = shazam_mod.default_shazam_dir(master)
        shazam_mod.stage_shazam_queue(master, dest=dest, dry_run=args.dry_run)
    else:
        print(f"Unknown shazam action: {args.action}")
        sys.exit(1)


def cmd_relocate(args):
    master = cfg.require_master()
    dest = master.parent
    print(f"Relocating WAV / Persian / comedy from Master -> {dest}")
    if args.dry_run:
        print("  DRY RUN — no files will be moved.")
    moved, errors = relocate_mod.relocate_from_master(
        master, dest=dest, dry_run=args.dry_run
    )
    print(f"\n{'Would move' if args.dry_run else 'Moved'}: {len(moved)}  Errors: {len(errors)}")


def cmd_tag(args):
    master = cfg.require_master()
    api_key = cfg.require_acoustid_key()
    days = args.days if not args.full else None
    tag_mod.tag_files(
        master,
        api_key,
        days=days,
        dry_run=args.dry_run,
        limit=args.limit,
    )


def cmd_cuts(args):
    master = cfg.require_master()
    if args.action == "standardize":
        days = args.days if not args.full else None
        cuts_mod.standardize_cuts(master, days=days, dry_run=args.dry_run)
    elif args.action == "dedupe":
        days = args.days if not args.full else None
        cuts_mod.dedupe_cuts(
            master,
            mode=args.mode,
            days=days,
            dry_run=not args.apply,
        )
    else:
        print(f"Unknown cuts action: {args.action}")
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
    p_pipe.add_argument("--no-newmusic",  action="store_true",
                        help="Skip NewMusic ingest and staging clear")
    p_pipe.add_argument("--no-tag", action="store_true",
                        help="Skip AcoustID tagging step")
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

    # audit
    p_audit = sub.add_parser("audit", help="Library audit reports")
    p_audit_sub = p_audit.add_subparsers(dest="audit_cmd", required=True)
    p_br = p_audit_sub.add_parser("bitrates", help="Report <=128 kbps; optional move to Shazam")
    p_br.add_argument("--move-shazam", action="store_true",
                      help="Move <=128 kbps files from Master to Shazam folder")
    p_br.add_argument("--tier-cleanup", action="store_true",
                      help="Delete <=160 kbps; move 161-192 kbps to LowQuality folder")
    p_br.add_argument("--dry-run", action="store_true")
    p_br.set_defaults(func=cmd_audit)

    # cleanup
    p_clean = sub.add_parser("cleanup", help="Remove junk/empty dirs under My Music")
    p_clean.add_argument("--dry-run", action="store_true")
    p_clean.set_defaults(func=cmd_cleanup)

    # shazam
    p_shazam = sub.add_parser("shazam", help="Shazam manual-tagging helpers")
    p_shazam_sub = p_shazam.add_subparsers(dest="action", required=True)
    p_shazam_stage = p_shazam_sub.add_parser(
        "stage", help="Move Shazam-queue files from Master to My Music/Shazam"
    )
    p_shazam_stage.add_argument("--dry-run", action="store_true",
                                help="Preview moves without relocating files")
    p_shazam_stage.set_defaults(func=cmd_shazam)

    # relocate
    p_reloc = sub.add_parser(
        "relocate",
        help="Move WAV / Persian / comedy from Master to My Music (parent)",
    )
    p_reloc.add_argument("--dry-run", action="store_true",
                         help="Preview moves without relocating files")
    p_reloc.set_defaults(func=cmd_relocate)

    # tag
    p_tag = sub.add_parser("tag", help="Tag untagged files via AcoustID")
    _add_days_full(p_tag)
    p_tag.add_argument("--dry-run", action="store_true",
                       help="Preview matches without writing tags")
    p_tag.add_argument("--limit", type=int, default=None,
                       help="Process at most N files (for testing)")
    p_tag.set_defaults(func=cmd_tag)

    # cuts
    p_cuts = sub.add_parser("cuts", help="Standardize cut tags; dedupe same-song versions")
    p_cuts_sub = p_cuts.add_subparsers(dest="action", required=True)
    p_cuts_std = p_cuts_sub.add_parser(
        "standardize", help="Rename intro aliases to canonical Intro Clean"
    )
    _add_days_full(p_cuts_std)
    p_cuts_std.add_argument("--dry-run", action="store_true")
    p_cuts_std.set_defaults(func=cmd_cuts)
    p_cuts_dd = p_cuts_sub.add_parser(
        "dedupe", help="Remove alternate cuts when Intro Clean exists (narrow)"
    )
    _add_days_full(p_cuts_dd)
    p_cuts_dd.add_argument(
        "--mode", choices=["narrow", "strict"], default="narrow",
        help="narrow: only when intro cut exists (default)",
    )
    p_cuts_dd.add_argument(
        "--apply", action="store_true",
        help="Delete files (default is dry-run report only)",
    )
    p_cuts_dd.set_defaults(func=cmd_cuts)

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
