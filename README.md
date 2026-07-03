# DJ Library Tools

Cross-platform Python CLI for managing a master DJ music library and syncing to Serato and Rekordbox.

**Works on macOS and Windows.** No bash required.

**Continuing on Windows?** Read [AGENT_HANDOFF.md](AGENT_HANDOFF.md) first.

---

## Quick start

```bash
# Install deps (once)
pip install -r requirements.txt

# After dropping new music into NewMusic:
python dj.py pipeline              # last 24 hours (default)
python dj.py pipeline --full       # full library scan
python dj.py pipeline --no-rekordbox
```

On Windows, run from PowerShell or CMD with `python dj.py ...`

---

## Commands

| Command | What it does |
|---------|-------------|
| `python dj.py pipeline` | import NewMusic → organize → rename → dedup → sync Rekordbox |
| `python dj.py organize` | Move non-audio files in Master root into `_meta` |
| `python dj.py rename` | Rename files to `Artist - Title.ext` from tags |
| `python dj.py dedup` | Deduplicate within Master (keeps highest bitrate) |
| `python dj.py sync serato` | Sync Master → Serato Latest Import |
| `python dj.py sync rekordbox` | Mirror sync Master → RekordboxMusic (deletes removed) |
| `python dj.py sync all` | Sync to both |
| `python dj.py refresh` | **Before Rekordbox:** pull new files NAS → local, verify |
| `python dj.py pull` | Pull only (no retry/verify); `--dry-run`, `--prune` |
| `python dj.py compare <dirs>` | Tag-based compare: old folders vs Master |
| `python dj.py compare --md5 <dirs>` | MD5-based compare (exact byte match) |

### Flags (pipeline, organize, rename, dedup)

| Flag | Meaning |
|------|---------|
| `--days N` | Only process files modified in last N days (default: 1) |
| `--full` | Full library scan |
| `--from STEP` | Start at STEP: import, organize, rename, dedup, or sync |
| `--serato` | Also sync to Serato (off by default) |
| `--no-rekordbox` | Skip Rekordbox sync |

---

## Setup

### 1. Install Python deps

```bash
pip install -r requirements.txt
```

### 2. Configure paths

Edit `config.json` with your NAS and local paths, **or** create `config.local.json` (gitignored) to override without touching the committed config:

```json
{
  "master": {
    "mac":     "/Volumes/buckles/My.Documents/My Music/Master",
    "windows": "Z:\\My.Documents\\My Music\\Master"
  },
  "serato_latest_import": {
    "mac":     "~/Music/_Serato_/Imported/Latest Import",
    "windows": "~\\Music\\_Serato_\\Imported\\Latest Import"
  },
  "rekordbox_music": {
    "mac":     "~/Music/RekordboxMusic",
    "windows": "~\\Music\\RekordboxMusic"
  }
}
```

On Windows, map the NAS share (buckles) to a drive letter (e.g. `Z:`) or use a UNC path.

### 3. (macOS) rsync is built-in. (Windows) robocopy is built-in — no extra install needed.

---

## Deduplicating the old library

If you have an old personal library alongside Master, see [notes/DEDUP_OLD_LIBRARY.md](notes/DEDUP_OLD_LIBRARY.md).

```bash
python dj.py compare \
  "/Volumes/buckles/My.Documents/My Music/A" \
  "/Volumes/buckles/My.Documents/My Music/B" \
  ...
```

---

## Project structure

```
dj-library-tools/
├── dj.py               # CLI entry point
├── config.json         # Default paths (mac + windows)
├── config.local.json   # Machine-specific overrides (gitignored)
├── requirements.txt
├── lib/
│   ├── config.py       # Path resolution
│   ├── dedup.py        # MD5 dedup, hash library
│   ├── organize.py     # Move non-audio files to _meta
│   ├── rename.py       # Rename by ID3 tags
│   ├── sync.py         # rsync / robocopy
│   └── compare.py      # Tag or MD5 compare vs Master
├── backup/             # Local copy of hash_library.json (gitignored)
└── notes/
    ├── WORKFLOW.md
    ├── SETUP.md
    ├── FOLDER_LAYOUT.md
    └── DEDUP_OLD_LIBRARY.md
```

---

## Runtime state (on NAS, not versioned)

`Master/_meta/` holds generated state. Safe to delete and rebuild with `python dj.py dedup --full`.

| File | Purpose |
|------|---------|
| `hash_library.json` | MD5 → path + bitrate cache |
| `duplicate_report.txt` | Last dedup report |
| `delete_duplicates.sh` | Generated rm script |
