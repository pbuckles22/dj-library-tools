# Folder Layout

## ~/dev/dj-master-meta (this project)

Versioned scripts and notes. Edit and run from here.

```
dj-master-meta/
├── README.md
├── WORKFLOW.md
├── config.sh              # MASTER, Serato, Rekordbox paths
├── requirements.txt
├── master_to_serato.sh    # main pipeline
├── pipeline_pre_rekordbox.sh
├── find_duplicates.py
├── organize_master.py
├── rename_by_tags.py
├── sync_master_to_serato.sh
├── sync_master_to_rekordbox.sh
├── backup/                # Local copy of NAS hash_library.json (gitignored)
└── notes/
    ├── SETUP.md
    └── FOLDER_LAYOUT.md
```

## Master/_meta on NAS (runtime only)

Generated when you run dedup. Safe to delete and rebuild with `--full`.

| File | Purpose |
|------|---------|
| `hash_library.json` | MD5 → path + bitrate cache |
| `duplicate_report.txt` | Human-readable list of files to remove |
| `delete_duplicates.sh` | Generated rm script (review before running) |

Non-audio files dropped in Master root are also moved here by `organize_master.py`.

## Master (NAS)

Flat song files at the top level. No subfolders for genres — DJ apps handle crates/playlists.

Excluded from Serato/Rekordbox sync: `_meta/`, `.DS_Store`, `Thumbs.db`, `Desktop.ini`.
