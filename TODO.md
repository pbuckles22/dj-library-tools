# DJ Library — TODO backlog

**User stories:** [doc/requirements/product.md](doc/requirements/product.md)  
**Coverage:** [doc/requirements/coverage.md](doc/requirements/coverage.md)

**Updated:** July 2026  
**Master:** ~5,205 tracks (5060 frozen, 256+ kbps club tier) · **LowQuality:** 921 · **Shazam:** ~2k · **Serato local:** ~5059

---

## Daily / when NewMusic has files (US-PIPE-01)

- [ ] **Run pipeline** after dropping files in `My Music/NewMusic`:
  ```bash
  python dj.py pipeline --no-rekordbox
  ```
  Ingest → organize → tag → rename → dedup → Serato sync → clear NewMusic staging.

- [ ] **Restart Serato** after sync (or run `python dj.py refresh` before opening Serato).

---

## Cut policy — Now (US-CUT-01, US-CUT-02, US-SYNC-02)

Run in order on NAS:

- [ ] **US-CUT-01** Preview renames:
  ```bash
  python dj.py cuts standardize --full --dry-run
  ```
- [ ] **US-CUT-01** Apply (~526 intro alias → `(Intro Clean)`):
  ```bash
  python dj.py cuts standardize --full
  ```
- [ ] **US-CUT-02** Dry-run narrow dedupe (~594 deletes when Intro Clean exists):
  ```bash
  python dj.py cuts dedupe --full
  ```
- [ ] Review `Master/_meta/cut_dedup_report.txt` — user approves before apply
- [ ] **US-CUT-02** Apply (only after approval):
  ```bash
  python dj.py cuts dedupe --full --apply
  ```
- [ ] **US-SYNC-02** Sync Serato and refresh local mirror:
  ```bash
  python dj.py sync serato
  python dj.py refresh
  ```

**Do not** run `cuts dedupe --mode strict` on Master (internal/experimental only).

---

## Serato setup (US-SYNC-02) — manual

See [notes/SERATO_SETUP.md](notes/SERATO_SETUP.md).

- [ ] Drives: only `~/Music/_Serato_/Imported/Latest Import`
- [ ] Remove missing entries
- [ ] Analyze all (local — no mass yellow triangles)
- [ ] Export to `/Volumes/DJ_USB` for CDJs when needed

---

## Shazam — manual tagging (you) (US-SHAZ-01)

**Folder:** `My Music/Shazam` (via `DJ_Master_Link` or NAS path)  
**List:** `Shazam/shazam_queue.txt`

- [ ] Stage queue files if needed: `python dj.py shazam stage`
- [ ] Play each file → Shazam on phone → note Artist + Title
- [ ] Write tags (Mp3tag / Serato / file properties)
- [ ] Move tagged files back to **Master**
- [ ] When a batch is done:
  ```bash
  python dj.py rename --full
  python dj.py sync serato
  ```
- [ ] Optional: export [shazam.com/myshazam](https://www.shazam.com/myshazam) CSV → ask agent to wire `dj.py shazam import` (US-SHAZ-02)

**Policy:** Shazam or verified only — no auto-tag from filename alone.

---

## Library quality (US-QUAL-02, US-QUAL-03, US-QUAL-04)

- [x] Move ≤128 kbps from Master → Shazam
- [x] Delete ≤160 kbps from Master (237 files)
- [x] Move 161–192 kbps → `My Music/LowQuality` (921 files)
- [ ] **Review LowQuality** — listen on PA; re-buy 320k from pool or delete (`LowQuality/low_quality_manifest.txt`)
- [ ] **Transcode audit** — spectral cutoff scan for fake 320k (upscaled 128k); not built yet (US-QUAL-03)
- [ ] **Fix edge cases in Master:**
  - 1 file at 32 kHz sample rate
  - 4 mono files (3× LMFAO dupes + 1 Goo Goo Dolls)
- [ ] **`python dj.py dedup --full`** after large moves — refresh hash library
- [ ] **`python dj.py sync serato`** after dedup/rename

---

## My Music folder cleanup (US-CLEAN-02)

**Goal:** Only operational folders at top level: `Master`, `NewMusic`, `Shazam`, `LowQuality`.

- [x] Delete junk / artwork / empty dirs (9,751 files, 5,436 dirs) — US-CLEAN-01
- [x] Relocate WAV / Persian / comedy out of Master — US-CLEAN-03
- [ ] **Review 34 legacy folders** still containing audio — see `Master/_meta/cleanup_report.txt`
  - **iTunes/** (~1,319 files) — biggest
  - Letter folders A–Z, `02_Pop_Iran`, `San Diego`, etc.
- [ ] Compare legacy folders vs Master → delete dupes, relocate personal
- [ ] User decision: delete remaining fishy folders after review

---

## Old NAS library (Phase 2) (US-OLD-01)

- [ ] Review **~1,951** files in `tag_compare_not_in_master.txt` (keepers / personal / non-DJ)
- [ ] Optional: re-run `python dj.py compare` on old folders if reports stale

---

## Engineering / repo (US-ENG-*)

- [x] Product backlog + coverage matrix (US + code surfaces)
- [x] Tier 1 suite green; ≥80% coverage
- [ ] Tech debt: Tier 2 pipeline tests, `lib/__init__.py`, ruff, PowerShell delete helper
- [ ] Optional: `dj.py shazam import` from Shazam CSV
- [ ] Optional: `dj.py audit transcodes` (spectral)

---

## Rekordbox (US-SYNC-01) — legacy opt-in only

- [ ] Only if still using Rekordbox: `python dj.py sync rekordbox` or `refresh --target rekordbox`
- [ ] `pull` / `pull --prune` for incremental NAS → local Rekordbox

---

## Quick reference — folders

| Folder | Purpose |
|--------|---------|
| `Master/` | Club source of truth (256+ kbps, frozen) |
| `NewMusic/` | Drop new downloads → pipeline ingests |
| `Shazam/` | ≤128 legacy + manual Shazam queue |
| `LowQuality/` | 192 kbps archive — review or replace |
| `~/Music/_Serato_/Imported/Latest Import` | Serato library root (local mirror) |
| `/Volumes/DJ_USB` | Gig export only — never library source |
| `My Music/A–Z, iTunes, …` | Legacy — pending cleanup |
