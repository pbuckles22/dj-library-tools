# Requirement coverage matrix

Maps every user story in [product.md](product.md) to automated Tier-1 evidence or an explicit manual/Tier-2 entry.

**Legend:** `auto` = Tier-1 pytest · `manual` = live NAS / user action · `backlog` = not built

| US ID | Status | Evidence |
|-------|--------|----------|
| US-CUT-01 | Built | auto: `tests/test_cuts.py` · manual: NAS apply |
| US-CUT-02 | Built | auto: `tests/test_cuts.py` · manual: NAS apply + approval |
| US-PIPE-01 | Done | auto: `tests/test_newmusic.py`, `tests/test_cli_pipeline.py` · manual: restart Serato |
| US-TAG-01 | Done | auto: `tests/test_tag.py` · ops evidence in handoff |
| US-SHAZ-01 | Backlog | auto: stage only (`tests/test_shazam_queue.py`) · manual: listen/tag batches |
| US-SHAZ-02 | Backlog | backlog — not built |
| US-QUAL-01 | Done | auto: `tests/test_bitrate_audit.py` · ops evidence |
| US-QUAL-02 | Backlog | manual only |
| US-QUAL-03 | Backlog | backlog — not built |
| US-QUAL-04 | Backlog | manual only |
| US-CLEAN-01 | Done | ops evidence |
| US-CLEAN-02 | Backlog | manual only |
| US-OLD-01 | Backlog | manual only |
| US-OLD-02 | Done | auto: `tests/test_compare.py` · ops evidence |
| US-SYNC-01 | Built | auto: `tests/test_sync_refresh.py` · manual: restart Rekordbox |
| US-SYNC-02 | Done | auto: `tests/test_sync_refresh.py`, `tests/test_cli_pipeline.py` · manual: Serato drives |
| US-ENG-01..05 | Backlog | backlog |
| US-ENG-06 | Done | auto: full Tier-1 suite + CI |
| US-ENG-07..08 | Backlog | backlog |
| US-ENG-09 | Done | `pytest --cov=lib --cov=dj` → **81%** |
| US-FREEZE-01 | Done | auto: `tests/test_freeze.py` |
| US-FREEZE-02 | Done | auto: `tests/test_freeze.py` |
| US-CLASH-01 | Done | auto: `tests/test_staging_clash.py` |
| US-NAS-01 | Done | auto: `tests/test_config.py` · manual: launchd on Mac |
| US-USB-01 | Done | auto: `tests/test_config.py` · manual: volume label |

## Orphan check

Every US ID in product.md appears above. Backlog stories without code are listed as `backlog` (requirement known; no orphan). Manual-only criteria are labeled `manual` on the acceptance criteria in product.md.

## Run

```bash
python -m pytest -q
```
