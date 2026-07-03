# Master Library → Serato + Rekordbox

**Goal:** Master holds songs on the NAS. Local mirrors feed Serato and Rekordbox. Run `refresh` before opening Rekordbox.

---

## Before opening Rekordbox (Mac)

Rekordbox must read from the **local** folder, not the NAS. SMB is unreliable and causes "problem loading" on many tracks.

```bash
# Mount NAS, then:
python ~/dev/dj-library-tools/dj.py refresh
```

This pulls new/changed files from NAS Master → `~/Music/RekordboxMusic`, retries over flaky SMB, and reports any unreadable NAS files.

**One-time Rekordbox setup:** File → Add to Collection → `~/Music/RekordboxMusic`. Do not point Rekordbox at the NAS.

**Gigs (CDJ + USB):** Prep in Rekordbox on the laptop, then Export to USB. The CDJ reads the export, not the NAS.

---

## Quick Start

```bash
# 1. Copy new music into NewMusic (or Master)
# 2. Run pipeline (incremental - last 24 hours, default):
python ~/dev/dj-library-tools/dj.py pipeline

# Or for a different window:
python ~/dev/dj-library-tools/dj.py pipeline --days 2
python ~/dev/dj-library-tools/dj.py pipeline --full
python ~/dev/dj-library-tools/dj.py pipeline --no-rekordbox

# Refresh local Rekordbox mirror only (no organize/rename/dedup):
python ~/dev/dj-library-tools/dj.py refresh

# Full mirror sync (also deletes removed files from local):
python ~/dev/dj-library-tools/dj.py sync rekordbox
```

**3. Open Rekordbox** after `refresh`. Restart Serato if you ran a Serato sync.

**First time or periodically:** Run `--full` once to build the hash library. Then `--days 1` (default) is fast for daily adds.

**macOS:** Install GNU rsync for accented filenames: `brew install rsync`

---

## Incremental vs Full

| Mode | When | Speed |
|------|------|-------|
| `--days 1` (default) | Daily adds (last 24 hrs) | Fast |
| `--days N` | Last N days | Varies |
| `--full` | Build/rebuild hash lib, full dedup | Slow (10k+ files) |

Hash library (`Master/_meta/hash_library.json`) stores MD5→path for known files. Incremental only hashes new files and checks against it.

---

## Structure

| Location | Contents |
|----------|----------|
| **Master** (NAS) | Songs only |
| **Master/_meta** | Generated state: hash library, dedup reports (not scripts) |
| **~/dev/dj-master-meta** | Scripts and notes (this repo) |
| **Latest Import** | Serato. Synced from Master (songs only). |
| **RekordboxMusic** | Rekordbox. Synced from Master (songs only). |

---

## End-to-End Script

After copying files into Master:

```bash
~/dev/dj-master-meta/master_to_serato.sh
```

Steps: organize → rename → dedup → sync Serato → sync Rekordbox.

---

## Manual Steps (if needed)

| Task | Command |
|------|---------|
| Organize | `python dj.py organize` |
| Rename | `python dj.py rename` |
| Dedup | `python dj.py dedup` then review `Master/_meta/delete_duplicates.sh` |
| Sync Serato | `python dj.py sync serato` |
| Sync Rekordbox | `python dj.py sync rekordbox` |
| Refresh local (before Rekordbox) | `python dj.py refresh` |

---

## One-Time Setup

See [notes/SETUP.md](notes/SETUP.md).

---

## Renaming Cleanup (Serato/Rekordbox)

After renaming files Serato already knew: Library → filter Missing → Remove from Crates.

---

## Folder Roles

| Folder | Purpose |
|--------|---------|
| Master | Single source. Songs only. New music lands here. |
| Master/_meta | Runtime dedup state on NAS. Excluded from sync. |
| ~/dev/dj-master-meta | Scripts and documentation. |
| Latest Import | Serato. Music only. |
| RekordboxMusic | Rekordbox. Music only. |
