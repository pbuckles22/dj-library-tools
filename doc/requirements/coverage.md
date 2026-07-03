# Requirement coverage matrix

Maps every user story in [product.md](product.md) to automated Tier-1 evidence or an explicit manual/Tier-2 entry.

Also maps every **public code surface** (`dj.py` CLI, `lib/` entry points used by CLI, `scripts/`) to a US ID or an **internal** note — no behavior that exists only in code.

**Legend:** `auto` = Tier-1 pytest · `manual` = live NAS / user action · `backlog` = not built · `internal` = no product surface (ops/analysis/dev only)

| US ID | Status | Evidence |
|-------|--------|----------|
| US-CUT-01 | Built | auto: `tests/test_cuts.py`, `tests/test_cli_freeze_cuts.py` · manual: NAS apply |
| US-CUT-02 | Built | auto: `tests/test_cuts.py`, `tests/test_cli_freeze_cuts.py` · manual: NAS apply + approval · `--mode strict` = internal only |
| US-PIPE-01 | Done | auto: `tests/test_newmusic.py`, `tests/test_cli_pipeline.py`, `tests/test_cli_commands.py` · manual: restart Serato |
| US-TAG-01 | Done | auto: `tests/test_tag.py` · ops evidence in handoff |
| US-SHAZ-01 | Backlog | auto: stage only (`tests/test_shazam_queue.py`) · manual: listen/tag batches |
| US-SHAZ-02 | Backlog | backlog — not built |
| US-QUAL-01 | Done | auto: `tests/test_bitrate_audit.py` · ops evidence |
| US-QUAL-02 | Backlog | manual only |
| US-QUAL-03 | Backlog | backlog — not built |
| US-QUAL-04 | Backlog | manual only |
| US-CLEAN-01 | Done | auto: `tests/test_cleanup.py` · ops evidence |
| US-CLEAN-02 | Backlog | manual only |
| US-CLEAN-03 | Done | auto: `tests/test_relocate.py`, `tests/test_cli_commands.py` |
| US-OLD-01 | Backlog | manual only |
| US-OLD-02 | Done | auto: `tests/test_compare.py` · ops evidence |
| US-SYNC-01 | Built | auto: `tests/test_sync_refresh.py`, `tests/test_cli_commands.py` · manual: restart Rekordbox |
| US-SYNC-02 | Done | auto: `tests/test_sync_refresh.py`, `tests/test_cli_pipeline.py` · manual: Serato drives |
| US-ENG-01..05 | Backlog | backlog |
| US-ENG-06 | Done | auto: full Tier-1 suite + CI |
| US-ENG-07..08 | Backlog | backlog |
| US-ENG-09 | Done | `pytest --cov=lib --cov=dj` → **81%** |
| US-FREEZE-01 | Done | auto: `tests/test_freeze.py`, `tests/test_cli_freeze_cuts.py` |
| US-FREEZE-02 | Done | auto: `tests/test_freeze.py` |
| US-CLASH-01 | Done | auto: `tests/test_staging_clash.py` |
| US-NAS-01 | Done | auto: `tests/test_config.py` · manual: launchd on Mac |
| US-USB-01 | Done | auto: `tests/test_config.py` · manual: volume label |

## Orphan check

Every US ID in product.md appears above. Backlog stories without code are listed as `backlog` (requirement known; no orphan). Manual-only criteria are labeled `manual` on the acceptance criteria in product.md.

## Code surface inventory (code → docs)

### `dj.py` CLI

| Command / flags | US ID | Notes |
|-----------------|-------|-------|
| `pipeline` | US-PIPE-01 | Default Serato sync; Rekordbox opt-in |
| `pipeline --days` / `--full` | US-PIPE-01 | Scope for organize/tag/rename/dedup |
| `pipeline --from STEP` | US-PIPE-01 | Steps: import, organize, tag, rename, dedup, sync, clear |
| `pipeline --no-serato` | US-PIPE-01 / US-SYNC-02 | |
| `pipeline --no-rekordbox` | US-PIPE-01 / US-SYNC-01 | Preferred daily flag |
| `pipeline --no-newmusic` | US-PIPE-01 | Skip ingest + clear |
| `pipeline --no-tag` | US-PIPE-01 / US-TAG-01 | |
| `organize` | US-PIPE-01 / US-FREEZE-02 | Standalone pipeline step |
| `rename` | US-PIPE-01 / US-FREEZE-02 | Standalone pipeline step |
| `dedup` / `--full` / `--days` | US-PIPE-01 / US-FREEZE-02 | MD5 hash-library dedup |
| `sync serato` | US-SYNC-02 | Primary |
| `sync rekordbox` | US-SYNC-01 | Legacy opt-in |
| `sync all` | US-SYNC-01 + US-SYNC-02 | |
| `pull` / `--dry-run` / `--prune` | US-SYNC-01 | NAS Master → local Rekordbox |
| `refresh` (default `--target serato`) | US-SYNC-02 | Pull + verify; `--retries` |
| `refresh --target rekordbox` | US-SYNC-01 | |
| `freeze status` / `mark-all` / `mark` / `unmark` | US-FREEZE-01 | |
| `audit bitrates` | US-QUAL-01 | Report only by default |
| `audit bitrates --move-shazam` | US-QUAL-01 | |
| `audit bitrates --tier-cleanup` | US-QUAL-01 | |
| `audit bitrates --dry-run` | US-QUAL-01 | |
| `cleanup` / `--dry-run` | US-CLEAN-01 | |
| `shazam stage` / `--dry-run` | US-SHAZ-01 | |
| `shazam import` | US-SHAZ-02 | **Not built** (backlog) |
| `relocate` / `--dry-run` | US-CLEAN-03 | |
| `tag` / `--days` / `--full` / `--dry-run` / `--limit` | US-TAG-01 | |
| `cuts standardize` | US-CUT-01 | |
| `cuts dedupe` (default `--mode narrow`) | US-CUT-02 | Product policy |
| `cuts dedupe --mode strict` | **internal** | Experimental; not product policy |
| `cuts dedupe --apply` | US-CUT-02 | Default is dry-run report |
| `compare` / `--md5` | US-OLD-02 | Reports feed US-OLD-01 manual review |
| `audit transcodes` | US-QUAL-03 | **Not built** (backlog) |

### `lib/` public entry points (CLI-facing)

| Module | Entry points | US ID |
|--------|--------------|-------|
| `lib/config.py` | `load`, `require_master`, getters, `ensure_nas_link` | US-NAS-01, US-USB-01 |
| `lib/staging.py` | `import_new_music` | US-PIPE-01, US-CLASH-01 |
| `lib/newmusic.py` | `ingest`, `clear_staging` | US-PIPE-01, US-CLASH-01 |
| `lib/organize.py` | `organize` | US-PIPE-01, US-FREEZE-02 |
| `lib/rename.py` | `rename_by_tags` | US-PIPE-01, US-FREEZE-02 |
| `lib/dedup.py` | `dedup`, hash lib helpers | US-PIPE-01, US-FREEZE-02 |
| `lib/tag.py` | `tag_files` | US-TAG-01 |
| `lib/sync.py` | `sync_serato`, `sync_rekordbox`, `pull_new`, `refresh_local` | US-SYNC-01, US-SYNC-02 |
| `lib/freeze.py` | `mark_done`, `unmark`, `status`, `mark_all`, `is_done` | US-FREEZE-01, US-FREEZE-02 |
| `lib/bitrate_audit.py` | `audit_bitrates`, tier helpers | US-QUAL-01 |
| `lib/cleanup.py` | `clean_my_music` | US-CLEAN-01 |
| `lib/relocate.py` | `relocate_from_master`, `classify_for_relocate` | US-CLEAN-03 |
| `lib/shazam_queue.py` | `stage_shazam_queue` | US-SHAZ-01 |
| `lib/cuts.py` | `standardize_cuts`, `dedupe_cuts` | US-CUT-01, US-CUT-02 |
| `lib/compare.py` | `compare_tags`, `compare_md5` | US-OLD-02 |

Private helpers (`_*`) are implementation detail — no product story required.

### `scripts/`

| Script | US ID / class | Notes |
|--------|---------------|-------|
| `scripts/update-nas-link.sh` | US-NAS-01 | Stable `DJ_Master_Link` |
| `scripts/install-nas-link-launchd.sh` | US-NAS-01 | Install watcher |
| `scripts/launchd/local.dj.nas-link.plist` | US-NAS-01 | launchd template |
| `scripts/shazam_bitrates.py` | **internal** | One-off bitrate ops helper |
| `scripts/master_bitrate_report.py` | **internal** | One-off report |
| `scripts/analyze_cuts.py` | **internal** | Cut-policy analysis |
| `scripts/simulate_cut_policy.py` | **internal** | Cut-policy simulation |
| `scripts/install-hooks.sh` | **internal** | Dev git hooks |
| `scripts/prepare-commit-msg` | **internal** | Dev commit-msg hook |

## Run

```bash
python -m pytest -q
```
