# Master Library → Serato + Rekordbox

**Goal:** Master holds songs. Scripts live in `~/dev/dj-master-meta`. Copy new music into Master, run the pipeline. Serato and Rekordbox stay in sync.

---

## Quick Start

```bash
# 1. Copy new music into Master (you do this)
# 2. Run (incremental - last 24 hours only, default):
python ~/dev/dj-library-tools/dj.py pipeline

# Or for a different window:
python ~/dev/dj-library-tools/dj.py pipeline --days 2
python ~/dev/dj-library-tools/dj.py pipeline --full
python ~/dev/dj-library-tools/dj.py pipeline --no-rekordbox
python ~/dev/dj-library-tools/dj.py pipeline --no-serato

# Sync only (no organize/rename/dedup):
python ~/dev/dj-library-tools/dj.py sync serato
python ~/dev/dj-library-tools/dj.py sync rekordbox
```

**3. Restart Serato and/or Rekordbox.** By default the main script syncs **both** apps (two full copies on disk). Use `--no-serato` or `--no-rekordbox` if you only want one local mirror.

**First time or periodically:** Run `--full` once to build the hash library. Then `--days 1` (default) is fast for daily adds.

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
