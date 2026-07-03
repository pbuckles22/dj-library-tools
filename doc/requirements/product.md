# Product backlog — DJ Library Tools

**Persona:** DJ / library owner managing a club-grade Master library on NAS and mirroring to **Serato** (primary). Rekordbox is sunset / opt-in only.

**Library snapshot (July 2026):** Master ~5,205 tracks (5060 frozen) · NewMusic 0 · LowQuality ~921 · Shazam ~2k manual queue · Serato local mirror ~5059 · Tier 1 tests green.

**Related docs:** [PM_PLAN.md](../../PM_PLAN.md) (phases) · [TODO.md](../../TODO.md) (operational checklist) · [TECH_DEBT.md](../../TECH_DEBT.md) (engineering debt) · [RISKS.md](../../RISKS.md) (operational risks) · [coverage.md](coverage.md) (requirement → test matrix)

---

## Prioritization

| Label | Meaning |
|-------|---------|
| **Now** | Do next on NAS or immediately after current session |
| **Next** | Phase 3 remainder or next sprint of library work |
| **Later** | Backlog — valuable but not blocking current phase |
| **Ongoing** | Repeat whenever trigger condition occurs |

**Status:** Done · Built (CLI ready; NAS run pending) · Backlog

**Coverage rule:** Every acceptance criterion is **Done** with evidence, has an **automated Tier-1 test** (see [coverage.md](coverage.md)), or is an explicit **manual / Tier-2** checklist item. No orphan requirements.

---

## Epic overview

| ID | Epic | Outcome | Priority | Status |
|----|------|---------|----------|--------|
| E01 | Cut policy | Consistent intro cut names; fewer redundant same-song versions | **Now** | Built — NAS run pending |
| E02 | Daily ingest pipeline | New downloads flow NewMusic → Master → Serato with no manual steps | Ongoing | Done |
| E03 | Metadata & tagging | Every club track tagged; Shazam queue cleared over time | Next | Partial |
| E04 | Library quality | Master holds only club-grade audio; fakes and edge cases resolved | Next | Partial |
| E05 | My Music folder hygiene | Top-level My Music is only operational folders; non-DJ content relocated | Later | Partial |
| E06 | Old NAS library review | Legacy folders reconciled; keepers identified | Later | Backlog |
| E07 | DJ app sync | Local Serato mirror matches Master after every material change | **Now** | Partial |
| E08 | Engineering platform | Repo is testable, linted, and safe to extend | Parallel | Partial |
| E09 | Freeze lock | Published Master tracks never altered by pipeline | **Now** | Done |
| E10 | Clash policy | Incoming NewMusic never overwrites Master | **Now** | Done |
| E11 | Stable NAS access | Config paths stay valid across NAS remounts | **Now** | Done |
| E12 | Gig USB | CDJ export volume is never a library source | **Now** | Done |

---

## E01 — Cut policy

**Outcome:** Intro cut filenames use `(Intro Clean)` consistently; extra same-song cut variants removed only when a preferred intro family exists.

### US-CUT-01 — Standardize intro aliases

**As a** DJ library owner, **I want** intro cut suffixes normalized to `(Intro Clean)` **so that** dedupe logic and DJ apps agree on cut naming.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Built — NAS run pending |
| Risk | Low (rename only); see [RISKS.md](../../RISKS.md) |
| Tests | `tests/test_cuts.py` |

**Acceptance criteria**

- [x] Dry-run reports renames without changing files (`test_standardize_dry_run_no_change`)
- [x] Apply renames intro aliases to `(Intro Clean)` (`test_standardize_renames_intro_alias`)
- [x] Already-canonical names are skipped (`test_standardize_skips_already_canonical`)
- [ ] `python dj.py cuts standardize --full --dry-run` reviewed on NAS (~526 renames expected) — **manual**
- [ ] `python dj.py cuts standardize --full` completed on NAS — **manual**
- [ ] Spot-check: renamed files show `(Intro Clean)` in filename — **manual**
- [x] No files deleted from Master during standardize (rename-only behavior)

**Commands**

```bash
python dj.py cuts standardize --full --dry-run
python dj.py cuts standardize --full
```

---

### US-CUT-02 — Narrow dedupe (Intro Clean wins)

**As a** DJ library owner, **I want** redundant cut versions removed when an Intro Clean family exists **so that** Master holds one best intro variant per song, not every pool download.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Built — user approval required before apply |
| Risk | **High** — deletes from Master; see [RISKS.md](../../RISKS.md) |
| Tests | `tests/test_cuts.py` |

**Policy:** Only removes extras when an Intro Clean family cut exists; keeps the best intro variant (~594 deletes expected per handoff 0003). Default `--mode narrow`.

**CLI note:** `--mode strict` (one file per song regardless of intro family) exists in code for experiments only — **not product policy**. Do not run on Master without an explicit new story.

**Acceptance criteria**

- [x] Dry-run writes report and keeps files (`test_dedupe_narrow_dry_run_keeps_files`)
- [x] Report path is `Master/_meta/cut_dedup_report.txt`
- [x] Apply deletes extras when Intro Clean family exists (`test_dedupe_narrow_apply_deletes_extras`)
- [x] Groups without Intro Clean are left alone (`test_dedupe_narrow_no_intro_skips_group`)
- [x] Default mode is `narrow` (product policy)
- [ ] `python dj.py cuts dedupe --full` dry-run completed on NAS — **manual**
- [ ] `Master/_meta/cut_dedup_report.txt` reviewed — **manual**
- [ ] User explicitly approves apply — **manual**
- [ ] `python dj.py cuts dedupe --full --apply` completed — **manual**
- [ ] US-SYNC-02 completed afterward — **manual**

**Commands**

```bash
python dj.py cuts dedupe --full
# Review Master/_meta/cut_dedup_report.txt
python dj.py cuts dedupe --full --apply
```

**Suggested order:** US-CUT-01 first (names match), then US-CUT-02 dry-run → review → apply.

---

## E02 — Daily ingest pipeline

**Outcome:** Drop files in NewMusic; one command ingests, tags, renames, dedupes, syncs Serato, and clears staging.

### US-PIPE-01 — NewMusic → Master pipeline

**As a** DJ library owner, **I want** new downloads processed automatically **so that** I only copy files and run one command.

| Field | Value |
|-------|-------|
| Priority | Ongoing |
| Status | Done |
| Tests | `tests/test_newmusic.py`, `tests/test_cli_pipeline.py` |

**Acceptance criteria**

- [x] Pipeline runs ingest → organize → tag → rename → dedup → Serato sync → NewMusic clear
- [x] `--no-rekordbox` skips Rekordbox; Serato remains default sync target
- [x] `--no-serato` skips Serato sync
- [x] `--no-tag` skips AcoustID step
- [x] `--no-newmusic` skips NewMusic ingest and staging clear
- [x] `--from STEP` starts at `import` | `organize` | `tag` | `rename` | `dedup` | `sync` | `clear`
- [x] `--days N` / `--full` scope organize, tag, rename, dedup steps (default last 1 day)
- [x] Standalone `organize`, `rename`, `dedup` run the same steps as pipeline (MD5 hash-library dedup)
- [x] NewMusic empty after successful validated clear (`test_clear_staging_*`)
- [ ] Serato restarted after sync (manual)

**Commands:** See [TODO.md](../../TODO.md) — Daily section. Prefer `python dj.py pipeline --no-rekordbox`.

---

## E03 — Metadata & tagging

**Outcome:** Master tracks have reliable Artist/Title tags; Shazam folder cleared via manual or assisted workflow.

### US-TAG-01 — AcoustID sweep on Master

**As a** DJ library owner, **I want** untagged Master files identified and tagged via AcoustID **so that** rename and compare tools work reliably.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Done |
| Tests | `tests/test_tag.py` |

**Acceptance criteria**

- [x] `python dj.py tag --full` run on Master
- [x] Zero untagged files remaining in Master
- [x] Dry-run does not write tags (`test_tag_files_dry_run_does_not_write`)
- [x] `--days N` / `--full` scope which untagged files are considered
- [x] `--limit N` processes at most N files (testing / batching)

---

### US-SHAZ-01 — Manual Shazam tagging queue

**As a** DJ library owner, **I want** low-bitrate and unidentified files tagged via Shazam listening **so that** they can re-enter Master with verified metadata.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Backlog (~2k files) |
| Tests | `tests/test_shazam_queue.py` (stage helper only) |

**Policy:** Shazam or verified only — no auto-tag from filename alone.

**Acceptance criteria**

- [x] `python dj.py shazam stage` moves queue-listed files to Shazam folder (`test_stage_shazam_queue_*`)
- [ ] Each batch: listen → tag → move to Master → `rename --full` → `sync serato` — **manual**
- [ ] Queue file `Shazam/shazam_queue.txt` reflects progress — **manual**
- [ ] Shazam folder count trending down — **manual**

**Refs:** [TODO.md](../../TODO.md) — Shazam section.

---

### US-SHAZ-02 — Shazam CSV import (optional)

**As a** DJ library owner, **I want** to import tags from shazam.com/myshazam CSV **so that** bulk tagging is faster than one-by-one listening.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Backlog — not built |
| Engineering | US-ENG-07 |

**Acceptance criteria**

- [ ] `python dj.py shazam import <csv>` maps CSV rows to files in Shazam folder
- [ ] No auto-tag without CSV match or user confirmation
- [ ] Tests cover CSV parsing edge cases

---

## E04 — Library quality

**Outcome:** Master contains only club-grade (≥256 kbps) tracks; marginal files reviewed or replaced.

### US-QUAL-01 — Bitrate tier cleanup

**As a** DJ library owner, **I want** sub-club bitrates moved out of Master **so that** Serato only sees gig-ready files.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Done |
| Tests | `tests/test_bitrate_audit.py` |

**Acceptance criteria**

- [x] `python dj.py audit bitrates` writes a report (no moves by default)
- [x] `--move-shazam` moves ≤128 kbps from Master → Shazam
- [x] `--tier-cleanup` deletes ≤160 kbps; moves 161–192 kbps → LowQuality
- [x] `--dry-run` previews moves/deletes without changing files
- [x] ≤128 kbps → Shazam; ≤160 kbps deleted; 161–192 kbps → LowQuality (ops complete)
- [x] Master ~5,205 tracks at ≥256 kbps

**Commands**

```bash
python dj.py audit bitrates
python dj.py audit bitrates --move-shazam --dry-run
python dj.py audit bitrates --tier-cleanup --dry-run
```

---

### US-QUAL-02 — Review LowQuality archive

**As a** DJ library owner, **I want** 192 kbps tracks reviewed on PA **so that** I re-buy 320k or delete consciously.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Backlog |

**Acceptance criteria**

- [ ] Each entry in `LowQuality/low_quality_manifest.txt` listened or decided — **manual**
- [ ] Re-buys moved to Master; rejects deleted — **manual**
- [ ] `dedup --full` and `sync serato` after batch moves — **manual**

---

### US-QUAL-03 — Transcode audit (fake 320k)

**As a** DJ library owner, **I want** upscaled 128k files detected **so that** I do not play transcodes on club PA.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Backlog — not built |
| Engineering | US-ENG-08 |

**Acceptance criteria**

- [ ] `python dj.py audit transcodes` reports spectral cutoff suspects
- [ ] Report reviewable without modifying Master
- [ ] User approves any moves/deletes separately

---

### US-QUAL-04 — Fix Master edge cases

**As a** DJ library owner, **I want** odd sample rates and mono dupes resolved **so that** library metadata is consistent.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Backlog |

**Acceptance criteria**

- [ ] 1 file at 32 kHz sample rate fixed or removed — **manual**
- [ ] 4 mono files resolved (3× LMFAO dupes + 1 Goo Goo Dolls) — **manual**

---

## E05 — My Music folder hygiene

**Outcome:** `My Music/` top level contains only `Master`, `NewMusic`, `Shazam`, `LowQuality`.

### US-CLEAN-01 — Junk and empty dir cleanup

**As a** DJ library owner, **I want** junk files and empty dirs removed under My Music **so that** only operational folders remain.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Done |
| Tests | `tests/test_cleanup.py` |

**Acceptance criteria**

- [x] `python dj.py cleanup` removes junk, artwork, and empty dirs under My Music
- [x] `--dry-run` reports deletes without removing files
- [x] Legacy folders that still contain audio are reported as fishy, not auto-deleted
- [x] Junk, artwork, empty dirs removed on NAS (9,751 files, 5,436 dirs) — **ops evidence**

---

### US-CLEAN-03 — Relocate non-DJ Master content

**As a** DJ library owner, **I want** WAV, Persian/regional, and comedy files moved out of Master **so that** the flat DJ library holds only club tracks.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Done |
| Tests | `tests/test_relocate.py`, `tests/test_cli_commands.py` |

**Acceptance criteria**

- [x] `python dj.py relocate` classifies WAV / Persian-keyword / comedy-keyword files
- [x] Matching files move from Master root to parent (`My Music/`)
- [x] DJ tracks (no match) stay in Master
- [x] `--dry-run` previews moves without relocating files
- [x] Name collisions get a unique destination (`stem (N).ext`)

**Commands**

```bash
python dj.py relocate --dry-run
python dj.py relocate
```

---

### US-CLEAN-02 — Review legacy audio folders

**As a** DJ library owner, **I want** 34 legacy folders reconciled with Master **so that** NAS storage is clean and nothing unique is lost.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Backlog |
| Risk | Medium — deletion requires review; see [RISKS.md](../../RISKS.md) |

**Acceptance criteria**

- [ ] `Master/_meta/cleanup_report.txt` reviewed — **manual**
- [ ] iTunes (~1,319 files) and letter folders compared vs Master — **manual**
- [ ] Dupes deleted; personal tracks relocated or kept by user decision — **manual**
- [ ] User sign-off before deleting remaining legacy folders — **manual**

**Refs:** [TODO.md](../../TODO.md) — My Music folder cleanup.

---

## E06 — Old NAS library review

**Outcome:** Files in old folders that are not in Master are classified (keeper / personal / delete).

### US-OLD-01 — Review not-in-Master report

**As a** DJ library owner, **I want** ~1,951 unmatched files classified **so that** I keep personal music and discard true junk.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Backlog |
| Risk | High — do not bulk-delete; see [RISKS.md](../../RISKS.md) |

**Acceptance criteria**

- [ ] `tag_compare_not_in_master.txt` reviewed file-by-file or by folder — **manual**
- [ ] Keepers moved or documented; deletes user-approved only — **manual**
- [ ] Optional: re-run `python dj.py compare` if reports stale — **manual**

**Refs:** [notes/DEDUP_OLD_LIBRARY.md](../../notes/DEDUP_OLD_LIBRARY.md)

---

### US-OLD-02 — Delete confirmed old-folder dupes

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Done |
| Tests | `tests/test_compare.py` |

**Acceptance criteria**

- [x] 16,798 files matched Master and deleted from old folders
- [x] Compare reports in-Master vs not-in-Master (`tests/test_compare.py`)

---

## E07 — DJ app sync

**Outcome:** Serato local mirror reflects Master after every material library change. Rekordbox is opt-in legacy.

### US-SYNC-01 — Rekordbox sync (legacy opt-in)

**As a** DJ library owner, **I want** Rekordbox updated when I still use it **so that** the legacy mirror matches Master.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Built — opt-in only |
| Tests | `tests/test_sync_refresh.py`, `tests/test_cli_commands.py` |

**Acceptance criteria**

- [x] `python dj.py sync rekordbox` copies Master → configured Rekordbox path
- [x] `python dj.py sync all` includes Rekordbox and Serato
- [x] Pipeline skips Rekordbox when `--no-rekordbox`
- [x] `python dj.py pull` copies new/changed files NAS Master → local Rekordbox folder
- [x] `pull --dry-run` previews without copying
- [x] `pull --prune` also deletes local files no longer in Master
- [x] `python dj.py refresh --target rekordbox` pull+verify for Rekordbox (opt-in)
- [ ] Rekordbox restarted after live sync — **manual**

---

### US-SYNC-02 — Serato sync (primary)

**As a** DJ library owner, **I want** Serato local mirror updated from Master **so that** I DJ from local files only (no NAS yellow triangles).

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Done |
| Tests | `tests/test_sync_refresh.py`, `tests/test_cli_pipeline.py` |

**Acceptance criteria**

- [x] `python dj.py sync serato` copies Master → `serato_latest_import`
- [x] `python dj.py sync all` includes Serato
- [x] `python dj.py refresh` defaults to `--target serato`
- [x] Refresh copies missing tracks into local mirror (retries over flaky SMB; default `--retries 3`)
- [x] Pipeline includes Serato unless `--no-serato`
- [ ] Serato drives: only `Latest Import`; analyze after sync — **manual** (see [notes/SERATO_SETUP.md](../../notes/SERATO_SETUP.md))

---

## E08 — Engineering platform

**Outcome:** CLI is tested, linted, and safe to extend; Windows and macOS workflows supported.

| ID | Story | Priority | Status | TECH_DEBT |
|----|-------|----------|--------|-----------|
| US-ENG-01 | Tier 2 pipeline integration tests | Parallel | Backlog | #2 |
| US-ENG-02 | `lib/__init__.py` + optional editable install | Parallel | Backlog | #3 |
| US-ENG-03 | ruff/format merge-ready gate | Parallel | Backlog | #4 |
| US-ENG-04 | PowerShell delete helper for compare reports | Parallel | Backlog | #5 |
| US-ENG-05 | Deep config merge | Later | Backlog | #6 |
| US-ENG-06 | Tier 1 test suite (lib + dj.py) | Parallel | Done | — |
| US-ENG-07 | `dj.py shazam import` | Later | Backlog | #7 |
| US-ENG-08 | `dj.py audit transcodes` | Later | Backlog | — |
| US-ENG-09 | ≥80% code coverage (`lib/` + `dj.py`) | Parallel | Done (81%) | — |

**US-ENG-06 acceptance criteria**

- [x] `python -m pytest -q` green
- [x] CI on Python 3.10 / 3.12 / 3.13
- [x] Requirement IDs mapped in [coverage.md](coverage.md)

Engineering items stay ranked in [TECH_DEBT.md](../../TECH_DEBT.md); this table provides story IDs for traceability.

---

## E09 — Freeze lock

**Outcome:** Tracks published to Master are locked; organize / rename / dedup never alter them.

*Promoted from inbox (gemini freeze-lock notes) and Serato-first architecture.*

### US-FREEZE-01 — Mark and query frozen tracks

**As a** DJ library owner, **I want** published tracks locked as done **so that** later pipeline runs never rename or delete them.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Done |
| Tests | `tests/test_freeze.py` |

**Acceptance criteria**

- [x] `freeze mark` records path + sha256 in `Master/_meta/frozen.json`
- [x] `freeze unmark` removes the lock
- [x] `freeze status` reports frozen / total counts
- [x] `freeze mark-all` freezes every audio file in Master root
- [x] macOS may also set xattr `user.djtools.status=done` (best-effort)

---

### US-FREEZE-02 — Pipeline respects freeze

**As a** DJ library owner, **I want** frozen tracks skipped by mutate steps **so that** Master published files stay sacred.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Done |
| Tests | `tests/test_freeze.py` |

**Acceptance criteria**

- [x] Rename leaves frozen files untouched
- [x] Organize leaves frozen non-audio untouched
- [x] Dedup never deletes a frozen track (frozen wins keeper priority)

---

## E10 — Clash policy

**Outcome:** On any clash between NewMusic and Master, incoming loses; Master is never overwritten.

*Promoted from Serato-first clash policy / Master sacred rule.*

### US-CLASH-01 — Incoming loses

**As a** DJ library owner, **I want** conflicting NewMusic imports rejected **so that** published Master tracks are never altered by new downloads.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Done |
| Tests | `tests/test_staging_clash.py` |

**Acceptance criteria**

- [x] Filename exists in Master → delete incoming, keep Master
- [x] MD5 matches a frozen Master track → delete incoming
- [x] Artist+Title matches a frozen Master track → delete incoming
- [x] Rejections append to `Master/_meta/rejected_imports.log`
- [x] Non-clashing files move into Master

---

## E11 — Stable NAS access

**Outcome:** Tools and Lexicon always use a stable symlink path, not a shifting `/Volumes/buckles*`.

*Promoted from inbox `master-pool-symlink.sh` / launchd template → `scripts/update-nas-link.sh`.*

### US-NAS-01 — DJ_Master_Link resolution

**As a** DJ library owner, **I want** Master paths resolved via `~/Music/DJ_Master_Link` **so that** remounts do not break config.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Done |
| Tests | `tests/test_config.py` |

**Acceptance criteria**

- [x] Config resolves `nas_link`, `master`, `newmusic`, `lexicon_root`, `serato_latest_import`, `gig_usb`
- [x] `require_master` invokes NAS link refresh on macOS before path checks
- [x] `scripts/update-nas-link.sh` creates `~/Music/DJ_Master_Link` → mounted `buckles*`
- [x] `scripts/install-nas-link-launchd.sh` + `scripts/launchd/local.dj.nas-link.plist` install the watcher
- [ ] launchd `local.dj.nas-link` active on this Mac — **manual / machine setup**

---

## E12 — Gig USB

**Outcome:** Gig stick is Serato export only; never a library source.

*Promoted from Serato/USB setup notes.*

### US-USB-01 — Export-only volume

**As a** DJ library owner, **I want** the gig USB configured as export-only **so that** Serato never treats the stick as the music library.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Done |
| Tests | `tests/test_config.py` |

**Acceptance criteria**

- [x] Config exposes `gig_usb` as `/Volumes/DJ_USB` on Mac
- [x] Serato library path is `serato_latest_import` (local), not `gig_usb`
- [ ] Volume labeled `DJ_USB` (exFAT) used only for Serato export — **manual**

---

## Shipped (Phase 2 and foundation)

| Story | Summary |
|-------|---------|
| US-OLD-02 | 16,798 old-folder dupes deleted; `compare` / `--md5` |
| US-PIPE-01 | NewMusic pipeline + flags + standalone organize/rename/dedup |
| US-TAG-01 | AcoustID full sweep — 0 untagged in Master |
| US-QUAL-01 | Bitrate audit report / `--move-shazam` / `--tier-cleanup` |
| US-CLEAN-01 | Junk/empty cleanup under My Music |
| US-CLEAN-03 | Relocate WAV / Persian / comedy out of Master |
| US-ENG-06 | Tier 1 tests; CI; SDD pre-commit gate |
| US-ENG-09 | ≥80% code coverage (`lib/` + `dj.py`) |
| US-FREEZE-01/02 | Freeze lock + pipeline respect |
| US-CLASH-01 | Incoming loses on clash |
| US-NAS-01 | Stable NAS link resolution + launchd install scripts |
| US-USB-01 | Gig USB export-only config |
| US-SYNC-01 | Rekordbox opt-in: `sync` / `pull` / `refresh --target rekordbox` |
| US-SYNC-02 | Serato primary: `sync serato` / `refresh` default |
| US-SHAZ-01 | `shazam stage` helper (manual listen/tag backlog) |

---

## Now / Next / Later summary

**Now**

1. US-CUT-01 — `cuts standardize --full` (dry-run first) — **manual NAS**
2. US-CUT-02 — `cuts dedupe --full` → review report → user-approved `--apply` — **manual NAS**
3. US-SYNC-02 — Serato drive cleanup + analyze — **manual**

**Next**

- US-SHAZ-01 — Shazam manual queue (listen/tag batches)
- US-QUAL-02 — LowQuality review
- US-QUAL-04 — Master edge cases

**Later**

- US-CLEAN-02 — legacy folder review
- US-OLD-01 — not-in-Master report
- US-SYNC-01 — Rekordbox live use (CLI already built)
- US-SHAZ-02, US-QUAL-03, US-ENG-* backlog

**Ongoing**

- US-PIPE-01 — pipeline when NewMusic has files (`--no-rekordbox` preferred)
