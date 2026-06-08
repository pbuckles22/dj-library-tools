# One-Time Setup

## 1. Create Master folder on NAS

```bash
mkdir -p "/Volumes/buckles/My.Documents/My Music/Master"
mkdir -p "/Volumes/buckles/My.Documents/My Music/Master/_meta"
```

## 2. Seed Master from Latest Import

```bash
rsync -av "$HOME/Music/_Serato_/Imported/Latest Import/" \
  "/Volumes/buckles/My.Documents/My Music/Master/"
```

(Excludes `_meta` if present — rsync copies songs only from the import folder.)

## 3. Add music from other sources

```bash
# DJ City downloads
cp -n ~/Documents/DJ\ Collection/* \
  "/Volumes/buckles/My.Documents/My Music/Master/" 2>/dev/null

# NewMusic staging folder
rsync -av "/Volumes/buckles/My.Documents/My Music/NewMusic/" \
  "/Volumes/buckles/My.Documents/My Music/Master/"
```

The `-n` on `cp` skips overwrites. rsync naturally skips identical files.

## 4. Initial dedup (full scan)

```bash
cd "/Volumes/buckles/My.Documents/My Music/Master"
python3 ~/dev/dj-master-meta/find_duplicates.py . --full
# Review Master/_meta/duplicate_report.txt, then:
bash _meta/delete_duplicates.sh
# Re-run until 0 duplicates
```

## 5. Rekordbox

File → Add to Collection → `~/Music/RekordboxMusic`

After first sync:

```bash
~/dev/dj-master-meta/sync_master_to_rekordbox.sh
```

## 6. Point DJ City to Master

In DJ City Download Manager preferences, set download location to:

```
/Volumes/buckles/My.Documents/My Music/Master
```

Or a subfolder like `Master/From DJ City` if you want downloads grouped.

## 7. Install Python deps (once)

```bash
pip3 install -r ~/dev/dj-master-meta/requirements.txt
```

Needed for `rename_by_tags.py` (mutagen). Dedup and organize use stdlib only.

---

## Ongoing: when you get new music

1. **DJ City** → downloads land in Master (if configured), or copy manually
2. **NewMusic / other sources** → copy into Master
3. Run `~/dev/dj-master-meta/master_to_serato.sh` (default: last 24h)

rsync only copies what's new or changed. If you deduped and removed files, `--delete` removes them from Latest Import and RekordboxMusic too.

After sync: restart Serato/Rekordbox or use Library → Reload.
