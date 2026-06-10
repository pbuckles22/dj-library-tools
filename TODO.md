# DJ Library — TODO backlog

**Updated:** June 2026  
**Master:** ~5,096 tracks (256+ kbps club tier) · **LowQuality:** 921 · **Shazam:** ~2,069

---

## Daily / when NewMusic has files

- [ ] **Run pipeline** after dropping files in `My Music/NewMusic`:
  ```powershell
  python dj.py pipeline --no-serato
  ```
  Ingest → organize → tag → rename → dedup → Rekordbox sync → clear NewMusic staging.

- [ ] **Restart Rekordbox** after sync.

---

## Shazam — manual tagging (you)

**Folder:** `\\chaosnas.local\buckles\My.Documents\My Music\Shazam`  
**List:** `Shazam\shazam_queue.txt`

- [ ] Play each file on PC → Shazam on phone → note Artist + Title.
- [ ] Write tags (Mp3tag / Rekordbox / file properties).
- [ ] Move tagged files back to **Master**.
- [ ] When a batch is done:
  ```powershell
  python dj.py rename --full
  python dj.py sync rekordbox
  ```
- [ ] Optional: export [shazam.com/myshazam](https://www.shazam.com/myshazam) CSV → ask agent to wire `dj.py shazam import`.

**Policy:** Shazam or verified only — no auto-tag from filename alone.

---

## Library quality

- [x] Move ≤128 kbps from Master → Shazam
- [x] Delete ≤160 kbps from Master (237 files)
- [x] Move 161–192 kbps → `My Music\LowQuality` (921 files)
- [ ] **Review LowQuality** — listen on PA; re-buy 320k from pool or delete (`LowQuality\low_quality_manifest.txt`)
- [ ] **Transcode audit** — spectral cutoff scan for fake 320k (upscaled 128k); not built yet
- [ ] **Fix edge cases in Master:**
  - 1 file at 32 kHz sample rate
  - 4 mono files (3× LMFAO dupes + 1 Goo Goo Dolls)
- [ ] **`python dj.py dedup --full`** after large moves — refresh hash library
- [ ] **`python dj.py sync rekordbox`** after dedup/rename

---

## My Music folder cleanup

**Goal:** Only operational folders at top level: `Master`, `NewMusic`, `Shazam`, `LowQuality`.

- [x] Delete junk / artwork / empty dirs (9,751 files, 5,436 dirs)
- [ ] **Review 34 legacy folders** still containing audio — see `Master\_meta\cleanup_report.txt`
  - **iTunes/** (~1,319 files) — biggest
  - Letter folders A–Z, `02_Pop_Iran`, `San Diego`, etc.
- [ ] Compare legacy folders vs Master → delete dupes, relocate personal
- [ ] User decision: delete remaining fishy folders after review

---

## Old NAS library (Phase 2)

- [ ] Review **~1,951** files in `tag_compare_not_in_master.txt` (keepers / personal / non-DJ)
- [ ] Optional: re-run `python dj.py compare` on old folders if reports stale

---

## Engineering / repo

- [ ] **Commit + push** uncommitted work (tag, newmusic, relocate, shazam, bitrate audit, cleanup, `TODO.md`)
- [ ] Watch CI after push
- [ ] Update `AGENT_HANDOFF.md` + `PM_PLAN.md` when scope ships
- [ ] Tech debt: Tier 2 pipeline tests, `lib/__init__.py`, ruff, PowerShell delete helper
- [ ] Optional: `dj.py shazam import` from Shazam CSV
- [ ] Optional: `dj.py audit transcodes` (spectral)

---

## Serato

- [ ] **Paused** — use `--no-serato` until tags and Master are solid
- [ ] Resume: `python dj.py sync serato` when ready

---

## Quick reference — folders

| Folder | Purpose |
|--------|---------|
| `Master/` | Club source of truth (256+ kbps) |
| `NewMusic/` | Drop new downloads → pipeline ingests |
| `Shazam/` | ≤128 legacy + manual Shazam queue |
| `LowQuality/` | 192 kbps archive — review or replace |
| `My Music/A–Z, iTunes, …` | Legacy — pending cleanup |
