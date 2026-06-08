# Deduplicating the Old NAS Library

## The situation

| Location | Files | Role |
|----------|-------|------|
| `My Music/Master` | ~8,161 | **Source of truth** — clean DJ library |
| `My Music/` old folders (A–Z, artist folders, iTunes…) | ~18,844 | Old personal library, 2004–2022 |
| `My Music/NewMusic` | ~586 | Staging — needs to be run through pipeline |
| `~/Music/RekordboxMusic` | ~6,965 | Local mirror of Master (stale, needs re-sync) |

Master was seeded from Serato (~5,214 deduped DJ tracks) and has grown since. The old folders are your pre-DJ personal library — they overlap with Master but also contain personal/non-DJ tracks that may or may not belong.

---

## Strategy

**Never delete blindly.** The old folder has 18,844 files; many are already in Master, but some may be personal tracks not in the DJ library.

Steps:

### 1. Run the comparison (read-only, safe)

```bash
python3 ~/dev/dj-master-meta/compare_to_master.py \
  "/Volumes/buckles/My.Documents/My Music/A" \
  "/Volumes/buckles/My.Documents/My Music/B" \
  ... (all the old lettered folders) \
  "/Volumes/buckles/My.Documents/My Music"   # root loose files
```

Or scan everything at once (excluding Master and NewMusic):

```bash
# Run from dj-master-meta — scans all old subdirs at once
python3 compare_to_master.py \
  "/Volumes/buckles/My.Documents/My Music/A" \
  "/Volumes/buckles/My.Documents/My Music/B" \
  "/Volumes/buckles/My.Documents/My Music/C" \
  "/Volumes/buckles/My.Documents/My Music/D" \
  "/Volumes/buckles/My.Documents/My Music/E" \
  "/Volumes/buckles/My.Documents/My Music/F" \
  "/Volumes/buckles/My.Documents/My Music/G" \
  "/Volumes/buckles/My.Documents/My Music/H" \
  "/Volumes/buckles/My.Documents/My Music/I" \
  "/Volumes/buckles/My.Documents/My Music/J" \
  "/Volumes/buckles/My.Documents/My Music/K" \
  "/Volumes/buckles/My.Documents/My Music/L" \
  "/Volumes/buckles/My.Documents/My Music/M" \
  "/Volumes/buckles/My.Documents/My Music/N" \
  "/Volumes/buckles/My.Documents/My Music/O" \
  "/Volumes/buckles/My.Documents/My Music/P" \
  "/Volumes/buckles/My.Documents/My Music/Q" \
  "/Volumes/buckles/My.Documents/My Music/R" \
  "/Volumes/buckles/My.Documents/My Music/S" \
  "/Volumes/buckles/My.Documents/My Music/T" \
  "/Volumes/buckles/My.Documents/My Music/U" \
  "/Volumes/buckles/My.Documents/My Music/V" \
  "/Volumes/buckles/My.Documents/My Music/W" \
  "/Volumes/buckles/My.Documents/My Music/X" \
  "/Volumes/buckles/My.Documents/My Music/Y" \
  "/Volumes/buckles/My.Documents/My Music/Z"
```

This is **read-only** — it only writes reports, nothing is deleted.

### 2. Review `master_compare_not_in_master.txt`

These files exist in your old library but NOT in Master. For each one, decide:
- **Add to Master** → copy the file there, then run `master_to_serato.sh --full` to dedup and sync
- **Not needed** → add it to the delete script manually (or just ignore the old folder)
- **Unsure** → leave it; you can always revisit

### 3. Delete the confirmed dupes

Once you're happy with the review:

```bash
bash ~/dev/dj-master-meta/master_compare_delete.sh
```

This removes only the files confirmed to be exact MD5 matches of something already in Master.

### 4. Process NewMusic into Master

```bash
~/dev/dj-master-meta/master_to_serato.sh --days 30
# or --full if NewMusic is older
```

### 5. Re-sync RekordboxMusic (stale)

Master has ~8,161 tracks; RekordboxMusic has ~6,965. After dedup and NewMusic processing:

```bash
~/dev/dj-master-meta/sync_master_to_rekordbox.sh
```

Restart Rekordbox → File → Update Library.

---

## What the comparison script does

- Loads Master's `hash_library.json` (fast; ~8k entries already hashed)
- MD5-hashes each file in the old folders
- Compares against Master's known hashes
- Outputs: `in_master` list, `not_in_master` list, ready-to-run delete script
- **Does not delete anything** unless you pass `--execute`
