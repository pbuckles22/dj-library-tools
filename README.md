# DJ Library Tools

Cross-platform Python CLI for managing a **Master** DJ music library on NAS and syncing to **Serato** (primary). Rekordbox is sunset / opt-in.

**Works on macOS and Windows.** No bash required for core commands.

**Continuing work?** Read [AGENT_HANDOFF.md](AGENT_HANDOFF.md) first. Requirements: [doc/requirements/product.md](doc/requirements/product.md) · [coverage.md](doc/requirements/coverage.md).

---

## Quick start

```bash
# Install deps (once)
pip install -r requirements.txt

# After dropping new music into NewMusic:
python dj.py pipeline --no-rekordbox   # last 24 hours (default); Serato sync
python dj.py pipeline --full           # full library scan

# Before opening Serato:
python dj.py refresh
```

On Windows, run from PowerShell or CMD with `python dj.py ...`

---

## Commands

| Command | What it does | Story |
|---------|--------------|-------|
| `python dj.py pipeline` | import → organize → tag → rename → dedup → sync → clear NewMusic | US-PIPE-01 |
| `python dj.py organize` | Move non-audio files in Master root into `_meta` | US-PIPE-01 |
| `python dj.py rename` | Rename files to `Artist - Title.ext` from tags | US-PIPE-01 |
| `python dj.py dedup` | MD5 dedup within Master (keeps highest bitrate) | US-PIPE-01 |
| `python dj.py tag` | AcoustID tag untagged files | US-TAG-01 |
| `python dj.py sync serato` | Sync Master → Serato Latest Import | US-SYNC-02 |
| `python dj.py sync rekordbox` | Mirror sync Master → RekordboxMusic (legacy) | US-SYNC-01 |
| `python dj.py sync all` | Sync to both | US-SYNC-01/02 |
| `python dj.py refresh` | **Before Serato:** pull NAS → local mirror, verify (default `--target serato`) | US-SYNC-02 |
| `python dj.py pull` | Pull only to Rekordbox local; `--dry-run`, `--prune` | US-SYNC-01 |
| `python dj.py freeze status` | Frozen vs total track count | US-FREEZE-01 |
| `python dj.py freeze mark-all` | Freeze entire Master (one-time) | US-FREEZE-01 |
| `python dj.py freeze mark/unmark <paths>` | Freeze or unfreeze specific files | US-FREEZE-01 |
| `python dj.py audit bitrates` | Report low bitrates; optional `--move-shazam` / `--tier-cleanup` | US-QUAL-01 |
| `python dj.py cleanup` | Remove junk/empty dirs under My Music | US-CLEAN-01 |
| `python dj.py relocate` | Move WAV / Persian / comedy out of Master | US-CLEAN-03 |
| `python dj.py shazam stage` | Move Shazam-queue files to `My Music/Shazam` | US-SHAZ-01 |
| `python dj.py cuts standardize` | Intro aliases → `(Intro Clean)` | US-CUT-01 |
| `python dj.py cuts dedupe` | Narrow cut dedupe (dry-run default; `--apply` deletes) | US-CUT-02 |
| `python dj.py compare <dirs>` | Tag-based compare: old folders vs Master | US-OLD-02 |
| `python dj.py compare --md5 <dirs>` | MD5-based compare (exact byte match) | US-OLD-02 |

### Pipeline flags

| Flag | Meaning |
|------|---------|
| `--days N` | Only process files modified in last N days (default: 1) |
| `--full` | Full library scan |
| `--from STEP` | Start at STEP: import, organize, tag, rename, dedup, sync, clear |
| `--no-serato` | Skip Serato sync |
| `--no-rekordbox` | Skip Rekordbox sync (preferred daily) |
| `--no-newmusic` | Skip NewMusic ingest and staging clear |
| `--no-tag` | Skip AcoustID tagging step |

### Other common flags

| Flag | Commands | Meaning |
|------|----------|---------|
| `--dry-run` | tag, pull, cleanup, relocate, shazam stage, audit, cuts | Preview without changing files |
| `--apply` | `cuts dedupe` | Actually delete (default is report-only) |
| `--target serato\|rekordbox` | refresh | Local mirror to refresh (default: serato) |
| `--retries N` | refresh | Rsync retry count over flaky SMB (default: 3) |

**Business rules:** Master is sacred. Frozen tracks are never renamed, organized, or deleted by pipeline. On NewMusic clash, **incoming loses** (deleted from NewMusic, logged).

---

## Setup

### 1. Install Python deps

```bash
pip install -r requirements.txt
# Dev / tests:
pip install -r requirements-dev.txt
```

### 2. Configure paths

Edit `config.json` with your NAS and local paths, **or** create `config.local.json` (gitignored) to override without touching the committed config.

On Mac, prefer stable link paths (`~/Music/DJ_Master_Link/...`) — see [AGENT_HANDOFF.md](AGENT_HANDOFF.md).

On Windows, map the NAS share (buckles) to a drive letter (e.g. `Z:`) or use a UNC path.

### 3. (macOS) Stable NAS link

```bash
bash scripts/update-nas-link.sh
# Optional auto-heal on remount:
bash scripts/install-nas-link-launchd.sh
```

GNU rsync recommended for accented filenames: `brew install rsync`.

### 4. Sync tools

(macOS) rsync. (Windows) robocopy — both built-in or brew-installable; no extra install required for robocopy.

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
├── requirements-dev.txt
├── lib/                # Library modules (see coverage.md inventory)
├── scripts/            # NAS link, launchd, internal analysis helpers
├── tests/              # Tier 1 blackbox tests
├── doc/requirements/   # product.md + coverage.md
└── notes/              # WORKFLOW, SERATO_SETUP, DEDUP_OLD_LIBRARY, …
```

---

## Runtime state (on NAS, not versioned)

`Master/_meta/` holds generated state. Safe to delete and rebuild with `python dj.py dedup --full` (hash library only; freeze manifest is separate).

| File | Purpose |
|------|---------|
| `hash_library.json` | MD5 → path + bitrate cache |
| `frozen.json` | Freeze lock manifest |
| `duplicate_report.txt` | Last MD5 dedup report |
| `cut_dedup_report.txt` | Last cut-policy dedupe report |
| `rejected_imports.log` | Clash policy rejections |
| `delete_duplicates.sh` | Generated rm script (MD5 dedup) |

---

## Tests

```bash
python -m pytest -q
```

See [TEST_PLAN.md](TEST_PLAN.md).
