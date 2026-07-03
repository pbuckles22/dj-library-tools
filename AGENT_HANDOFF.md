# Agent handoff — DJ Library Tools

**Read this first** when continuing library, Serato, or pipeline work.

**Repo:** https://github.com/pbuckles22/dj-library-tools  
**GitHub account:** `pbuckles22`  
**Primary machine:** Mac (`~/dev/dj-library-tools`)

---

## Purpose

Python CLI to manage the **Master** DJ music library on NAS (`buckles`) and sync to **Serato** (primary). Rekordbox is sunset.

- **Source of truth:** `Master/` on NAS — flat DJ tracks
- **This repo:** scripts, config, docs (not the music files)
- **Runtime state on NAS:** `Master/_meta/` — hash library, freeze manifest, dedup reports

**Business rule:** Files already in Master (frozen / published) are sacred. New imports never alter them. On clash, **delete the incoming NewMusic file**, not Master.

---

## Current state (Mac, July 2026)

### Done

| Item | Status |
|------|--------|
| Freeze lock | **5060 tracks** marked done (`Master/_meta/frozen.json` + macOS xattr) |
| Stable NAS path | `~/Music/DJ_Master_Link` → `/Volumes/buckles*` via `scripts/update-nas-link.sh` |
| launchd auto-heal | `local.dj.nas-link` watches `/Volumes` (installed on this Mac) |
| Clash policy | Incoming NewMusic deleted on filename / frozen tag / MD5 clash |
| Pipeline skips frozen | organize / rename / dedup never touch frozen tracks |
| Rename hardening | mutagen handles closed before rename; `mark_done` after rename |
| Dedup priority | frozen > hash_lib > bitrate; never delete frozen |
| Gig USB | Formatted **exFAT**, volume **`DJ_USB`** → `/Volumes/DJ_USB` |
| Serato local mirror | **5059** tracks in `~/Music/_Serato_/Imported/Latest Import` |
| `refresh` default | Targets Serato (`--target serato` default; rekordbox opt-in) |
| Serato setup doc | [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) |

### Uncommitted work (commit before handoff if user asks)

All of the above is **local only** — not pushed. Modified/new files include:

- `dj.py`, `config.json`, `lib/freeze.py`, `lib/staging.py`, `lib/config.py`, `lib/sync.py`, `lib/rename.py`, `lib/organize.py`, `lib/dedup.py`
- `scripts/update-nas-link.sh`, `scripts/install-nas-link-launchd.sh`, `scripts/launchd/local.dj.nas-link.plist`
- `notes/SERATO_SETUP.md`, `notes/WORKFLOW.md`, `README.md`
- `doc/inbox-from-meowdoku/` — **not yet disseminated** into `doc/requirements/`

### User progress (Serato)

- Serato is installed and was pointed at NAS/USB (caused yellow triangles).
- Local sync completed; user should use **only** `Latest Import` as a Serato drive.
- Analyze may still be pending after drive cleanup.

### Known issues

| Issue | Detail |
|-------|--------|
| NAS ghost files | ~4–7 accented filenames list on SMB but cannot open (Aminé 4Eva, Tití Me Preguntó, Tiësto Click Click Click, etc.). Re-download into Master when convenient. |
| `freeze status` over SMB | Slow if it re-hashes; manifest-based status is preferred (already optimized). |
| Pipeline defaults | Still Rekordbox-on by default (`--serato` opt-in). Plan: flip to Serato-default / `--no-serato` opt-out. |
| Inbox docs | `doc/inbox-from-meowdoku/` not promoted to `doc/requirements/` yet. |
| Lexicon | Documented in plan; not wired beyond `lexicon_root` in config. |
| MeowdokuHelper | DJ files were moved here; verify Meowdoku has no remaining DJ docs if cleaning that repo. |

---

## Architecture (do not break)

```text
NewMusic (NAS)
    │  clash? → delete incoming, keep Master
    ▼
Master (NAS) ── freeze lock on published tracks
    │
    ├── python dj.py sync serato / refresh
    ▼
~/Music/_Serato_/Imported/Latest Import   ← Serato library root ONLY
    │
    ├── Serato analyze / prep
    ▼
/Volumes/DJ_USB   ← Serato export for CDJs (never library source)

Stable NAS access: ~/Music/DJ_Master_Link → /Volumes/buckles*
```

**Never** point Serato or Lexicon at `/Volumes/buckles` or the gig USB as the music library source.

---

## Commands (Mac)

```bash
cd ~/dev/dj-library-tools

# Mount NAS (buckles) in Finder first, or:
# open 'smb://chaosnas.local/buckles'

# Stable link (also auto-run by require_master / launchd)
bash scripts/update-nas-link.sh

# Freeze
python dj.py freeze status
python dj.py freeze mark-all      # one-time only — already done
python dj.py freeze mark PATH
python dj.py freeze unmark PATH

# Daily (after NewMusic drops)
python dj.py pipeline --serato --no-rekordbox

# Before Serato session
python dj.py refresh              # NAS → Latest Import (default)
python dj.py sync serato          # full mirror (uses --delete)

# Gig USB
# Export from Serato to /Volumes/DJ_USB
```

**macOS:** GNU rsync required for accented filenames: `brew install rsync` (already installed on this Mac).

---

## Config paths (`config.json`)

| Key | Mac path |
|-----|----------|
| `nas_volume` | `buckles` |
| `master` | `~/Music/DJ_Master_Link/My.Documents/My Music/Master` |
| `new_music` | `~/Music/DJ_Master_Link/My.Documents/My Music/NewMusic` |
| `serato_latest_import` | `~/Music/_Serato_/Imported/Latest Import` |
| `gig_usb` | `/Volumes/DJ_USB` |
| `lexicon_root` | same as Master via `DJ_Master_Link` |
| `rekordbox_music` | `~/Music/RekordboxMusic` (legacy) |

Overrides: `config.local.json` (gitignored).

---

## Recommended next steps (priority order)

1. **Commit** current uncommitted work (user must ask — do not commit unprompted).
2. **Serato drive cleanup (user):** Settings → Library → Drives — remove `buckles` / old USB; only `Latest Import`. Remove missing tracks. Analyze all.
3. **Flip pipeline defaults** to Serato-on / Rekordbox-off (`--no-serato`, `--rekordbox` legacy).
4. **Disseminate** `doc/inbox-from-meowdoku/` into `doc/requirements/` (freeze, stable-nas-path, serato-usb, lexicon), then delete inbox folder.
5. **Update** [notes/WORKFLOW.md](notes/WORKFLOW.md) / [README.md](README.md) fully Serato-first (partially done).
6. **Lexicon:** point library at `~/Music/DJ_Master_Link/.../Master`; document in requirements.
7. **Gig USB export:** first Serato Prepare USB / export to `/Volumes/DJ_USB` after analyze.
8. **Optional:** re-download NAS ghost files; old-library dupe cleanup (16k confirmed matches — still pending user approval).

Plan reference: `~/.cursor/plans/serato-first_dj_pipeline_0989f77e.plan.md`

---

## Serato setup checklist (user)

See [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md).

1. `python dj.py sync serato` or `refresh` (done once; re-run after new music)
2. Serato drives: **only** `~/Music/_Serato_/Imported/Latest Import`
3. Remove missing entries
4. Analyze all (local files — no mass yellow triangles)
5. Export to `/Volumes/DJ_USB` for CDJs

Yellow triangles = Serato reading NAS/USB paths. Fix drives, do not re-analyze over SMB.

---

## Agent notes

- **Master is sacred.** Never delete Master tracks without explicit user approval.
- **Frozen tracks:** never rename, organize, or delete via dedup.
- **Clash policy:** incoming loses — delete from NewMusic, log to `Master/_meta/rejected_imports.log`.
- **Do not commit:** `config.local.json`, `backup/`, `tag_compare_*`, `master_compare_*`
- **Do not commit unless user asks.**
- **TDD / Flutter rules:** N/A — standalone Python CLI

---

## Docs index

| File | Contents |
|------|----------|
| [README.md](README.md) | CLI reference (partially outdated — Rekordbox-first in places) |
| [notes/WORKFLOW.md](notes/WORKFLOW.md) | Day-to-day pipeline |
| [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md) | Local-first Serato + DJ_USB |
| [notes/SETUP.md](notes/SETUP.md) | One-time setup (partially outdated) |
| [notes/FOLDER_LAYOUT.md](notes/FOLDER_LAYOUT.md) | Scripts vs runtime state |
| [notes/DEDUP_OLD_LIBRARY.md](notes/DEDUP_OLD_LIBRARY.md) | Old NAS cleanup (pending) |
| [doc/inbox-from-meowdoku/](doc/inbox-from-meowdoku/) | Inbox to promote (freeze, NAS symlink, launchd) |
