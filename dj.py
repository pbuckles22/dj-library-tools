#!/usr/bin/env python3
"""
DJ Library Tools — cross-platform CLI.

Usage:
  python dj.py pipeline              # import NewMusic → organize → rename → dedup → Rekordbox (last 24h)
  python dj.py pipeline --full       # full library scan
  python dj.py pipeline --days 3     # last 3 days
  python dj.py pipeline --serato     # also sync Serato
  python dj.py pipeline --from sync  # skip to Rekordbox sync only
  python dj.py pipeline --no-rekordbox

  python dj.py organize              # move non-audio files to _meta
  python dj.py rename                # rename to "Artist - Title.ext"
  python dj.py dedup                 # dedup within Master (incremental)
  python dj.py dedup --full          # dedup within Master (full scan)

  python dj.py sync serato           # rsync/robocopy Master → Serato
  python dj.py sync rekordbox        # rsync/robocopy Master → Rekordbox (mirror)
  python dj.py sync all              # both

  python dj.py pull                  # pull only new/changed files NAS → local Rekordbox
  python dj.py pull --dry-run        # preview what would be pulled
  python dj.py pull --prune          # mirror (also delete removed files)

  python dj.py refresh               # run before opening Serato (pull + verify local)

  python dj.py freeze status           # show frozen vs total tracks
  python dj.py freeze mark-all         # lock entire Master library (one-time)
  python dj.py freeze mark <file>      # lock one track
  python dj.py freeze unmark <file>    # unlock one track

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
from lib import staging as staging_mod
from lib import freeze as freeze_mod


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

PIPELINE_STEPS = ("import", "organize", "rename", "dedup", "sync")


def _from_step_index(from_step: str) -> int:
    try:
        return PIPELINE_STEPS.index(from_step)
    except ValueError:
        print(f"Error: unknown --from step {from_step!r}. Use: {', '.join(PIPELINE_STEPS)}")
        sys.exit(1)


def cmd_pipeline(args):
    master = cfg.require_master()
    meta   = master / "_meta"
    meta.mkdir(exist_ok=True)

    days      = None if args.full else args.days
    full      = args.full
    from_idx  = _from_step_index(args.from_step)

    print("=" * 50)
    label = f"(from {args.from_step})" if from_idx else ""
    print(f"  DJ Pipeline {'(FULL)' if full else f'(last {days} day(s))'} {label}".rstrip())
    print("=" * 50)

    step = 0
    total = sum([
        from_idx <= PIPELINE_STEPS.index("import") and not args.no_import,
        from_idx <= PIPELINE_STEPS.index("organize"),
        from_idx <= PIPELINE_STEPS.index("rename"),
        from_idx <= PIPELINE_STEPS.index("dedup"),
        from_idx <= PIPELINE_STEPS.index("sync") and (args.serato or not args.no_rekordbox),
    ])

    if from_idx <= PIPELINE_STEPS.index("import") and not args.no_import:
        step += 1
        print(f"\n[{step}/{total}] Importing NewMusic → Master...")
        staging_mod.import_new_music(cfg.get_new_music(), master)
    elif from_idx <= PIPELINE_STEPS.index("import"):
        print("\n  NewMusic import skipped.")

    if from_idx <= PIPELINE_STEPS.index("organize"):
        step += 1
        print(f"\n[{step}/{total}] Organizing...")
        organize_mod.organize(master, days=None if full else days)

    if from_idx <= PIPELINE_STEPS.index("rename"):
        step += 1
        print(f"\n[{step}/{total}] Renaming...")
        rename_mod.rename_by_tags(master, days=None if full else days)

    if from_idx <= PIPELINE_STEPS.index("dedup"):
        step += 1
        print(f"\n[{step}/{total}] Deduplicating...")
        to_delete = dedup_mod.dedup(master, full=full, days=days)
        if to_delete:
            del_script = meta / "delete_duplicates.sh"
            print(f"  Running delete script ({len(to_delete)} files)...")
            import subprocess, platform
            if platform.system() == "Windows":
                for p in to_delete:
                    try:
                        Path(p).unlink(missing_ok=True)
                    except OSError as e:
                        print(f"  Could not delete {p}: {e}")
            else:
                subprocess.run(["bash", str(del_script)])

    if from_idx <= PIPELINE_STEPS.index("sync"):
        if args.serato:
            step += 1
            print(f"\n[{step}/{total}] Syncing → Serato...")
            sync_mod.sync_serato(master, cfg.get_serato())
        if not args.no_rekordbox:
            step += 1
            print(f"\n[{step}/{total}] Syncing → Rekordbox...")
            sync_mod.sync_rekordbox(master, cfg.get_rekordbox())
        elif not args.serato:
            print("\n  Sync skipped (use --serato and/or drop --no-rekordbox).")

    print("\n" + "=" * 50)
    parts = []
    if args.serato:              parts.append("Serato")
    if not args.no_rekordbox:    parts.append("Rekordbox")
    if parts and from_idx <= PIPELINE_STEPS.index("sync"):
        print(f"  Done. Restart {' and '.join(parts)}.")
    else:
        print("  Done.")
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


def cmd_pull(args):
    master = cfg.require_master()
    sync_mod.pull_new(master, cfg.get_rekordbox(),
                      prune=args.prune, dry_run=args.dry_run)


def cmd_refresh(args):
    master = cfg.require_master()
    target = cfg.get_serato() if args.target == "serato" else cfg.get_rekordbox()
    rc = sync_mod.refresh_local(master, target, retries=args.retries)
    sys.exit(rc)


def cmd_freeze(args):
    master = cfg.require_master()
    action = args.freeze_action
    if action == "status":
        frozen, total = freeze_mod.status(master)
        print(f"Frozen: {frozen} / {total} tracks in Master")
    elif action == "mark-all":
        print("=" * 50)
        print("  Freezing entire Master library")
        print("=" * 50)
        n = freeze_mod.mark_all(master)
        frozen, total = freeze_mod.status(master)
        print(f"\nDone. Marked {n} tracks. Frozen: {frozen} / {total}")
    elif action == "mark":
        if not args.paths:
            print("Error: provide at least one file path.")
            sys.exit(1)
        for p in args.paths:
            path = Path(p).expanduser().resolve()
            if freeze_mod.mark_done(path, master):
                print(f"  frozen: {path.name}")
            else:
                print(f"  FAILED: {path}")
    elif action == "unmark":
        if not args.paths:
            print("Error: provide at least one file path.")
            sys.exit(1)
        for p in args.paths:
            path = Path(p).expanduser().resolve()
            if freeze_mod.unmark(path, master):
                print(f"  unfrozen: {path.name}")
            else:
                print(f"  FAILED: {path}")


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
  In Master:      {len(in_m)}   ← safe to delete
  Not in Master:  {len(not_in_m)}   ← REVIEW

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
    p_pipe = sub.add_parser("pipeline", help="Full pipeline: import→organize→rename→dedup→sync")
    _add_days_full(p_pipe)
    p_pipe.add_argument("--from", dest="from_step", default="import",
                        choices=list(PIPELINE_STEPS),
                        metavar="STEP",
                        help="Start at STEP (import, organize, rename, dedup, sync)")
    p_pipe.add_argument("--no-import",    action="store_true",
                        help="Skip moving files from NewMusic into Master")
    p_pipe.add_argument("--serato",       action="store_true",
                        help="Also sync to Serato (off by default)")
    p_pipe.add_argument("--no-rekordbox", action="store_true",
                        help="Skip Rekordbox sync")
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

    # pull
    p_pull = sub.add_parser(
        "pull",
        help="Pull new/changed files from NAS Master into local Rekordbox folder")
    p_pull.add_argument("--prune", action="store_true",
                        help="Mirror: also delete local files no longer in Master")
    p_pull.add_argument("--dry-run", action="store_true",
                        help="Preview changes without copying")
    p_pull.set_defaults(func=cmd_pull)

    # refresh — run before opening Rekordbox
    p_refresh = sub.add_parser(
        "refresh",
        help="Pull NAS → local mirror; verify before opening Serato/Rekordbox")
    p_refresh.add_argument("--target", choices=["serato", "rekordbox"], default="serato",
                           help="Local mirror to refresh (default: serato)")
    p_refresh.add_argument("--retries", type=int, default=3,
                           help="Rsync retry count over flaky SMB (default: 3)")
    p_refresh.set_defaults(func=cmd_refresh)

    # freeze
    p_freeze = sub.add_parser("freeze", help="Lock processed tracks (pipeline skips them)")
    freeze_sub = p_freeze.add_subparsers(dest="freeze_action", required=True)
    p_fs = freeze_sub.add_parser("status", help="Show frozen vs total track count")
    p_fs.set_defaults(func=cmd_freeze)
    p_fa = freeze_sub.add_parser("mark-all", help="Freeze entire Master library (one-time)")
    p_fa.set_defaults(func=cmd_freeze)
    p_fm = freeze_sub.add_parser("mark", help="Freeze specific file(s)")
    p_fm.add_argument("paths", nargs="+")
    p_fm.set_defaults(func=cmd_freeze)
    p_fu = freeze_sub.add_parser("unmark", help="Unfreeze specific file(s)")
    p_fu.add_argument("paths", nargs="+")
    p_fu.set_defaults(func=cmd_freeze)

    # compare
    p_cmp = sub.add_parser("compare", help="Compare old folders to Master")
    p_cmp.add_argument("dirs", nargs="*", help="Old directories to scan")
    p_cmp.add_argument("--md5", action="store_true",
                       help="Use MD5 hash instead of tag matching")
    p_cmp.set_defaults(func=cmd_compare)

    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
