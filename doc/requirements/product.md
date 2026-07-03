# Product backlog — DJ Library Tools

**Persona:** DJ / library owner managing a club-grade Master library on NAS and mirroring to Rekordbox (Serato paused).

**Library snapshot (June 2026):** Master ~5,205 tracks · NewMusic 0 · LowQuality ~921 · Shazam ~2k manual queue · Rekordbox synced · 66 Tier 1 tests green.

**Related docs:** [PM_PLAN.md](../../PM_PLAN.md) (phases) · [TODO.md](../../TODO.md) (operational checklist) · [TECH_DEBT.md](../../TECH_DEBT.md) (engineering debt) · [RISKS.md](../../RISKS.md) (operational risks)

---

## Prioritization

| Label | Meaning |
|-------|---------|
| **Now** | Do next on NAS or immediately after current session |
| **Next** | Phase 3 remainder or next sprint of library work |
| **Later** | Backlog — valuable but not blocking current phase |
| **Ongoing** | Repeat whenever trigger condition occurs |

**Status:** Done · Built (CLI ready; NAS run pending) · Backlog

---

## Epic overview

| ID | Epic | Outcome | Priority | Status |
|----|------|---------|----------|--------|
| E01 | Cut policy | Consistent intro cut names; fewer redundant same-song versions | **Now** | Built — NAS run pending |
| E02 | Daily ingest pipeline | New downloads flow NewMusic → Master → Rekordbox with no manual steps | Ongoing | Done |
| E03 | Metadata & tagging | Every club track tagged; Shazam queue cleared over time | Next | Partial |
| E04 | Library quality | Master holds only club-grade audio; fakes and edge cases resolved | Next | Partial |
| E05 | My Music folder hygiene | Top-level My Music is only operational folders | Later | Partial |
| E06 | Old NAS library review | Legacy folders reconciled; keepers identified | Later | Backlog |
| E07 | DJ app sync | Local mirrors match Master after every material change | **Now** | Partial |
| E08 | Engineering platform | Repo is testable, linted, and safe to extend | Parallel | Partial |

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

**Acceptance criteria**

- [ ] `python dj.py cuts standardize --full --dry-run` reviewed (~526 renames expected)
- [ ] `python dj.py cuts standardize --full` completed on NAS
- [ ] Spot-check: renamed files show `(Intro Clean)` in filename
- [ ] No files deleted from Master

**Commands**

```powershell
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

**Policy:** Only removes extras when an Intro Clean family cut exists; keeps the best intro variant (~594 deletes expected per handoff 0003).

**Acceptance criteria**

- [ ] `python dj.py cuts dedupe --full` dry-run completed
- [ ] `Master\_meta\cut_dedup_report.txt` reviewed
- [ ] User explicitly approves apply
- [ ] `python dj.py cuts dedupe --full --apply` completed
- [ ] US-SYNC-01 completed afterward

**Commands**

```powershell
python dj.py cuts dedupe --full
# Review Master\_meta\cut_dedup_report.txt
python dj.py cuts dedupe --full --apply
```

**Suggested order:** US-CUT-01 first (names match), then US-CUT-02 dry-run → review → apply.

---

## E02 — Daily ingest pipeline

**Outcome:** Drop files in NewMusic; one command ingests, tags, renames, dedupes, syncs, and clears staging.

### US-PIPE-01 — NewMusic → Master pipeline

**As a** DJ library owner, **I want** new downloads processed automatically **so that** I only copy files and run one command.

| Field | Value |
|-------|-------|
| Priority | Ongoing |
| Status | Done |

**Acceptance criteria**

- [x] `python dj.py pipeline --no-serato` runs ingest → organize → tag → rename → dedup → Rekordbox sync → NewMusic clear
- [x] NewMusic empty after successful run
- [ ] Rekordbox restarted after sync (manual)

**Commands:** See [TODO.md](../../TODO.md) — Daily section.

---

## E03 — Metadata & tagging

**Outcome:** Master tracks have reliable Artist/Title tags; Shazam folder cleared via manual or assisted workflow.

### US-TAG-01 — AcoustID sweep on Master

**As a** DJ library owner, **I want** untagged Master files identified and tagged via AcoustID **so that** rename and compare tools work reliably.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Done |

**Acceptance criteria**

- [x] `python dj.py tag --full` run on Master
- [x] Zero untagged files remaining in Master

---

### US-SHAZ-01 — Manual Shazam tagging queue

**As a** DJ library owner, **I want** low-bitrate and unidentified files tagged via Shazam listening **so that** they can re-enter Master with verified metadata.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Backlog (~2k files) |

**Policy:** Shazam or verified only — no auto-tag from filename alone.

**Acceptance criteria**

- [ ] Each batch: listen → tag → move to Master → `rename --full` → `sync rekordbox`
- [ ] Queue file `Shazam\shazam_queue.txt` reflects progress
- [ ] Shazam folder count trending down

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

**As a** DJ library owner, **I want** sub-club bitrates moved out of Master **so that** Rekordbox only sees gig-ready files.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Done |

**Acceptance criteria**

- [x] ≤128 kbps → Shazam; ≤160 kbps deleted; 161–192 kbps → LowQuality
- [x] Master ~5,205 tracks at ≥256 kbps

---

### US-QUAL-02 — Review LowQuality archive

**As a** DJ library owner, **I want** 192 kbps tracks reviewed on PA **so that** I re-buy 320k or delete consciously.

| Field | Value |
|-------|-------|
| Priority | Next |
| Status | Backlog |

**Acceptance criteria**

- [ ] Each entry in `LowQuality\low_quality_manifest.txt` listened or decided
- [ ] Re-buys moved to Master; rejects deleted
- [ ] `dedup --full` and `sync rekordbox` after batch moves

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

- [ ] 1 file at 32 kHz sample rate fixed or removed
- [ ] 4 mono files resolved (3× LMFAO dupes + 1 Goo Goo Dolls)

---

## E05 — My Music folder hygiene

**Outcome:** `My Music/` top level contains only `Master`, `NewMusic`, `Shazam`, `LowQuality`.

### US-CLEAN-01 — Junk and empty dir cleanup

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Done |

**Acceptance criteria**

- [x] Junk, artwork, empty dirs removed (9,751 files, 5,436 dirs)

---

### US-CLEAN-02 — Review legacy audio folders

**As a** DJ library owner, **I want** 34 legacy folders reconciled with Master **so that** NAS storage is clean and nothing unique is lost.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Backlog |
| Risk | Medium — deletion requires review; see [RISKS.md](../../RISKS.md) |

**Acceptance criteria**

- [ ] `Master\_meta\cleanup_report.txt` reviewed
- [ ] iTunes (~1,319 files) and letter folders compared vs Master
- [ ] Dupes deleted; personal tracks relocated or kept by user decision
- [ ] User sign-off before deleting remaining legacy folders

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

- [ ] `tag_compare_not_in_master.txt` reviewed file-by-file or by folder
- [ ] Keepers moved or documented; deletes user-approved only
- [ ] Optional: re-run `python dj.py compare` if reports stale

**Refs:** [notes/DEDUP_OLD_LIBRARY.md](../../notes/DEDUP_OLD_LIBRARY.md)

---

### US-OLD-02 — Delete confirmed old-folder dupes

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Done |

**Acceptance criteria**

- [x] 16,798 files matched Master and deleted from old folders

---

## E07 — DJ app sync

**Outcome:** Rekordbox (and eventually Serato) local mirrors reflect Master after every material library change.

### US-SYNC-01 — Rekordbox sync after cut ops

**As a** DJ library owner, **I want** Rekordbox updated after cut standardize/dedupe **so that** my DJ library matches Master on disk.

| Field | Value |
|-------|-------|
| Priority | **Now** |
| Status | Backlog — run after E01 |

**Acceptance criteria**

- [ ] `python dj.py sync rekordbox` run after US-CUT-01 and US-CUT-02
- [ ] Rekordbox restarted
- [ ] Spot-check cut variants visible and correct in Rekordbox

---

### US-SYNC-02 — Resume Serato sync

**As a** DJ library owner, **I want** Serato mirror re-enabled **so that** both DJ apps stay in sync when I use Serato again.

| Field | Value |
|-------|-------|
| Priority | Later |
| Status | Paused |

**Acceptance criteria**

- [ ] Tags and Master stable (E01, E03 substantially complete)
- [ ] `python dj.py sync serato` or full pipeline without `--no-serato`
- [ ] Serato restarted; library spot-checked

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

**US-ENG-06 acceptance criteria**

- [x] `python -m pytest -q` — 66 tests green
- [x] CI on Python 3.10 / 3.12 / 3.13

Engineering items stay ranked in [TECH_DEBT.md](../../TECH_DEBT.md); this table provides story IDs for traceability.

---

## Shipped (Phase 2 and foundation)

| Story | Summary |
|-------|---------|
| US-OLD-02 | 16,798 old-folder dupes deleted |
| US-PIPE-01 | NewMusic pipeline with validated clear |
| US-TAG-01 | AcoustID full sweep — 0 untagged in Master |
| US-QUAL-01 | Bitrate tier cleanup complete |
| US-CLEAN-01 | Junk/empty cleanup under My Music |
| US-ENG-06 | 66 Tier 1 tests; CI; SDD pre-commit gate |
| — | `dj.py` helpers: relocate, cleanup, audit bitrates, shazam stage, compare |

---

## Now / Next / Later summary

**Now**

1. US-CUT-01 — `cuts standardize --full` (dry-run first)
2. US-CUT-02 — `cuts dedupe --full` → review report → user-approved `--apply`
3. US-SYNC-01 — `sync rekordbox` + restart Rekordbox

**Next**

- US-SHAZ-01 — Shazam manual queue
- US-QUAL-02 — LowQuality review
- US-QUAL-04 — Master edge cases

**Later**

- US-CLEAN-02 — legacy folder review
- US-OLD-01 — not-in-Master report
- US-SYNC-02 — Serato resume
- US-SHAZ-02, US-QUAL-03, US-ENG-* backlog

**Ongoing**

- US-PIPE-01 — pipeline when NewMusic has files
